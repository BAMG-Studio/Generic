# ForgeTrace Control Center - Deployment Checklist

## ✅ Pre-Deployment Checklist

### Local Testing
- [ ] Run `./deploy.sh development`
- [ ] Backend starts successfully
- [ ] Frontend loads at http://localhost:5173
- [ ] Can login with admin@forgetrace.pro / admin123
- [ ] Can create new user via API
- [ ] Can create API token
- [ ] Token authentication works
- [ ] OAuth buttons appear (even if not working locally)

### Configuration Files
- [ ] `backend/.env.production` exists
- [ ] `backend/.env.production` has strong SECRET_KEY
- [ ] `backend/.env.production` has strong JWT_SECRET
- [ ] `backend/.env.production` has correct OAuth credentials
- [ ] `frontend/.env.production` exists
- [ ] `frontend/.env.production` has correct API_URL

### OAuth Apps
- [ ] GitHub OAuth app created
- [ ] GitHub callback URL updated for production
- [ ] Google OAuth app created
- [ ] Google callback URL updated for production
- [ ] OAuth credentials in backend/.env.production

### AWS/Cloud
- [ ] AWS account ready
- [ ] AWS credentials added to .env
- [ ] S3 buckets created (optional for MVP)
- [ ] SES configured (optional for MVP)

### Stripe
- [ ] Stripe account: acct_1SZ4Mh2Qubn5pZwk
- [ ] Stripe API keys added to .env (optional for MVP)

## 🚀 Production Deployment Checklist

### Server Setup
- [ ] Server provisioned (AWS EC2, VPS, etc.)
- [ ] SSH access configured
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Nginx installed
- [ ] Certbot installed

### DNS Configuration (Hostinger)
- [ ] A record: @ → server IP
- [ ] A record: www → server IP
- [ ] A record: app → server IP
- [ ] A record: api → server IP
- [ ] DNS propagation verified (dig commands)

### SSL Certificates
- [ ] Certificates obtained for all domains
- [ ] Certificates in /etc/letsencrypt/live/forgetrace.pro/
- [ ] Auto-renewal configured
- [ ] Nginx configured with SSL

### Application Deployment
- [ ] Repository cloned to server
- [ ] Environment files configured
- [ ] `./deploy.sh production` executed successfully
- [ ] All containers running (docker-compose ps)
- [ ] Database migrations completed
- [ ] Super admin user created

### Nginx Configuration
- [ ] Nginx config created
- [ ] Config enabled in sites-enabled
- [ ] Nginx test passed (nginx -t)
- [ ] Nginx restarted
- [ ] HTTP redirects to HTTPS

### Verification
- [ ] https://api.forgetrace.pro/health returns healthy
- [ ] https://app.forgetrace.pro loads
- [ ] https://www.forgetrace.pro loads (or redirects)
- [ ] Can login with email/password
- [ ] GitHub OAuth works
- [ ] Google OAuth works
- [ ] Can create API token
- [ ] Token authentication works

### Security
- [ ] Firewall configured (ufw)
- [ ] Only ports 22, 80, 443 open
- [ ] Strong passwords used
- [ ] Secrets not committed to git
- [ ] .gitignore configured

### Monitoring & Backups
- [ ] Monitoring script created
- [ ] Monitoring cron job added
- [ ] Backup script created
- [ ] Backup cron job added (daily at 2 AM)
- [ ] Test backup/restore process

### Documentation
- [ ] Production URLs documented
- [ ] Admin credentials stored securely
- [ ] OAuth app URLs documented
- [ ] Deployment process documented

## 📋 Post-Deployment Checklist

### Day 1
- [ ] Monitor logs for errors
- [ ] Test all authentication methods
- [ ] Create test users
- [ ] Create test API tokens
- [ ] Verify email notifications (if configured)

### Week 1
- [ ] Monitor performance
- [ ] Check backup success
- [ ] Review error logs
- [ ] Test disaster recovery
- [ ] Gather user feedback

### Month 1
- [ ] Review usage metrics
- [ ] Optimize performance
- [ ] Update documentation
- [ ] Plan feature roadmap

## 🔧 Rollback Plan

If deployment fails:

```bash
# Stop services
docker-compose down

# Restore from backup
docker-compose exec postgres psql -U forgetrace forgetrace_platform < backup.sql

# Restart services
docker-compose up -d
```

## 📞 Emergency Contacts

- **Technical**: hello@bamgstudio.com
- **Server Provider**: [Your hosting provider]
- **DNS Provider**: Hostinger support

## 🎯 Success Criteria

Deployment is successful when:

1. ✅ All domains resolve correctly
2. ✅ SSL certificates valid
3. ✅ Backend API responding
4. ✅ Frontend loading
5. ✅ All authentication methods work
6. ✅ No errors in logs
7. ✅ Backups running
8. ✅ Monitoring active

## 📝 Notes

**Deployment Date**: _______________

**Deployed By**: _______________

**Server IP**: _______________

**Issues Encountered**:
_______________________________________
_______________________________________
_______________________________________

**Resolution**:
_______________________________________
_______________________________________
_______________________________________

---

**ForgeTrace Control Center v1.0.0**

Built by Peter Kolawole, BAMG Studio LLC
