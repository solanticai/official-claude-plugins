# Changelog Generator — Reference Material

## Conventional Commits → Keep a Changelog Mapping

| Conventional type | Section in Keep a Changelog | Notes |
|-------------------|----------------------------|-------|
| `feat:` | Added | New user-facing capability |
| `fix:` | Fixed | Bug fix |
| `perf:` | Changed | Performance improvement (mention scale) |
| `refactor:` | (usually omit) | Internal-only; include if user-observable |
| `docs:` | (usually omit) | Unless major doc restructure |
| `chore:` | (omit) | Tooling, deps; non-user-facing |
| `style:` | (omit) | Whitespace, formatting |
| `test:` | (omit) | Test-only changes |
| `build:` | (usually omit) | Build-system; include if installs change |
| `ci:` | (omit) | CI-only |
| `revert:` | Mention in Changed | Reference both the revert and the original |
| BREAKING | Top of section with **bold marker** | Migration steps required |

---

## Breaking-Change Detection

Look for these signals in any commit:

- `!:` suffix after type — e.g. `feat(api)!: rename endpoint`
- `BREAKING CHANGE:` in commit footer
- File-deletion in a public-API file
- Version bump in `package.json` major
- Removed exports
- Database migration that drops a column / table

Surface all breaking changes at the top of the changelog section with explicit migration notes.

---

## Semver Bump Rules

- **Major** — any BREAKING change → X+1.0.0
- **Minor** — features (Added) without breaking → x.X+1.0
- **Patch** — only fixes → x.x.X+1
- **Pre-release** — append `-rc.1`, `-beta.2` as appropriate
- Marketplace plugins should NEVER skip versions (e.g. 1.2 → 1.5)

---

## Keep a Changelog Sections (1.1.0 spec)

1. **Added** — new features
2. **Changed** — changes in existing functionality
3. **Deprecated** — soon-to-be-removed features
4. **Removed** — features removed in this release
5. **Fixed** — bug fixes
6. **Security** — security-relevant changes (CVE refs welcome)

Order matters: Added first; Security last.

---

## Style Guidelines

- **User-facing language.** "Login is 2× faster" not "refactored AuthService to use connection pooling"
- **Past tense for changes.** "Added X" not "Adds X"
- **Specific, not vague.** "Fixed crash on Safari mobile when uploading > 50MB file" not "Fixed iOS bug"
- **Reference issues/PRs** where useful — `(closes #123)` or `(#456)`
- **AU spelling.** behaviour, colour, organisation
- **Markdown links** for repo references — `[#123](https://github.com/org/repo/issues/123)`

---

## Common Mistakes

1. **Listing every commit individually** — group related work
2. **Including chore/build commits users don't care about**
3. **Forgetting to surface breaking changes**
4. **Inconsistent versioning** — semver discipline matters for tooling and trust
5. **No date** — Keep a Changelog requires `## [vX.Y.Z] - YYYY-MM-DD`
6. **Reverting commits but still listing the original feature** — exclude both (net-zero)
