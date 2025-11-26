#!/bin/bash
# Production health verification script

set -e

echo "🏥 ForgeTrace Platform - Production Health Check"
echo "================================================"
echo ""

# Configuration
API_URL="${1:-https://api.forgetrace.pro}"
APP_URL="${2:-https://www.forgetrace.pro}"
NAMESPACE="${3:-production}"

FAILED=0
PASSED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test API health endpoint
test_api_health() {
    echo "Testing API health endpoint..."
    if curl -sf "${API_URL}/health" > /dev/null; then
        pass "API health endpoint responding"
    else
        fail "API health endpoint not responding"
    fi
}

# Test API docs
test_api_docs() {
    echo "Testing API documentation..."
    if curl -sf "${API_URL}/docs" > /dev/null; then
        pass "API docs accessible"
    else
        fail "API docs not accessible"
    fi
}

# Test frontend
test_frontend() {
    echo "Testing frontend..."
    if curl -sf "${APP_URL}" > /dev/null; then
        pass "Frontend accessible"
    else
        fail "Frontend not accessible"
    fi
}

# Test HTTPS redirect
test_https_redirect() {
    echo "Testing HTTPS redirect..."
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://${APP_URL#https://}")
    if [ "$RESPONSE" = "301" ] || [ "$RESPONSE" = "302" ] || [ "$RESPONSE" = "308" ]; then
        pass "HTTP redirects to HTTPS"
    else
        warn "HTTP not redirecting to HTTPS (got $RESPONSE)"
    fi
}

# Test SSL certificate
test_ssl_cert() {
    echo "Testing SSL certificate..."
    if echo | openssl s_client -connect "${API_URL#https://}:443" -servername "${API_URL#https://}" 2>/dev/null | openssl x509 -noout -checkend 86400 > /dev/null; then
        pass "SSL certificate valid and not expiring soon"
    else
        fail "SSL certificate invalid or expiring soon"
    fi
}

# Test Kubernetes pods
test_k8s_pods() {
    if command -v kubectl &> /dev/null; then
        echo "Testing Kubernetes pods..."
        
        BACKEND_PODS=$(kubectl get pods -n $NAMESPACE -l app=forgetrace-backend --field-selector=status.phase=Running 2>/dev/null | grep -c Running || echo 0)
        if [ "$BACKEND_PODS" -ge 1 ]; then
            pass "Backend pods running ($BACKEND_PODS)"
        else
            fail "No backend pods running"
        fi
        
        FRONTEND_PODS=$(kubectl get pods -n $NAMESPACE -l app=forgetrace-frontend --field-selector=status.phase=Running 2>/dev/null | grep -c Running || echo 0)
        if [ "$FRONTEND_PODS" -ge 1 ]; then
            pass "Frontend pods running ($FRONTEND_PODS)"
        else
            fail "No frontend pods running"
        fi
    else
        warn "kubectl not found, skipping Kubernetes checks"
    fi
}

# Test database connectivity
test_database() {
    if command -v kubectl &> /dev/null; then
        echo "Testing database connectivity..."
        
        # Try to exec into a backend pod and check database
        BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=forgetrace-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
        
        if [ -n "$BACKEND_POD" ]; then
            if kubectl exec -n $NAMESPACE "$BACKEND_POD" -- python -c "from app.db.session import SessionLocal; SessionLocal().execute('SELECT 1')" 2>/dev/null; then
                pass "Database connectivity verified"
            else
                fail "Database connectivity failed"
            fi
        else
            warn "No backend pod found to test database"
        fi
    fi
}

# Test Redis connectivity
test_redis() {
    if command -v kubectl &> /dev/null; then
        echo "Testing Redis connectivity..."
        
        BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=forgetrace-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
        
        if [ -n "$BACKEND_POD" ]; then
            if kubectl exec -n $NAMESPACE "$BACKEND_POD" -- python -c "import redis; r = redis.from_url('redis://redis:6379/0'); r.ping()" 2>/dev/null; then
                pass "Redis connectivity verified"
            else
                warn "Redis connectivity failed (optional)"
            fi
        fi
    fi
}

# Test API response time
test_response_time() {
    echo "Testing API response time..."
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' "${API_URL}/health")
    RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc)
    
    if (( $(echo "$RESPONSE_TIME < 0.5" | bc -l) )); then
        pass "API response time: ${RESPONSE_MS}ms (< 500ms)"
    elif (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
        warn "API response time: ${RESPONSE_MS}ms (acceptable but slow)"
    else
        fail "API response time: ${RESPONSE_MS}ms (> 1000ms)"
    fi
}

# Test security headers
test_security_headers() {
    echo "Testing security headers..."
    
    HEADERS=$(curl -sI "${API_URL}/health")
    
    if echo "$HEADERS" | grep -qi "strict-transport-security"; then
        pass "HSTS header present"
    else
        warn "HSTS header missing"
    fi
    
    if echo "$HEADERS" | grep -qi "x-content-type-options"; then
        pass "X-Content-Type-Options header present"
    else
        warn "X-Content-Type-Options header missing"
    fi
}

# Run all tests
echo "Running health checks..."
echo ""

test_api_health
test_api_docs
test_frontend
test_https_redirect
test_ssl_cert
test_response_time
test_security_headers
test_k8s_pods
test_database
test_redis

echo ""
echo "================================================"
echo "Health Check Summary"
echo "================================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please investigate.${NC}"
    exit 1
fi
