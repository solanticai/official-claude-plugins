# Container Audit — Reference

## §1 — Audit Taxonomy

### A. Base image
| ID | Check |
|---|---|
| A.1 | Smallest appropriate base (distroless / alpine / scratch where feasible) |
| A.2 | Base image pinned by digest, not tag |
| A.3 | Base image from a trusted registry (Docker Hub official, GCR distroless, vendor registries) |
| A.4 | Base image patch level current (<30 days old in live mode) |
| A.5 | No `latest` tag on production images |

### B. User & privileges
| ID | Check |
|---|---|
| B.1 | Explicit non-root `USER` directive set before ENTRYPOINT/CMD |
| B.2 | UID / GID numeric (not reliant on passwd lookup) |
| B.3 | `--cap-drop=ALL` runtime hint (via `.dockerignore` or docs) |
| B.4 | Read-only root filesystem hint (via `docker run --read-only` docs or compose `read_only: true`) |
| B.5 | No `RUN sudo`, no `USER 0` late in file |

### C. Secrets & leaks
| ID | Check |
|---|---|
| C.1 | No `ARG` named `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*KEY*` |
| C.2 | No `ENV` that sets a secret value (even if empty) |
| C.3 | No `COPY .env*` into the image |
| C.4 | Build-time secrets use BuildKit `--mount=type=secret` |
| C.5 | No `echo $SECRET` or embedding of `${{ secrets.* }}` via bind args |
| C.6 | `.dockerignore` excludes `.env*` |

### D. Layer efficiency
| ID | Check |
|---|---|
| D.1 | Multi-stage build for any image that compiles code |
| D.2 | `COPY --from=builder` pattern used for artefact transfer |
| D.3 | `RUN apt-get update && apt-get install && rm -rf /var/lib/apt/lists/*` combined |
| D.4 | Lockfile COPY'd before source COPY (for cache) |
| D.5 | Build tools not shipped in final image |
| D.6 | Image size reasonable for the workload (<300MB for a typical Node/Python API) |

### E. Signals & shutdown
| ID | Check |
|---|---|
| E.1 | PID 1 handler (tini / dumb-init) for Node/Python if not using init-capable base |
| E.2 | `STOPSIGNAL` explicit where relevant (e.g., nginx `SIGQUIT`) |
| E.3 | `CMD` in exec form (`["node", "server.js"]`), not shell form (`node server.js`) |
| E.4 | ENTRYPOINT handles signal forwarding if wrapping the real command |

### F. Healthcheck
| ID | Check |
|---|---|
| F.1 | HEALTHCHECK directive present |
| F.2 | Command tests the application, not just the process (not `pgrep node`) |
| F.3 | Interval and timeout sensible (default 30s+30s is often too lazy for k8s) |
| F.4 | No circular dependency (healthcheck calls a service that depends on this image) |

### G. `.dockerignore`
| ID | Check |
|---|---|
| G.1 | Excludes `.git`, `.github`, `.circleci`, etc. |
| G.2 | Excludes `node_modules`, `__pycache__`, `target/`, `build/` |
| G.3 | Excludes `.env`, `.env.*`, `*.pem`, `*.key` |
| G.4 | Excludes `tests/`, `*.test.*`, `coverage/` |
| G.5 | Excludes OS junk (`.DS_Store`, `Thumbs.db`) |

### H. docker-compose
| ID | Check |
|---|---|
| H.1 | No `privileged: true` |
| H.2 | No `network_mode: host` unless justified |
| H.3 | No `pid: host`, `ipc: host` |
| H.4 | Named volumes, not host paths, for persistent data |
| H.5 | Resource limits (`mem_limit`, `cpus`) set |
| H.6 | `restart:` policy declared |
| H.7 | Secrets via `secrets:` top-level, not `environment:` |
| H.8 | No `latest` tags on service images |

---

## §2 — Severity Rubric

| Severity | Examples |
|---|---|
| **CRITICAL** | `USER root` final state + secrets in ENV, `privileged: true` in compose, hardcoded credential in Dockerfile |
| **HIGH** | No `USER` directive (default root), secret ARG, `latest` tag on prod image, build tools shipped in prod image |
| **MEDIUM** | Tag-pinned base, no HEALTHCHECK on a service container, missing `.dockerignore` for `.env` |
| **INFO** | Layer order suboptimal for cache, STOPSIGNAL not set on nginx |

---

## §3 — Scoring Weights

| Category | Weight |
|---|---|
| A. Base image | 15 |
| B. User & privileges | 20 |
| C. Secrets & leaks | 20 |
| D. Layer efficiency | 10 |
| E. Signals & shutdown | 5 |
| F. Healthcheck | 10 |
| G. `.dockerignore` | 10 |
| H. docker-compose | 10 |

---

## §4 — CIS Docker Benchmark Mapping

| CIS control | Covered by category | Notes |
|---|---|---|
| 4.1 Dockerfile user created | B.1 | Non-root USER |
| 4.2 Trusted base images | A.3 | Registry trust |
| 4.3 Packages not installed | D.5 | Final image slim |
| 4.6 HEALTHCHECK | F.1 | |
| 4.7 Not using update alone | D.3 | `apt-get update && install` combined |
| 4.9 COPY vs ADD | D.* | ADD should be avoided |
| 4.10 Secrets not stored | C.* | |
| 5.* Runtime (compose) | H.* | privileged / host-ns / caps |
