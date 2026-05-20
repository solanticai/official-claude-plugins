#!/usr/bin/env node
/**
 * virustotal-audit.mjs
 *
 * Scans every plugin listed in `.claude-plugin/marketplace.json` against
 * VirusTotal's public API v3 and renders human- and machine-readable reports.
 *
 * Strategy: tarball-per-plugin + hash-first dedup.
 *   1. `tar czf /tmp/<name>.tar.gz <category>/<name>` — one archive per plugin.
 *   2. Compute local SHA-256.
 *   3. GET /files/{sha256} — if known, reuse prior scan (1 request).
 *   4. If 404, POST /files + poll /analyses/{id} until completed (2–4 requests).
 *   5. Sleep 20s between all VT calls — the public tier is 4 req/min.
 *
 * Outputs:
 *   - .virustotal/<plugin>.json    — raw normalised payload per plugin
 *   - <category>/<plugin>/VIRUSTOTAL.md — per-plugin markdown summary
 *   - SECURITY.md                   — repo-wide policy + summary table (table only is auto-updated)
 *
 * Auth: reads process.env.VT_API_KEY. The GitHub Actions workflow maps this
 * from the `VIRUS_TOTAL_API_KEY` org secret.
 *
 * Usage (CI):
 *   VT_API_KEY=... node scripts/virustotal-audit.mjs
 *
 * Exit codes:
 *   0 — scan completed
 *   1 — missing API key or fatal error
 */

import { readFile, writeFile, mkdir, stat } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const repoRoot = resolve(dirname(__filename), "..");

// ---------- tunables ----------
const API_BASE = "https://www.virustotal.com/api/v3";
const RATE_SLEEP_MS = 20_000;          // 20s between VT calls — public tier is 4/min
const MAX_UPLOAD_BYTES = 30 * 1024 * 1024;
const POLL_MAX_ATTEMPTS = 6;
const VT_SUMMARY_START = "<!-- vt-summary:start -->";
const VT_SUMMARY_END = "<!-- vt-summary:end -->";

const API_KEY = process.env.VT_API_KEY;
if (!API_KEY) {
  console.error("✗ VT_API_KEY is not set.");
  process.exit(1);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const today = () => new Date().toISOString().slice(0, 10);
const nowIso = () => new Date().toISOString();

// ---------- HTTP helpers ----------

async function vtFetch(path, init = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const headers = { "x-apikey": API_KEY, ...(init.headers || {}) };
  const res = await fetch(url, { ...init, headers });
  await sleep(RATE_SLEEP_MS);
  return res;
}

async function lookupHash(sha256) {
  const res = await vtFetch(`/files/${sha256}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`hash lookup failed ${res.status}: ${await res.text()}`);
  return (await res.json()).data;
}

async function uploadFile(filePath) {
  const buf = await readFile(filePath);
  const size = buf.length;
  if (size > MAX_UPLOAD_BYTES) {
    throw new Error(`tarball exceeds ${MAX_UPLOAD_BYTES} bytes: ${size}`);
  }
  const form = new FormData();
  form.append("file", new Blob([buf]), filePath.split("/").pop());
  const res = await vtFetch(`/files`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`upload failed ${res.status}: ${await res.text()}`);
  return (await res.json()).data.id;
}

async function pollAnalysis(analysisId) {
  for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
    const res = await vtFetch(`/analyses/${analysisId}`);
    if (!res.ok) throw new Error(`analysis poll failed ${res.status}: ${await res.text()}`);
    const body = await res.json();
    if (body.data.attributes.status === "completed") {
      return body;
    }
  }
  throw new Error(`analysis ${analysisId} did not complete after ${POLL_MAX_ATTEMPTS} polls`);
}

// ---------- tarball + hash ----------

function makeTarball(pluginName, sourcePath) {
  const tarPath = `/tmp/anthril-plugin-${pluginName}.tar.gz`;
  // sourcePath is the marketplace `source` like "./engineering/devops"; strip leading "./".
  const rel = sourcePath.replace(/^\.\//, "");
  execFileSync("tar", ["czf", tarPath, "-C", repoRoot, rel], {
    stdio: ["ignore", "ignore", "inherit"],
  });
  return tarPath;
}

async function sha256File(path) {
  const buf = await readFile(path);
  return createHash("sha256").update(buf).digest("hex");
}

// ---------- normalise VT response ----------

function normalise(data, { pluginName, sourcePath, sha256, sizeBytes, scanSource }) {
  const attrs = data?.attributes ?? {};
  const stats = attrs.last_analysis_stats ?? { harmless: 0, malicious: 0, suspicious: 0, undetected: 0, timeout: 0 };
  const totalEngines = Object.values(stats).reduce((a, b) => a + (b || 0), 0);
  return {
    schema_version: "1.0",
    scanned_at: nowIso(),
    scan_source: scanSource, // "hash-lookup" | "upload"
    tarball: {
      path: sourcePath.replace(/^\.\//, ""),
      sha256,
      size_bytes: sizeBytes,
    },
    detections: {
      malicious: stats.malicious ?? 0,
      suspicious: stats.suspicious ?? 0,
      harmless: stats.harmless ?? 0,
      undetected: stats.undetected ?? 0,
      timeout: stats.timeout ?? 0,
      total_engines: totalEngines,
    },
    reputation: attrs.reputation ?? 0,
    last_analysis_date: attrs.last_analysis_date ?? null,
    gui_url: `https://www.virustotal.com/gui/file/${sha256}`,
    engine_results: Object.entries(attrs.last_analysis_results ?? {}).map(([name, r]) => ({
      engine: name,
      category: r.category,
      result: r.result,
    })),
  };
}

// ---------- renderers ----------

function renderPerPluginMd(pluginName, report) {
  const d = report.detections;
  const flagged = d.malicious + d.suspicious;
  const verdict = flagged === 0 ? "clean" : `${flagged} flagged`;
  const scanDate = report.last_analysis_date
    ? new Date(report.last_analysis_date * 1000).toISOString().slice(0, 10)
    : report.scanned_at.slice(0, 10);

  const flaggedEngines = report.engine_results.filter((e) => e.category === "malicious" || e.category === "suspicious");
  const flaggedTable =
    flaggedEngines.length === 0
      ? "_No engine flagged this file._"
      : [
          "| Engine | Category | Result |",
          "|---|---|---|",
          ...flaggedEngines.map((e) => `| ${e.engine} | ${e.category} | ${e.result ?? "—"} |`),
        ].join("\n");

  return `# VirusTotal — ${pluginName}

**Last scan:** ${scanDate} · **Verdict:** ${verdict}
**Detections:** ${d.malicious} malicious · ${d.suspicious} suspicious · ${d.harmless} harmless · ${d.undetected} undetected (of ${d.total_engines} engines)
**Reputation:** ${report.reputation}
**Tarball SHA-256:** \`${report.tarball.sha256}\`
**Full report:** ${report.gui_url}

## Engine results

${flaggedTable}

_Scan refreshed weekly. Cadence and policy: [SECURITY.md](../../SECURITY.md)._
`;
}

function renderSummaryTable(allReports) {
  const rows = allReports
    .sort((a, b) => a.pluginName.localeCompare(b.pluginName))
    .map((r) => {
      const d = r.report.detections;
      const flagged = d.malicious + d.suspicious;
      const dateStr = r.report.last_analysis_date
        ? new Date(r.report.last_analysis_date * 1000).toISOString().slice(0, 10)
        : r.report.scanned_at.slice(0, 10);
      return `| ${r.pluginName} | ${flagged} / ${d.total_engines} | ${dateStr} | [detail](${r.report.tarball.path}/VIRUSTOTAL.md) |`;
    });
  return [
    `## Latest scan — ${today()}`,
    "",
    "| Plugin | Detections | Last scan | Report |",
    "|---|---:|---|---|",
    ...rows,
  ].join("\n");
}

async function updateSecurityMd(summaryBlock) {
  const path = join(repoRoot, "SECURITY.md");
  let body;
  try {
    body = await readFile(path, "utf8");
  } catch {
    // First run — the file was created as part of this change; bail out loud.
    throw new Error(`SECURITY.md not found at ${path}`);
  }
  const start = body.indexOf(VT_SUMMARY_START);
  const end = body.indexOf(VT_SUMMARY_END);
  if (start === -1 || end === -1) {
    throw new Error("SECURITY.md is missing the vt-summary:start/end markers.");
  }
  const before = body.slice(0, start + VT_SUMMARY_START.length);
  const after = body.slice(end);
  const next = `${before}\n${summaryBlock}\n${after}`;
  await writeFile(path, next);
}

// ---------- main ----------

async function scanPlugin(pluginName, sourcePath) {
  const tarballPath = makeTarball(pluginName, sourcePath);
  const sizeBytes = (await stat(tarballPath)).size;
  const sha256 = await sha256File(tarballPath);

  let data = await lookupHash(sha256);
  let scanSource = "hash-lookup";

  if (!data) {
    if (sizeBytes > MAX_UPLOAD_BYTES) {
      console.warn(`⚠ ${pluginName}: tarball ${sizeBytes}B exceeds ${MAX_UPLOAD_BYTES}B; skipping upload`);
      return null;
    }
    const analysisId = await uploadFile(tarballPath);
    await pollAnalysis(analysisId);
    data = await lookupHash(sha256);
    scanSource = "upload";
    if (!data) throw new Error(`post-upload hash lookup still returned null for ${sha256}`);
  }

  return normalise(data, { pluginName, sourcePath, sha256, sizeBytes, scanSource });
}

async function main() {
  const marketplace = JSON.parse(
    await readFile(join(repoRoot, ".claude-plugin", "marketplace.json"), "utf8"),
  );
  const plugins = marketplace.plugins
    .filter((p) => typeof p.name === "string" && typeof p.source === "string")
    .map((p) => ({ name: p.name, source: p.source }));

  await mkdir(join(repoRoot, ".virustotal"), { recursive: true });

  const allReports = [];
  for (const { name: pluginName, source: sourcePath } of plugins) {
    console.log(`→ scanning ${pluginName}`);
    try {
      const report = await scanPlugin(pluginName, sourcePath);
      if (!report) continue;
      await writeFile(
        join(repoRoot, ".virustotal", `${pluginName}.json`),
        `${JSON.stringify(report, null, 2)}\n`,
      );
      await writeFile(
        join(repoRoot, sourcePath.replace(/^\.\//, ""), "VIRUSTOTAL.md"),
        renderPerPluginMd(pluginName, report),
      );
      allReports.push({ pluginName, report });
      const d = report.detections;
      console.log(`  ✓ ${pluginName}: ${d.malicious + d.suspicious}/${d.total_engines} flagged (${report.scan_source})`);
    } catch (err) {
      console.error(`  ✗ ${pluginName}: ${err.message}`);
    }
  }

  if (allReports.length > 0) {
    await updateSecurityMd(renderSummaryTable(allReports));
    console.log(`\n✓ Updated SECURITY.md summary with ${allReports.length} plugin(s).`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
