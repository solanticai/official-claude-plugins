---
name: cli-ux-audit
description: Audit any CLI tool for terminal user experience — help text, command structure, error messages, output formatting, discoverability, and accessibility — produces a scored report with actionable fixes
argument-hint: [cli-binary-or-package-path]
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(command:*), Bash(./scripts/*:*), Bash(man:*), Bash(which:*), Agent
effort: high
---

# CLI UX Audit

ultrathink

## Before You Start

1. **Locate the CLI.** If the user gave a binary name (`gh`, `eslint`), resolve it with `command -v <name>` and note whether it is a wrapper script or a compiled binary. If a repo path was given, find the entry point (`bin` in `package.json`, `[project.scripts]` in `pyproject.toml`, `cmd/*/main.go`, `src/main.rs`, or a top-level shell script). If neither, ask the user.
2. **Run the CLI once.** Capture `--version`, `--help`, and the no-argument invocation. These three runs seed every downstream phase, so do them before scoring anything.
3. **Identify the framework.** Use `${CLAUDE_PLUGIN_ROOT}/skills/cli-ux-audit/scripts/detect-cli-framework.sh <path>` to detect commander, yargs, oclif, meow, click, argparse, typer, cobra, clap, thor, or raw. Framework hints tell you which idioms are expected.
4. **Check permissions.** If running probes on a remote CLI, confirm the user is okay with you executing `--help`, `--version`, and a deliberately bad flag. Never run destructive subcommands to probe behaviour.

## User Context

$ARGUMENTS

CLI state:
- Binary: !`command -v "$ARGUMENTS" 2>/dev/null || echo "resolve manually"`
- Version output: !`("$ARGUMENTS" --version 2>&1 | head -3) || echo "no --version"`
- TTY: !`[ -t 1 ] && echo "stdout is a TTY" || echo "stdout is not a TTY"`

---

## Audit Phases

Execute every phase in order. For each phase, score using the rubric in `${CLAUDE_PLUGIN_ROOT}/skills/cli-ux-audit/reference.md` and report findings with reproducible probe commands and — where source is available — file paths and line numbers. Do not skip phases; mark as N/A if genuinely not applicable (e.g. single-command tool has no subcommand tree).

---

### Phase 1: Discovery & Invocation

**Objective:** Identify the CLI, its framework, surface area, and invocation modes.

1. Resolve the binary path and detect whether it is Node, Python, Go, Rust, Ruby, or shell.
2. Run `detect-cli-framework.sh` and record the framework (commander, yargs, oclif, click, typer, cobra, clap, thor, argparse, raw).
3. Enumerate subcommands by parsing `--help` output. Record the subcommand tree and its depth.
4. Identify the entry point source file(s). For open-source CLIs, open them for reference in later phases.
5. Run the probe script: `${CLAUDE_PLUGIN_ROOT}/skills/cli-ux-audit/scripts/probe-cli.sh <binary>` to capture baseline output for `--help`, `-h`, `help`, `--version`, no-args, and a deliberately bad flag. Save the artefacts — later phases inspect them.

This phase is context-only — no score.

---

### Phase 2: Help & Documentation (15 points)

**Objective:** Verify the help system is complete, discoverable, and readable.

Refer to the help-output checklist in `${CLAUDE_PLUGIN_ROOT}/skills/cli-ux-audit/reference.md`.

1. **Both flags work.** `--help` and `-h` produce identical output and exit with code 0.
2. **Subcommand help exists.** For a multi-command CLI, `cli help <cmd>` and `cli <cmd> --help` both work.
3. **Output goes to stdout.** Help content is on stdout, not stderr (check by redirecting `2>/dev/null` — help text should still appear).
4. **Structural completeness.** Help output contains: a one-line synopsis, a short description, an options block, a commands/subcommands block (if multi-command), and — critically — an **examples block**. Missing examples is a common CRITICAL finding.
5. **Per-option descriptions.** Every flag has a description, not just a name. Mandatory vs optional flags visibly distinguished.
6. **Readable width.** Lines wrap at ≤ 80 characters by default. Run `COLUMNS=40 <cli> --help` and confirm the output still wraps sensibly.
7. **Defaults shown.** Flag defaults are displayed inline (e.g. `--timeout <ms> (default: 5000)`).
8. **Version line.** `--version` emits the version number and — ideally — the commit hash or build date. Exits with code 0.
9. **Man pages.** For system-level CLIs, a man page is shipped or generated (`man <cli>` works).

---

### Phase 3: Command Structure & Argument Parsing (15 points)

**Objective:** Verify the command tree is consistent, discoverable, and parses input predictably.

1. **Naming consistency.** Subcommands follow a consistent grammar (all verb-noun or all noun-verb, not mixed).
2. **Short aliases.** Common flags have short forms (`--verbose` ↔ `-v`, `--output` ↔ `-o`). No collisions between subcommands and their flags.
3. **Negatable booleans.** Boolean flags support `--no-<name>` or pair with an opposite flag.
4. **Required-arg validation.** Missing required arguments produce a clear usage error **before** any side effects (not halfway through execution).
5. **Unknown-flag rejection.** `cli --bogus` fails with a message; bonus points if it suggests a close match.
6. **Flag order independence.** `cli --flag cmd` and `cli cmd --flag` both work, unless positional ambiguity makes that unsafe.
7. **Positional separator.** `--` correctly stops flag parsing (`cli -- --this-is-not-a-flag`).
8. **Confirmation on destructive actions.** Irreversible subcommands (delete, rm, drop, reset) require interactive confirmation or an explicit `--yes` / `--force`.
9. **Subcommand tree depth.** Tree is shallow (≤ 3 levels). Deep trees hurt discoverability.
10. **Mutually exclusive flags.** Documented and enforced (e.g. `--json` vs `--yaml`).

---

### Phase 4: Error Messages & Exit Codes (15 points)

**Objective:** Verify failures produce actionable errors and correct exit codes.

Probe deliberately broken invocations and record stdout, stderr, and exit code. See `probe-cli.sh` outputs.

1. **Distinct exit codes.** 0 on success, 2 on usage error, non-zero otherwise. Preferably follows `sysexits.h` conventions (see reference.md). Avoid "always exit 1".
2. **Stderr for errors.** Error messages go to stderr, not stdout. Machine-consumable success output stays clean on stdout.
3. **Three-part error format.** Each error states: *what* failed, *why* (the underlying cause), and *how to fix* it (a next step, flag to try, or docs URL).
4. **No raw stack traces.** Python tracebacks, Node `Error: ENOENT` dumps, Go panic output, or Rust `RUST_BACKTRACE=1` output must be gated behind `--debug` / `--verbose`. Default failures show a human-readable message.
5. **Actionable missing input.** Missing required args say *which* arg and *what* it expects.
6. **Network / permission / file errors.** Invalid hostnames, 401/403, EACCES, and ENOENT produce clear messages — not silent exits or generic "something went wrong".
7. **Signal handling.** Ctrl+C (SIGINT) exits cleanly: removes partial files, releases locks, restores the terminal. Do not leave the terminal in raw mode on crash.
8. **No sensitive data in errors.** Tokens, passwords, and full URLs with credentials are redacted from error output.

---

### Phase 5: Output Formatting & Visual Clarity (10 points)

**Objective:** Verify output is readable, consistently formatted, and machine-parseable when requested.

1. **Alignment.** Columns in tables and list output align (use fixed-width formatters, not `printf "%s\t%s"`).
2. **Semantic colour.** Red for errors, yellow for warnings, green for success, cyan/blue for info. Colour never used decoratively.
3. **NO_COLOR honoured.** Setting `NO_COLOR=1 <cli> ...` disables every ANSI colour code. Test with the `check-isatty-behaviour.sh` script.
4. **Pipe-safe defaults.** `cli ... | cat` strips colour automatically (detects non-TTY stdout).
5. **Structured output mode.** `--json` or `--format=json` emits clean JSON (one object or NDJSON), suitable for `jq`.
6. **Progress to stderr.** Progress bars, status updates, and spinners write to stderr or overwrite a single line. They never interleave with structured stdout.
7. **Icons degrade.** Unicode icons (✓, ✗, ⚠) have ASCII fallback via `--ascii` or auto-detection on non-UTF-8 terminals.

---

### Phase 6: Interactivity & Progress Feedback (10 points)

**Objective:** Verify long operations give feedback and interactive prompts behave well in both TTY and CI.

1. **Feedback within 2s.** Any command that takes longer than ~2 seconds shows a spinner, progress bar, or status line.
2. **Spinners disabled on non-TTY.** When stdout is piped or redirected, animated output is suppressed.
3. **Battle-tested prompt libraries.** Prompts use inquirer/prompts/enquirer (Node), questionary/prompt_toolkit (Python), bubbletea/survey (Go), or dialoguer (Rust). Not raw `read` / `input()`.
4. **Defaults visible.** Yes/no prompts display `[Y/n]` or `[y/N]` with the default highlighted.
5. **Non-interactive escape hatch.** `--yes`, `--no-input`, `--non-interactive`, or an env var (`CI`, `<APP>_NONINTERACTIVE`) bypasses every prompt.
6. **CI auto-detection.** The CLI checks `CI=true` or `isatty(stdin) === false` and refuses to prompt — instead either uses defaults, exits with a usage error, or reads from flags.
7. **Input validation.** Prompts re-prompt on bad input rather than crashing.
8. **Ctrl+C from prompt.** Cancels cleanly with exit code 130, no partial state.

---

### Phase 7: Discoverability & Onboarding (10 points)

**Objective:** Verify first-time users can find their way without reading external docs.

1. **No-args behaviour.** `cli` with no arguments shows help or top-level usage — never an error, never silence.
2. **Top-level subcommand list.** The first page of help lists every top-level subcommand with a one-line description.
3. **Typo suggestions.** `cli brnach` suggests `did you mean: branch?`.
4. **Shell completions.** `cli completion bash|zsh|fish|powershell` emits a completion script. Installation documented.
5. **First-run guidance.** After install, a new user can find: a "getting started" command (`cli init`, `cli setup`), at least one copy-pasteable example, and a docs URL.
6. **Version tells the truth.** `--version` includes version + commit hash or build date when possible. Helps bug reports.
7. **Upgrade hints.** When a new version is available and telemetry is allowed, the CLI mentions it — without spamming.

---

### Phase 8: Accessibility & Internationalisation (10 points)

**Objective:** Verify output is usable by people with visual impairments, colour-vision deficiencies, screen readers, and non-English locales.

1. **Colour is not the only signal.** Every coloured status also has a text or symbol cue (✓ / FAIL / [WARN]). Colour-blind users must still be able to read status.
2. **Safe palette.** Avoid red-only vs green-only contrasts. Prefer red+symbol vs green+symbol. See reference.md for a CVD-safe palette.
3. **Screen-reader friendly.** Critical information is in text, not ASCII art, banners, or box-drawing characters.
4. **Locale awareness.** Timestamps, numbers, and currency follow `LANG`/`LC_ALL` where relevant — or explicitly use ISO 8601 / fixed formats.
5. **Unicode degradation.** On `LANG=C` or legacy terminals, Unicode output falls back to ASCII cleanly.
6. **Translation hooks.** For tools with user-facing strings, gettext / i18next / fluent integration is at least scaffolded. Not a must — but a suggestion for widely used CLIs.
7. **High-contrast-friendly.** Does not assume a dark-on-light or light-on-dark terminal — colour choices work on both.

---

### Phase 9: Terminal Compatibility & Piping Safety (10 points)

**Objective:** Verify the CLI behaves well across terminals, when piped, and after crashes.

1. **No ANSI leakage on pipes.** `cli list | grep foo` has no escape codes in output. Test with `cat -v`.
2. **isatty detection.** CLI uses `isatty(stdout)` (or equivalent) to turn off colour, cursor control, and spinners when not interactive. Confirm via `check-isatty-behaviour.sh`.
3. **Cross-terminal support.** Works in: xterm, GNOME Terminal, iTerm, Windows Terminal, cmd.exe, PowerShell, plain `dumb` terminal, and `tmux`/`screen` sessions. Document known-broken environments.
4. **Width independence.** Queries `COLUMNS` (or `tput cols`) at runtime; falls back to 80 if unknown. Never hardcodes 132 or 160.
5. **SIGWINCH handling.** Interactive UIs redraw on terminal resize rather than mangling.
6. **Clean exit.** Terminal is left in cooked mode with cursor visible after normal exit, crash, or Ctrl+C.
7. **Respects `TERM=dumb`.** Falls back to plain text — no cursor addressing or colour.
8. **UTF-8 mismatch.** Running with `LANG=C` does not produce mojibake — either degrades to ASCII or clearly documents UTF-8 requirement.

---

### Phase 10: Performance Perception & Responsiveness (5 points)

**Objective:** Verify the CLI feels responsive for common cheap operations.

1. **Fast help/version.** `time <cli> --version` and `time <cli> --help` complete in under ~200 ms on cold cache. Slow startup usually signals heavy top-level imports.
2. **No network in help/version paths.** `<cli> --version` with network disabled still completes.
3. **First-keystroke latency.** In interactive prompts, feedback within 100 ms of a keystroke.
4. **Progress for long ops.** See Phase 6 — doubles as a perception check.
5. **Lazy-load expensive subsystems.** DB clients, auth flows, and telemetry only initialise when the subcommand that needs them is invoked.

---

## Scoring

Calculate scores per phase using the rubric in `${CLAUDE_PLUGIN_ROOT}/skills/cli-ux-audit/reference.md`.

**Verdict thresholds:**
- **90-100**: PASS — polished CLI, safe to ship to a broad audience
- **70-89**: PASS WITH WARNINGS — usable but rough edges that will frustrate users
- **50-69**: CONDITIONAL — fundamental UX problems; fix before a public release
- **0-49**: FAIL — users will bounce; substantial rework required

---

## Reporting

After all phases, produce a structured report. Use the template from `${CLAUDE_PLUGIN_ROOT}/skills/cli-ux-audit/templates/output-template.md`.

The report must include:
- A clear PASS / FAIL / PASS WITH WARNINGS verdict per phase
- Every finding must include a **reproducible probe command** (e.g. `NO_COLOR=1 cli list | cat -v`) and — where source is available — a **file path and line number**
- Severity ratings: **CRITICAL** (blocks usability), **WARNING** (frustrates users), **SUGGESTION** (polish)
- A prioritised action list at the end, grouped by severity
- Mermaid pie chart for visual severity distribution
- A JSON sidecar validating against `templates/findings-schema.json`

---

## Important Principles

- **Run the CLI. Don't guess.** Every finding must be backed by observed output — capture it via `probe-cli.sh` or your own invocation, and quote it in the report.
- **Be specific.** "Improve help text" is useless. Say: *"`cli deploy --help` omits an examples block; users have no copy-pasteable starting point."*
- **Don't fix during the audit.** Report findings. Let the maintainer decide.
- **Think like a new user.** Would someone who just installed this be able to complete their first task without opening a browser tab?
- **Think like a script author.** Would this CLI be safe to wrap in a bash pipeline? Are exit codes trustworthy? Is `--json` output stable?
- **Respect the framework's idioms.** A clap-based Rust CLI and a commander-based Node CLI have different conventions. Score against the platform norm, not a universal ideal.

## Edge Cases

1. **Closed-source binary.** You cannot read source files. Rely on probe-based evidence only; cite exact commands and their output.
2. **CLI requires authentication.** If subcommands need login, note it and audit only what is reachable pre-auth — plus help/version paths.
3. **Wrapper CLIs.** `tsx`, `uv`, `npx`, `pnpm dlx`-style wrappers — audit the outermost surface but note that many behaviours are delegated.
4. **TUIs vs CLIs.** Interactive full-screen TUIs (like `lazygit`, `htop`) follow different conventions. Skip pipe-safety checks that don't apply; focus on keyboard UX, resize handling, and escape hatches.
5. **Multi-binary packages.** Some packages install several bins. Treat each as a separate audit unless they clearly share a codebase — then audit the primary binary and spot-check the others.
6. **Framework-defaults-only CLIs.** If the tool has no custom UX and is 100% framework defaults (e.g. vanilla `argparse`), score that against the framework's quality bar and note the opportunity cost.
7. **Single-command tools.** No subcommand tree — mark Phase 3 checks related to subcommands as N/A.
