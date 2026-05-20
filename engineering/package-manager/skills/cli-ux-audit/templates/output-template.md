# CLI UX Audit Report

## Summary

| Field | Value |
|-------|-------|
| **CLI** | {{binary-name}} |
| **Version** | {{version}} |
| **Date** | {{YYYY-MM-DD}} |
| **Overall Score** | {{X}}/100 |
| **Overall Verdict** | {{PASS / FAIL / PASS WITH WARNINGS / CONDITIONAL}} |
| **Critical Issues** | {{count}} |
| **Warnings** | {{count}} |
| **Suggestions** | {{count}} |

## CLI Identity

| Field | Value |
|-------|-------|
| Binary path | {{/usr/local/bin/cli}} |
| Language / Runtime | {{Node / Python / Go / Rust / Ruby / Shell / compiled}} |
| Framework | {{commander / yargs / oclif / click / typer / cobra / clap / thor / argparse / raw}} |
| Subcommand tree depth | {{N}} |
| Top-level subcommands | {{count}} |
| Source repo | {{URL or "closed source"}} |

---

## Phase Results

### Phase 1: Discovery & Invocation -- CONTEXT

{{CLI identity, framework, invocation probes, baseline captured}}

### Phase 2: Help & Documentation -- {{X}}/15 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| `--help` and `-h` both work | {{PASS/FAIL}} | {{details}} |
| Per-subcommand help works | {{PASS/FAIL}} | {{details}} |
| Help to stdout | {{PASS/FAIL}} | {{details}} |
| Synopsis line | {{PASS/FAIL}} | {{details}} |
| Options block with descriptions | {{PASS/FAIL}} | {{details}} |
| **Examples block** | {{PASS/FAIL}} | {{details}} |
| Defaults shown inline | {{PASS/FAIL}} | {{details}} |
| Wraps at narrow width | {{PASS/FAIL}} | `COLUMNS=40` result |
| `--version` exits 0 | {{PASS/FAIL}} | {{details}} |
| Man page shipped | {{PASS/FAIL}} | {{details}} |

### Phase 3: Command Structure & Argument Parsing -- {{X}}/15 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Consistent subcommand grammar | {{PASS/FAIL}} | {{details}} |
| Short aliases for common flags | {{PASS/FAIL}} | {{details}} |
| Negatable booleans | {{PASS/FAIL}} | {{details}} |
| Required-arg validation | {{PASS/FAIL}} | {{details}} |
| Unknown-flag rejection | {{PASS/FAIL}} | {{details}} |
| Typo suggestions | {{PASS/FAIL}} | {{details}} |
| Flag order independence | {{PASS/FAIL}} | {{details}} |
| `--` separator | {{PASS/FAIL}} | {{details}} |
| Destructive actions gated | {{PASS/FAIL}} | {{details}} |
| Tree depth ≤ 3 | {{PASS/FAIL}} | {{details}} |
| Mutually exclusive flags enforced | {{PASS/FAIL}} | {{details}} |

### Phase 4: Error Messages & Exit Codes -- {{X}}/15 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Distinct exit codes | {{PASS/FAIL}} | {{codes seen}} |
| `sysexits.h` convention | {{PASS/FAIL}} | {{details}} |
| Errors to stderr | {{PASS/FAIL}} | {{details}} |
| Three-part error format | {{PASS/FAIL}} | {{details}} |
| No raw stack traces | {{PASS/FAIL}} | {{details}} |
| Missing-input names the arg | {{PASS/FAIL}} | {{details}} |
| Graceful network/FS errors | {{PASS/FAIL}} | {{details}} |
| Clean signal handling | {{PASS/FAIL}} | {{details}} |
| Secrets redacted | {{PASS/FAIL}} | {{details}} |

### Phase 5: Output Formatting -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Aligned tables/lists | {{PASS/FAIL}} | {{details}} |
| Semantic colour usage | {{PASS/FAIL}} | {{details}} |
| `NO_COLOR` honoured | {{PASS/FAIL}} | `NO_COLOR=1` probe result |
| Pipe-safe (strips ANSI) | {{PASS/FAIL}} | `cli ... | cat -v` result |
| `--json` or structured mode | {{PASS/FAIL}} | {{details}} |
| Progress to stderr | {{PASS/FAIL}} | {{details}} |

### Phase 6: Interactivity & Progress Feedback -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Feedback for ops > 2s | {{PASS/FAIL}} | {{details}} |
| Spinners disabled on non-TTY | {{PASS/FAIL}} | {{details}} |
| Tested prompt library | {{PASS/FAIL}} | {{library}} |
| Defaults shown in prompt | {{PASS/FAIL}} | {{details}} |
| Non-interactive escape hatch | {{PASS/FAIL}} | {{--yes / env var}} |
| `CI=true` auto-detected | {{PASS/FAIL}} | {{details}} |
| Ctrl+C on prompt exits 130 | {{PASS/FAIL}} | {{details}} |

### Phase 7: Discoverability & Onboarding -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| No-args shows help | {{PASS/FAIL}} | {{details}} |
| Top-level subcommand list | {{PASS/FAIL}} | {{details}} |
| Typo suggestions | {{PASS/FAIL}} | {{details}} |
| Shell completions | {{PASS/FAIL}} | {{bash/zsh/fish/pwsh}} |
| First-run guidance | {{PASS/FAIL}} | {{details}} |
| `--version` includes commit/date | {{PASS/FAIL}} | {{details}} |

### Phase 8: Accessibility & I18n -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Status has text/symbol cue | {{PASS/FAIL}} | {{details}} |
| CVD-safe palette | {{PASS/FAIL}} | {{details}} |
| Critical info as text | {{PASS/FAIL}} | {{details}} |
| Locale awareness | {{PASS/FAIL}} | {{details}} |
| Unicode degrades on `LANG=C` | {{PASS/FAIL}} | {{details}} |
| High-contrast friendly | {{PASS/FAIL}} | {{details}} |

### Phase 9: Terminal Compatibility & Piping Safety -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| No ANSI leakage on pipes | {{PASS/FAIL}} | {{details}} |
| `isatty` detection | {{PASS/FAIL}} | {{details}} |
| Cross-terminal support | {{PASS/FAIL}} | {{terminals tested}} |
| `COLUMNS` handling | {{PASS/FAIL}} | {{details}} |
| SIGWINCH (TUIs only) | {{PASS/FAIL/N/A}} | {{details}} |
| Clean exit restores terminal | {{PASS/FAIL}} | {{details}} |
| `TERM=dumb` respected | {{PASS/FAIL}} | {{details}} |

### Phase 10: Performance Perception -- {{X}}/5 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| `--help` / `--version` < 200 ms | {{PASS/FAIL}} | `time cli --version` = {{Xms}} |
| No network in help/version paths | {{PASS/FAIL}} | {{details}} |
| Prompt latency < 100 ms | {{PASS/FAIL}} | {{details}} |
| Lazy-load heavy subsystems | {{PASS/FAIL}} | {{details}} |

---

## Prioritised Action List

### Critical (must fix — blocks usability)
1. {{finding with probe command + evidence}}

### Warnings (should fix)
1. {{finding with probe command + evidence}}

### Suggestions (polish)
1. {{finding}}

---

## Visual Summary

```mermaid
pie title Issues by Severity
    "Critical" : {{count}}
    "Warning" : {{count}}
    "Suggestion" : {{count}}
```

```mermaid
pie title Score Distribution by Phase
    "Help & Docs" : {{score}}
    "Command Structure" : {{score}}
    "Errors & Exit Codes" : {{score}}
    "Output Formatting" : {{score}}
    "Interactivity" : {{score}}
    "Discoverability" : {{score}}
    "Accessibility" : {{score}}
    "Terminal Compat" : {{score}}
    "Performance" : {{score}}
```
