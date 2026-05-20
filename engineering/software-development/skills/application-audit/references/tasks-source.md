# Source Notes — `tasks.md`

> Canonical brief that drives the `frontend-auditor`, `backend-auditor`, and
> `cross-cutting-security-auditor` agents. Decomposed into per-agent prompts
> in `agents/application-audit/<role>.md` — auditors read those, not this
> file. Preserved here as a load-bearing reference for skill maintenance.

Below is the stack-specific audit list for a Next.js 15 + React 19 + strict TypeScript + Supabase + Tailwind app. The biggest wins usually come from making rendering and caching decisions explicit, shrinking client JavaScript, locking down Supabase authorization, and then measuring query/runtime hotspots with proper observability.

## Front end audit / optimisation tasks

- Audit every page, layout, and route handler for its intended rendering mode. In Next.js 15, request-time APIs like `cookies()`, `headers()`, `draftMode()`, and route `params` are async, and the caching model is explicit enough that each route should be reviewed for "static and cacheable", "dynamic but streamable", or "fully fresh per request."
- Minimize `use client` boundaries. In the App Router, pages and layouts are Server Components by default, and marking a file with `"use client"` pulls its imports and children into the client bundle. Audit top-level components and push interactivity down into small leaf components instead of making large trees client-side.
- Review every data-fetching path for cache correctness. Decide which queries should use cacheable server rendering, which should stay uncached, and which should stream behind `Suspense`. For cached scopes, avoid reading runtime-only values like cookies or headers inside the cached function; read them outside and pass them in.
- Check every personalized screen for accidental caching. User-specific dashboards, role-based UI, or anything keyed off auth/session/cookies should be treated carefully so cached output is not reused incorrectly across users or requests.
- Audit all Route Handlers for freshness assumptions. Next.js route handlers can prerender in some cases, but reading request properties, cookies, headers, or doing non-deterministic work changes that behavior. Confirm each handler is behaving the way you expect in production.
- Add or tighten `Suspense` boundaries around slow server data. React's streaming SSR and selective hydration work with `Suspense`, and Next.js recommends `Suspense` when you need fresh async data without blocking the whole page.
- Rework mutation-heavy forms to use React 19 Actions where it simplifies the app. Audit forms that currently juggle pending, error, optimistic state, and manual request orchestration; many can be simplified with `<form>` Actions plus `useActionState`, `useOptimistic`, and `useFormStatus`.
- Audit manual memoization. React now documents that the compiler can apply memoization automatically, reducing the need for broad `memo`, `useMemo`, and `useCallback` usage. Profile first, keep only memoization that clearly helps, and use compiler directives sparingly as escape hatches rather than defaults.
- Run a bundle audit on both client and server output. Use the Next.js bundle analyzer, identify large client-only dependencies, and split or lazy-load code that is not needed on the initial route.
- Audit third-party scripts. Move ad, analytics, chat, maps, and other external scripts to `next/script`, and load them only where needed so they do not block or bloat initial rendering.
- Audit images. Make sure you are using `next/image` for responsive images, and set `sizes` correctly when using `fill` or responsive layouts so browsers do not download oversized assets.
- Audit fonts. Use `next/font` instead of external font CSS where possible so fonts are self-hosted, privacy-friendlier, and less likely to cause layout shift. Also review subsets and axes so you are not shipping unnecessary font data.
- Audit Tailwind content scanning. Confirm all source paths are included, and remove patterns that generate class names dynamically via string concatenation if Tailwind cannot see them at build time. Tailwind's scanning is what keeps CSS output small.
- Centralize design tokens in Tailwind theme variables. Colors, spacing, typography, breakpoints, radii, and shadows should come from a single theme layer instead of one-off arbitrary values scattered across the app.
- Audit dark mode and state variants for completeness. Tailwind treats dark mode as a first-class variant, so review whether your full component library, not just main pages, has consistent dark-mode behavior.

## Back end audit / optimisation tasks

- Audit Supabase SSR auth setup. Supabase's SSR guidance for Next.js is cookie-based, not local-storage-based, and the current path is `@supabase/ssr`. If you are still mixing older auth helpers with the SSR package, clean that up first.
- Review every exposed table for Row Level Security. Supabase explicitly recommends RLS for tables in exposed schemas, and browser access is only safe when those policies are correct. Audit selects, inserts, updates, and deletes separately; do not rely on auth existing without row ownership rules.
- Separate browser-safe keys from privileged keys. The publishable/anon key can be used in the browser with RLS; the `service_role` key must never be exposed in the browser and should live only in server-only code or secure function environments.
- Audit storage security. Buckets are private by default, access is governed by RLS on `storage.objects`, and signed URLs should be used for time-limited sharing of private files. Review every upload and download path accordingly.
- Audit Edge Functions for auth and exposure. Supabase Edge Functions require a valid JWT by default; only disable JWT verification intentionally for true public endpoints such as selected webhooks, and document why each exception exists.
- Review API and mutation boundaries. Any privileged write, admin action, billing operation, or ownership-sensitive mutation should happen in a trusted server context, with the authenticated user checked before the write and RLS acting as the final guardrail.
- Tune database queries using actual telemetry, not guesswork. Supabase ships with `pg_stat_statements`, and its docs recommend using those statistics alongside `EXPLAIN` to find hot and slow queries. Audit the top queries by total time and frequency.
- Add indexes that match real query patterns. Supabase's guidance is to align indexes with common filters, ordering, and joins; the dashboard Performance Advisor and Index Advisor can help identify missing indexes, while reminding you that indexes also add write and storage overhead.
- Check for dead weight in the database. Use Supabase inspection tooling to look at bloat, blocking queries, and cache-hit rates so you are not only fixing latency but also fixing the reasons it keeps returning.
- Load-test critical flows on staging. Supabase's production guidance explicitly recommends load testing and using query stats to identify resource limits before they become production incidents.
- Move schema changes into migrations. Supabase documents migrations as the standard way to track schema evolution over time; audit whether your team is drifting via dashboard-only changes and bring those changes back into migration files.
- Generate and refresh TypeScript types from the database schema. The Supabase CLI supports schema-driven type generation, which is valuable in a strict TypeScript app because it reduces mismatches between database reality and application types.

## Cross-cutting security / operational tasks

- Audit environment variable exposure. In Next.js, server env vars stay server-side by default, while `NEXT_PUBLIC_` values are inlined into the browser bundle at build time. Review `.env*` usage so only truly public values get the prefix.
- Add security headers intentionally. Next.js supports response headers in config, so audit CSP, frame restrictions, referrer policy, and similar headers instead of accepting platform defaults blindly.
- If you use Server Actions across origins, audit `serverActions.allowedOrigins`. Next.js documents this as a CSRF-related control; same-origin is the default, and extra origins should be added only deliberately.
- Instrument the app end to end. Next.js recommends OpenTelemetry for application instrumentation, and Supabase provides Logs Explorer plus product reports for database, auth, storage, realtime, and API systems. Without this, optimization work turns into guesswork.

## Suggested audit order

1. Fix auth, RLS, service-role exposure, storage policies, and function exposure first. Those are correctness and security issues, not just performance issues.
2. Then audit server/client boundaries, route caching, and data-fetching behavior, because Next.js 15 and React 19 make these choices more explicit and more important.
3. Then do bundle, script, image, and font optimization to cut initial load and hydration cost.
4. Then use Supabase query stats, advisors, logs, and reports to tune the actual hotspots you measured.
