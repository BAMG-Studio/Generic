# Security Policy

## Reporting Security Vulnerabilities

**DO NOT** open public GitHub issues for security vulnerabilities.

Instead, report security issues privately to:
- **Email**: peter@beaconagile.net
- **Subject**: [SECURITY] ForgeTrace Vulnerability Report

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

We aim to respond within 48 hours and provide a fix within 7 days for critical vulnerabilities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |
| < 1.0   | :x:                |

## Secret Rotation Schedule

Regular rotation of credentials minimizes the impact of potential compromises.

| Secret | Rotation Frequency | Owner | Last Rotated |
|--------|-------------------|-------|--------------|
| AWS Access Keys | Every 90 days | DevOps Lead | 2025-11-16 |
| GitHub Token | Every 90 days | DevOps Lead | 2025-11-16 |
| MLflow Password | Every 180 days | ML Lead | 2025-11-16 |
| Database Passwords | Every 90 days | DevOps Lead | 2025-11-16 |

### Rotation Process

1. **Generate New Credentials**
   - AWS: IAM Console → Users → Security Credentials → Create Access Key
   - GitHub: Settings → Developer Settings → Personal Access Tokens → Generate New Token
   - MLflow: Update `.htpasswd` file and restart nginx container

2. **Test in Staging**
   ```bash
   # Test AWS
   AWS_ACCESS_KEY_ID=<new_key> aws s3 ls s3://<bucket>/
   
   # Test GitHub
   curl -H "Authorization: token <new_token>" https://api.github.com/user
   
   # Test MLflow
   curl -u mlflow_admin:<new_password> http://<mlflow_uri>/health
   ```

3. **Update GitHub Secrets**
   - Repository → Settings → Secrets and Variables → Actions
   - Update each secret individually
   - Document update date in this file

4. **Verify CI/CD**
   - Actions → Test Secrets workflow → Run workflow
   - Verify all checks pass
   - Monitor next scheduled pipeline run

5. **Deactivate Old Credentials**
   - Wait 7 days grace period
   - Delete old AWS access keys from IAM
   - Revoke old GitHub tokens
   - Remove old passwords from configuration

6. **Update Documentation**
   - Update "Last Rotated" column in table above
   - Commit changes to this file
   - Tag commit: `git tag security-rotation-YYYY-MM-DD`

### Emergency Rotation (Suspected Compromise)

If secrets are suspected to be compromised:

1. **Immediate Actions** (within 1 hour)
   - Revoke compromised credentials immediately
   - Generate new credentials
   - Update GitHub Secrets
   - Restart affected services

2. **Investigation** (within 24 hours)
   - Check AWS CloudTrail for unauthorized API calls
   - Review GitHub audit log for suspicious commits
   - Examine MLflow access logs
   - Identify scope of compromise

3. **Remediation** (within 48 hours)
   - Rotate all related secrets (not just compromised ones)
   - Review and tighten IAM policies
   - Enable additional security controls (MFA, IP restrictions)
   - Update incident log (see below)

4. **Post-Incident** (within 1 week)
   - Document lessons learned
   - Update security procedures
   - Conduct team security training
   - Implement preventive measures

## Incident Log

| Date | Incident | Severity | Actions Taken | Status |
|------|----------|----------|---------------|--------|
| 2025-11-16 | Initial security policy created | N/A | Documented procedures | Complete |
<!-- Add new incidents above this line -->

## Access Control

### GitHub Repository Access Levels

- **Admin**: @papaert-cloud
- **Write**: (Team members with commit access)
- **Read**: (External collaborators, auditors)

### AWS IAM Policies

ForgeTrace CI/CD user has access to:
- S3: Full access to `forgetrace-models-*` buckets
- CloudWatch Logs: Write access for monitoring

**Least Privilege Principle**: Never grant more permissions than necessary.

### MLflow Access

- **Admin**: Full access to experiments, models, artifacts
- **Viewer**: Read-only access to experiments and metrics

## Security Best Practices

### For Developers

1. **Never commit secrets**
   - Use `.env` files (added to `.gitignore`)
   - Use GitHub Secrets for CI/CD
   - Use environment variables for local development

2. **Dependency management**
   - Run `pip-audit` before merging PRs
   - Review Dependabot alerts weekly
   - Pin versions in `requirements.txt`

3. **Code scanning**
   - Enable GitHub Secret Scanning
   - Enable GitHub Dependabot
   - Review Bandit reports in CI/CD

4. **Git hygiene**
   - Sign commits with GPG (optional but recommended)
   - Use branch protection rules
   - Require PR reviews before merging

### For Operations

1. **Infrastructure as Code**
   - Store all configuration in version control
   - Use Docker Compose for reproducible deployments
   - Document manual steps in deployment guides

2. **Monitoring**
   - Enable AWS CloudTrail for API audit logs
   - Set up alerts for suspicious activity
   - Review logs monthly

3. **Backups**
   - MLflow database: Daily backups to S3
   - Training data: Versioned with DVC
   - Configuration: Stored in Git

4. **Disaster recovery**
   - Document recovery procedures
   - Test recovery process quarterly
   - Maintain offline backup of critical secrets

## Compliance

### Data Classification

ForgeTrace handles the following data types:

| Data Type | Classification | Retention | Encryption |
|-----------|---------------|-----------|------------|
| Source Code (client repos) | Confidential | Per engagement | At rest (S3) |
| Training Datasets | Internal | 2 years | At rest (S3) |
| ML Models | Internal | Indefinite | At rest (S3) |
| Audit Reports | Confidential | 7 years | At rest (S3) |
| Logs | Internal | 90 days | At rest (CloudWatch) |
| Credentials | Secret | N/A | GitHub Secrets |

### Regulatory Considerations

- **GDPR**: If processing EU customer code, ensure data processing agreements
- **SOC 2**: Implement access controls and audit logging
- **ISO 27001**: Follow security policies and regular reviews

## Security Tools in Use

| Tool | Purpose | Status |
|------|---------|--------|
| GitHub Secret Scanning | Detect leaked secrets | ✅ Enabled |
| GitHub Dependabot | Vulnerability alerts | ✅ Enabled |
| pip-audit | PyPI vulnerability scanning | ✅ CI/CD |
| Bandit | Python security linting | ✅ CI/CD |
| Safety | Dependency security checks | ✅ CI/CD |
| AWS CloudTrail | API audit logging | ⚠️ To configure |
| MLflow Authentication | Access control | ⚠️ Optional |

## Contact

For security-related questions:
- **Primary**: Peter Kolawole (peter@beaconagile.net)
- **Organization**: BAMG Studio LLC

---

**Last Updated**: 2025-11-16  
**Next Review**: 2026-02-16 (quarterly review)
