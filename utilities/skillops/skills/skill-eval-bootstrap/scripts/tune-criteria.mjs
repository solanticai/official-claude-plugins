#!/usr/bin/env node
// tune-criteria.mjs — replace placeholder judge_criteria in evals/suite.yaml
// with concrete, skill-specific criteria derived from the skill's SKILL.md.
//
// Usage:
//   node tune-criteria.mjs <skill-dir> [--write]
//   node tune-criteria.mjs --all [--write]
//
// Default is dry-run; pass --write to persist changes. Always emits a JSON
// summary to stdout: { skill, before, after, changed }.
//
// Derivation:
//   1. Read SKILL.md frontmatter + body.
//   2. Extract description → derive "Australian English" criterion (always) + an action-specific one.
//   3. Scan body for `## Output Format` (or "Output Specification") → derive "produces <artefact>" criteria.
//   4. Scan phases for explicit outputs (lines like "**Outputs:**" or "### Output") → enrich.
//   5. If template/output-template.md mentions specific section headings, add a "report contains <heading>" criterion.
//   6. Cap at 5 criteria; always lead with Australian English.

import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join, basename } from "node:path";

const AUS_CRIT = "Australian English used throughout the narrative (colour, optimise, behaviour, organise)";

function readSkill(skillDir) {
  const skillMdPath = join(skillDir, "SKILL.md");
  const text = readFileSync(skillMdPath, "utf8").replace(/\r\n/g, "\n").replace(/^﻿/, "");
  const fmMatch = text.match(/^---\n([\s\S]*?)\n---/);
  const fm = {};
  if (fmMatch) {
    for (const line of fmMatch[1].split("\n")) {
      const kv = line.match(/^([a-zA-Z_-]+):\s*(.*)$/);
      if (kv) fm[kv[1]] = kv[2].replace(/^["']|["']$/g, "").trim();
    }
  }
  return { text, fm };
}

function readTemplate(skillDir) {
  const tdir = join(skillDir, "templates");
  if (!existsSync(tdir)) return null;
  const files = readdirSync(tdir).filter(f => f.endsWith(".md"));
  if (files.length === 0) return null;
  // Prefer output-template.md if present.
  const preferred = files.find(f => f.includes("output")) || files[0];
  return readFileSync(join(tdir, preferred), "utf8").replace(/\r\n/g, "\n");
}

function deriveCriteria(skillDir, { text, fm }) {
  const out = [AUS_CRIT];

  // Action-verb criterion. Description is "Verb X across Y producing Z" or similar.
  const desc = fm.description || "";
  const verbMatch = desc.match(/^(\w+)\b/);
  if (verbMatch) {
    const verb = verbMatch[1].toLowerCase();
    // Phrase the criterion around what the verb implies the artefact should do.
    const verbCriterion = {
      audit:    "Findings cite file:line evidence and are categorised by severity",
      review:   "Findings cite file:line evidence and recommend specific actions",
      build:    "Artefact is a working specification, not a hypothetical or placeholder",
      create:   "Artefact is a complete, runnable specification — not a placeholder",
      generate: "Output is machine-readable where the description implies (valid JSON/SQL/YAML)",
      produce:  "Output is structured and parseable per the declared schema",
      design:   "Artefact includes both the design and its rationale (trade-offs surfaced)",
      analyse:  "Conclusions are evidence-backed with explicit data points",
      analyze:  "Conclusions are evidence-backed with explicit data points",
      estimate: "Estimates show their working — assumptions, ranges, sensitivity",
      calculate:"Calculation steps are shown; inputs and assumptions are explicit",
      map:      "Mapping is exhaustive — every input has an output and vice versa",
      diagram:  "Diagram is renderable (Mermaid/JSON-LD/etc.) and labels every node",
      evaluate: "Scoring rubric is applied transparently; every score has evidence",
      assess:   "Assessment is bounded — explicit scope, explicit out-of-scope",
      run:      "Output documents what was executed, with reproducible commands",
      scaffold: "Scaffolded artefact has all required sections and no TODO markers",
      configure:"Configuration is complete; no required keys left blank",
      detect:   "Detections are precise — false-positive rate is acknowledged"
    }[verb];
    if (verbCriterion) out.push(verbCriterion);
  }

  // Output Format / Output Specification block — derive "produces X" criterion.
  const outputBlock = text.match(/##\s+Output\s+(Format|Specification|Spec)\b[\s\S]*?(?=\n##\s|\Z)/i);
  if (outputBlock) {
    const block = outputBlock[0];
    // Look for bullet lines or list items naming artefacts.
    const artefacts = [...block.matchAll(/^[\-*]\s+`([^`]+)`/gm)].map(m => m[1]).slice(0, 3);
    if (artefacts.length > 0) {
      out.push(`Produces the declared artefacts: ${artefacts.join(", ")}`);
    } else {
      // Fallback: extract the first bold-labelled deliverable.
      const labelled = block.match(/\*\*([A-Z][A-Za-z ]+?)\*\*[:\.]?\s+([^.\n]{10,80})/);
      if (labelled) out.push(`${labelled[1]}: ${labelled[2].trim()}`);
    }
  }

  // Template-derived: if the output template references explicit section headings, require them.
  const tmpl = readTemplate(skillDir);
  if (tmpl) {
    const headings = [...tmpl.matchAll(/^##\s+([^\n{]{3,40})/gm)].map(m => m[1].trim()).filter(h => !h.includes("{{"));
    const distinctive = headings.filter(h => !/^(summary|findings|appendix|notes|references)$/i.test(h)).slice(0, 2);
    if (distinctive.length > 0) {
      out.push(`Report includes the canonical sections: ${distinctive.map(h => `\"${h}\"`).join(", ")}`);
    }
  }

  // Argument-hint criterion: if argument-hint declares input types, require the artefact reflects them.
  const hint = fm["argument-hint"] || "";
  if (hint && hint.includes("path")) {
    out.push("Artefact references the input path or target by name (no placeholder paths)");
  }

  // De-duplicate, cap at 5.
  const seen = new Set();
  const final = [];
  for (const c of out) {
    const key = c.toLowerCase().slice(0, 60);
    if (!seen.has(key)) { seen.add(key); final.push(c); }
    if (final.length >= 5) break;
  }
  return final;
}

function isPlaceholderCriterion(c) {
  return /\{\{|<replace|<skill-specific|Australian English used throughout the narrative$/i.test(c)
      || /Australian English used throughout$/i.test(c)
      || c === "Australian English used throughout the narrative"
      || /Output matches the structure of .* example file/.test(c)
      || /\b(?:put|add|insert)\s+a\b/i.test(c);
}

function patchSuiteYaml(yamlText, newCriteria) {
  // Find the judge_criteria block under the functional case and replace its bullets.
  // Pattern: "    judge_criteria:" followed by lines of "      - ..." until the next field
  // at the same indent or a new case.
  const lines = yamlText.replace(/\r\n/g, "\n").split("\n");
  let outLines = [];
  let i = 0;
  let patched = false;
  while (i < lines.length) {
    const line = lines[i];
    if (/^\s{4}judge_criteria:\s*$/.test(line)) {
      outLines.push(line);
      // Skip existing bullets.
      let j = i + 1;
      while (j < lines.length && /^\s{6}-\s+/.test(lines[j])) j++;
      // Insert new bullets.
      for (const c of newCriteria) {
        outLines.push(`      - "${c.replace(/\\/g, "\\\\").replace(/"/g, "\\\"")}"`);
      }
      i = j;
      patched = true;
      continue;
    }
    outLines.push(line);
    i++;
  }
  return { text: outLines.join("\n"), patched };
}

function processSkill(skillDir, { write }) {
  const suitePath = join(skillDir, "evals/suite.yaml");
  if (!existsSync(suitePath)) {
    return { skill: basename(skillDir), changed: false, reason: "no-suite" };
  }
  const skill = readSkill(skillDir);
  const criteria = deriveCriteria(skillDir, skill);
  const before = readFileSync(suitePath, "utf8").replace(/\r\n/g, "\n");

  // Quick check: are existing criteria placeholders? If they look reasonable, leave alone.
  const existing = [...before.matchAll(/^\s{6}-\s+"([^"]+)"/gm)].map(m => m[1]);
  const allPlaceholder = existing.length === 0 || existing.every(isPlaceholderCriterion);
  if (!allPlaceholder) {
    return { skill: basename(skillDir), changed: false, reason: "criteria-already-tuned", existing };
  }

  const { text: nextText, patched } = patchSuiteYaml(before, criteria);
  if (!patched) {
    return { skill: basename(skillDir), changed: false, reason: "no-judge_criteria-block" };
  }

  if (write) {
    writeFileSync(suitePath, nextText, "utf8");
  }
  return {
    skill: basename(skillDir),
    changed: true,
    before: existing,
    after: criteria
  };
}

function findAllSkills() {
  const cats = ["lifestyle", "smb", "marketing", "engineering", "data-science", "economics", "utilities"];
  const out = [];
  for (const cat of cats) {
    if (!existsSync(cat)) continue;
    for (const plugin of readdirSync(cat)) {
      const skillsDir = join(cat, plugin, "skills");
      if (!existsSync(skillsDir)) continue;
      for (const skill of readdirSync(skillsDir)) {
        const dir = join(skillsDir, skill);
        if (existsSync(join(dir, "SKILL.md"))) out.push(dir);
      }
    }
  }
  return out;
}

// ---------- CLI ----------
const args = process.argv.slice(2);
const write = args.includes("--write");
const all = args.includes("--all");
const target = args.find(a => !a.startsWith("--"));

const skills = all ? findAllSkills() : (target ? [target] : []);
if (skills.length === 0) {
  console.error("usage: tune-criteria.mjs <skill-dir> [--write]   or   --all [--write]");
  process.exit(2);
}

const results = skills.map(s => processSkill(s, { write }));
const summary = {
  total: results.length,
  changed: results.filter(r => r.changed).length,
  unchanged: results.filter(r => !r.changed).length,
  reasons: {}
};
for (const r of results) {
  if (!r.changed) summary.reasons[r.reason] = (summary.reasons[r.reason] || 0) + 1;
}
console.log(JSON.stringify({ summary, results }, null, 2));
