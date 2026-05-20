# Source Notes — `client-connection-audit.md`

> Canonical brief for the connection-related auditors. Decomposed into per-agent
> prompts in `agents/application-audit/{client-connection,server-client,postgres,connection-limit,leak-detection}-auditor.md`.
> Preserved here as the load-bearing reference for the connection-path audit.

For this stack, the connection audit breaks into four distinct paths:

1. browser/client components → Supabase Data APIs / Realtime
2. Next.js server runtime → Supabase server client or direct Postgres client
3. direct Postgres / ORM traffic → pooled or direct DB connections
4. Realtime WebSocket usage → concurrent connection quota and subscription lifecycle

Supabase's own connection guidance is to use the Data API from frontend apps, use direct connections for persistent backend services, use Supavisor session mode for persistent backends that need IPv4, and use Supavisor transaction mode for short-lived/serverless or edge workloads.

## 1) First audit: map every connection path

Audit every place your app talks to Supabase or Postgres and label it as one of these: browser Data API, browser Realtime, Server Component / Server Action / Route Handler, direct Postgres via ORM/driver, migrations/admin tools, or background jobs. The point is to stop treating all "database access" as one thing, because Supabase recommends different connection methods depending on whether the caller is frontend, a persistent backend, or a temporary/serverless runtime.

Your first deliverable should be a connection inventory with:

- entrypoint
- runtime (browser, Node serverless, VM/container, edge)
- library used (`@supabase/ssr`, `@supabase/supabase-js`, Prisma, Drizzle, postgres.js, etc.)
- auth context
- connection method (Data API, direct, Supavisor session, Supavisor transaction, dedicated pooler)
- whether it is long-lived or bursty
- whether it opens Realtime channels

## 2) Browser/client connection audit

For frontend CRUD and reads, verify you are using the Supabase Data API / client library rather than trying to use Postgres connection strings from the browser. Supabase's guidance is that frontend applications should use the Data API, and the client libraries wrap those APIs and handle auth for you. That means "pooling" in the browser is mostly about reducing duplicate HTTP calls and duplicate Realtime subscriptions, not tuning raw Postgres sockets.

Audit these items:

- Check that every browser data call is truly needed in the browser. Move reads that do not require client interactivity into Server Components where possible, since Next.js supports database/async I/O in Server Components and Supabase SSR is designed for server rendering with cookie-based auth.
- Reduce duplicate browser fetches. In Next.js App Router, identical `fetch` calls in a React component tree are memoized by default, and `fetch` is not cached by default unless you opt in. Audit repeated profile/session/config/API requests and consolidate them so you are not opening unnecessary outbound requests on every render or route transition.
- Audit client-side data libraries. If you use SWR or React Query in Client Components, check for overly aggressive revalidation, multiple keys pointing to the same underlying resource, and duplicated polling that could be moved server-side.
- Audit Realtime subscription lifecycle in client components. Supabase notes that Realtime usage is billed and limited by simultaneous connections, and each connected client can join multiple channels. Review whether components subscribe more than once, fail to unsubscribe, or subscribe before the UI actually needs live updates.
- Audit where you instantiate the browser Supabase client. Supabase recommends a dedicated browser client utility for Client Components; review whether you are recreating clients ad hoc across files instead of standardizing creation through one utility path.

## 3) Next.js SSR / server-client audit

Supabase's current SSR guidance for Next.js is to maintain two client types: a browser client for Client Components and a server client for Server Components, Server Actions, and Route Handlers. Review your codebase to make sure those boundaries are clean and not mixed together.

Audit these items:

- Confirm you have separate `lib/supabase/client` and `lib/supabase/server` utilities, or an equivalent pattern, instead of importing one generic client everywhere.
- Review middleware Proxy usage. The Proxy is needed because Server Components cannot write cookies, and Supabase's docs note the matcher should exclude routes that do not access Supabase. Audit your matcher so you are not refreshing auth tokens and touching cookies on routes that never use Supabase.
- Audit auth-refresh churn. The Proxy is responsible for refreshing claims and writing refreshed cookies to request/response. If it runs too broadly, you create unnecessary request-time work and cookie writes across the app.
- Audit caching around auth. Supabase explicitly warns that SSR/ISR/CDN caching of responses that include refreshed session cookies can cause one user to receive another user's session. Review any CDN, ISR, or full-page caching on auth-aware routes.
- Push data access server-side where possible. Server Components can use direct async I/O including an ORM or database, and Supabase SSR notes server-side rendering reduces client bundle size and execution time. Audit any client → API → DB hop that could instead be server-rendered.

## 4) Direct Postgres / ORM connection audit

This section only applies if you are using Prisma, Drizzle, postgres.js, or another direct Postgres client in server code, jobs, or admin scripts. If you are only using `supabase-js`/Data APIs, most of the raw DB pooling work below does not apply to your browser path.

Audit these items:

- Decide whether each runtime is persistent or temporary. Supabase recommends direct connections for persistent servers, session pooler as an IPv4-friendly alternative for persistent backends, and transaction pooler for serverless or edge functions. Audit every ORM/client by deployment target, not by developer preference.
- For serverless or edge workloads, verify they use Supavisor transaction mode on port `6543`, not direct DB connections, because transaction mode is specifically intended for many transient connections.
- If using transaction mode, audit prepared statements immediately. Supabase explicitly says transaction mode does not support prepared statements and advises turning them off in your connection library. This is one of the most common correctness issues when pairing serverless runtimes with ORM/native clients.
- For persistent Node servers, containers, or VMs, prefer direct connections when your environment supports IPv6; if you need IPv4, audit whether Supavisor session mode is the right fallback.
- Separate application-runtime traffic from admin traffic. Direct connections are best for long-lived sessions and are the right choice for migrations, `pg_dump`, backup, and management tools. Audit admin jobs so they are not sharing the same runtime pool strategy as your request-serving app.
- Audit whether you are accidentally stacking poolers. You can technically run Supavisor and PgBouncer together, but it is generally not recommended because it increases the risk of hitting max database connections on smaller tiers.
- Review whether you are using the right kind of pooler at the app layer. Application-side poolers are built into libraries such as Prisma and are satisfactory for long-standing containers/VMs, while server-side poolers are best for auto-scaling edge/serverless systems. Audit whether your current mix matches your actual hosting model.
- Confirm SSL is enabled on every direct or pooled Postgres connection.

## 5) Pool sizing and connection-limit audit

This is where most teams guess. Supabase gives you the right model:

- client connections = how many clients can connect to the pooler
- backend connections = how many real Postgres connections the pooler opens
- total backend DB load = direct connections + Supavisor backend connections + PgBouncer backend connections, all within the DB max connection limit

Audit these items:

- Check whether your team is confusing pool size with client limit. Pool size and "max pooler clients" are different limits and apply independently to Supavisor and PgBouncer.
- Review your current Supavisor pool size in Database Settings. Every compute add-on has a preconfigured direct-connection count and Supavisor pool size; you can change the pool size in the dashboard.
- Compare current pool size with your actual workload mix. Supabase's general rule is: if you rely heavily on PostgREST, be cautious raising pool size past about 40% of DB max connections; otherwise, you can often allocate around 80% to the pool, leaving room for Auth and other utilities.
- Audit combined mode usage. Supavisor session mode (`5432`) and transaction mode (`6543`) share the same total Supavisor backend pool budget. Do not assume each mode gets a fully separate database budget.
- If you also use PgBouncer, include it explicitly in capacity planning. Both Supavisor and PgBouncer reference the same pool-size setting independently, so combined usage can produce much higher backend connection pressure than expected.

## 6) Realtime connection audit

If you use Realtime, treat it as its own connection system, not just "another Supabase feature." Supabase defines concurrent peak connections as the number of simultaneous Realtime connections, and one connected client can join multiple channels.

Audit these items:

- Inventory every place you create a Realtime client or subscribe to channels. Make sure subscriptions are attached only where live updates are a product requirement.
- Review whether you can downgrade some live features to server-rendered refreshes, on-demand refetch, or periodic revalidation instead of permanent socket connections.
- Check for duplicate channel subscriptions for the same resource in different components, layouts, or tabs/windows.
- Ensure subscriptions are torn down on unmount, route change, sign-out, and auth-context changes.
- Monitor both message volume and concurrent peak connections, since Supabase prices/bounds Realtime on those dimensions.

## 7) Monitoring and leak-detection audit

Supabase's connection-management docs are very clear that you should monitor both historical and live connection usage.

Audit these items:

- In Supabase observability, review historical charts for `Postgres`, `PostgREST`, `Auth`, `Storage`, and other role-based connection types. These charts help identify connection leaks and plan capacity.
- Use `pg_stat_activity` to inspect live connections and look for idle sessions holding slots unnecessarily.
- Tag/identify applications consistently. In `pg_stat_activity`, check `application_name`, connected role, state, query age, and backend start time so you can tell request traffic apart from Prisma/Drizzle/admin tools/background jobs.
- Build alerts for: rising idle connection count, pooler client saturation, backend connection saturation, Realtime connection spikes, and sudden PostgREST/Auth connection jumps.

## 8) Concrete "fix this if found" items

These are the highest-value fixes to look for:

- Browser pages doing client-side fetching for data that could be rendered in a Server Component.
- Multiple ad hoc Supabase client creation patterns instead of a dedicated browser utility and server utility.
- Middleware Proxy matcher covering too many routes and refreshing auth on pages that do not access Supabase.
- ORM/native Postgres usage in serverless runtimes pointing at direct Postgres instead of Supavisor transaction mode.
- Prepared statements still enabled while using transaction mode.
- Supavisor and PgBouncer both enabled without a deliberate capacity model.
- Pool size increased without checking how much PostgREST/Auth/Storage traffic also needs connection headroom.
- Realtime subscriptions created too early, too often, or never cleaned up.

## 9) Recommended default for your stack

For a typical Next.js 15 + Supabase app:

- In the browser, use the Supabase client/Data API, not direct Postgres.
- In Server Components, Server Actions, and Route Handlers, use the server-side Supabase client pattern from `@supabase/ssr`.
- If you also use Prisma/Drizzle/postgres.js in serverless functions, point that traffic at Supavisor transaction mode (`6543`) and disable prepared statements where required.
- If you run a persistent Node server/container/VM, prefer direct Postgres if IPv6 is available; otherwise consider session mode.
- Do not run both Supavisor and PgBouncer by default.
- Monitor connection history and live activity before changing pool sizes.
