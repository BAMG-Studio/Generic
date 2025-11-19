# Current AWS Account Placement - Milestone 2 Status

**Document Purpose**: Visual representation of current account placement across OUs (as of second screenshot)  
**Status**: 75% Complete - 3 accounts misplaced, 3 accounts missing  
**Date**: November 7, 2025  
**Organization ID**: o-3l9ybracw9

---

## Quick Reference: Current vs. Target State

| OU Name | Current Count | Target Count | Status | Action Required |
|---------|---------------|--------------|--------|-----------------|
| DO-NOT-TOUCH | 4 accounts | 2 accounts | ⚠️ Overpopulated | Move 3 accounts OUT |
| Non-production-OU | 2 accounts | 3 accounts | 🔄 Incomplete | Create 1 account |
| Production-OU | 1 account | 1 account | ✅ Complete | None |
| Sandbox-OU | 1 account | 3 accounts | 🔄 Incomplete | Move 2 accounts IN |
| Security-OU | 2 accounts | 4 accounts | 🔄 Incomplete | Move 1 IN, Create 1 |
| **TOTAL** | **10 accounts** | **13 accounts** | **77% Complete** | **Move 3, Create 3** |

---

## Organizational Hierarchy: Current State

```
AWS Organizations (o-3l9ybracw9)
│
├─ Root (r-im88) 
   │
   ├─ DO-NOT-TOUCH OU (ou-im88-16gred4y) ⚠️ ISSUE: 3 accounts shouldn't be here
   │  ├── ✅ Client-S3-Storage-Prod (Management Account) - 005965605891
   │  │   └─ Email: seun.beaconagilelogix+Client-S3-Storage-Prod@gmail.com
   │  │   └─ Purpose: Management account (CORRECT PLACEMENT)
   │  │   └─ Created: Before 2025/11/06
   │  │
   │  ├── ⚠️ houston-medical-sandbox - 489361287086  
   │  │   └─ Email: seun.beaconagilelogix+houston-medical-sandbox@gmail.com
   │  │   └─ Purpose: Healthcare sandbox experimentation
   │  │   └─ Created: 2025/11/06
   │  │   └─ ❌ MISPLACED - Should be in: Sandbox-OU
   │  │   └─ Action: MOVE to Sandbox-OU
   │  │
   │  ├── ⚠️ peter-devsecops-engineer - 058305886119
   │  │   └─ Email: seun.beaconagilelogix+peter-devsecops-engineer@gmail.com
   │  │   └─ Purpose: DevSecOps engineering workspace
   │  │   └─ Created: 2025/11/06
   │  │   └─ ❌ MISPLACED - Should be in: Sandbox-OU
   │  │   └─ Action: MOVE to Sandbox-OU
   │  │
   │  └── ⚠️ Security Office Team 2 - 992412711616
   │      └─ Email: seun.beaconagilelogix+Security+Office+Team+2@gmail.com
   │      └─ Purpose: Secondary security operations team
   │      └─ Created: 2025/11/06
   │      └─ ❌ MISPLACED - Should be in: Security-OU
   │      └─ Action: MOVE to Security-OU
   │
   ├─ Non-production-OU (ou-im88-ozx04ihn) 🔄 INCOMPLETE: Missing 1 account
   │  ├── ✅ Dev-Environment - 211182599226
   │  │   └─ Email: seun.beaconagilelogix+Dev-Environment@gmail.com
   │  │   └─ Purpose: Development environment
   │  │   └─ Created: 2025/11/06
   │  │   └─ Status: ✅ CORRECT PLACEMENT
   │  │
   │  ├── ✅ Test-Environment - 654654055353
   │  │   └─ Email: seun.beaconagilelogix+Test-Environment@gmail.com
   │  │   └─ Purpose: Testing environment
   │  │   └─ Created: 2025/11/06
   │  │   └─ Status: ✅ CORRECT PLACEMENT
   │  │
   │  └── 🔜 Staging-Environment - [NOT YET CREATED]
   │      └─ Email: seun.beaconagilelogix+Staging-Environment@gmail.com
   │      └─ Purpose: Pre-production staging environment
   │      └─ Status: ❌ MISSING - NEEDS CREATION
   │      └─ Action: CREATE new account in Non-production-OU
   │      └─ Priority: HIGH (critical for release pipeline)
   │
   ├─ Production-OU (ou-im88-v1z00uzh) ✅ COMPLETE
   │  └── ✅ Prod-Application - 366508127438
   │      └─ Email: seun.beaconagilelogix+Prod-Application@gmail.com
   │      └─ Purpose: Production application workloads
   │      └─ Created: 2025/11/06
   │      └─ Status: ✅ CORRECT PLACEMENT
   │
   ├─ Sandbox-OU (ou-im88-1r7by4at) 🔄 INCOMPLETE: Missing 2 accounts (being moved)
   │  ├── ✅ marissa-ui-designer - 471198055906
   │  │   └─ Email: seun.beaconagilelogix+marissa-ui-designer@gmail.com
   │  │   └─ Purpose: UI/UX design experimentation
   │  │   └─ Created: 2025/11/06
   │  │   └─ Status: ✅ CORRECT PLACEMENT
   │  │
   │  ├── 🔄 houston-medical-sandbox - 489361287086 [WILL MOVE HERE]
   │  │   └─ Currently in: DO-NOT-TOUCH
   │  │   └─ Action: Incoming from DO-NOT-TOUCH OU
   │  │
   │  └── 🔄 peter-devsecops-engineer - 058305886119 [WILL MOVE HERE]
   │      └─ Currently in: DO-NOT-TOUCH
   │      └─ Action: Incoming from DO-NOT-TOUCH OU
   │
   └─ Security-OU (ou-im88-o8bz8kx1) 🔄 INCOMPLETE: Missing 2 accounts
      ├── ✅ Security Office Team 1 - 448742660421
      │   └─ Email: seun.beaconagilelogix+Security+Office+Team+1@gmail.com
      │   └─ Purpose: Primary security operations team
      │   └─ Created: 2025/11/06
      │   └─ Status: ✅ CORRECT PLACEMENT
      │
      ├── ✅ Log-Archive-Account - 021387476733
      │   └─ Email: seun.beaconagilelogix+Log-Archive-Account@gmail.com
      │   └─ Purpose: Centralized logging and archival
      │   └─ Created: 2025/11/06
      │   └─ Status: ✅ CORRECT PLACEMENT
      │
      ├── 🔄 Security Office Team 2 - 992412711616 [WILL MOVE HERE]
      │   └─ Currently in: DO-NOT-TOUCH
      │   └─ Action: Incoming from DO-NOT-TOUCH OU
      │
      └── 🔜 Audit-Compliance - [NOT YET CREATED]
          └─ Email: seun.beaconagilelogix+Audit-Compliance@gmail.com
          └─ Purpose: Independent audit and compliance monitoring
          └─ Status: ❌ MISSING - NEEDS CREATION
          └─ Action: CREATE new account in Security-OU
          └─ Priority: HIGH (required for compliance independence)
```

---

## Visual Status Summary

### Legend

- ✅ **Correct Placement**: Account is in the right OU
- ⚠️ **Misplaced**: Account exists but in wrong OU (needs move)
- 🔜 **Missing**: Account needs to be created
- 🔄 **In Transition**: Account will move here or being worked on

### Color-Coded Status by OU

```
┌─────────────────────────────────────────────────────────────────┐
│ DO-NOT-TOUCH OU                                    ⚠️ CRITICAL   │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Client-S3-Storage-Prod (Management)                          │
│ ⚠️ houston-medical-sandbox          [MOVE → Sandbox-OU]        │
│ ⚠️ peter-devsecops-engineer         [MOVE → Sandbox-OU]        │
│ ⚠️ Security Office Team 2           [MOVE → Security-OU]       │
│ 🔜 Network-Hub                      [CREATE HERE]              │
│                                                                 │
│ Status: 4/2 accounts (2 overpopulated)                         │
│ Action: Remove 3, Add 1 = Net -2 accounts                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Non-production-OU                                  🔄 INCOMPLETE │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Dev-Environment                                              │
│ ✅ Test-Environment                                             │
│ 🔜 Staging-Environment              [CREATE HERE]              │
│                                                                 │
│ Status: 2/3 accounts                                           │
│ Action: Create 1 account                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Production-OU                                      ✅ COMPLETE   │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Prod-Application                                             │
│                                                                 │
│ Status: 1/1 accounts                                           │
│ Action: None required                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Sandbox-OU                                         🔄 INCOMPLETE │
├─────────────────────────────────────────────────────────────────┤
│ ✅ marissa-ui-designer                                          │
│ 🔄 houston-medical-sandbox          [INCOMING]                 │
│ 🔄 peter-devsecops-engineer         [INCOMING]                 │
│                                                                 │
│ Status: 1/3 accounts (2 incoming)                              │
│ Action: Receive 2 accounts from DO-NOT-TOUCH                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Security-OU                                        🔄 INCOMPLETE │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Security Office Team 1                                       │
│ ✅ Log-Archive-Account                                          │
│ 🔄 Security Office Team 2           [INCOMING]                 │
│ 🔜 Audit-Compliance                 [CREATE HERE]              │
│                                                                 │
│ Status: 2/4 accounts (1 incoming, 1 to create)                 │
│ Action: Receive 1 account + Create 1 account                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Account Movement Matrix

### Priority 1: Account Moves (10-15 minutes)

| Account Name | Account ID | Current OU | Target OU | Reason | Priority |
|--------------|------------|------------|-----------|--------|----------|
| houston-medical-sandbox | 489361287086 | DO-NOT-TOUCH | Sandbox-OU | Healthcare experimentation belongs in sandbox | HIGH |
| peter-devsecops-engineer | 058305886119 | DO-NOT-TOUCH | Sandbox-OU | Engineering workspace belongs in sandbox | HIGH |
| Security Office Team 2 | 992412711616 | DO-NOT-TOUCH | Security-OU | Security operations belong in Security-OU | HIGH |

### Priority 2: Account Creations (15-20 minutes)

| Account Name | Target OU | Email | Purpose | Priority |
|--------------|-----------|-------|---------|----------|
| Staging-Environment | Non-production-OU | seun.beaconagilelogix+Staging-Environment@gmail.com | Pre-production testing | CRITICAL |
| Network-Hub | DO-NOT-TOUCH | seun.beaconagilelogix+Network-Hub@gmail.com | Centralized networking (Transit Gateway, etc.) | CRITICAL |
| Audit-Compliance | Security-OU | seun.beaconagilelogix+Audit-Compliance@gmail.com | Independent compliance monitoring | CRITICAL |

---

## Target State After Corrections

```
AWS Organizations (o-3l9ybracw9)
│
├─ Root (r-im88) 
   │
   ├─ DO-NOT-TOUCH OU - 2 accounts ✅
   │  ├── Client-S3-Storage-Prod (Management)
   │  └── Network-Hub
   │
   ├─ Non-production-OU - 3 accounts ✅
   │  ├── Dev-Environment
   │  ├── Test-Environment
   │  └── Staging-Environment
   │
   ├─ Production-OU - 1 account ✅
   │  └── Prod-Application
   │
   ├─ Sandbox-OU - 3 accounts ✅
   │  ├── marissa-ui-designer
   │  ├── houston-medical-sandbox
   │  └── peter-devsecops-engineer
   │
   └─ Security-OU - 4 accounts ✅
      ├── Security Office Team 1
      ├── Security Office Team 2
      ├── Log-Archive-Account
      └── Audit-Compliance
```

**Total: 13 accounts across 5 OUs**

---

## Completion Checklist

### Immediate Actions (Next 30-45 minutes)

- [ ] **Phase 1: Move Misplaced Accounts** (10-15 min)
  - [ ] Move `houston-medical-sandbox` from DO-NOT-TOUCH to Sandbox-OU
  - [ ] Move `peter-devsecops-engineer` from DO-NOT-TOUCH to Sandbox-OU
  - [ ] Move `Security Office Team 2` from DO-NOT-TOUCH to Security-OU
  - [ ] Verify all 3 moves completed successfully

- [ ] **Phase 2: Create Missing Accounts** (15-20 min)
  - [ ] Create `Staging-Environment` in Non-production-OU
  - [ ] Create `Network-Hub` in DO-NOT-TOUCH
  - [ ] Create `Audit-Compliance` in Security-OU
  - [ ] Verify all 3 accounts created successfully

- [ ] **Phase 3: Verification** (5 min)
  - [ ] Take screenshot of final account placement
  - [ ] Verify account counts match target:
    - DO-NOT-TOUCH: 2 accounts
    - Non-production-OU: 3 accounts
    - Production-OU: 1 account
    - Sandbox-OU: 3 accounts
    - Security-OU: 4 accounts
  - [ ] Total: 13 accounts

- [ ] **Phase 4: Documentation** (5-10 min)
  - [ ] Submit final screenshot for documentation
  - [ ] Update README with completion status
  - [ ] Mark Milestone 2 as 100% complete

---

## Why These Accounts Need to Move

### houston-medical-sandbox → Sandbox-OU

**Current Problem**: In DO-NOT-TOUCH (reserved for management account and critical shared infrastructure)

**Why It Should Move**:

- **Purpose**: Healthcare-specific experimentation and development
- **Risk Level**: Sandbox accounts have experimental workloads
- **SCP Impact**: DO-NOT-TOUCH has strictest policies; sandbox needs more freedom
- **Organizational Logic**: All sandbox environments should be together for consistent policy application

**Business Impact**: Prevents overly restrictive policies from blocking legitimate healthcare experimentation

---

### peter-devsecops-engineer → Sandbox-OU

**Current Problem**: In DO-NOT-TOUCH (reserved for management account and critical shared infrastructure)

**Why It Should Move**:

- **Purpose**: DevSecOps engineering workspace for personal/experimental work
- **User Type**: Individual contributor workspace
- **Risk Level**: Development/testing workloads, not production-critical
- **SCP Impact**: Needs flexibility for tool testing and development
- **Organizational Logic**: Personal development accounts belong in sandbox

**Business Impact**: Enables DevSecOps engineer to test tools and automation without restrictive policies

---

### Security Office Team 2 → Security-OU

**Current Problem**: In DO-NOT-TOUCH (should be with other security team accounts)

**Why It Should Move**:

- **Purpose**: Security operations team account
- **Organizational Logic**: Security Office Team 1 is already in Security-OU
- **Team Consistency**: Same team type should have same policies
- **SCP Impact**: Security-OU has security-specific policies (CloudTrail required, etc.)
- **Centralized Management**: All security accounts together for compliance tracking

**Business Impact**: Ensures consistent security policies across all security team accounts

---

## Account Creation Justifications

### Staging-Environment (Non-production-OU)

**Purpose**: Pre-production staging environment for final testing before production deployment

**Why Critical**:

- **Release Pipeline**: Modern DevOps requires Dev → Test → **Staging** → Prod
- **Production Parity**: Staging mimics production configuration for realistic testing
- **Risk Mitigation**: Catches issues before they reach production
- **Compliance**: Many frameworks require staging environment for change validation

**Without This Account**: No way to validate changes in production-like environment before deployment

---

### Network-Hub (DO-NOT-TOUCH)

**Purpose**: Centralized networking infrastructure (Transit Gateway, Direct Connect, VPN)

**Why Critical**:

- **Hub-and-Spoke Model**: Central network hub for all account connectivity
- **DO-NOT-TOUCH Placement**: Network infrastructure is foundational, should not be modified casually
- **Cost Optimization**: Single Transit Gateway shared across accounts
- **Security**: Centralized network controls and monitoring

**Without This Account**: Each account would need separate networking (expensive, complex, inconsistent)

---

### Audit-Compliance (Security-OU)

**Purpose**: Independent audit trail and compliance monitoring separate from operational security

**Why Critical**:

- **Separation of Duties**: Audit function must be independent from operations
- **Compliance Requirements**: Many frameworks require separate audit account
- **Immutable Logs**: Independent account prevents log tampering
- **Third-Party Audits**: Provides controlled access for external auditors

**Without This Account**: Audit trails could be modified by operational teams (compliance violation)

---

## Next Steps After Milestone 2 Completion

Once all 13 accounts are correctly placed:

1. **Take Final Screenshot**: Document final state for records
2. **Update All Documentation**: Mark Milestone 2 as 100% complete
3. **Proceed to Milestone 3**: Implement Service Control Policies (SCPs)
4. **Milestone 3 Prerequisites**: Account structure MUST be correct before SCP implementation

---

## Reference Documents

- **Detailed Action Guide**: `docs/MILESTONE-2-ACTION-GUIDE.md`
- **Screenshot Analysis**: `screenshots/milestone-1-ou-creation/02-complete-account-placement.md`
- **Progress Tracking**: `notes.md` - Milestone 2 Section
- **Original OU Structure**: `diagrams/OU-STRUCTURE-DIAGRAM.md`

---

**Document Status**: Current as of November 7, 2025  
**Next Update**: After account moves and creations complete  
**Milestone 2 Progress**: 75% → Target: 100%
