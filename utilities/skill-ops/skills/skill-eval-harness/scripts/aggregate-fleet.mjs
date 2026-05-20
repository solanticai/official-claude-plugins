#!/usr/bin/env node
// aggregate-fleet.mjs — collate audits/<date>/judge/results/*.json into a
// fleet judge report (markdown) and JSON summary.
//
// Usage:
//   node aggregate-fleet.mjs <results-dir> <output-dir>
//
// Output:
//   <output-dir>/fleet-judge.md   — human-readable report
//   <output-dir>/fleet-judge.json — JSON aggregate

import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const resultsDir = process.argv[2];
const outDir = process.argv[3];
if (!resultsDir || !outDir) {
  console.error("usage: aggregate-fleet.mjs <results-dir> <output-dir>");
  process.exit(2);
}

const files = readdirSync(resultsDir).filter(f => f.endsWith(".json")).sort();
const records = [];
const parseErrors = [];

for (const f of files) {
  const raw = readFileSync(join(resultsDir, f), "utf8");
  try {
    records.push(JSON.parse(raw));
  } catch (err) {
    parseErrors.push({ file: f, error: err.message });
  }
}

const summary = {
  total_skills: records.length,
  parse_errors: parseErrors.length,
  activation: {
    total_cases: 0,
    pass: 0,
    fail: 0,
    by_skill_pass_rate: {}
  },
  judge: {
    pass: 0,
    partial: 0,
    fail: 0,
    skipped: 0,
    by_verdict: {}
  }
};

const skillSummaries = [];

for (const r of records) {
  const acts = r.activation_results || [];
  const aPass = acts.filter(a => a.pass).length;
  summary.activation.total_cases += acts.length;
  summary.activation.pass += aPass;
  summary.activation.fail += acts.length - aPass;
  summary.activation.by_skill_pass_rate[r.skill] = `${aPass}/${acts.length}`;

  const judge = r.judge_result || {};
  const verdict = judge.status === "skipped" ? "skipped" : (judge.verdict || "unknown");
  summary.judge[verdict] = (summary.judge[verdict] || 0) + 1;
  summary.judge.by_verdict[r.skill] = verdict;

  skillSummaries.push({
    skill: r.skill,
    activation_pass_rate: `${aPass}/${acts.length}`,
    activation_failures: acts.filter(a => !a.pass).map(a => a.id),
    judge_verdict: verdict,
    judge_notes: (judge.notes || "").slice(0, 240),
    judge_criteria_met: (judge.criterion_results || []).filter(c => c.met).length,
    judge_criteria_total: (judge.criterion_results || []).length
  });
}

skillSummaries.sort((a, b) => {
  // Sort: judge failures first, then partials, then passes, then skipped.
  const order = { fail: 0, partial: 1, pass: 2, skipped: 3, unknown: 4 };
  return (order[a.judge_verdict] ?? 5) - (order[b.judge_verdict] ?? 5);
});

// Render markdown report.
const md = [];
md.push("# Fleet Judge Report — 2026-05-20");
md.push("");
md.push("LLM-as-judge run across every skill in the marketplace. Each skill received one Agent (subagent_type=general-purpose, fresh context) that performed two tasks:");
md.push("");
md.push("1. **Activation classification** — verify the 5 activation test cases (3 positive + 2 negative) from the skill's `evals/suite.yaml`.");
md.push("2. **Functional judge** — read the skill's `examples/*.md` artefact and grade it against the suite's `judge_criteria`.");
md.push("");
md.push("## Fleet summary");
md.push("");
md.push(`- **Total skills judged:** ${summary.total_skills} / 67`);
md.push(`- **Activation cases:** ${summary.activation.pass} / ${summary.activation.total_cases} pass (${((summary.activation.pass / summary.activation.total_cases) * 100).toFixed(1)}%)`);
md.push(`- **Judge verdicts:**`);
md.push(`  - pass: ${summary.judge.pass || 0}`);
md.push(`  - partial: ${summary.judge.partial || 0}`);
md.push(`  - fail: ${summary.judge.fail || 0}`);
md.push(`  - skipped (no example artefact): ${summary.judge.skipped || 0}`);
if (summary.judge.unknown) md.push(`  - unknown: ${summary.judge.unknown}`);
if (parseErrors.length > 0) md.push(`- **Parse errors:** ${parseErrors.length} (see appendix)`);
md.push("");
md.push("## Per-skill verdicts");
md.push("");
md.push("| Skill | Activation | Criteria met | Judge | Notes (truncated) |");
md.push("|---|---|---:|---|---|");
for (const s of skillSummaries) {
  const crit = s.judge_criteria_total > 0 ? `${s.judge_criteria_met}/${s.judge_criteria_total}` : "—";
  md.push(`| ${s.skill} | ${s.activation_pass_rate} | ${crit} | ${s.judge_verdict} | ${s.judge_notes.replace(/\|/g, "\\|").replace(/\n/g, " ")} |`);
}

if (parseErrors.length > 0) {
  md.push("");
  md.push("## Appendix — parse errors");
  for (const e of parseErrors) md.push(`- ${e.file}: ${e.error}`);
}

writeFileSync(join(outDir, "fleet-judge.md"), md.join("\n") + "\n", "utf8");
writeFileSync(join(outDir, "fleet-judge.json"), JSON.stringify({ summary, skills: skillSummaries }, null, 2) + "\n", "utf8");
console.log(`wrote ${join(outDir, "fleet-judge.md")}`);
console.log(`wrote ${join(outDir, "fleet-judge.json")}`);
console.log(`\nFleet summary: ${summary.total_skills} skills, ${summary.activation.pass}/${summary.activation.total_cases} activation pass, judge: ${summary.judge.pass || 0}P / ${summary.judge.partial || 0}∼ / ${summary.judge.fail || 0}F / ${summary.judge.skipped || 0}S`);
