# Milestone 2: Account Management and Placement - Action Guide

## 📋 Executive Summary

**Current Status**: 10 AWS accounts created, but 3 are misplaced  
**Priority Actions**: Move 3 accounts + Create 3 critical accounts  
**Timeline**: 1-2 hours to complete  
**Complexity**: Medium (account movement requires care)

---

## 🎯 Current State Analysis

### What You Have (Good News! ✅)

1. **10 Accounts Created** - Excellent progress!
2. **Proper Email Convention** - Using Gmail plus-addressing consistently
3. **No Accounts at Root** - Following best practices
4. **Recent Activity** - 6 accounts created on 2025/11/06 (rapid implementation)
5. **Security Focus** - Dedicated security accounts in place

### What Needs Fixing (Critical ⚠️)

**3 Misplaced Accounts in DO-NOT-TOUCH OU**:
- `houston-medical-sandbox` → Should be in **Sandbox-OU**
- `peter-devsecops-engineer` → Should be in **Sandbox-OU**
- `Security Office Team 2` → Should be in **Security-OU**

**Why This Matters**:
- DO-NOT-TOUCH should only contain critical infrastructure
- These accounts will get wrong SCPs when we implement them (Milestone 3)
- Sandbox accounts need more freedom, not maximum restriction

---

## 🚨 PRIORITY 1: Fix Misplaced Accounts (Do This First!)

### Step 1: Move houston-medical-sandbox to Sandbox-OU

**Why**: It's a sandbox account, belongs with experimentation accounts

**How to Move** (Click-by-Click):

1. **Navigate to Organizations Console**
   - Go to AWS Console
   - Search for "Organizations"
   - Click "AWS accounts" in left sidebar

2. **Find the Account**
   - Expand DO-NOT-TOUCH OU
   - Locate `houston-medical-sandbox` (Account ID: 855808870680)
   - ✅ Confirm it says "Created 2025/06/12"

3. **Initiate Move**
   - Select the checkbox next to `houston-medical-sandbox`
   - Click "Actions" dropdown at top
   - Select "Move AWS account"

4. **Choose Destination**
   - In the "Move AWS account" dialog:
   - Under "Destination", select **Sandbox-OU**
   - OU ID should show: ou-im88-1r7by4at
   - Click "Move AWS account" button

5. **Verify**
   - Expand Sandbox-OU
   - Confirm `houston-medical-sandbox` now appears there
   - Confirm it no longer appears in DO-NOT-TOUCH

**⏱️ Time Required**: 2-3 minutes

---

### Step 2: Move peter-devsecops-engineer to Sandbox-OU

**Why**: Engineering/DevSecOps testing account, not critical infrastructure

**How to Move** (Click-by-Click):

1. **Find the Account**
   - Expand DO-NOT-TOUCH OU (if not already expanded)
   - Locate `peter-devsecops-engineer` (Account ID: 058264577640)

2. **Initiate Move**
   - Select the checkbox next to `peter-devsecops-engineer`
   - Click "Actions" dropdown
   - Select "Move AWS account"

3. **Choose Destination**
   - Destination: **Sandbox-OU** (ou-im88-1r7by4at)
   - Click "Move AWS account"

4. **Verify**
   - Expand Sandbox-OU
   - Confirm `peter-devsecops-engineer` is now there
   - Sandbox-OU should now have 3 accounts total

**⏱️ Time Required**: 2-3 minutes

---

### Step 3: Move Security Office Team 2 to Security-OU

**Why**: Security team account belongs in Security-OU, not DO-NOT-TOUCH

**How to Move** (Click-by-Click):

1. **Find the Account**
   - Expand DO-NOT-TOUCH OU
   - Locate `Security Office Team 2` (Account ID: 355582442217)

2. **Initiate Move**
   - Select checkbox next to `Security Office Team 2`
   - Click "Actions" dropdown
   - Select "Move AWS account"

3. **Choose Destination**
   - Destination: **Security-OU** (ou-im88-o8bz8kx1)
   - Click "Move AWS account"

4. **Verify**
   - Expand Security-OU
   - Confirm `Security Office Team 2` is now there
   - Security-OU should now have 3 accounts total

5. **Final Verification**
   - Expand DO-NOT-TOUCH OU
   - **CRITICAL**: Should contain ONLY `Client-S3-Storage-Prod`
   - If you see any other accounts, they need to be moved

**⏱️ Time Required**: 2-3 minutes

---

### ✅ Checkpoint: After Moving Accounts

Your structure should now look like this:

```
DO-NOT-TOUCH: 1 account ✅
├── Client-S3-Storage-Prod (Management Account)

Non-production-OU: 2 accounts ✅
├── Dev-Environment
└── Test-Environment

Production-OU: 1 account ✅
└── Prod-Application

Sandbox-OU: 3 accounts ✅
├── Experiment-Account
├── houston-medical-sandbox (MOVED)
└── peter-devsecops-engineer (MOVED)

Security-OU: 3 accounts ✅
├── Security-Logging-Account
├── Security-Tools
└── Security Office Team 2 (MOVED)
```

**Total**: 10 accounts, all correctly placed

**⏱️ Total Time for Priority 1**: 10-15 minutes

---

## 🎯 PRIORITY 2: Create Critical Missing Accounts

### Step 4: Create Staging-Environment (Non-production-OU)

**Why Critical**: Staging is essential for pre-production validation

**Purpose**: 
- Final testing before production deployment
- Mirrors production configuration
- Cost optimization (can be smaller than production)

**How to Create** (Click-by-Click):

1. **Navigate to Account Creation**
   - In Organizations console
   - Click "AWS accounts" in left sidebar
   - Click "Add an AWS account" button (top right)

2. **Fill Account Details**
   - Select "Create an AWS account"
   - **AWS account name**: `Staging-Environment`
   - **Email address**: `seun.beaconagilelogix+Staging-Environment@gmail.com`
   - **IAM role name**: Leave as `OrganizationAccountAccessRole` (default)

3. **Choose Parent OU**
   - Under "Parent organizational unit"
   - Select **Non-production-OU** (ou-im88-ozx04ihn)

4. **Create**
   - Click "Create AWS account"
   - Wait 1-2 minutes for account creation
   - You'll see a success message

5. **Verify**
   - Expand Non-production-OU
   - Confirm `Staging-Environment` appears
   - Should show "Created 2025/11/09"
   - Non-production-OU should now have 3 accounts

**⏱️ Time Required**: 5-7 minutes (includes AWS provisioning time)

**What This Account is For** (Layman):
Think of staging as your dress rehearsal. It's where you do a final check before going live, in an environment that looks just like production but isn't serving real customers yet.

---

### Step 5: Create Network-Hub (DO-NOT-TOUCH)

**Why Critical**: Centralized networking is fundamental infrastructure

**Purpose**:
- Centralized Transit Gateway (hub-and-spoke networking)
- VPN connections
- Direct Connect (if using on-premises connectivity)
- Shared networking resources

**How to Create** (Click-by-Click):

1. **Navigate to Account Creation**
   - Click "Add an AWS account" button

2. **Fill Account Details**
   - Select "Create an AWS account"
   - **AWS account name**: `Network-Hub`
   - **Email address**: `seun.beaconagilelogix+Network-Hub@gmail.com`
   - **IAM role name**: `OrganizationAccountAccessRole`

3. **Choose Parent OU**
   - Select **DO-NOT-TOUCH** (ou-im88-16gred4y)
   - This is correct - networking is critical shared infrastructure

4. **Create**
   - Click "Create AWS account"
   - Wait for provisioning

5. **Verify**
   - Expand DO-NOT-TOUCH OU
   - Should now have 2 accounts:
     - Client-S3-Storage-Prod (Management)
     - Network-Hub (NEW)

**⏱️ Time Required**: 5-7 minutes

**What This Account is For** (Technical):
The Network-Hub centralizes all networking infrastructure. When you implement Transit Gateway, all VPCs in other accounts will connect through this hub. This enables shared networking policies and simplifies network management.

---

### Step 6: Create Audit-Compliance (Security-OU)

**Why Critical**: Compliance and audit functions should be separate

**Purpose**:
- AWS Config aggregation across all accounts
- Compliance dashboard (CIS benchmarks, PCI-DSS, etc.)
- Audit report generation
- Separate from security tools for independence

**How to Create** (Click-by-Click):

1. **Navigate to Account Creation**
   - Click "Add an AWS account" button

2. **Fill Account Details**
   - Select "Create an AWS account"
   - **AWS account name**: `Audit-Compliance`
   - **Email address**: `seun.beaconagilelogix+Audit-Compliance@gmail.com`
   - **IAM role name**: `OrganizationAccountAccessRole`

3. **Choose Parent OU**
   - Select **Security-OU** (ou-im88-o8bz8kx1)

4. **Create**
   - Click "Create AWS account"
   - Wait for provisioning

5. **Verify**
   - Expand Security-OU
   - Should now have 4 accounts:
     - Security-Logging-Account
     - Security-Tools
     - Security Office Team 2
     - Audit-Compliance (NEW)

**⏱️ Time Required**: 5-7 minutes

**What This Account is For** (Layman):
This is like an independent auditor's office. It watches all your AWS accounts and generates compliance reports. By keeping it separate from security tools, you maintain independence (auditors shouldn't audit themselves).

---

### ✅ Checkpoint: After Creating Recommended Accounts

Your structure should now be:

```
DO-NOT-TOUCH: 2 accounts ✅
├── Client-S3-Storage-Prod (Management Account)
└── Network-Hub (NEW)

Non-production-OU: 3 accounts ✅
├── Dev-Environment
├── Test-Environment
└── Staging-Environment (NEW)

Production-OU: 1 account ✅
└── Prod-Application

Sandbox-OU: 3 accounts ✅
├── Experiment-Account
├── houston-medical-sandbox
└── peter-devsecops-engineer

Security-OU: 4 accounts ✅
├── Security-Logging-Account
├── Security-Tools
├── Security Office Team 2
└── Audit-Compliance (NEW)
```

**Total**: 13 accounts, all correctly placed and purposeful

**⏱️ Total Time for Priority 2**: 15-20 minutes

---

## 🎯 OPTIONAL: Additional Accounts (As Needed)

### Optional Account 1: Prod-Database (Production-OU)

**When to Create**:
- ✅ If you're separating database tier from application tier
- ✅ If database has different IAM permission requirements
- ✅ If you want separate billing/cost tracking for databases

**When NOT to Create**:
- ❌ If databases run in same account as applications
- ❌ If team structure doesn't require separation

**How to Create** (if needed):
- Name: `Prod-Database`
- Email: `seun.beaconagilelogix+Prod-Database@gmail.com`
- OU: Production-OU
- Purpose: RDS instances, DynamoDB tables, Aurora clusters

---

### Optional Account 2: Shared-Services (DO-NOT-TOUCH)

**When to Create**:
- ✅ If you have Active Directory / LDAP
- ✅ If you have centralized DNS (Route 53 Resolver)
- ✅ If you have shared Docker registries / artifact repos

**When NOT to Create**:
- ❌ If you don't have shared services yet
- ❌ If Network-Hub can house these services

**How to Create** (if needed):
- Name: `Shared-Services`
- Email: `seun.beaconagilelogix+Shared-Services@gmail.com`
- OU: DO-NOT-TOUCH
- Purpose: Centralized shared infrastructure

---

### Optional Account 3: Prod-DataLake (Production-OU)

**When to Create**:
- ✅ If you're building data lake / data warehouse
- ✅ If you have big data analytics requirements
- ✅ If you want to separate data analytics billing

**When NOT to Create**:
- ❌ If you're not doing data analytics
- ❌ If analytics can live in Prod-Application

**How to Create** (if needed):
- Name: `Prod-DataLake`
- Email: `seun.beaconagilelogix+Prod-DataLake@gmail.com`
- OU: Production-OU
- Purpose: S3 data lake, Athena, Glue, Redshift

---

## 📊 Account Naming Analysis

### Your Current Naming Convention ✅

**Pattern**: `{Purpose}-{Environment}` or `{Purpose}-{Type}`

**Examples**:
- `Dev-Environment` ✅ Clear
- `Test-Environment` ✅ Clear
- `Prod-Application` ✅ Clear
- `Security-Logging-Account` ✅ Clear
- `Experiment-Account` ✅ Clear

**Email Pattern**: `seun.beaconagilelogix+{AccountName}@gmail.com`

**Why This is Excellent**:
1. ✅ Uses Gmail plus-addressing (all emails to one inbox)
2. ✅ Easy to filter by account
3. ✅ No need for multiple email accounts
4. ✅ Consistent across all new accounts
5. ✅ Self-documenting (account name in email)

**Exceptions** (Legacy accounts):
- `Client-S3-Storage-Prod` - Uses different email, likely pre-existing
- `houston-medical-sandbox` - Uses different email, project-specific
- `peter-devsecops-engineer` - Personal account, uses personal email

**Recommendation**: ✅ Keep your current convention for all NEW accounts

---

## 🔒 Account Access & Security Notes

### Default IAM Role

Every account is created with `OrganizationAccountAccessRole` which allows:
- Management account to assume role and administer member account
- Full AdministratorAccess permissions

**Security Best Practice**:
1. Use this role only for initial setup
2. Create proper IAM users/roles with least privilege
3. Enable MFA on all accounts (especially management)
4. Use AWS SSO (IAM Identity Center) for centralized access

### Account Root User

Each account has a root user with email address you specified:
- Can reset password using "Forgot Password" on AWS login
- Requires access to the email inbox
- Should be used ONLY for account recovery

**Best Practice**: Enable MFA on root user immediately after account creation

---

## 📸 Documentation Requirements

### After Completing Moves and Creates

1. **Take Screenshot** of final account structure
   - Show all OUs expanded
   - Verify account counts match expectations
   - Save as `03-corrected-account-placement.png`

2. **Document Each Account** (Update notes.md):
   - Account name
   - Account ID
   - Email address
   - OU placement
   - Purpose
   - Created/joined date
   - Owner/team responsible

3. **Update Diagrams**:
   - Update OU-STRUCTURE-DIAGRAM.md with actual account names
   - Show account counts per OU

---

## ✅ Success Criteria Checklist

### After Priority 1 (Account Moves)
- [ ] DO-NOT-TOUCH contains ONLY management account (1 account)
- [ ] Sandbox-OU has 3 accounts
- [ ] Security-OU has 3 accounts
- [ ] All accounts in correct OUs based on purpose

### After Priority 2 (Critical Account Creation)
- [ ] Staging-Environment created in Non-production-OU
- [ ] Network-Hub created in DO-NOT-TOUCH
- [ ] Audit-Compliance created in Security-OU
- [ ] Total account count is 13

### Overall Milestone 2 Completion
- [ ] All accounts correctly placed in appropriate OUs
- [ ] No accounts at Root level (except management account which is in DO-NOT-TOUCH)
- [ ] Account naming convention documented
- [ ] Email convention consistent (plus-addressing)
- [ ] All accounts documented with purpose
- [ ] Screenshot of final structure captured
- [ ] Ready for Milestone 3 (SCP implementation)

---

## ⏱️ Time Estimates Summary

| Task | Time Required |
|------|---------------|
| **Priority 1: Move 3 accounts** | 10-15 minutes |
| **Priority 2: Create 3 accounts** | 15-20 minutes |
| **Documentation & screenshots** | 10-15 minutes |
| **Optional accounts** | 5-7 min each |
| **Total (Priority 1 + 2 + Docs)** | **35-50 minutes** |

---

## 🎯 Recommended Execution Order

### Session 1: Fix Critical Issues (20-30 minutes)
1. ✅ Move houston-medical-sandbox → Sandbox-OU
2. ✅ Move peter-devsecops-engineer → Sandbox-OU
3. ✅ Move Security Office Team 2 → Security-OU
4. ✅ Verify DO-NOT-TOUCH has only management account
5. 📸 Take screenshot of corrected structure

### Session 2: Add Critical Accounts (20-30 minutes)
6. ✅ Create Staging-Environment → Non-production-OU
7. ✅ Create Network-Hub → DO-NOT-TOUCH
8. ✅ Create Audit-Compliance → Security-OU
9. ✅ Verify all accounts created successfully
10. 📸 Take screenshot of complete structure

### Session 3: Documentation (15-20 minutes)
11. ✅ Update notes.md with all account details
12. ✅ Update diagrams with actual accounts
13. ✅ Document account ownership
14. ✅ Mark Milestone 2 as complete

---

## 🚀 What Happens After Milestone 2

Once all accounts are correctly placed:

**Milestone 3: Service Control Policies**
- Create baseline security SCP
- Create geo-restriction SCP
- Create encryption enforcement SCP
- Attach SCPs to each OU
- Test SCP enforcement

**Why Account Placement Matters**:
- SCPs are attached to OUs, not individual accounts
- All accounts in an OU inherit the same SCPs
- Misplaced accounts get wrong permissions
- Fixing placement now prevents security issues later

---

## 📞 Quick Reference

### Current OU IDs
- **DO-NOT-TOUCH**: ou-im88-16gred4y
- **Non-production-OU**: ou-im88-ozx04ihn
- **Production-OU**: ou-im88-v1z00uzh
- **Sandbox-OU**: ou-im88-1r7by4at
- **Security-OU**: ou-im88-o8bz8kx1

### Account Count Targets
- DO-NOT-TOUCH: 2 accounts (was 4, move 3 out, add 1)
- Non-production-OU: 3 accounts (was 2, add 1)
- Production-OU: 1 account (stays same for now)
- Sandbox-OU: 3 accounts (was 1, add 2 via moves)
- Security-OU: 4 accounts (was 2, add 1 via move + 1 new)

**Total**: 13 accounts

---

**Action Guide Version**: 1.0  
**Last Updated**: November 9, 2025  
**Status**: Ready for Implementation  
**Estimated Completion Time**: 1 hour total
