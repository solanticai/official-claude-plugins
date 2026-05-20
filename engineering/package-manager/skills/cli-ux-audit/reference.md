# CLI UX Audit — Reference Material

Dense reference tables extracted from `SKILL.md`. Use during scoring and when writing findings.

---

## Table of Contents

- [Scoring rubrics](#scoring-rubrics)
- [CLI framework lookup](#cli-framework-lookup)
- [Terminal environment reference](#terminal-environment-reference)
- [Exit code conventions (`sysexits.h`)](#exit-code-conventions-sysexitsh)
- [CVD-safe colour palette](#cvd-safe-colour-palette)
- [Severity tiers](#severity-tiers)
- [Finding template](#finding-template)

---

## Scoring rubrics

Each phase is scored against the checks listed in SKILL.md. Award points per check; total the phase and clamp to the phase maximum. Failing a check means zero for that line item — do not split hairs on partial credit unless explicitly noted.

### Phase 2 — Help & Documentation (15 pts)

| Check | Points | Notes |
|---|---:|---|
| `--help` and `-h` both work and match | 2 | Identical text; both exit 0 |
| Per-subcommand help works | 2 | Both `cli help X` and `cli X --help` |
| Help goes to stdout | 1 | Check `<cli> --help 2>/dev/null` |
| Synopsis line present | 1 | `Usage: cli [options] command` |
| Options block present with descriptions | 2 | Every flag has a description |
| Examples block present | 3 | **Often missing — flag CRITICAL if absent** |
| Defaults shown inline | 1 | `(default: foo)` |
| Wraps at narrow width | 1 | `COLUMNS=40 cli --help` |
| `--version` present and exits 0 | 1 | Emits at least a version string |
| Man page or generated docs shipped | 1 | Optional for Node/Python tooling |

### Phase 3 — Command Structure & Argument Parsing (15 pts)

| Check | Points |
|---|---:|
| Consistent subcommand grammar | 2 |
| Short aliases for common flags | 1 |
| Negatable booleans | 1 |
| Required args validated before side effects | 2 |
| Unknown flags rejected | 1 |
| Typo suggestion on unknown flag/subcommand | 1 |
| Flag order independence | 1 |
| `--` separator respected | 1 |
| Destructive actions gated by confirmation/`--yes` | 3 |
| Subcommand tree depth ≤ 3 | 1 |
| Mutually exclusive flags enforced | 1 |

### Phase 4 — Error Messages & Exit Codes (15 pts)

| Check | Points |
|---|---:|
| Distinct exit codes (not "always 1") | 2 |
| `sysexits.h` convention followed | 1 |
| Errors to stderr | 2 |
| Three-part format (what/why/how-to-fix) | 3 |
| No raw stack traces by default | 2 |
| Missing-input error names the arg | 1 |
| Graceful network/permission/FS errors | 2 |
| Clean signal handling (Ctrl+C) | 1 |
| Secrets redacted from error output | 1 |

### Phase 5 — Output Formatting (10 pts)

| Check | Points |
|---|---:|
| Aligned tables/lists | 2 |
| Semantic colour (red=error etc.) | 1 |
| `NO_COLOR` honoured | 2 |
| Pipe-safe (isatty on stdout strips ANSI) | 2 |
| `--json` / structured output mode | 2 |
| Progress to stderr or single-line overwrite | 1 |

### Phase 6 — Interactivity & Progress Feedback (10 pts)

| Check | Points |
|---|---:|
| Feedback for operations > 2s | 2 |
| Spinners disabled on non-TTY | 2 |
| Prompts use tested library (not raw stdin) | 1 |
| Defaults shown in prompt `[Y/n]` | 1 |
| `--yes` / `--no-input` / env escape hatch | 2 |
| `CI=true` auto-detected | 1 |
| Ctrl+C on prompt exits cleanly (code 130) | 1 |

### Phase 7 — Discoverability & Onboarding (10 pts)

| Check | Points |
|---|---:|
| No-args shows help (not error, not silent) | 2 |
| Top-level subcommand list with one-liners | 1 |
| Typo suggestions | 2 |
| Shell completions (bash/zsh/fish/pwsh) | 2 |
| First-run command or docs URL in help | 2 |
| `--version` includes commit or build date | 1 |

### Phase 8 — Accessibility & I18n (10 pts)

| Check | Points |
|---|---:|
| Status has text/symbol cue alongside colour | 3 |
| CVD-safe palette | 2 |
| Critical info as text, not ASCII art | 1 |
| Locale awareness or explicit ISO format | 1 |
| Unicode degrades on `LANG=C` | 2 |
| High-contrast friendly (works on light & dark) | 1 |

### Phase 9 — Terminal Compatibility & Piping Safety (10 pts)

| Check | Points |
|---|---:|
| No ANSI leakage on pipes | 2 |
| `isatty` detection on stdout | 2 |
| Works on Windows Terminal + cmd + PowerShell | 2 |
| `COLUMNS`/`tput cols` used, sane fallback | 1 |
| SIGWINCH handled (TUIs only) | 1 |
| Clean exit restores terminal | 1 |
| `TERM=dumb` respected | 1 |

### Phase 10 — Performance Perception (5 pts)

| Check | Points |
|---|---:|
| `--help` / `--version` under ~200 ms | 2 |
| No network in help/version paths | 1 |
| Interactive-prompt latency < 100 ms | 1 |
| Lazy-load of heavy subsystems | 1 |

---

## CLI framework lookup

Use during Phase 1 to anchor expectations.

| Framework | Language | Default `--help` | NO_COLOR | Completions | Typo suggestions |
|---|---|---|---|---|---|
| **commander** | Node | Yes | No (manual) | 3rd-party | Optional (`showSuggestionAfterError`) |
| **yargs** | Node | Yes | No (manual) | Built-in (`yargs.completion()`) | Yes |
| **oclif** | Node | Yes (rich) | Yes | Built-in | Yes |
| **meow** | Node | Minimal | No | No | No |
| **argparse** | Python | Yes | No (manual) | 3rd-party (argcomplete) | No |
| **click** | Python | Yes | Yes (via `click.echo`) | Built-in | No |
| **typer** | Python | Yes (rich) | Yes | Built-in | Yes |
| **cobra** | Go | Yes | No (manual) | Built-in | Yes |
| **urfave/cli** | Go | Yes | No (manual) | Built-in | Yes |
| **clap** | Rust | Yes (rich) | Yes | Built-in (`clap_complete`) | Yes (with `suggestions` feature) |
| **thor** | Ruby | Yes | No (manual) | 3rd-party | No |
| **raw** | any | N/A | N/A | N/A | N/A — build from scratch (usually CRITICAL) |

Framework defaults set the floor. Score against the platform norm — don't dock a Rust CLI for not using Python conventions.

---

## Terminal environment reference

### `NO_COLOR`

Spec: <https://no-color.org>. Any non-empty value disables colour. Test:

```bash
NO_COLOR=1 <cli> <cmd> | cat -v
```

If ANSI escapes appear in `cat -v` output (`^[[31m`), the CLI ignores `NO_COLOR`.

### `FORCE_COLOR`

Opposite of `NO_COLOR`. Common values: `0` (off), `1` (16 colours), `2` (256), `3` (truecolour). A well-behaved CLI respects both variables.

### `isatty(fd)` detection

| Language | Idiom |
|---|---|
| Node | `process.stdout.isTTY` |
| Python | `sys.stdout.isatty()` |
| Go | `golang.org/x/term.IsTerminal(int(os.Stdout.Fd()))` |
| Rust | `std::io::IsTerminal` (1.70+) or `is-terminal` crate |
| Shell | `[ -t 1 ]` |

### `TERM=dumb`

Legacy terminals and many CI systems export `TERM=dumb`. A CLI that honours it should:

- Emit no ANSI escapes
- Skip spinners and progress bars
- Use plain linebreaks instead of cursor addressing

### `CI` environment variable

Most CI systems export `CI=true` (GitHub Actions, GitLab, CircleCI, Travis, Buildkite). The CLI should treat this as "non-interactive, no prompts".

---

## Exit code conventions (`sysexits.h`)

| Code | Name | When to use |
|---|---|---|
| 0 | success | |
| 1 | general failure | Runtime error not covered below |
| 2 | usage error | Bad flags, missing args, help shown |
| 64 | `EX_USAGE` | Usage error (sysexits) |
| 65 | `EX_DATAERR` | Input data malformed |
| 66 | `EX_NOINPUT` | Input file missing |
| 69 | `EX_UNAVAILABLE` | Service unavailable |
| 70 | `EX_SOFTWARE` | Internal software error |
| 74 | `EX_IOERR` | I/O error |
| 77 | `EX_NOPERM` | Permission denied |
| 130 | SIGINT | User pressed Ctrl+C |
| 143 | SIGTERM | Process terminated |

Using `sysexits.h` codes is a nice-to-have. The baseline expectation is: exit 0 on success, exit 2 on usage error, exit non-zero (stable per failure class) on other errors.

---

## CVD-safe colour palette

When scoring Phase 8 accessibility, check that red/green contrasts are **paired with symbols**, not relied on alone. Safe-by-default pairings:

| Status | Colour | Symbol | Text |
|---|---|---|---|
| Success | green (`\e[32m`) | ✓ | PASS / OK |
| Warning | yellow (`\e[33m`) | ⚠ / ! | WARN |
| Error | red (`\e[31m`) | ✗ / × | FAIL / ERROR |
| Info | blue/cyan (`\e[36m`) | · / i | INFO |

Red-green alone is the most common CVD pitfall (~8% of men, ~0.5% of women). Symbols decouple meaning from colour.

---

## Severity tiers

| Tier | When to assign |
|---|---|
| **CRITICAL** | Blocks core usability: help missing examples, destructive subcommand with no confirmation, errors with no explanation, crashes on pipe, ignores `NO_COLOR`. |
| **WARNING** | Frustrates users: inconsistent subcommand grammar, raw stack traces on default, no shell completions, colour-only status signals. |
| **SUGGESTION** | Polish: commit hash in `--version`, man page generation, i18n hooks, structured `--json` mode when not strictly needed. |

Every finding in the report must pick exactly one tier.

---

## Finding template

```
### <phase>.<n>  <short title>

**Severity:** CRITICAL | WARNING | SUGGESTION
**Probe:** `<reproducible command>`
**Observed:**
\`\`\`
<actual output or key excerpt>
\`\`\`
**Source:** <file:line if available>
**Expected:** <what a good CLI would do here>
**Fix:** <concrete next step, e.g. add `--yes` flag, wire up NO_COLOR check>
```
