# ADR-007 — Docker Compose as the Single Deployable Unit (`docker compose up`)

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** Author (sole)
- **Source inputs:** README notes #2 and #4, `docs/00.defining.md` Q2.5,
  Q2.6, 300-Q1.3

## Context

README note #2 mandates `docker compose` as the single-command run target.
The defining doc confirms there is one service (`app`) and zero infra
dependencies (no Postgres, no Redis, no broker). We need to fix the
base image, Python version, and dependency-installation strategy.

## Options Considered

1. **`python:3.14-slim` + `pip install -r requirements.txt`.** Familiar, but
   `pip` resolution is slow and lockfile semantics are weak.
2. **`python:3.14.6-slim` (digest-pinned) + `uv sync --frozen`.** Modern,
   lockfile-aware, ~10× faster install, single `pyproject.toml`.
3. **Distroless / Chainguard.** Smallest attack surface. Adds a vendor
   dependency that the author does not control.

## Decision

**Option 2.** Multi-stage Dockerfile (single stage is sufficient — no
compiled C extensions beyond what `numpy` ships):

```dockerfile
FROM python:3.14.6-slim@sha256:<digest>
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY src/ ./src/
COPY data/mock/ ./data/mock/
ENTRYPOINT ["uv", "run", "mc-risk"]
```

`docker-compose.yml` defines a single service (`app`) with a bind-mounted
`./output/` volume. `docker compose up` runs the default simulation and
exits. `OMP_NUM_THREADS` is set to the container's CPU limit per
Defining 300-Q6.6.

## Consequences

**Positive**
- One command. Matches README.
- `uv sync --frozen` makes CI installs deterministic.
- Digest-pinned base image makes Trivy scans reproducible (ADR-010 +
  300-Q8.4).

**Negative**
- Requires Docker on the author's laptop. Already a hard prerequisite per
  README note #2.
- Image size ~400 MB (NumPy + Matplotlib are heavy). Acceptable for a
  learning repo.

**Reversibility**
- Fully reversible by swapping the base image and dependency manager.
