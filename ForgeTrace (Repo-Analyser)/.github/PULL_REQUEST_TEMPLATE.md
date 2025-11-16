## Description
<!-- Briefly describe what this PR accomplishes -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Model update (ML model retraining or architecture change)
- [ ] Infrastructure change (CI/CD, deployment, configuration)
- [ ] Documentation update

## Related Issues
<!-- Link related issues: Fixes #123, Relates to #456 -->

## Testing
<!-- Describe the tests you ran to verify your changes -->
- [ ] Unit tests pass locally (`pytest tests/`)
- [ ] Integration tests pass
- [ ] Manual testing performed
- [ ] Benchmarks show no significant degradation

## ML Model Changes (if applicable)
If this PR includes model changes, please provide metrics:

- [ ] Training accuracy: ___% (baseline: 99.9%)
- [ ] Testing accuracy: ___%
- [ ] Inference latency: ___ms (baseline: 2ms)
- [ ] Model size: ___MB (baseline: 2.9MB)
- [ ] Feature importance analysis completed
- [ ] Cross-validation performed (k=___)
- [ ] Model card updated (`docs/MODEL_CARD.md`)

**Feature Changes:**
<!-- List any new features or removed features -->

**Performance Impact:**
<!-- Describe any performance improvements or regressions -->

## Vulnerability Scanner Changes (if applicable)
If this PR affects vulnerability scanning:

- [ ] Tested against known vulnerable packages
- [ ] Cache invalidation logic verified
- [ ] Risk heuristics validated
- [ ] GitHub Advisory API tested with token
- [ ] OSV API rate limiting tested

## Security Checklist
- [ ] No sensitive data (API keys, passwords) in code
- [ ] Secrets properly managed via environment variables
- [ ] Input validation added for user-facing endpoints
- [ ] Dependencies scanned for vulnerabilities (`pip-audit`)
- [ ] No new hardcoded credentials introduced
- [ ] Security scanning passes (Bandit, Safety)

## Documentation
- [ ] Code comments added/updated
- [ ] README.md updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] CHANGELOG.md updated
- [ ] Configuration examples updated (if config changes)

## Breaking Changes
<!-- List any breaking changes and migration steps -->
- [ ] No breaking changes
- [ ] Breaking changes documented below:

<!-- Describe breaking changes and migration path -->

## Performance Considerations
- [ ] No significant performance impact
- [ ] Performance impact documented below:

<!-- Describe performance changes -->

## Deployment Notes
<!-- Any special deployment considerations? -->
- [ ] Requires environment variable changes (list in PR description)
- [ ] Requires infrastructure updates (AWS, MLflow, etc.)
- [ ] Requires data migration
- [ ] Safe to deploy without downtime

## Screenshots/Logs
<!-- Add any relevant screenshots or log outputs -->

## Reviewers
<!-- Tag specific reviewers based on change type -->
/cc @papaert-cloud

<!-- Uncomment as needed:
For ML changes: /cc @ml_expert
For infra changes: /cc @devops_lead
For security changes: /cc @security_expert
-->

## Additional Notes
<!-- Any additional context, design decisions, or considerations -->

---

**Checklist before requesting review:**
- [ ] PR title clearly describes the change
- [ ] Branch is up-to-date with base branch
- [ ] CI/CD pipeline passes
- [ ] Self-review completed
- [ ] Tests cover new functionality
