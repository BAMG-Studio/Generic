# Production Deployment Checklist

## Pre-Deployment

### Infrastructure

- [ ] Kubernetes cluster provisioned (GKE, EKS, or AKS)
- [ ] kubectl configured with cluster access
- [ ] Ingress controller installed (nginx-ingress)
- [ ] Cert-manager installed for Let's Encrypt
- [ ] DNS records configured:
  - [ ] `app.forgetrace.com` → Ingress IP
  - [ ] `api.forgetrace.com` → Ingress IP
  - [ ] `www.forgetrace.pro` → Ingress IP
  - [ ] `api.forgetrace.pro` → Ingress IP
- [ ] PostgreSQL database provisioned
  - [ ] Automated backups enabled
  - [ ] Connection pooling configured
  - [ ] SSL enabled
- [ ] Redis cluster provisioned
  - [ ] Persistence enabled
  - [ ] High availability configured
- [ ] S3 bucket created for artifacts
  - [ ] Versioning enabled
  - [ ] Lifecycle policies configured
  - [ ] IAM role/user with appropriate permissions

### Secrets Management

- [ ] Kubernetes secrets created:
  ```bash
  kubectl create namespace production
  
  kubectl create secret generic forgetrace-secrets -n production \
    --from-literal=database-url='postgresql+asyncpg://...' \
    --from-literal=redis-url='redis://...' \
    --from-literal=secret-key='...' \
    --from-literal=jwt-secret='...'
  
  kubectl create secret generic aws-credentials -n production \
    --from-literal=access-key-id='...' \
    --from-literal=secret-access-key='...'
  
  kubectl create secret generic oauth-credentials -n production \
    --from-literal=github-client-id='...' \
    --from-literal=github-client-secret='...' \
    --from-literal=google-client-id='...' \
    --from-literal=google-client-secret='...'
  ```

### GitHub Configuration

- [ ] GitHub secrets configured:
  - [ ] `KUBE_CONFIG_PRODUCTION`
  - [ ] `REGISTRY_TOKEN` (GHCR access)
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `DATABASE_URL`
  - [ ] `REDIS_URL`
  - [ ] `SECRET_KEY`
  - [ ] `JWT_SECRET`

### Security

- [ ] Security group / firewall rules configured
  - [ ] HTTPS (443) allowed
  - [ ] HTTP (80) allowed (redirects to HTTPS)
  - [ ] All other ports blocked
- [ ] SSL/TLS certificates configured
- [ ] WAF rules configured (if applicable)
- [ ] Rate limiting configured
- [ ] CORS origins whitelisted
- [ ] OAuth applications registered:
  - [ ] GitHub OAuth app
  - [ ] Google OAuth app
  - [ ] Callback URLs updated:
    - [ ] `https://www.forgetrace.pro/api/v1/auth/callback/github`
    - [ ] `https://www.forgetrace.pro/api/v1/auth/callback/google`
    - [ ] Legacy `.com` callbacks still present during transition (if dual-hosting)

## Deployment Steps

### 1. Build and Push Images

```bash
# Set variables
export VERSION=$(git describe --tags --always)
export REGISTRY=ghcr.io/your-org

# Build backend
docker build -t $REGISTRY/forgetrace-backend:$VERSION \
  -f forge_platform/infra/docker/Dockerfile.backend \
  forge_platform/backend

docker push $REGISTRY/forgetrace-backend:$VERSION

# Build frontend
docker build -t $REGISTRY/forgetrace-frontend:$VERSION \
  -f forge_platform/infra/docker/Dockerfile.frontend \
  --build-arg VITE_API_URL=https://api.forgetrace.pro/api/v1 \
  forge_platform/frontend

docker push $REGISTRY/forgetrace-frontend:$VERSION

# Tag as latest
docker tag $REGISTRY/forgetrace-backend:$VERSION $REGISTRY/forgetrace-backend:latest
docker tag $REGISTRY/forgetrace-frontend:$VERSION $REGISTRY/forgetrace-frontend:latest
docker push $REGISTRY/forgetrace-backend:latest
docker push $REGISTRY/forgetrace-frontend:latest
```

- [ ] Backend image built and pushed
- [ ] Frontend image built and pushed
- [ ] Images tagged with version and latest

### 2. Database Migration

```bash
# Run migrations in a job
kubectl run alembic-migration \
  --image=$REGISTRY/forgetrace-backend:$VERSION \
  --restart=Never \
  --namespace=production \
  --env="DATABASE_URL=$(kubectl get secret forgetrace-secrets -n production -o jsonpath='{.data.database-url}' | base64 -d)" \
  -- alembic upgrade head

# Wait for completion
kubectl wait --for=condition=complete --timeout=300s job/alembic-migration -n production

# Check logs
kubectl logs job/alembic-migration -n production
```

- [ ] Migrations executed successfully
- [ ] Database schema verified

### 3. Deploy to Kubernetes

```bash
cd forge_platform/infra/k8s

# Set environment variables
export REGISTRY=ghcr.io/your-org
export VERSION=$(git describe --tags --always)

# Deploy backend
envsubst < backend-deployment.yaml | kubectl apply -f - -n production

# Deploy frontend
envsubst < frontend-deployment.yaml | kubectl apply -f - -n production

# Deploy ingress
kubectl apply -f ingress.yaml -n production

# Deploy HPA
kubectl apply -f hpa.yaml -n production
```

- [ ] Backend deployment successful
- [ ] Frontend deployment successful
- [ ] Ingress configured
- [ ] HPA configured

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n production

# Check deployments
kubectl get deployments -n production

# Check services
kubectl get services -n production

# Check ingress
kubectl get ingress -n production
```

- [ ] All pods running (3 backend, 2 frontend)
- [ ] Services healthy
- [ ] Ingress has external IP
- [ ] DNS resolves to ingress IP

## Post-Deployment

### Smoke Tests

- [ ] Frontend loads: <https://app.forgetrace.com>
- [ ] API health check: <https://api.forgetrace.pro/health>
- [ ] API docs accessible: <https://api.forgetrace.pro/docs>
- [ ] User signup works
- [ ] User login works
- [ ] Repository connection works
- [ ] Scan execution works
- [ ] Results display correctly

### Performance Tests

```bash
# Test API response time
curl -w "@curl-format.txt" -o /dev/null -s https://api.forgetrace.pro/health

# Load test (use k6 or similar)
k6 run load-test.js
```

- [ ] API response time < 200ms
- [ ] Frontend load time < 2s
- [ ] Load test passes (1000 RPS)

### Security Verification

- [ ] HTTPS redirect working
- [ ] SSL certificate valid
- [ ] Security headers present:
  - [ ] `Strict-Transport-Security`
  - [ ] `X-Content-Type-Options`
  - [ ] `X-Frame-Options`
  - [ ] `X-XSS-Protection`
- [ ] CORS configured correctly
- [ ] Rate limiting active

### Monitoring Setup

- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards configured
- [ ] Alerts configured:
  - [ ] High error rate
  - [ ] High response time
  - [ ] Pod crash loop
  - [ ] Database connection issues
- [ ] Log aggregation working (e.g., ELK, Loki)
- [ ] Uptime monitoring configured (e.g., UptimeRobot)

### Backup Verification

- [ ] Database backups running
- [ ] Backup restoration tested
- [ ] S3 versioning working
- [ ] Disaster recovery plan documented

## Rollback Plan

If issues occur:

```bash
# Rollback to previous version
kubectl rollout undo deployment/forgetrace-backend -n production
kubectl rollout undo deployment/forgetrace-frontend -n production

# Or rollback to specific revision
kubectl rollout history deployment/forgetrace-backend -n production
kubectl rollout undo deployment/forgetrace-backend --to-revision=X -n production
```

- [ ] Rollback procedure tested
- [ ] Previous versions available
- [ ] Database rollback procedure documented

## Go-Live Checklist

- [ ] All pre-deployment items complete
- [ ] All deployment steps executed
- [ ] All smoke tests passing
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Monitoring active
- [ ] Team notified
- [ ] Documentation updated
- [ ] Support team briefed
- [ ] Incident response plan ready

## Post-Go-Live

- [ ] Monitor for 24 hours
- [ ] Review metrics and logs
- [ ] Address any issues
- [ ] Update status page
- [ ] Announce launch
- [ ] Gather user feedback

---

## Notes

**Date Deployed:** _______________  
**Version:** _______________  
**Deployed By:** _______________  
**Issues Encountered:** _______________  
**Resolution:** _______________
