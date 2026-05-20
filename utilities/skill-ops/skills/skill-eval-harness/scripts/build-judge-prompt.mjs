#!/usr/bin/env node
// build-judge-prompt.mjs — emit a single judge prompt for one skill on stdout.
//
// Usage:
//   node build-judge-prompt.mjs <skill-dir>
//
// The prompt bundles activation classification (5 cases) and the functional
// judge (1 case against the skill's example artefact) into one task so a
// single Agent invocation can return a complete per-skill verdict.

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, basename } from "node:path";

const skillDir = process.argv[2];
if (!skillDir) {
  console.error("usage: build-judge-prompt.mjs <skill-dir>");
  process.exit(2);
}

function read(p) { return readFileSync(p, "utf8").replace(/\r\n/g, "\n").replace(/^﻿/, ""); }

const skillMd = read(join(skillDir, "SKILL.md"));
const fmMatch = skillMd.match(/^---\n([\s\S]*?)\n---/);
const fm = {};
if (fmMatch) {
  for (const line of fmMatch[1].split("\n")) {
    const kv = line.match(/^([a-zA-Z_-]+):\s*(.*)$/);
    if (kv) fm[kv[1]] = kv[2].replace(/^["']|["']$/g, "").trim();
  }
}

const suitePath = join(skillDir, "evals/suite.yaml");
if (!existsSync(suitePath)) {
  console.error(`no suite at ${suitePath}`);
  process.exit(3);
}
const suite = read(suitePath);

// Parse activation cases.
const activationCases = [];
const caseBlocks = suite.split(/(?=^  - id:)/m);
let judgeCriteria = [];
let functionalDescription = "";
for (const block of caseBlocks) {
  const id = (block.match(/^\s*-\s+id:\s+(\S+)/m) || [])[1];
  if (!id) continue;
  const kind = (block.match(/^\s+kind:\s+(\S+)/m) || [])[1];
  const desc = (block.match(/^\s+description:\s+"([^"]*)"/m) || [])[1];
  const userInput = (block.match(/^\s+user_input:\s+"([^"]*)"/m) || [])[1] || "";
  const expectedAct = (block.match(/^\s+expected_activation:\s+(true|false)/m) || [])[1];
  if (kind === "activation" && expectedAct !== undefined) {
    activationCases.push({
      id,
      description: desc || "",
      user_input: userInput,
      expected_activation: expectedAct === "true"
    });
  }
  if (kind === "functional") {
    functionalDescription = desc || "";
    const critBlock = block.match(/judge_criteria:\s*\n([\s\S]*?)(?=\n\s*(timeout_seconds|expected_|tags|kind:|id:|$))/);
    if (critBlock) {
      // YAML quotes embedded inner quotes as \" — match the whole quoted scalar
      // (escape-aware) rather than stopping at the first inner quote.
      judgeCriteria = [...critBlock[1].matchAll(/^\s+-\s+"((?:\\.|[^"\\])*)"/gm)]
        .map(m => m[1].replace(/\\"/g, '"').replace(/\\\\/g, "\\"));
    }
  }
}

// Pick the first example artefact to judge.
let exampleArtefact = "(no example artefact in this skill)";
let exampleFile = null;
const examplesDir = join(skillDir, "examples");
if (existsSync(examplesDir)) {
  const exampleFiles = readdirSync(examplesDir).filter(f => f.endsWith(".md"));
  if (exampleFiles.length > 0) {
    exampleFile = exampleFiles[0];
    const full = read(join(examplesDir, exampleFile));
    // Cap at 6000 chars to keep prompts tight; judges don't need the entire file.
    exampleArtefact = full.length > 6000
      ? full.slice(0, 6000) + "\n\n... [example truncated for prompt size]"
      : full;
  }
}

const skillName = fm.name || basename(skillDir);
const description = fm.description || "";
const paths = fm.paths || "(none)";

const prompt = `You are evaluating a Claude Code skill. Two independent tasks; return ONE JSON object with both results. No prose outside the JSON.

## Skill under test

- **name:** ${skillName}
- **description:** ${description}
- **paths:** ${paths}

## Task 1 — Activation classification (${activationCases.length} cases)

For each case below, decide whether the skill would activate (be invoked) for the given user input. Use only the description and skill name as evidence.

${activationCases.map((c, i) => `### Case ${i + 1} — id: ${c.id}
- description: ${c.description}
- user_input: ${JSON.stringify(c.user_input)}
- expected_activation: ${c.expected_activation}
`).join("\n")}

Rules:
- \`verdict: true\` only when a reasonable reader of the description would expect the skill to fire.
- Borderline cases → \`false\`. Activation should be precise.

## Task 2 — Functional judge

${exampleFile
  ? `Read the example artefact below — it is the kind of output this skill should produce. Verify each judge criterion against the artefact.

### Functional case
${functionalDescription}

### Judge criteria
${judgeCriteria.map((c, i) => `${i + 1}. ${c}`).join("\n") || "(no criteria declared)"}

### Artefact (example output)
\`\`\`
${exampleArtefact}
\`\`\`
`
  : `This skill has no example artefact. Skip the functional judge — return \`{ "status": "skipped", "reason": "no-example-artefact" }\` for the judge block.`}

## Output schema

Return exactly this JSON shape (no markdown fences, no preamble, no trailing prose):

\`\`\`json
{
  "skill": "${skillName}",
  "activation_results": [
    {"id": "<case-id>", "verdict": true | false, "expected": true | false, "pass": true | false, "reason": "<one sentence>"}
  ],
  "judge_result": ${exampleFile ? `{
    "verdict": "pass" | "fail" | "partial",
    "criterion_results": [
      {"text": "<criterion>", "met": true | false, "evidence": "<short>"}
    ],
    "notes": "<one paragraph>"
  }` : `{"status": "skipped", "reason": "no-example-artefact"}`}
}
\`\`\`

Return the JSON only.`;

process.stdout.write(prompt);
