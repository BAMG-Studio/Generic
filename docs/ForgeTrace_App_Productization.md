# ForgeTrace App: UI Polish and Tokenized API Consumption

This document proposes a detailed, phased approach to elevate the ForgeTrace UI/UX and productize the platform as a scalable app with token-based API access. It includes visual/interaction refinements, information architecture, accessibility, and a full API token and usage metering design suitable for phased rollout.

## Product Vision
- Deliver a credible, enterprise-grade interface for IP provenance and policy enforcement.
- Support multiple consumption modes: in-browser SPA, programmatic API, and automation via CI/CD.
- Token-based access with quotas, metering, and billing for sustainable growth.

## UX/UI Polish Plan
- Typography & spacing: tighten hierarchy (H1–H4 consistent scale), increase line-height and section spacing, standardize 8px spacing grid.
- Layout: responsive two-column templates for settings and review; preserve scanning order; add sticky subnav for long forms.
- Components: consistent section headers, description text, help tooltips, inline validation, accessible toggles/sliders.
- Microinteractions: hover/focus states, optimistic actions with toasts, skeleton loaders for heavy lists.
- Empty states: friendly guidance with primary action; sample data on first-run.
- Accessibility: color-contrast AA+, keyboard traps eliminated, skip-to-content, ARIA labels and landmarks.
- Performance: code-split routes, lazy charts, memoized lists, virtualize long tables.
- Internationalization-ready: copy centralization and message IDs (phase 3).

### Settings Page Rework (screenshot context)
- Break into logical cards: Analysis Thresholds, Policy Enforcement, Integrations, Data Retention.
- Add helper copy under labels; show current value inline (e.g., “70%”).
- Make slider keyboard-accessible and numeric-editable; provide reset-to-default.
- Group integrations with clear status badges and CTA buttons (Configure/Manage/Test).

### Navigation & IA
- Primary: Dashboard, Explorer, Review, Settings, Admin (org-level), Developer (API & tokens).
- Secondary within Settings: General, Policies, Integrations, Security, Data.

## Visual System
- Tokens: `--fg-primary`, `--fg-muted`, `--bg-surface`, `--border-subtle`; dark-first with accessible contrasts.
- Brand mapping: Purple as accent for ForgeTrace states (info) with red/orange/yellow for risk levels.
- Motion: subtle 150–200ms transitions; prefers-reduced-motion respected.

## Token/API Consumption Design

### Token Types & Scopes
- Personal Access Tokens (PAT): user-scoped; rotate/revoke; limited scopes (read:reports, write:audits, admin:tokens).
- Organization Tokens: service-account style for CI/CD; bound to org and environment (dev/stage/prod).
- Ephemeral Tokens: short-lived, mint via OAuth for delegated flows.

### Authentication
- HTTP header: `Authorization: Bearer <token>`.
- Token format: opaque ID mapped to hashed secret in DB; optional JWT for org-scoped service tokens.
- Rotation: dual-token strategy with overlapping validity; audit log on create/rotate/revoke.

### Rate Limiting & Quotas
- Per-token and per-org policies: sliding window (e.g., 1 min), burst bucket.
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- 429 responses with retry hints; structured error body.

### Usage Metering
- Billable units: audit submissions, files scanned, tokens generated, storage GB-hours.
- Event table (append-only) + daily aggregates per token/org; idempotency keys to dedupe.
- Export to billing provider (Stripe) or internal invoicing; webhook for overage alerts.

### Plans & Pricing (example)
- Free: 1,000 files/month, low priority, community support.
- Pro: 50,000 files/month, priority queue, email support.
- Team: pooled quota, SSO, audit logs, webhook events.
- Enterprise: SLA, private tenancy options, custom DLP/policies, onboarding support.

### Developer Portal (App → Developer)
- List tokens with last used, scopes, created by; create/rotate/revoke.
- Usage graphs (daily/weekly); CSV export; webhooks with HMAC signing.
- API docs: OpenAPI, Postman collection, SDKs (Python/JS), example CI snippets.

### API Surface (v1)
- `POST /api/v1/audits` submit audit (repo URL, SBOM, or tarball; idempotency-key).
- `GET /api/v1/audits/{id}` status + summary; links to reports.
- `GET /api/v1/reports/{id}` fetch HTML/JSON summaries.
- `GET /api/v1/tokens` list; `POST /api/v1/tokens` create; `DELETE /api/v1/tokens/{id}` revoke (scoped).
- Pagination via `page`, `limit`, `next_token`.
- Errors: machine-readable codes, correlation IDs.

### Security & Compliance
- PII-avoidant by design; optional redaction for code metadata.
- Encrypt secrets at rest; rotate KMS keys; hash token secrets (argon2/bcrypt + pepper).
- Audit logs for all token operations; signed webhook payloads; TLS everywhere.

### Multi-Tenancy
- `org_id` on all records; policies enforced at org boundary; SSO (SAML/OIDC) for enterprise.

## Phased Rollout
- Phase 1 (Foundations): UI polish, Developer section stub, PAT generation, basic rate limit, usage counters.
- Phase 2 (Growth): Org tokens, pooled quotas, usage graphs, webhook events, SDKs.
- Phase 3 (Scale): Billing integration, enterprise features (SSO, audit logs export), regional data controls.

## Implementation Plan (High-Level)
- Backend: models (Token, TokenEvent, UsageAggregate), CRUD endpoints, middlewares for auth + rate limit, idempotency.
- Frontend: Developer screens (tokens list/create/revoke, usage graphs), Settings polish refactor, shared UI tokens.
- Infra: Redis for rate limiting counters, Postgres views for aggregates, scheduled jobs; Nginx headers for rate limit.
- Docs: README/USAGE updates, API reference, quickstart examples; changelog entries.

## Documentation Updates Required
- Replace “AI” references with “ForgeTrace” across UI and docs.
- README: Add “ForgeTrace App” overview and “Developer (Tokens)” section.
- USAGE: Add API token quickstart with curl and SDKs.
- Docs: Add “API & Tokens” guide with scopes, rate limits, and examples.

---
Prepared by GitHub Copilot — initial productization blueprint for review.

