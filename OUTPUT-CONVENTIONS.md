# Output Conventions — `.anthril/` Folder Scheme

Every skill in this repo that writes files to disk MUST emit them under a
canonical `.anthril/<output-type>/` folder inside the working directory. This
keeps the user's project root clean and makes outputs discoverable, gitignorable,
and easy to clean up.

## Folder scheme

```
.anthril/
├── .anthril/audits/        # audit reports + JSON sidecars + suggested patches
├── plans/         # plan files, migration plans, strategy plans
├── reports/       # analysis reports, snapshots, readouts
├── scaffolds/     # generated code, schemas, scaffolded artefacts
├── data/          # CSVs, JSON datasets, keyword lists, design tokens
└── briefs/        # creative briefs, content briefs, stakeholder briefs
```

## Rules

1. **Always create the target folder first.** Before any `Write`, run
   `mkdir -p .anthril/<type>/` (or the multi-file subfolder equivalent).
2. **Never write to the project root.** No more `./<skill-name>.md` or
   `./report.json` at cwd. Every output goes under `.anthril/<type>/`.
3. **Filenames stay as before.** The convention only changes the prefix, not
   the basename. `database-design-audit.md` becomes
   `.anthril/audits/database-design-audit.md` — not renamed.
4. **Skills emitting multiple artefacts get their own subfolder.** A skill
   that writes a report plus an agent-reports directory plus sidecar JSON
   should write to `.anthril/<type>/<skill-name>/...` (or use a run ID for
   audits — see `application-audit` as the reference implementation).
5. **Templates and scripts must use the same paths.** Update
   `templates/*.md` and `scripts/*.sh` / `scripts/*.py` alongside `SKILL.md`
   so the convention is documented end-to-end.
6. **`.anthril/` belongs in `.gitignore` for downstream user projects.**
   This repo's own `.gitignore` may explicitly NOT ignore it for fixtures.

## Output-type guidance

| Type | When to use |
|---|---|
| `.anthril/audits/` | A review of existing state — code, config, schema, infrastructure, content, finance — producing findings + severity + suggested fixes. |
| `plans/` | A forward-looking sequence of steps the user will execute — migrations, rollouts, strategy plans, training programs. |
| `reports/` | A point-in-time analysis or summary — snapshots, performance reports, readouts, projections. Read-only narrative, no required action list. |
| `scaffolds/` | Generated executable artefacts — SQL bootstrap, RLS policies, JSON-LD schema, scaffolded skill directories. The output is meant to be applied as-is. |
| `data/` | Structured data the user feeds into other tools — CSV keyword lists, design tokens, entity graphs, redirect tables. |
| `briefs/` | Short input documents for collaborators — creative briefs, content briefs, stakeholder briefs, logo briefs. |

When in doubt, pick `reports/`. Cross-type artefacts go where the *primary*
artefact belongs (e.g. an audit with a tiny scaffold sidecar lives in
`.anthril/audits/`).

## Exclusions

**`lifestyle/` plugins are out of scope** for this convention. The lifestyle
category (`health-wellness`, `home-life-logistics`, `personal-finance`,
`personal-productivity`) is designed for chat / Cowork environments, not
Claude Code project sessions. Those skills render their output in the chat
transcript itself; a working-directory `.anthril/` folder has no meaning in
that context.

Lifestyle skills retain their existing "save as" semantics for callers that
do happen to invoke them inside Claude Code. Do NOT retrofit them.

## Reference implementations

- `engineering/software-development/skills/application-audit` — multi-file
  audit using `.anthril/audits/application-audit/<AUDIT_ID>/`.
- `utilities/utilities/skills/audit-resolver` — ledger pattern using
  `.anthril/audits/<date>/`.

New skills SHOULD model their output layout on whichever of these is closer
to their shape.

## Adding a new skill

When scaffolding a new skill with `skill-creator`:

1. Pick the matching output type from the table above.
2. In `SKILL.md`'s output section, use:
   ```
   Save as: .anthril/<type>/<skill-name>.md
   (Run `mkdir -p .anthril/<type>` first.)
   ```
3. If the skill writes multiple files, use
   `.anthril/<type>/<skill-name>/<artefact>` instead.
4. Update `templates/` and `scripts/` to match.
