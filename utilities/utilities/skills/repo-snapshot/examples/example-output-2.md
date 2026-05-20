# Repo Snapshot — Next.js + Supabase B2B SaaS (`acme-platform`)

**Date:** 20/05/2026
**Audience:** new-hire (engineering)

This is a worked example for a typical AU B2B SaaS repository — distinct from the meta-example targeting this very plugins repo.

---

## At a Glance

| Aspect | Value |
|--------|-------|
| Primary language | TypeScript (~92% LOC) + a small Python data-pipeline (~5%) + SQL (~3%) |
| Framework | Next.js 15 App Router + React 19 + Server Components |
| Build tool | pnpm + Turborepo (monorepo: `apps/web`, `apps/admin`, `packages/ui`, `packages/db`) |
| Test framework | Vitest (unit + component) + Playwright (e2e) |
| Database | Supabase (Postgres 16) — RLS-driven multi-tenant via `org_id` |
| Deployment | Vercel (web + admin) + Supabase managed (db + auth + storage) |
| CI | GitHub Actions — type-check + lint + test + build per PR |
| Total LOC | ~62,000 (excluding generated types + lockfile) |
| Top-level folders | 4 (`apps/`, `packages/`, `supabase/`, `infra/`) |
| Last commit | 19/05/2026 (yesterday) — currently active |

---

## Folder Tree (curated)

```
acme-platform/
├── apps/
│   ├── web/                # Public-facing customer app — Next.js
│   │   ├── app/            # App Router routes
│   │   ├── components/     # React components
│   │   ├── lib/            # Shared utilities (supabase client, auth helpers)
│   │   └── server/         # Server actions
│   ├── admin/              # Internal admin dashboard — Next.js
│   └── data-pipeline/      # Python — Daily ETL into reporting tables
├── packages/
│   ├── ui/                 # Shared shadcn-based UI primitives
│   ├── db/                 # Database client types + Supabase wrappers
│   ├── config/             # Shared ESLint + tsconfig + tailwind
│   └── analytics/          # Posthog + Sentry helpers
├── supabase/
│   ├── migrations/         # SQL migrations (timestamped, ~40 to date)
│   ├── functions/          # Edge functions (Deno)
│   └── seed.sql            # Local dev seed
├── infra/
│   └── github-actions/     # CI workflow files
├── package.json            # Workspace root
├── pnpm-workspace.yaml
├── turbo.json              # Turborepo pipeline config
├── README.md
└── CLAUDE.md               # Project-level Claude Code instructions
```

Top-level files of note:

- `README.md` — onboarding + getting-started
- `CLAUDE.md` — project conventions (Australian English, no `any`, RLS-first, etc.)
- `turbo.json` — read this to understand the build graph
- `supabase/migrations/` — read in order to understand schema evolution

---

## Top Files by LOC

| File | LOC | Worth attention? |
|------|-----|-----------------|
| `apps/web/lib/supabase/server.ts` | 480 | Yes — server-side Supabase client + auth refresh logic; touched by every server action |
| `apps/web/app/(authenticated)/dashboard/page.tsx` | 420 | Yes — god-page; should be split |
| `packages/db/types.generated.ts` | 1,840 | Generated via `supabase gen types typescript` — do not edit |
| `apps/web/components/data-table.tsx` | 380 | Yes — used by 14 routes; understand its prop API |
| `apps/web/lib/auth.ts` | 310 | Yes — RLS-aware session helpers |
| `supabase/migrations/20240612120000_init.sql` | 290 | Yes — original schema; read once |
| `apps/admin/app/(admin)/users/page.tsx` | 270 | Yes — service-role usage example (server-side only) |
| `packages/ui/components/button.tsx` | 95 | Reference for the design system pattern |

---

## Dependency Surface

- **Runtime deps:** 47 (pnpm, deduplicated across workspace)
- **Dev deps:** 38
- **Notable libs:**
  - State: TanStack Query + Zustand (lightweight)
  - Auth: `@supabase/ssr` + `@supabase/supabase-js`
  - Forms: react-hook-form + zod
  - UI: shadcn-style on Radix primitives + Tailwind
  - Observability: Sentry + Posthog
- **Risk flags:**
  - 3 deps last-updated > 12 months (acceptable; verify CVE status quarterly)
  - No deprecated APIs detected
  - Lock file (`pnpm-lock.yaml`) committed

---

## Contributor + Cadence

- **Top 3 contributors (last 6 mo):** alice@ (founding eng), bob@ (CTO), charlie@ (mid eng — joined Feb)
- **Commits per month (last 3 mo avg):** ~140
- **Activity status:** very active; daily commits Mon–Fri
- **PRs merged per week:** ~9 average
- **Avg PR size:** ~280 lines

---

## Onboarding Recommendations

For audience = new-hire (engineering), read in order:

1. `README.md` + `CLAUDE.md` — project conventions; what does our team value
2. `supabase/migrations/20240612120000_init.sql` — the schema; the foundation of every feature
3. `apps/web/lib/supabase/server.ts` — how we wrap Supabase server-side; auth refresh; RLS bypass via service_role
4. `apps/web/lib/auth.ts` — session lifecycle; protect-route pattern
5. `apps/web/app/(authenticated)/dashboard/page.tsx` — typical authenticated route; demonstrates server-action + RLS-aware queries
6. Pick a tiny `good-first-issue` PR — usually under 50 lines; learn the CI gating

---

## Risks Surfaced

1. **Two-person bus-factor on auth + Supabase wrapper code.** alice@ + bob@ are the only two who deeply understand `lib/supabase/server.ts`. Charlie joined Feb but isn't onboarded to this file. Mitigation: pair charlie@ with alice@ on the next auth-touching PR; require it as part of the on-call rotation prep.
2. **God-page in dashboard.** `apps/web/app/(authenticated)/dashboard/page.tsx` is 420 lines and likely needs decomposition into 4–5 sub-components. Filed as `tech-debt/dashboard-split` ticket.
3. **Generated types in source control.** `packages/db/types.generated.ts` is committed but regenerated from CI. PR conflicts on this file are noisy — consider a pre-commit hook or generation-on-deploy strategy.
4. **No dependency-update automation.** Dependabot or Renovate would catch CVEs faster than the current quarterly manual review.
5. **3 old deps (last update > 12 mo).** Audit current CVE status; upgrade where security-relevant.
6. **No load testing.** With B2B SaaS scaling toward enterprise, k6 or similar tooling should be wired into CI for critical endpoints before signing larger contracts.

---

## How to use this snapshot

- **For a new engineer:** read top-to-bottom. Should take ~30 minutes. By the end, you have a mental map.
- **For an investor:** focus on Risks + Contributor cadence + Activity status. Skip the file-by-file detail.
- **For a future-you (you wrote this code 18 months ago and forgot):** the "Onboarding Recommendations" section is your fastest re-orientation.
