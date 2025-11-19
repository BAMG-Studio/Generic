# AWS Organizations Structure Diagram

## Visual Representation: Organizational Hierarchy

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                     AWS ORGANIZATION                                 │
│                    Organization ID: o-3l9ybracw9                     │
│                   Management Account: 0059-6560-5891                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                                  ▼
         ┌────────────────────────────────────────────────┐
         │              ROOT ORGANIZATIONAL UNIT          │
         │                  ID: r-im88                    │
         │          (Top-level container - immutable)     │
         └────────────────────────────────────────────────┘
                                  │
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          │                       │                       │
┌─────────▼─────────┐   ┌─────────▼─────────┐   ┌───────▼──────────┐
│                   │   │                   │   │                  │
│  DO-NOT-TOUCH     │   │  Non-production   │   │  Production-OU   │
│                   │   │       -OU         │   │                  │
│  ou-im88-16gred4y │   │  ou-im88-ozx04ihn │   │ ou-im88-v1z00uzh │
│                   │   │                   │   │                  │
│  ⚠️ CRITICAL ⚠️    │   │   🛠️ DEV/TEST     │   │   🏭 LIVE PROD   │
│                   │   │                   │   │                  │
└───────────────────┘   └───────────────────┘   └──────────────────┘
  Purpose:                Purpose:                Purpose:
  • Management account    • Development           • Production apps
  • Core infrastructure   • Testing/QA            • Customer-facing
  • Break-glass access    • Staging               • Critical systems
  • Transit Gateway       • Experimentation       • Live databases
                                                  
  SCP Strategy:           SCP Strategy:           SCP Strategy:
  • Most restrictive      • Moderate restrictions • Strict controls
  • Multi-party approval  • Developer freedom     • Change management
  • No modifications      • Cost optimization     • High compliance


          │                       │
          │                       │
┌─────────▼─────────┐   ┌─────────▼─────────┐
│                   │   │                   │
│   Sandbox-OU      │   │   Security-OU     │
│                   │   │                   │
│  ou-im88-1r7by4at │   │  ou-im88-o8bz8kx1 │
│                   │   │                   │
│  🏖️ PLAYGROUND     │   │   🔒 SECURITY     │
│                   │   │                   │
└───────────────────┘   └───────────────────┘
  Purpose:                Purpose:
  • POC work              • Security tools
  • Learning/training     • GuardDuty
  • Tool evaluation       • Security Hub
  • Unrestricted testing  • CloudTrail logs
                          • Audit/compliance
                          
  SCP Strategy:           SCP Strategy:
  • Minimal SCPs          • Prevent tool disable
  • Budget limits only    • Restrictive access
  • No production data    • Logging enforcement
  • Auto-cleanup          • Compliance controls
```

---

## Flat Hierarchy Visualization

This organization uses a **flat hierarchy** structure:

```
Level 0:    [Root]
              │
Level 1:      ├── DO-NOT-TOUCH
              ├── Non-production-OU
              ├── Production-OU
              ├── Sandbox-OU
              └── Security-OU
```

**Characteristics:**
- **Single tier**: All OUs at the same hierarchical level
- **Simple inheritance**: All OUs inherit directly from Root
- **Clear boundaries**: No nested complexity
- **Easy to understand**: Straightforward organizational model

---

## OU Relationship Matrix

| OU Name | Parent | Level | Siblings | Typical Account Count | Isolation Level |
|---------|--------|-------|----------|----------------------|-----------------|
| DO-NOT-TOUCH | Root | 1 | 4 | 1-3 | Maximum |
| Non-production-OU | Root | 1 | 4 | 5-20 | Moderate |
| Production-OU | Root | 1 | 4 | 3-15 | High |
| Sandbox-OU | Root | 1 | 4 | 10-50 | Low |
| Security-OU | Root | 1 | 4 | 2-5 | Maximum |

---

## Information Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ROOT POLICIES                            │
│  • FullAWSAccess (default - allows everything)                  │
│  • Future SCPs will apply globally to all OUs                   │
└─────────────────────────────────────────────────────────────────┘
                              │
            Policies Inherited by All Child OUs ▼
                              │
    ┌─────────────┬───────────┼───────────┬────────────┐
    │             │           │           │            │
    ▼             ▼           ▼           ▼            ▼
[DO-NOT]    [Non-prod]   [Production] [Sandbox]  [Security]
    │             │           │           │            │
Additional SCPs  Additional  Additional  Additional  Additional
can be attached  SCPs        SCPs        SCPs        SCPs
here (additive   attached    attached    attached    attached
restrictions)    here        here        here        here
```

**Key Concept**: SCPs work by **intersection** (most restrictive wins)
- Root SCP: Allows actions A, B, C, D, E
- Production-OU SCP: Allows actions A, B, C only
- **Result for Production accounts**: Can only perform A, B, C (intersection)

---

## Account Placement Strategy Diagram

```
                    New AWS Account Created
                              │
                              ▼
                    ┌──────────────────────┐
                    │ What's the purpose?  │
                    └──────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  Is it critical        Is it for           Is it for
  infrastructure?      production use?     experimentation?
        │                     │                     │
       YES                   YES                   YES
        │                     │                     │
        ▼                     ▼                     ▼
  ┌─────────────┐      ┌──────────────┐     ┌─────────────┐
  │ DO-NOT-     │      │ Production-  │     │ Sandbox-OU  │
  │ TOUCH       │      │ OU           │     │             │
  └─────────────┘      └──────────────┘     └─────────────┘
        
                              │
                    Is it for development/
                         testing?
                              │
                             YES
                              │
                              ▼
                      ┌──────────────────┐
                      │ Non-production-  │
                      │ OU               │
                      └──────────────────┘
                      
                              │
                    Is it for security
                       monitoring?
                              │
                             YES
                              │
                              ▼
                       ┌──────────────┐
                       │ Security-OU  │
                       └──────────────┘
```

---

## SCP Attachment Strategy (Future State)

This shows how SCPs will be applied in later milestones:

```
                        ┌─────────────────┐
                        │      ROOT       │
                        │   (No SCP yet)  │
                        └─────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │ DO-NOT-TOUCH │  │ Non-prod-OU  │  │Production-OU │
      │              │  │              │  │              │
      │ Future SCPs: │  │ Future SCPs: │  │ Future SCPs: │
      │ • Deny all   │  │ • Baseline   │  │ • Baseline   │
      │   except     │  │   security   │  │   security   │
      │   emergency  │  │ • Geo-       │  │ • Geo-       │
      │              │  │   restrict   │  │   restrict   │
      │              │  │              │  │ • Encryption │
      └──────────────┘  └──────────────┘  │   required   │
                                          └──────────────┘
              │                 │
              ▼                 ▼
      ┌──────────────┐  ┌──────────────┐
      │ Sandbox-OU   │  │ Security-OU  │
      │              │  │              │
      │ Future SCPs: │  │ Future SCPs: │
      │ • Baseline   │  │ • Baseline   │
      │   security   │  │   security   │
      │ • Budget     │  │ • Deny       │
      │   limits     │  │   security   │
      │              │  │   tool       │
      │              │  │   disable    │
      └──────────────┘  └──────────────┘
```

---

## OU Naming Convention Breakdown

```
Example OU Name: "Production-OU"
                 └─────┬────┘ └┬┘
                       │        │
                       │        └─── Suffix indicating type (Organizational Unit)
                       │
                       └─────────── Descriptive name indicating purpose
                                   (PascalCase or kebab-case)

All OU Names Follow Pattern:
    [Purpose/Function] + "-" + "OU"

Examples:
    • Security-OU      ✓ (Clear purpose + standard suffix)
    • Production-OU    ✓ (Environment type + standard suffix)
    • DO-NOT-TOUCH     ✓ (Special case - intentionally stands out)
    
Counter-examples (not used):
    • Prod             ✗ (Unclear, no suffix)
    • production_ou    ✗ (Inconsistent separator)
    • OUProduction     ✗ (Suffix in wrong position)
```

---

## OU ID Format Explained

```
OU ID Format: ou-im88-o8bz8kx1
              │  │    │
              │  │    └─── Unique hash (8 characters)
              │  └──────── Organization identifier (4 chars from org ID)
              └─────────── Prefix indicating resource type

Breakdown of Each OU ID:

DO-NOT-TOUCH:       ou-im88-16gred4y
                    ││ ││   ││││││││
                    ││ ││   └───┬───┘
                    ││ ││       └───── Unique identifier: 16gred4y
                    ││ └┴──────────── Org ID portion: im88
                    └┴────────────── Resource type: Organizational Unit

Non-production-OU:  ou-im88-ozx04ihn
                    ││ ││   ││││││││
                    ││ ││   └───┬───┘
                    ││ ││       └───── Unique identifier: ozx04ihn
                    ││ └┴──────────── Org ID portion: im88
                    └┴────────────── Resource type: Organizational Unit

Production-OU:      ou-im88-v1z00uzh
Security-OU:        ou-im88-o8bz8kx1
Sandbox-OU:         ou-im88-1r7by4at

Common Pattern:
    • All start with "ou-"
    • All contain "im88" (from org ID: o-3l9ybracw9)
    • All have 8-character unique hash
    • Total length: 20 characters (ou- + im88- + 8 chars)
```

---

## Growth Projection Diagram

### Current State (Milestone 1)

```
Root
├── DO-NOT-TOUCH         (0 accounts)
├── Non-production-OU    (0 accounts)
├── Production-OU        (0 accounts)
├── Sandbox-OU           (0 accounts)
└── Security-OU          (0 accounts)

Total: 5 OUs, 0 member accounts (management account is separate)
```

### 6 Months from Now (Projected)

```
Root
├── DO-NOT-TOUCH         (2 accounts)
│   ├── Network-Hub-Account
│   └── Shared-Services-Account
│
├── Non-production-OU    (8 accounts)
│   ├── Dev-App-Account-1
│   ├── Dev-App-Account-2
│   ├── Test-Account
│   ├── QA-Account
│   ├── Staging-Account
│   └── ...
│
├── Production-OU        (5 accounts)
│   ├── Prod-App-Account-1
│   ├── Prod-Database-Account
│   ├── Prod-Web-Frontend-Account
│   └── ...
│
├── Sandbox-OU           (15 accounts)
│   ├── User-Sandbox-Alice
│   ├── User-Sandbox-Bob
│   ├── POC-ML-Project
│   └── ...
│
└── Security-OU          (3 accounts)
    ├── Security-Tools-Account (GuardDuty, Security Hub)
    ├── Audit-Logging-Account (CloudTrail aggregation)
    └── Compliance-Account

Total: 5 OUs, ~33 accounts
```

### Scalability Notes

**Current Structure Supports:**
- ✅ Up to 100 accounts comfortably without changes
- ✅ Clear categorization for rapid growth
- ✅ SCP strategy that scales without modification
- ✅ Straightforward account placement logic

**If Growth Exceeds 100 Accounts, Consider:**
- Introducing sub-OUs (e.g., by geography or business unit)
- Using account tags for additional categorization
- Implementing OU naming v2 with region codes
- Reviewing OU consolidation opportunities

---

## Cross-Reference: OU to Documentation

Each OU has associated documentation:

```
DO-NOT-TOUCH
    │
    ├── Created: Milestone 1
    ├── Documentation: MILESTONE-1-COMPLETE-GUIDE.md (Step 9)
    ├── Screenshot: 01-aws-organizations-hierarchy-view.md
    ├── SCP Plans: [Milestone 3] Deny-all except emergency
    └── Account Plans: Network hub, shared services

Non-production-OU
    │
    ├── Created: Milestone 1
    ├── Documentation: MILESTONE-1-COMPLETE-GUIDE.md (Step 7)
    ├── Screenshot: 01-aws-organizations-hierarchy-view.md
    ├── SCP Plans: [Milestone 3] Baseline + geo-restriction
    └── Account Plans: Dev, test, staging environments

Production-OU
    │
    ├── Created: Milestone 1
    ├── Documentation: MILESTONE-1-COMPLETE-GUIDE.md (Step 6)
    ├── Screenshot: 01-aws-organizations-hierarchy-view.md
    ├── SCP Plans: [Milestone 3] Baseline + geo + encryption
    └── Account Plans: Production workloads

Sandbox-OU
    │
    ├── Created: Milestone 1
    ├── Documentation: MILESTONE-1-COMPLETE-GUIDE.md (Step 8)
    ├── Screenshot: 01-aws-organizations-hierarchy-view.md
    ├── SCP Plans: [Milestone 3] Baseline + budget limits
    └── Account Plans: POCs, learning, experimentation

Security-OU
    │
    ├── Created: Milestone 1
    ├── Documentation: MILESTONE-1-COMPLETE-GUIDE.md (Step 5)
    ├── Screenshot: 01-aws-organizations-hierarchy-view.md
    ├── SCP Plans: [Milestone 3] Prevent security tool disable
    └── Account Plans: Security tools, audit, compliance
```

---

## Alternative Hierarchy Patterns (Not Used)

For reference, here are other common patterns organizations use:

### Pattern 1: Geographic Nested OUs (Not Used)

```
Root
├── US-Region-OU
│   ├── US-Production-OU
│   └── US-Non-Production-OU
└── EU-Region-OU
    ├── EU-Production-OU
    └── EU-Non-Production-OU
```

**When to Use:** Multi-national organizations with region-specific compliance

### Pattern 2: Business Unit Nested OUs (Not Used)

```
Root
├── Marketing-BU-OU
│   ├── Marketing-Prod-OU
│   └── Marketing-Dev-OU
├── Engineering-BU-OU
│   ├── Engineering-Prod-OU
│   └── Engineering-Dev-OU
└── Finance-BU-OU
    └── ...
```

**When to Use:** Large enterprises with independent business units

### Pattern 3: Your Flat Structure (✓ Used)

```
Root
├── DO-NOT-TOUCH
├── Non-production-OU
├── Production-OU
├── Sandbox-OU
└── Security-OU
```

**Why This Works Best for You:**
- ✅ Simple to manage
- ✅ Clear purpose separation
- ✅ Easy SCP application
- ✅ Scalable to 100+ accounts
- ✅ Low cognitive overhead

---

## Summary Table: Complete OU Reference

| Attribute | DO-NOT-TOUCH | Non-production-OU | Production-OU | Sandbox-OU | Security-OU |
|-----------|-------------|-------------------|---------------|------------|-------------|
| **OU ID** | ou-im88-16gred4y | ou-im88-ozx04ihn | ou-im88-v1z00uzh | ou-im88-1r7by4at | ou-im88-o8bz8kx1 |
| **Parent** | Root (r-im88) | Root (r-im88) | Root (r-im88) | Root (r-im88) | Root (r-im88) |
| **Hierarchy Level** | 1 | 1 | 1 | 1 | 1 |
| **Purpose** | Critical infrastructure | Dev/test/staging | Production workloads | Experimentation | Security tooling |
| **Access Level** | Emergency only | Developer access | Production access | Open access | Restricted access |
| **Change Control** | Multi-party approval | Moderate | Strict | None | Strict |
| **Typical Account Count** | 1-3 | 5-20 | 3-15 | 10-50 | 2-5 |
| **Compliance Level** | Maximum | Moderate | High | Low | Maximum |
| **SCP Strictness** | Most restrictive | Moderate | Strict | Minimal | Strict |
| **Cost Sensitivity** | Low spend | Medium spend | High spend | Controlled spend | Low spend |
| **Monitoring Level** | Maximum | Standard | Enhanced | Basic | Maximum |

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Visual Type:** ASCII art diagrams, relationship matrices, flow diagrams  
**Purpose:** Visual reference for AWS Organizations structure
