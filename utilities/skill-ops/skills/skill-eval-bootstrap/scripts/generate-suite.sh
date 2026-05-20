#!/usr/bin/env bash
# generate-suite.sh — produce a complete evals/suite.yaml for a skill.
#
# This is the workhorse: the SKILL.md phases describe the design, this script
# implements it deterministically so bootstrapping is reproducible.
#
# Usage:
#   generate-suite.sh <target_dir> [--force]
#
# Side effects:
#   - Creates <target_dir>/evals/ if absent.
#   - Writes <target_dir>/evals/suite.yaml (refuses if it exists, unless --force).
#   - Writes <target_dir>/evals/iteration-log.md (created only if absent).
#
# Exit codes:
#   0 — generated
#   1 — skill missing required input (e.g. empty description)
#   2 — suite already exists and --force was not passed

set -u

TARGET="${1:-}"
FORCE=0
shift || true
for arg in "$@"; do
  [ "$arg" = "--force" ] && FORCE=1
done

if [ -z "$TARGET" ] || [ ! -f "$TARGET/SKILL.md" ]; then
  echo "missing target SKILL.md" >&2
  exit 1
fi

EVALS="$TARGET/evals"
SUITE="$EVALS/suite.yaml"

if [ -f "$SUITE" ] && [ "$FORCE" != "1" ]; then
  echo "suite already exists at $SUITE (pass --force to overwrite)" >&2
  exit 2
fi

mkdir -p "$EVALS"

SCRIPT_DIR="$(dirname "$0")"
TRIGGERS_JSON=$(bash "$SCRIPT_DIR/extract-triggers.sh" "$TARGET")
ERROR_CODES=$(bash "$SCRIPT_DIR/extract-error-codes.sh" "$TARGET")

# Use Node to compose the YAML — bash string templating gets gnarly fast
# and we have node available everywhere the harness runs.
node -e '
const fs = require("node:fs");
const triggers = JSON.parse(process.argv[1]);
const errorCodes = process.argv[2].split("\n").filter(Boolean);
const target = process.argv[3];
const today = new Date().toISOString().slice(0, 10);

if (!triggers.description) {
  console.error("Skill description is empty — cannot generate activation cases.");
  process.exit(1);
}

const name = triggers.name;
const desc = triggers.description;
const firstSentence = desc.split(/[.—–·]/)[0].trim();

// Activation positives.
const verbMatch = desc.match(/^(\w+)/);
const leadingVerb = verbMatch ? verbMatch[1] : "Run";
const synonymMap = {
  Audit: "Review", Review: "Audit", Build: "Create", Create: "Build",
  Generate: "Produce", Produce: "Generate", Analyse: "Examine",
  Design: "Architect", Architect: "Design", Evaluate: "Assess",
  Assess: "Evaluate", Estimate: "Calculate", Calculate: "Estimate",
  Map: "Diagram", Diagram: "Map", Scaffold: "Generate", Run: "Execute"
};
const paraphraseVerb = synonymMap[leadingVerb] || leadingVerb;
const paraphrase = desc.replace(new RegExp("^" + leadingVerb), paraphraseVerb);

const cases = [];

cases.push({
  id: "activate-positive-canonical",
  kind: "activation",
  description: "should fire on the canonical use case",
  user_input: firstSentence,
  expected_activation: true
});
cases.push({
  id: "activate-positive-paraphrase",
  kind: "activation",
  description: `should fire when leading verb is swapped (${leadingVerb} → ${paraphraseVerb})`,
  user_input: paraphrase.split(/[.—–·]/)[0].trim(),
  expected_activation: true
});
cases.push({
  id: "activate-positive-name-mention",
  kind: "activation",
  description: "should fire when the skill is mentioned by name",
  user_input: `run ${name}`,
  expected_activation: true
});

// Activation negatives — generic off-topic + near-miss.
cases.push({
  id: "activate-negative-unrelated",
  kind: "activation",
  description: "should NOT fire on unrelated coding question",
  user_input: "how do I configure SSH key forwarding on Windows?",
  expected_activation: false
});
cases.push({
  id: "activate-negative-near-miss",
  kind: "activation",
  description: "should NOT fire on a query that names a related concept but is out of scope",
  user_input: "remind me what skills are",
  expected_activation: false
});

// Functional case — only if examples/ exists.
const examplesDir = `${target}/examples`;
let hasExamples = false;
try { hasExamples = fs.readdirSync(examplesDir).some(f => f.endsWith(".md")); } catch {}
if (hasExamples) {
  const hint = (triggers.argument_hint || "").replace(/^\[|\]$/g, "");
  const exampleInput = hint && !hint.includes("|") ? `<replace-with-real-${hint}>` : "<replace-with-real-input>";
  cases.push({
    id: "functional-golden",
    kind: "functional",
    description: "produces the artefact described in examples/",
    user_input: exampleInput,
    expected_outputs: [
      { kind: "file_created", path_glob: "*.md" }
    ],
    judge_criteria: [
      "Australian English used throughout the narrative",
      `Output matches the structure of ${name}'\''s example file`
    ],
    timeout_seconds: 240
  });
}

// Edge cases.
const emptyCode = errorCodes.includes("empty-argument") ? "empty-argument" : "empty-argument";
const missingCode = errorCodes.find(c => /not-found|missing/.test(c)) || "target-not-found";
cases.push({
  id: "edge-empty-input",
  kind: "edge-case",
  description: "handles empty input gracefully",
  user_input: "",
  expected_error: emptyCode
});
cases.push({
  id: "edge-nonexistent-target",
  kind: "edge-case",
  description: "handles a target that does not exist",
  user_input: "this-target-definitely-does-not-exist-xyz",
  expected_error: missingCode
});

// Render YAML.
function quote(s) {
  s = String(s);
  // Single-line scalars only — escape backslashes and double quotes.
  return "\"" + s.replace(/\\/g, "\\\\").replace(/"/g, "\\\"") + "\"";
}
const lines = [];
lines.push(`# Auto-generated by skill-eval-bootstrap on ${today}.`);
lines.push("# Review and tune judge_criteria + edge expectations before relying on this suite.");
lines.push("");
lines.push(`skill: ${name}`);
lines.push(`description: ${quote("Baseline eval suite generated for " + name)}`);
lines.push("");
lines.push("test_cases:");
for (const c of cases) {
  lines.push(`  - id: ${c.id}`);
  lines.push(`    kind: ${c.kind}`);
  lines.push(`    description: ${quote(c.description)}`);
  lines.push(`    user_input: ${quote(c.user_input)}`);
  if (typeof c.expected_activation === "boolean") {
    lines.push(`    expected_activation: ${c.expected_activation}`);
  }
  if (c.expected_error) {
    lines.push(`    expected_error: ${quote(c.expected_error)}`);
  }
  if (c.expected_outputs) {
    lines.push(`    expected_outputs:`);
    for (const o of c.expected_outputs) {
      lines.push(`      - kind: ${o.kind}`);
      if (o.path_glob) lines.push(`        path_glob: ${quote(o.path_glob)}`);
      if (o.text)      lines.push(`        text: ${quote(o.text)}`);
      if (o.pattern)   lines.push(`        pattern: ${quote(o.pattern)}`);
    }
  }
  if (c.judge_criteria) {
    lines.push(`    judge_criteria:`);
    for (const j of c.judge_criteria) lines.push(`      - ${quote(j)}`);
  }
  if (c.timeout_seconds) lines.push(`    timeout_seconds: ${c.timeout_seconds}`);
}

process.stdout.write(lines.join("\n") + "\n");
' "$TRIGGERS_JSON" "$ERROR_CODES" "$TARGET" > "$SUITE"

if [ ! -s "$SUITE" ]; then
  rm -f "$SUITE"
  echo "suite generation produced empty output" >&2
  exit 1
fi

# Iteration log — create only if absent.
LOG="$EVALS/iteration-log.md"
if [ ! -f "$LOG" ]; then
  SKILL_NAME=$(basename "$TARGET")
  cat > "$LOG" <<EOF
# Iteration log — $SKILL_NAME

One row per eval run. Append-only. Used to track regression vs improvement as the skill evolves.

| Date | Pass-rate | Regressions | Wins | New | Mode | Notes |
|---|---:|---:|---:|---:|---|---|
EOF
fi

echo "wrote $SUITE"
echo "log  $LOG"
