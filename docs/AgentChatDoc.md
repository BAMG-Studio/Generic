# ForgeTrace Production Deployment — Agent Chat Documentation

This document captures the end-to-end journey of building, deploying, and stabilizing the ForgeTrace platform (frontend + backend) to production, including decisions, errors encountered, fixes applied, tools used, and operational lessons. Emphasis is on the production phase and practical control of `www.forgetrace.pro`.

## Timeline & Milestones

- Frontend implementation (React + Vite + Tailwind, dark theme, enterprise UI)
- Local build and validation (vite build, unit test scaffolding via Vitest)
- VPS provisioning and sync (`/opt/forgetrace`)
- Backend service via systemd + Uvicorn, Nginx reverse proxy
- TLS enablement with Let’s Encrypt (Certbot)
- Production fixes: Python versioning, missing dependencies, service path, workers, Nginx rules, caching
- Route base alignment to `/app` for SPA

## Architecture Overview

- Frontend: React 18, TypeScript, Vite, Tailwind CSS, React Router v6, Zustand, React Query, Lucide icons, Recharts
- Backend: FastAPI (ASGI), Uvicorn, SQLAlchemy/Alembic, Redis (planned), OAuth (GitHub/Google), MLflow integration
- Infra: Ubuntu 24.04, systemd for backend, Nginx for TLS + reverse proxy, Certbot for certificates, rsync for deploys

## Frontend — What We Built

- Shell and navigation: `AppLayout` with sidebar and topbar
- Pages: Dashboard, Explorer (FileTree + CodeViewer), Review (human-in-loop), Settings
- State & data: `useAuditStore` (Zustand), mock data, React Query ready
- Tailwind theme: Dark “Cyber-Physical” palette with brand/IP risk colors
- Router: React Router v6
- Build: Vite production build (`dist/`)

### Key Files (Frontend)

- `forge_platform/frontend/src/components/layout/AppLayout.tsx`
- `forge_platform/frontend/src/pages/{Dashboard,Explorer,Review,Settings}.tsx`
- `forge_platform/frontend/tailwind.config.js`
- `forge_platform/frontend/vite.config.ts`
- `forge_platform/frontend/src/main.tsx`

## Backend — What We Deployed

- FastAPI app entry: `forge_platform/backend/app/main.py` (routers include auth, scans, repositories, consent, oauth)
- Config: `forge_platform/backend/app/core/config.py` (ENV, API_PREFIX `/api/v1`, CORS, OAuth, AWS/S3, etc.)
- System service: `forgetrace-backend.service` (Uvicorn binding to 127.0.0.1:8000)
- Nginx: Frontend SPA + `/api/` proxy to backend upstream

### Key Files (Backend)

- `forge_platform/backend/app/main.py`
- `forge_platform/backend/app/core/config.py`
- `forge_platform/backend/requirements.txt`
- Systemd unit: `/etc/systemd/system/forgetrace-backend.service`
- Nginx site: `/etc/nginx/sites-available/forgetrace` (enabled via symlink)

## Production Issues & Fixes

### 1) Python 3.11 not found on Ubuntu 24.04

- Symptom: `apt install python3.11` failed
- Root cause: Ubuntu 24.04 ships Python 3.12 by default
- Fix: Generalize scripts to `python3` + `python3-venv`

### 2) Backend service failed to start (203/EXEC)

- Symptom: systemd service exited with `203/EXEC`
- Root causes:
  - Wrong app module path (`api.main:app` vs `app.main:app`)
  - `uvicorn` not installed from root `requirements.txt`
- Fixes:
  - Install `forge_platform/backend/requirements.txt` in venv (includes `uvicorn[standard]`, `fastapi`)
  - Correct ExecStart to `uvicorn app.main:app`
  - Expand `PYTHONPATH` to include project and backend paths

### 3) ImportError: email-validator

- Symptom: Pydantic EmailStr required `email-validator`
- Fix: Added `email-validator>=2.0.0` to backend requirements and installed

### 4) ImportError: httpx

- Symptom: OAuth service uses `httpx` for async HTTP
- Fix: Added `httpx>=0.27.0` to backend requirements and installed

### 5) OOM / too many workers

- Symptom: Service spawned 4 workers, high memory, shutdown loop
- Fix: Reduce to `--workers 1` in systemd ExecStart for stability on small VPS

### 6) TLS challenge failures (ACME HTTP-01)

- Symptom: 404 for `/.well-known/acme-challenge/*`
- Causes: SPA routing and caching interfered with ACME path; webroot mapping mismatch
- Fixes:
  - Create `/var/www/letsencrypt` webroot and Nginx location for challenges
  - Alternatively, used `certbot --standalone` after stopping Nginx
  - Installed cert for `www.forgetrace.pro` (apex can be added via `--expand`)

### 7) Frontend route base mismatch (`/app` vs `/`)

- Symptom: UI not matching latest build at `/app/dashboard`
- Root cause: SPA was built for `/`, but deployed under `/app`
- Fixes:
  - Vite `base: '/app/'`
  - React Router `<BrowserRouter basename="/app">`
  - Nginx `/app/` alias mapping and `/` → `/app/` redirect
  - `index.html` `Cache-Control: no-cache` to avoid stale entry

## Deploy & Operations

### One-time VPS Setup

- Create venv: `python3 -m venv .venv && source .venv/bin/activate`
- Install packages: `pip install -r requirements.txt && pip install -r forge_platform/backend/requirements.txt && pip install -e .`
- Systemd service (run with 1 worker):
  - Exec: `/opt/forgetrace/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1`
- Nginx reverse proxy + SPA serving
- Certbot for TLS certificates (webroot or standalone)

### Deploy Frontend

- Build: `cd forge_platform/frontend && npm install && npm run build`
- Rsync to VPS: `rsync -avz --delete forge_platform/frontend/dist/ root@<IP>:/opt/forgetrace/forge_platform/frontend/dist/`
- Reload Nginx: `nginx -t && systemctl reload nginx`

### Useful Commands

- Backend logs: `journalctl -u forgetrace-backend -f`
- Service status: `systemctl status forgetrace-backend`
- Test API: `curl http://127.0.0.1:8000/health`
- Test via Nginx: `curl https://www.forgetrace.pro/api/v1/health`
- Check ports: `ss -ltnp | grep 8000`

## Tools, Packages & Concepts (Plain-English)

- React: UI library for building components
- Vite: Fast dev server and production bundler
- Tailwind CSS: Utility-first styling
- React Router: Client-side routing (URLs → pages)
- Zustand: Lightweight global state store
- React Query: Data fetching/caching
- Recharts: Charting library for dashboards
- Lucide: Icon set for modern UIs
- FastAPI: Python web framework for APIs, fast + typed
- Uvicorn: ASGI server that runs FastAPI
- Systemd: Linux service manager to keep backend running
- Nginx: Web server and reverse proxy (TLS, routing)
- Certbot/Let’s Encrypt: Free TLS certificates and auto-renewal
- rsync: Efficient file copy for deployments
- Pydantic: Data validation (EmailStr requires email-validator)
- httpx: HTTP client used in OAuth flows
- MLflow: Experiment tracking/integration (configured later)

## Why Issues Happened (And How We Fixed Them)

- Version drift: OS Python version mismatch → generalized to `python3`
- Missing deps: Fast iteration missed runtime-only packages → added to backend requirements
- Memory constraints: Too many workers for VPS → `--workers 1`
- SPA routing: Deployed under `/app` without adjusting build/router → set Vite base + router basename, fixed Nginx alias
- TLS challenges: SPA & caching interfered → used dedicated ACME location or standalone mode

## Repeatable Production Steps

1. Build frontend (with Vite `base: '/app/'`)
2. Rsync `dist/` to `/opt/forgetrace/forge_platform/frontend/dist/`
3. Validate and reload Nginx
4. Ensure backend service is active (1 worker)
5. Certbot renew timer active (`systemctl status certbot.timer`)

## Switching Route Base Later (Control Strategy)

- To move app to `/` instead of `/app/`:
  - Vite `base: '/'`, React Router remove `basename`
  - Nginx: serve `location /` instead of `/app/`, remove redirect
  - Deploy and reload
- To preserve old links, keep a temporary redirect from `/app/*` → `/*`

## Checklists

### Production Readiness

- [x] Backend healthy at 127.0.0.1:8000
- [x] Frontend served via Nginx at `/app/`
- [x] HTTPS enabled on `www.forgetrace.pro`
- [x] Cert renewal timer active
- [x] Index no-cache set to avoid stale UI
- [x] Logs verifiable; service restart resilient

### Troubleshooting Quickies

- If service fails: `journalctl -u forgetrace-backend -n 100`
- If port busy: ensure only one Uvicorn instance runs
- If TLS fails: check ACME location or run standalone certbot
- If UI stale: hard refresh, verify `index.html` no-cache, redeploy

---

Prepared by Agent (GitHub Copilot) — updated automatically during the production deployment session.
