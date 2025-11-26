# Agent Codex Deployment & Fixes Roadmap

This document captures the end‑to‑end troubleshooting and deployment journey for ForgeTrace (frontend + backend), with emphasis on production bring‑up. It lists what broke, why, how we fixed it, and what tools/packages do in plain language.

---
## High‑Level Timeline & Checkpoints
1) DNS & TLS readiness  
   - Pointed `forgetrace.pro` / `www.forgetrace.pro` to the frontend load balancer/IP; `api.forgetrace.pro` to the API LB/IP.  
   - Obtained LetsEncrypt cert (`www.forgetrace.pro`, `api.forgetrace.pro`) via certbot + nginx plugin.

2) Frontend container build and tests  
   - Fixed TypeScript test errors (missing imports, wrong module paths).  
   - Swapped Vitest to `happy-dom` for Node 18 compatibility; added polyfills in `src/test/setup.ts`.  
   - Ensured `npm test` and `npm run build` pass.  
   - Built image with `VITE_API_URL=https://api.forgetrace.pro/api/v1`.

3) Backend container build and crashes  
   - Async DB driver mismatch: `sqlite:///` failed with SQLAlchemy async; switched to `sqlite+aiosqlite:///` and installed `aiosqlite`.  
   - Missing deps: added `email-validator` and `httpx` to requirements.  
   - Path resolution crash in `scanner.py` (used `parents[4]` in a shallow container); fixed with env override and safe parent clamp.

4) Nginx reverse proxy and ports  
   - Frontend on 3001, backend on 8000; Nginx terminates TLS on 443 and proxies to containers.  
   - Added HTTP→HTTPS redirect on 80 for all hosts.

5) Systemd conflict and port binding  
   - A host `uvicorn` service (`forgetrace-backend.service`) occupied 8000; stopped/disabled the service before starting the Dockerized backend.

6) Final verification targets  
   - Local health: `curl http://127.0.0.1:8000/health`, `curl -I http://127.0.0.1:3001/`.  
   - Public: `curl -I https://api.forgetrace.pro/health`, `curl -I https://www.forgetrace.pro`.

---
## Errors Encountered, Causes, and Fixes

- **TypeScript/Vitest errors (frontend)**  
  - *Cause*: Missing imports (`vi`, `fireEvent`, React), wrong relative paths, and default `jsdom` requiring Node 20.  
  - *Fix*: Corrected imports, switched Vitest environment to `happy-dom`, added polyfills, reran tests.

- **TLS/HTTPS failures**  
  - *Cause*: Nginx not listening on 443 for new hosts; cert not applied.  
  - *Fix*: Added HTTPS server blocks, pointed to LetsEncrypt cert paths, reloaded Nginx.

- **Backend restart loop: async driver**  
  - *Cause*: SQLAlchemy async engine with sync SQLite driver (`pysqlite`).  
  - *Fix*: Use `sqlite+aiosqlite:///` and install `aiosqlite`.

- **Backend restart loop: missing packages**  
  - *Cause*: `email-validator` and `httpx` not installed.  
  - *Fix*: Added to `requirements.txt`, rebuilt without cache.

- **Backend crash: path IndexError in `scanner.py`**  
  - *Cause*: `Path(__file__).resolve().parents[4]` out of range in the container.  
  - *Fix*: Safe resolution with `FORGETRACE_PROJECT_ROOT` env override; fallback to `parents[2]` clamp.

- **Port binding failures on 8000**  
  - *Cause*: Systemd `forgetrace-backend.service` (host uvicorn) already on 127.0.0.1:8000.  
  - *Fix*: `systemctl stop/disable forgetrace-backend.service`, then start Docker container.

- **Nginx 502s**  
  - *Cause*: Backend container down or proxied to wrong port.  
  - *Fix*: Ensure backend running on 8000, upstream updated, Nginx reloaded.

---
## What Worked vs. What Didn’t

**Worked**  
- Rebuilding images without cache after dependency changes.  
- Using async SQLite driver (`sqlite+aiosqlite`) for quick, file‑based storage.  
- `happy-dom` for Vitest on Node 18.  
- Nginx TLS termination + reverse proxy to Dockerized services.  
- Stopping systemd services that conflict with container ports.

**Didn’t Work / Pain Points**  
- Running async engine against sync SQLite driver.  
- `parents[4]` path lookup in a flattened container image.  
- Leaving the host uvicorn service active while trying to bind the same port in Docker.  
- Cached Docker builds masking missing dependencies (httpx, email-validator, aiosqlite) until no‑cache rebuild.

---
## Tooling, Packages, and What They Do (Plain Language)
- **Nginx**: Web server and reverse proxy; terminates HTTPS and forwards traffic to app containers.  
- **Certbot**: Obtains/renews HTTPS certificates from LetsEncrypt and can auto‑configure Nginx.  
- **Docker**: Container runtime to package and run the app in isolated environments.  
- **Vitest**: Test runner for Vue/React/TS; here used with `happy-dom` to simulate the browser.  
- **happy-dom**: Lightweight DOM implementation for tests without a real browser.  
- **SQLAlchemy (async)**: Database toolkit; async engine needs async drivers (e.g., `aiosqlite`, `asyncpg`).  
- **aiosqlite**: Async driver for SQLite; enables async DB calls.  
- **asyncpg**: Async Postgres driver (for production DB if you switch from SQLite).  
- **email-validator**: Validates email fields for Pydantic models.  
- **httpx**: HTTP client library used by backend OAuth/services.  
- **Uvicorn**: ASGI server that runs the FastAPI backend.  
- **FastAPI**: Python web framework powering the backend API.  
- **Pydantic**: Data validation and settings management (v2 in use).  
- **clsx**: Small utility for conditional CSS class names in React components.

---
## Production Nginx Template (current shape)
```
upstream frontend { server 127.0.0.1:3001; keepalive 32; }
upstream backend  { server 127.0.0.1:8000; keepalive 32; }

server {
    listen 80;
    server_name forgetrace.pro www.forgetrace.pro api.forgetrace.pro;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name forgetrace.pro www.forgetrace.pro;
    ssl_certificate /etc/letsencrypt/live/www.forgetrace.pro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.forgetrace.pro/privkey.pem;

    location / { proxy_pass http://frontend; ... }
    location /api/ { proxy_pass http://backend/; ... }
}

server {
    listen 443 ssl http2;
    server_name api.forgetrace.pro;
    ssl_certificate /etc/letsencrypt/live/www.forgetrace.pro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.forgetrace.pro/privkey.pem;

    location / { proxy_pass http://backend/; ... }
}
```

---
## Backend Run Command (async SQLite)
```
docker run -d --name forgetrace-backend \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./forgetrace.db" \
  -e SECRET_KEY="your-secret-key-change-in-production" \
  -e ALLOWED_ORIGINS="https://www.forgetrace.pro,https://api.forgetrace.pro" \
  --restart unless-stopped \
  forgetrace-backend:prod
```

---
## Quick Validation Checklist
- `docker ps` shows frontend on 3001 and backend on 8000 (both Up, not Restarting).  
- `curl http://127.0.0.1:8000/health` returns 200.  
- `curl -I http://127.0.0.1:3001/` returns 200.  
- `curl -I https://api.forgetrace.pro/health` returns 200.  
- `curl -I https://www.forgetrace.pro` returns 200.  
- Nginx `nginx -t` is clean; cert valid per `certbot certificates`.

---
## Lessons Learned
- Always align async DB URLs with async drivers.  
- Avoid deep parent lookups in containers; allow env override and clamp parents to avoid IndexErrors.  
- Rebuild without cache after changing requirements to avoid stale images.  
- Stop conflicting systemd services before binding the same port in Docker.  
- Use lightweight DOM environments for frontend tests on older Node versions (`happy-dom` for Node 18).

---
## Next Steps
- If you move to Postgres in production: set `DATABASE_URL="postgresql+asyncpg://..."`, ensure `asyncpg` is installed, rebuild, and run.  
- Keep certs renewed via certbot timers; monitor expiry.  
- Add runtime checks/health probes to catch backend restarts early.  
- Consider code‑splitting in frontend (Rollup/Vite chunks) to reduce bundle >500 kB warning.

---
## Optional: Switching Backend to Postgres (Async)
- Ensure Postgres is reachable and credentials are known.  
- Set `DATABASE_URL="postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME"` when starting the container.  
- Confirm `asyncpg` is in `requirements.txt` (it already is).  
- Rebuild the backend image (no cache) and restart the container with the Postgres URL.  
- Run Alembic migrations if applicable: inside the container, `alembic upgrade head` (only if your workflow uses Alembic at runtime).

---
## CI/CD Pointers (build & deploy)
- Frontend build: `docker build -t <registry>/forgetrace-frontend:<tag> -f forge_platform/infra/docker/Dockerfile.frontend --build-arg VITE_API_URL=https://api.forgetrace.pro/api/v1 forge_platform/frontend`  
- Backend build: `docker build -t <registry>/forgetrace-backend:<tag> -f forge_platform/infra/docker/Dockerfile.backend forge_platform/backend`  
- Push images: `docker push <registry>/forgetrace-*>:<tag>`  
- Deploy: update tags in your manifests/Helm/compose and apply.  
- Smoke tests: run the curl checks (local and public) and `docker ps` to ensure containers are Up (not Restarting).

### CI example (GitHub Actions) with environment separation
```yaml
name: ci-cd
on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io/your-org
  FRONTEND_IMAGE: ${{ env.REGISTRY }}/forgetrace-frontend
  BACKEND_IMAGE: ${{ env.REGISTRY }}/forgetrace-backend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push frontend (prod API URL)
        run: |
          docker buildx build \
            -t $FRONTEND_IMAGE:${{ github.sha }} \
            -f forge_platform/infra/docker/Dockerfile.frontend \
            --build-arg VITE_API_URL=https://api.forgetrace.pro/api/v1 \
            --push \
            forge_platform/frontend

      - name: Build & push backend
        run: |
          docker buildx build \
            -t $BACKEND_IMAGE:${{ github.sha }} \
            -f forge_platform/infra/docker/Dockerfile.backend \
            --push \
            forge_platform/backend

  deploy-vps:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: SSH deploy to VPS (example)
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            docker pull $FRONTEND_IMAGE:${{ github.sha }}
            docker pull $BACKEND_IMAGE:${{ github.sha }}
            docker rm -f forgetrace-frontend forgetrace-backend || true
            docker run -d --name forgetrace-frontend -p 3001:80 --restart unless-stopped $FRONTEND_IMAGE:${{ github.sha }}
            docker run -d --name forgetrace-backend -p 8000:8000 \
              -e DATABASE_URL="sqlite+aiosqlite:///./forgetrace.db" \
              -e SECRET_KEY="${{ secrets.SECRET_KEY }}" \
              -e ALLOWED_ORIGINS="https://www.forgetrace.pro,https://api.forgetrace.pro" \
              --restart unless-stopped \
              $BACKEND_IMAGE:${{ github.sha }}
            nginx -t && systemctl reload nginx

  deploy-k8s:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: azure/setup-kubectl@v4
        with:
          version: v1.29.0
      - name: Configure kubeconfig
        run: echo "${{ secrets.KUBE_CONFIG }}" > kubeconfig && chmod 600 kubeconfig
      - name: Set images and roll out
        env:
          KUBECONFIG: kubeconfig
        run: |
          kubectl set image deploy/forgetrace-frontend frontend=$FRONTEND_IMAGE:${{ github.sha }} -n production
          kubectl set image deploy/forgetrace-backend backend=$BACKEND_IMAGE:${{ github.sha }} -n production
          kubectl rollout status deploy/forgetrace-frontend -n production
          kubectl rollout status deploy/forgetrace-backend -n production
```

Environment distinctions:
- **Local dev (VS Code shell)**: run `npm test`, `npm run dev`, `uvicorn app.main:app --reload` with local env vars.  
- **VPS**: Docker runtime + Nginx TLS termination; use SSH deploy step above.  
- **Kubernetes**: Use `kubectl set image`/Helm to roll new tags; ensure ingress and cert-manager cover `forgetrace.pro`/`api.forgetrace.pro`.

---
## Cert Renewal & Verification
- Cert status: `certbot certificates | grep forgetrace -A3`  
- Manual renewal (usually automated by timer): `certbot renew`  
- Verify SANs/expiry: `openssl s_client -connect api.forgetrace.pro:443 -servername api.forgetrace.pro </dev/null 2>/dev/null | openssl x509 -noout -dates -ext subjectAltName`

---
## Quick Troubleshooting Cheatsheet
- Port conflicts: `ss -tlnp | grep ':8000'` (or 3001/443/80). Stop services or containers occupying the port.  
- Backend crash logs: `docker logs forgetrace-backend --tail 100`  
- Nginx syntax: `nginx -t && systemctl reload nginx`  
- Container health: `docker ps` (look for Restarting), `curl http://127.0.0.1:8000/health`  
- Frontend static check: `curl -I http://127.0.0.1:3001/`  
- Public check: `curl -I https://api.forgetrace.pro/health`, `curl -I https://www.forgetrace.pro`

---
## Security & Maintenance
- Keep system packages and Docker updated (`apt update && apt upgrade`).  
- Remove or disable any leftover systemd services that conflict with container ports.  
- Rotate `SECRET_KEY` for production; store secrets in a secure vault or env vars, not in code.  
- Restrict SSH access and ensure firewall allows only necessary ports (80/443, 22 as needed).  
- Monitor cert expiry and container health (consider a lightweight uptime probe).
