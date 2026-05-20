# Env Var Audit — example-app (Next.js + Supabase)

**Date:** 20/05/2026

---

## Inventory Summary

- `.env.example` location: `.env.example`
- Declared vars: 12
- Code references found: 14
- Healthy (declared + used): 9
- Drift (declared, unused): 3
- Missing docs (used, undeclared): 5
- Hidden config (in .env not .env.example): 1
- Security flags: 2

---

## Drift — Declared, Never Used (consider removing)

| Variable | Comment in .env.example | Recommended action |
|----------|------------------------|--------------------|
| OLD_API_BASE_URL | (none) | No code reference found; remove or verify it's a CI-only override |
| LEGACY_FLAG | (none) | Last used in commit abc123 (March 2025); safe to remove |
| SLACK_WEBHOOK_DEV | "for dev notifications" | Move to dev-only `.env.example.dev`; not used in production code |

---

## Missing Documentation — Used in code, never declared

| Variable | First found | Recommended action |
|----------|-------------|--------------------|
| STRIPE_WEBHOOK_SECRET | `app/api/webhooks/stripe/route.ts:42` | Add to .env.example with `# DO NOT COMMIT actual secret; provision via Stripe dashboard` |
| SENTRY_DSN | `app/lib/observability.ts:8` | Add — public DSN (safe to commit) |
| FEATURE_FLAG_AI | `app/features/ai/gate.ts:14` | Add with default value |
| NEXT_PUBLIC_SITE_URL | `app/lib/seo.ts:12` | Add — note "NEXT_PUBLIC_" prefix means client-visible |
| RESEND_API_KEY | `app/lib/email.ts:5` | Add to .env.example with `# DO NOT COMMIT; provision via Resend dashboard` |

---

## Hidden Config — In .env not in .env.example

| Variable | Recommended action |
|----------|--------------------|
| INTERNAL_DEBUG_AUTH_BYPASS | **Critical: name suggests local-dev bypass. Verify never used in prod code. Document in .env.example with strong warning.** |

---

## Security Flags

| Variable | Pattern matched | Recommended action |
|----------|----------------|--------------------|
| STRIPE_WEBHOOK_SECRET | name contains 'SECRET' | Already used; add to .env.example with `# DO NOT COMMIT actual value` |
| RESEND_API_KEY | name contains 'KEY' | Same |

---

## Recommended Actions

1. **Add 5 missing vars to .env.example** with example values + comments — STRIPE_WEBHOOK_SECRET, SENTRY_DSN, FEATURE_FLAG_AI, NEXT_PUBLIC_SITE_URL, RESEND_API_KEY.
2. **Remove 3 drift vars** (OLD_API_BASE_URL, LEGACY_FLAG, SLACK_WEBHOOK_DEV) after confirming no CI usage via `grep -r OLD_API_BASE_URL .github/`.
3. **Audit INTERNAL_DEBUG_AUTH_BYPASS urgently** — name suggests dev-only auth bypass. Verify with `grep -r INTERNAL_DEBUG_AUTH_BYPASS app/` that no production code path uses it. If safe, document in .env.example with `# Local dev only — production must never set this`.
4. **Establish convention:** All secret vars end in `_SECRET`, `_KEY`, `_TOKEN`, `_PRIVATE`. All publicly-visible client-side vars use `NEXT_PUBLIC_` prefix.
5. **Add a `.env.example` linter to CI** — e.g. compare extracted env-var refs from code vs declared each PR.
