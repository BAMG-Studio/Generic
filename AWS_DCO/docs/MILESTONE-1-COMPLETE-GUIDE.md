# Milestone 1: AWS Organizations - Creation of OUs and Structure

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Learning Objectives](#learning-objectives)
4. [Complete Step-by-Step Guide](#complete-step-by-step-guide)
5. [Verification Steps](#verification-steps)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## Overview

### What is Milestone 1?
**Layman Explanation:**
Milestone 1 is about setting up the basic organizational structure in AWS Organizations. Think of it like creating the filing cabinet system for your company - you're creating different drawers (called Organizational Units or OUs) where you'll later put different types of AWS accounts. Just like you might have file drawers labeled "HR", "Finance", "Operations", this creates digital containers for different purposes like "Production", "Development", "Security", etc.

**Technical Explanation:**
Milestone 1 establishes the foundational organizational hierarchy within AWS Organizations by creating Organizational Units (OUs). This structure enables:
- **Hierarchical account management**: Grouping AWS accounts by function, environment, or business unit
- **Policy inheritance**: SCPs applied at the OU level cascade to all member accounts
- **Logical separation**: Isolating workloads by environment (production vs. non-production) or sensitivity level
- **Scalable governance**: Creating a framework that supports future growth and policy application

### What You'll Build
A complete AWS Organization with the following OU structure:
```
Root (r-im88)
├── DO-NOT-TOUCH
├── Non-production-OU
├── Production-OU
├── Sandbox-OU
└── Security-OU
```

---

## Prerequisites

### Technical Requirements
- ✅ **AWS Account**: You need an AWS account with administrative access
- ✅ **AWS Organizations Enabled**: Your account must be the management account (formerly master account)
- ✅ **IAM Permissions**: You need permissions to create and manage Organizations
  - `organizations:CreateOrganizationalUnit`
  - `organizations:ListRoots`
  - `organizations:DescribeOrganization`
- ✅ **Billing Access**: Access to AWS Console with billing enabled (Organizations is a management service)

### Knowledge Prerequisites
**Beginner Level:**
- Basic understanding of AWS Console navigation
- Familiarity with web browser usage
- Understanding of organizational structures (like company departments)

**Technical Level:**
- Understanding of AWS account structure
- Basic knowledge of IAM (Identity and Access Management)
- Awareness of cloud governance concepts

### Before You Start
1. **Verify Organization Status**: Ensure AWS Organizations is enabled in your account
2. **Document Current State**: If you have existing OUs, document them
3. **Review Naming Conventions**: Understand the OU naming strategy (covered below)
4. **Browser Preparation**: Use a modern browser (Chrome, Firefox, Edge) with JavaScript enabled

---

## Learning Objectives

By the end of this milestone, you will:

### Knowledge Objectives
- ✅ Understand what AWS Organizations is and why it's used
- ✅ Explain the concept of Organizational Units (OUs)
- ✅ Describe the hierarchical structure of AWS Organizations
- ✅ Identify the purpose of each OU in the structure
- ✅ Understand the difference between Root, OUs, and AWS Accounts

### Skill Objectives
- ✅ Navigate to AWS Organizations console from the main AWS Console
- ✅ Create Organizational Units using the AWS Console
- ✅ Organize OUs in a hierarchical structure
- ✅ Verify OU creation and structure
- ✅ Understand OU naming conventions and IDs

### Application Objectives
- ✅ Design an OU structure that supports environment separation
- ✅ Implement a governance-ready organizational hierarchy
- ✅ Prepare the foundation for Service Control Policy (SCP) application
- ✅ Create a scalable organizational structure for future growth

---

## Complete Step-by-Step Guide

### Phase 1: Accessing AWS Organizations Console

#### Step 1: Log into AWS Console

**Layman Instructions:**
1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Go to: `https://console.aws.amazon.com`
3. Enter your AWS account email address
4. Click "Next"
5. Enter your password
6. Click "Sign in"
7. If you have MFA (multi-factor authentication) enabled, enter your MFA code

**Technical Details:**
- You must log in as a user with `organizations:*` permissions or as the root user
- The account you're logging into must be the **management account** of the organization
- If you're using IAM Identity Center (formerly AWS SSO), use your SSO portal URL instead

**What's Happening Behind the Scenes:**
When you log in, AWS authenticates your credentials against IAM (Identity and Access Management), validates your permissions, and establishes a session with temporary security credentials. These credentials are stored in browser cookies for the duration of your session.

---

#### Step 2: Navigate to AWS Organizations Service

**Layman Instructions (Method 1 - Using Search):**
1. Look at the top of the AWS Console page
2. Find the search box (it says "Search" with a magnifying glass icon)
3. Click inside the search box
4. Type: `Organizations`
5. In the dropdown that appears, click on "AWS Organizations" under "Services"

**Layman Instructions (Method 2 - Using Services Menu):**
1. At the top-left of the AWS Console, click the "Services" dropdown (or the grid icon ☰)
2. In the left sidebar, click "Management & Governance"
3. Scroll down and click "AWS Organizations"

**Technical Details:**
- **Service Endpoint**: You're navigating to the Organizations service console at `console.aws.amazon.com/organizations/v2/home`
- **Region Independence**: AWS Organizations is a global service - it's not tied to any specific AWS region
- **API Behind the Console**: The console makes calls to the AWS Organizations API endpoint

**Navigation Evidence in Screenshot:**
In your screenshot, you can see:
- The breadcrumb trail: "AWS Organizations > AWS accounts"
- The left sidebar showing "AWS Organizations" section
- The service is already active (blue highlight on navigation)

**What You Should See:**
- The AWS Organizations dashboard
- Left sidebar with sections: AWS accounts, Invitations, Multi-party approval, Services, Policies, Settings, Get started
- The main panel showing your organizational structure

---

#### Step 3: Understanding the AWS Organizations Console Layout

**Layman Explanation:**
The AWS Organizations console is like a control panel with different sections:

1. **Left Sidebar (Navigation Panel)**: This is your menu of options
   - **AWS accounts**: View and manage all accounts in your organization
   - **Invitations**: Send or respond to invitations to join organizations
   - **Multi-party approval**: Set up approval workflows (advanced feature)
   - **Services**: Enable/disable AWS services across your organization
   - **Policies**: Create and manage rules (SCPs, Tag Policies, etc.)
   - **Settings**: Configure organization-level settings
   - **Get started**: Quick start guides and tutorials

2. **Top Bar**: 
   - Search box to find accounts or OUs quickly
   - "Hierarchy" and "List" view toggles
   - Your account information (top-right)

3. **Main Panel**: 
   - Shows your organizational structure when in "Hierarchy" view
   - Displays the tree of OUs and accounts

**Technical Explanation:**
The Organizations console is a single-page application (SPA) that uses React/JavaScript to render the UI. The layout consists of:

- **Navigation Pane**: Static sidebar for service feature access
- **Content Pane**: Dynamic area that updates based on selected navigation item
- **Toolbar**: Contains search, view options, and action buttons
- **Hierarchy Visualization**: Tree structure rendered using recursive components

**Console Elements Visible in Screenshot:**
- ✅ Top navigation bar with search (`[Alt+S]` keyboard shortcut visible)
- ✅ Breadcrumb: "AWS Organizations > AWS accounts"
- ✅ Left sidebar navigation expanded
- ✅ "Hierarchy" button selected (blue) vs "List" button (gray)
- ✅ Organization ID displayed: `o-3l9ybracw9`
- ✅ Account ID visible in top-right: `0059-6560-5891`
- ✅ Global region selector showing "Global"

---

### Phase 2: Understanding Your Starting Point

#### Step 4: Identify the Root Organization

**Layman Explanation:**
Every AWS Organization has a "Root" - this is the very top of your organizational tree. You can't delete the Root, and you can't create more than one Root. Think of it like the trunk of a tree - everything branches off from here.

In the screenshot, you see:
- **Root** at the top of the hierarchy
- **ID**: `r-im88`

This is automatically created when you enable AWS Organizations.

**Technical Explanation:**
The Root is the top-level container in an AWS Organization's hierarchy. It has specific characteristics:

- **Unique Identifier**: Every Root has an ID format of `r-{random-string}` (e.g., `r-im88`)
- **Automatic Creation**: The Root is created automatically when you create an organization
- **Cannot Be Deleted**: The Root persists as long as the organization exists
- **Policy Attachment Point**: SCPs can be attached directly to Root, affecting all OUs and accounts
- **Organizational Boundary**: All OUs and accounts must exist under the Root

**What the Root ID Tells Us:**
- `r-im88`: The `r-` prefix indicates this is a Root object
- `im88`: This is the unique identifier for your specific organization's root
- The Root ID is immutable and permanent for the lifetime of the organization

**How to View Root Details:**
1. In the Hierarchy view, the Root is always at the top
2. Click on "Root" to see its details in the right panel
3. The Root cannot be renamed or moved

---

### Phase 3: Creating Organizational Units

#### Step 5: Create Your First OU - "Security-OU"

**Pre-Creation Planning:**

**Why "Security-OU"?**
- **Layman**: This OU will hold AWS accounts dedicated to security functions - like your company's security department
- **Technical**: Security-OU will contain accounts for security tools (GuardDuty, Security Hub, CloudTrail aggregation), audit logging, and security monitoring. Isolating security functions in a dedicated OU enables:
  - Restricted access (tighter IAM policies)
  - Specific SCPs that prevent security tool disablement
  - Centralized security visibility
  - Compliance requirement fulfillment (SOC 2, ISO 27001, etc.)

**Click-by-Click Instructions:**

**Step 5.1: Initiate OU Creation**
1. In the Hierarchy view, locate "Root" in the organizational structure
2. Click on "Root" to select it (it should highlight)
3. Look for the "Actions" button (usually top-right of the main panel)
4. Click the "Actions" dropdown button
5. From the dropdown menu, select "Create new" → "Create organizational unit"

**Alternative Method:**
1. Right-click on "Root" in the hierarchy tree
2. Select "Create organizational unit" from the context menu

**What You Should See:**
- A modal dialog box titled "Create organizational unit" will appear
- The dialog will have:
  - A text field labeled "Organizational unit name"
  - Parent OU information showing "Root"
  - "Cancel" and "Create organizational unit" buttons

**Step 5.2: Name the Organizational Unit**
1. In the "Organizational unit name" field, click to activate it
2. Type exactly: `Security-OU`
3. **Important**: Use this exact naming convention:
   - Capital 'S' in Security
   - Hyphen between words (not underscore, not space)
   - Capital 'OU' at the end

**Naming Best Practices:**
- **Layman**: Use descriptive names that clearly indicate the purpose. Avoid abbreviations that others might not understand.
- **Technical**: 
  - Use kebab-case or PascalCase for consistency
  - Suffix with "-OU" to clearly distinguish OUs from account names
  - Avoid special characters that might cause API issues (stick to alphanumeric and hyphens)
  - Maximum length: 128 characters
  - No leading/trailing whitespace

**Step 5.3: Confirm OU Creation**
1. Review the name you entered: `Security-OU`
2. Verify the Parent is "Root"
3. Click the "Create organizational unit" button
4. Wait for the confirmation message (usually 1-3 seconds)

**What Happens Behind the Scenes:**
```
API Call: organizations:CreateOrganizationalUnit
Parameters:
  ParentId: r-im88
  Name: Security-OU
  
Response:
  OrganizationalUnit:
    Id: ou-im88-o8bz8kx1
    Arn: arn:aws:organizations::123456789012:ou/o-3l9ybracw9/ou-im88-o8bz8kx1
    Name: Security-OU
```

The AWS Organizations service:
1. Validates your permissions
2. Checks naming constraints
3. Generates a unique OU ID (format: `ou-{org-id}-{unique-hash}`)
4. Creates the OU object in the organization's directory
5. Returns the OU details

**Verification:**
- You should see "Security-OU" appear in the hierarchy tree under Root
- Next to it, you'll see the OU ID: `ou-im88-o8bz8kx1`
- The OU will have a folder icon next to its name
- It will be collapsible (has an arrow/chevron icon)

---

#### Step 6: Create "Production-OU"

**Why "Production-OU"?**
- **Layman**: This is where you'll put AWS accounts that run your live, customer-facing systems - like the actual store that customers shop in (not the warehouse or testing area)
- **Technical**: Production-OU houses accounts running production workloads that serve end-users. Characteristics:
  - Requires strictest change management
  - Subject to the most restrictive SCPs
  - Typically has higher compliance requirements
  - Separate from development/testing to prevent accidental production impact
  - Often has additional monitoring, backup, and disaster recovery requirements

**Click-by-Click Instructions:**

Repeat the process from Step 5, but with the name "Production-OU":

1. Click on "Root" in the hierarchy (to ensure it's selected as the parent)
2. Click "Actions" → "Create new" → "Create organizational unit"
3. In the name field, type: `Production-OU`
4. Click "Create organizational unit"
5. Verify "Production-OU" appears under Root with ID `ou-im88-v1z00uzh`

**Pro Tip:**
You can create multiple OUs in succession. The console will keep the Root selected, so you can repeat the process quickly.

---

#### Step 7: Create "Non-production-OU"

**Why "Non-production-OU"?**
- **Layman**: This is for testing, development, and experimentation - like a workshop where you build and test things before they go into the store
- **Technical**: Non-production-OU contains development, testing, QA, and staging environments. Benefits:
  - More relaxed SCPs (developers need more freedom to experiment)
  - Cost optimization opportunities (can use spot instances, shut down during off-hours)
  - Safe experimentation without production impact
  - Typically mirrors production architecture but with less stringent requirements

**Click-by-Click Instructions:**

1. Ensure "Root" is selected
2. Click "Actions" → "Create new" → "Create organizational unit"
3. Type: `Non-production-OU`
4. Click "Create organizational unit"
5. Verify creation with ID `ou-im88-ozx04ihn`

**Common Naming Alternatives:**
- Some organizations use: `Development-OU`, `Dev-OU`, `NonProd-OU`, `Testing-OU`
- Choose a convention and stick with it across your organization

---

#### Step 8: Create "Sandbox-OU"

**Why "Sandbox-OU"?**
- **Layman**: A sandbox is a safe play area for children. Similarly, this OU is for completely unrestricted experimentation - like a lab where people can try new things without any rules, knowing nothing here will affect real systems
- **Technical**: Sandbox-OU provides isolated environments for:
  - Proof-of-concept work
  - Learning and training
  - Third-party tool evaluation
  - Service limit testing
  - Generally has the most permissive SCPs (or none at all)
  - Accounts here should never contain production data
  - Often has automatic cleanup policies or spending limits

**Click-by-Click Instructions:**

1. Select "Root"
2. Click "Actions" → "Create new" → "Create organizational unit"
3. Type: `Sandbox-OU`
4. Click "Create organizational unit"
5. Verify creation with ID `ou-im88-1r7by4at`

**Security Note:**
Even though Sandbox is for experimentation, you should still:
- Set billing alerts/budgets to prevent runaway costs
- Require MFA for access
- Prohibit storage of production data
- Consider time-limited access

---

#### Step 9: Create "DO-NOT-TOUCH"

**Why "DO-NOT-TOUCH"?**
- **Layman**: This is like a locked cabinet in an office - you keep critical things here that nobody should mess with unless absolutely necessary. It's clearly labeled so people know to stay away.
- **Technical**: The DO-NOT-TOUCH OU serves special purposes:
  - Houses the management account itself
  - Contains critical shared services accounts (e.g., Transit Gateway, Networking hub)
  - May contain break-glass emergency access accounts
  - Subject to the most restrictive SCPs to prevent accidental modification
  - Often requires multi-party approval for any changes
  - Clear naming prevents accidental modifications

**Click-by-Click Instructions:**

1. Select "Root"
2. Click "Actions" → "Create new" → "Create organizational unit"
3. Type: `DO-NOT-TOUCH`
   - Note: All caps, with hyphens between words
   - This unconventional naming is intentional - it grabs attention
4. Click "Create organizational unit"
5. Verify creation with ID `ou-im88-16gred4y`

**Why All Caps?**
The all-caps naming convention is a visual safety mechanism. It:
- Immediately draws attention
- Signals "proceed with extreme caution"
- Differentiates it from standard OUs
- Makes it stand out in logs, reports, and console views

**Alternative Names You Might See:**
- `Critical-Infrastructure-OU`
- `Protected-OU`
- `Management-OU`
- `Core-Infrastructure-OU`

The key is making it obviously special.

---

### Phase 4: Verification and Validation

#### Step 10: Verify All OUs Are Created

**Visual Verification Checklist:**

Look at your hierarchy view (as shown in the screenshot) and confirm you see:

```
✅ Root (r-im88)
   ✅ DO-NOT-TOUCH (ou-im88-16gred4y)
   ✅ Non-production-OU (ou-im88-ozx04ihn)
   ✅ Production-OU (ou-im88-v1z00uzh)
   ✅ Sandbox-OU (ou-im88-1r7by4at)
   ✅ Security-OU (ou-im88-o8bz8kx1)
```

**Detailed Verification Steps:**

**Visual Check:**
1. Count the OUs under Root - you should have exactly 5
2. Verify each OU name is spelled correctly
3. Confirm each OU has a unique ID starting with `ou-`
4. Check that all OUs are at the same hierarchical level (all are direct children of Root)

**Interactive Verification:**
1. Click on each OU one by one
2. In the right panel (or details pane), verify:
   - OU Name matches what you created
   - Parent ID is the Root ID (`r-im88`)
   - No accounts are attached yet (Account count: 0)

**Technical Verification via Console:**

**Method 1: Using List View**
1. Click the "List" button (next to "Hierarchy" at the top)
2. You should see a table listing all OUs
3. Verify the columns show:
   - Name
   - Type (should say "Organizational Unit")
   - ID
   - Parent (should all say "Root")

**Method 2: Using Search**
1. Click in the search box at the top
2. Type: `OU`
3. The search should filter to show only OUs
4. Count that all 5 appear

**What Each ID Tells Us:**

The OU ID format is: `ou-{organization-id}-{unique-hash}`

Example: `ou-im88-o8bz8kx1`
- `ou-`: Prefix indicating this is an Organizational Unit
- `im88`: Your organization's unique identifier (from org ID `o-3l9ybracw9`)
- `o8bz8kx1`: Unique hash for this specific OU

These IDs are:
- Globally unique across all AWS Organizations
- Immutable (never change, even if you rename the OU)
- Used in API calls, SCPs, and CloudFormation templates
- Important for audit trails and logging

---

#### Step 11: Understanding the Organizational Hierarchy

**Layman Explanation:**

Your organization now looks like this structure:

```
Your Company (Root)
├── DO-NOT-TOUCH (Critical systems - nobody touches!)
├── Non-production-OU (Test kitchen - try recipes here)
├── Production-OU (The restaurant - customers eat here)
├── Sandbox-OU (Playground - experiment freely)
└── Security-OU (Security office - monitors everything)
```

Think of it like organizing a company:
- The **Root** is the company itself (e.g., "Acme Corporation")
- Each **OU** is a department or division
- Later, you'll put **AWS Accounts** into these OUs (like employees in departments)
- You'll apply **rules (SCPs)** at the OU level that apply to all accounts in that OU

**Technical Explanation:**

This is a **flat organizational hierarchy** - all OUs are at the same level, directly under Root. This design choice has implications:

**Advantages of Flat Hierarchy:**
- Simple to understand and manage
- Clear delineation of purposes
- Easy to apply SCPs (less inheritance complexity)
- Straightforward account placement logic
- Reduced risk of misconfiguration

**Alternative: Nested Hierarchy**
Some organizations use nested OUs:
```
Root
├── Production-OU
│   ├── Prod-US-East-OU
│   └── Prod-EU-West-OU
├── Non-Production-OU
│   ├── Development-OU
│   └── Testing-OU
```

**When to Use Nested vs Flat:**
- **Flat** (what you've built): Best for smaller organizations, simple governance models, clear separation of concerns
- **Nested**: Best for large enterprises, geographic separation, complex compliance requirements, or when you need granular policy application

**Policy Inheritance in Your Structure:**
```
Root (can have SCP)
├── DO-NOT-TOUCH (can have SCP) → inherits Root SCP
├── Non-production-OU (can have SCP) → inherits Root SCP
├── Production-OU (can have SCP) → inherits Root SCP
├── Sandbox-OU (can have SCP) → inherits Root SCP
└── Security-OU (can have SCP) → inherits Root SCP
```

Any SCP attached to Root will apply to ALL OUs and their accounts. SCPs at the OU level add additional restrictions (SCPs can only deny, not allow).

---

### Phase 5: Understanding What You've Built

#### Step 12: Document Your Organizational Structure

**Why Documentation Matters:**

**Layman Reason:**
Imagine giving someone directions to rooms in a building. If you don't write down which room is which, people will get lost. Similarly, as your AWS organization grows, you need clear documentation so everyone knows which accounts go where and why.

**Technical Reason:**
Proper documentation enables:
- Onboarding new team members
- Compliance audits (auditors need to understand your structure)
- Disaster recovery (knowing what goes where)
- Change management (understanding impact of changes)
- Knowledge transfer (preventing single points of failure)

**What to Document:**

Create a document (you're building this now!) that includes:

1. **OU Purpose Table**

| OU Name | Purpose | Intended Accounts | SCP Strategy | Access Level |
|---------|---------|-------------------|--------------|--------------|
| Security-OU | Security and compliance tools | - Security Hub account<br>- GuardDuty master<br>- CloudTrail logs<br>- Audit/compliance | Strictest SCPs preventing security tool disablement | Highly restricted |
| Production-OU | Live customer-facing systems | - Production app accounts<br>- Production data stores<br>- Customer-facing APIs | Restrictive SCPs, require change management | Production access only |
| Non-production-OU | Development, testing, staging | - Dev environments<br>- QA/test accounts<br>- Staging replicas | Moderate SCPs, allow broader experimentation | Developer access |
| Sandbox-OU | Learning, POCs, experiments | - Training accounts<br>- POC accounts<br>- Personal learning | Minimal/no SCPs, maximum freedom | Open access with cost limits |
| DO-NOT-TOUCH | Critical infrastructure | - Management account<br>- Network hub (Transit GW)<br>- Break-glass accounts | Extremely restrictive, multi-party approval | Emergency access only |

2. **OU Hierarchy Diagram** (see your screenshot - this is your visual reference!)

3. **OU ID Reference**
```
Root: r-im88
├── DO-NOT-TOUCH: ou-im88-16gred4y
├── Non-production-OU: ou-im88-ozx04ihn
├── Production-OU: ou-im88-v1z00uzh
├── Sandbox-OU: ou-im88-1r7by4at
└── Security-OU: ou-im88-o8bz8kx1
```

4. **Decision Log**
Document why you made specific choices:
- Why these 5 OUs? (Environment separation, security isolation, safe experimentation)
- Why flat hierarchy? (Simplicity, clear boundaries, straightforward governance)
- Why these specific names? (Self-documenting, industry-standard patterns)

---

#### Step 13: Understanding OU Attributes and Metadata

**What Information Is Stored for Each OU?**

When you create an OU, AWS stores several attributes:

**Core Attributes:**
1. **Name**: The human-readable identifier (e.g., "Security-OU")
   - Mutable: Can be changed later
   - Constraints: 1-128 characters, no leading/trailing whitespace
   - Used in: Console display, reports, documentation

2. **ID**: The unique identifier (e.g., "ou-im88-o8bz8kx1")
   - Immutable: Never changes
   - Format: `ou-{org-id}-{unique-hash}`
   - Used in: API calls, SCPs, CloudFormation, automation

3. **ARN**: Amazon Resource Name
   - Format: `arn:aws:organizations::{management-account-id}:ou/{org-id}/{ou-id}`
   - Example: `arn:aws:organizations::005965605891:ou/o-3l9ybracw9/ou-im88-o8bz8kx1`
   - Used in: IAM policies, resource-based policies, cross-service integrations

4. **Parent ID**: The OU or Root that contains this OU
   - For all your OUs: `r-im88` (the Root)
   - Used in: Hierarchy traversal, determining policy inheritance

**Metadata:**
- Creation timestamp
- Last modified timestamp
- Creator principal (who created it)

**Viewable in Console:**
Click on any OU in the hierarchy to see its details panel showing these attributes.

---

## Verification Steps

### Manual Console Verification

**Comprehensive Checklist:**

- [ ] **Login Verification**
  - Logged into correct AWS account (management account)
  - Console shows correct account ID: `0059-6560-5891`
  - Region shows "Global" for Organizations service

- [ ] **Navigation Verification**
  - Successfully reached AWS Organizations console
  - Left sidebar shows "AWS Organizations" section
  - Breadcrumb shows "AWS Organizations > AWS accounts"

- [ ] **Hierarchy Verification**
  - "Hierarchy" view is active (button is blue/selected)
  - Root displays with ID `r-im88`
  - Exactly 5 OUs appear under Root

- [ ] **OU Creation Verification**
  - ✅ DO-NOT-TOUCH created (ou-im88-16gred4y)
  - ✅ Non-production-OU created (ou-im88-ozx04ihn)
  - ✅ Production-OU created (ou-im88-v1z00uzh)
  - ✅ Sandbox-OU created (ou-im88-1r7by4at)
  - ✅ Security-OU created (ou-im88-o8bz8kx1)

- [ ] **OU Structure Verification**
  - All OUs are direct children of Root (flat hierarchy)
  - No OUs are nested under other OUs
  - No duplicate OU names
  - All OU names follow naming convention

- [ ] **OU Details Verification**
  - Each OU shows unique OU ID
  - Each OU shows Parent as "Root" (r-im88)
  - Each OU shows 0 accounts (none moved yet)
  - Each OU is expandable (has arrow/chevron icon)

### Using AWS CLI for Verification

If you want to verify via command line:

```bash
# List all OUs under Root
aws organizations list-organizational-units-for-parent \
  --parent-id r-im88

# Expected output: JSON array with 5 OUs

# Describe a specific OU
aws organizations describe-organizational-unit \
  --organizational-unit-id ou-im88-o8bz8kx1

# List all roots in organization
aws organizations list-roots
```

### Using AWS CloudShell

**Layman: What is CloudShell?**
CloudShell is like having a terminal/command prompt built into your AWS Console. You can type commands instead of clicking buttons.

**How to Access:**
1. In the AWS Console, look for the CloudShell icon (terminal/command prompt icon) in the top toolbar
2. Click it - a terminal window opens at the bottom of your screen
3. You can now run AWS CLI commands without installing anything

**Verification Commands:**
```bash
# See your organization details
aws organizations describe-organization

# List all OUs
aws organizations list-organizational-units-for-parent --parent-id r-im88 \
  --query 'OrganizationalUnits[*].[Name,Id]' --output table
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Access Denied" When Creating OUs

**Symptoms:**
- Error message: "You don't have permission to perform this operation"
- Console shows error banner when trying to create OU

**Causes:**
- You're not logged in as a user with sufficient permissions
- You're not in the management account
- Organizations service is not enabled

**Solutions:**

**Layman Solution:**
1. Make sure you're logged into the correct AWS account (the one that created the organization)
2. Ask your administrator for permissions to manage Organizations
3. Try logging out and back in

**Technical Solution:**
1. Verify IAM permissions - you need:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "organizations:CreateOrganizationalUnit",
       "organizations:DescribeOrganization",
       "organizations:ListRoots"
     ],
     "Resource": "*"
   }
   ```

2. Confirm you're in the management account:
   ```bash
   aws organizations describe-organization
   ```
   Look for: `"MasterAccountId"` should match your current account

3. Check if Organizations is enabled:
   - Go to Organizations console
   - If you see "Create organization" button, Organizations isn't enabled yet

---

#### Issue 2: OU Not Appearing in Hierarchy

**Symptoms:**
- Created OU but don't see it in the tree
- Success message appeared but OU is missing

**Solutions:**

**Layman Solution:**
1. Refresh your browser page (F5 or Ctrl+R)
2. Wait 30 seconds - sometimes there's a delay
3. Make sure you're looking in the right place (under Root, not under another OU)
4. Try switching between "Hierarchy" and "List" views

**Technical Solution:**
1. Check browser console for JavaScript errors (F12 → Console tab)
2. Clear browser cache and cookies for AWS Console
3. Verify OU was actually created using CLI:
   ```bash
   aws organizations list-organizational-units-for-parent --parent-id r-im88
   ```
4. Check for eventual consistency issues - wait 60 seconds and retry

---

#### Issue 3: Cannot Create OU With Desired Name

**Symptoms:**
- Error: "An organizational unit with that name already exists"
- Name validation error

**Causes:**
- Duplicate name at the same hierarchical level
- Name contains invalid characters
- Name has leading/trailing spaces

**Solutions:**

**Layman Solution:**
1. Check if an OU with that exact name already exists under Root
2. Try a slightly different name (add a number or modifier)
3. Make sure you didn't accidentally add spaces before or after the name

**Technical Solution:**
1. OU names must be unique among siblings (OUs at the same level)
2. Valid characters: a-z, A-Z, 0-9, space, hyphen, underscore, period
3. Trim whitespace:
   - ✗ `" Security-OU"` (leading space)
   - ✓ `"Security-OU"` (no spaces)

4. Query existing names:
   ```bash
   aws organizations list-organizational-units-for-parent \
     --parent-id r-im88 \
     --query 'OrganizationalUnits[*].Name'
   ```

---

#### Issue 4: Wrong Parent for OU

**Symptoms:**
- Created OU under wrong parent
- OU appears in wrong place in hierarchy

**Solutions:**

**Layman Solution:**
- You cannot move an OU after creation through the console easily
- Best approach: Delete the OU (if it has no accounts) and recreate it under the correct parent

**How to Delete an OU:**
1. Make sure the OU has no accounts in it
2. Make sure no SCPs are attached to it
3. Click on the OU
4. Click "Actions" → "Delete"
5. Confirm deletion

**Technical Solution:**
- Use AWS CLI to move the OU:
  ```bash
  # This requires the OU to be empty (no child OUs or accounts)
  aws organizations move-organizational-unit \
    --organizational-unit-id ou-xxxx-xxxxxxxx \
    --source-parent-id r-im88 \
    --destination-parent-id ou-yyyy-yyyyyyyy
  ```

**Prevention:**
- Always verify the selected parent before clicking "Create"
- Double-check the "Parent OU" field in the creation dialog

---

#### Issue 5: Hit OU Limit

**Symptoms:**
- Error: "You have reached the maximum number of organizational units"
- Cannot create additional OUs

**Causes:**
- Default quota: 1000 OUs per organization
- If you hit this, you likely have a design issue (too granular)

**Solutions:**

**Layman Solution:**
- Review your OU structure - you probably have too many OUs
- Consider consolidating similar OUs
- Contact AWS Support to request a quota increase if truly needed

**Technical Solution:**
1. Check current OU count:
   ```bash
   aws organizations list-organizational-units-for-parent \
     --parent-id r-im88 \
     --query 'length(OrganizationalUnits)'
   ```

2. Request quota increase:
   - Go to Service Quotas console
   - Search for "Organizations"
   - Request increase for "Organizational units"

3. Redesign consideration:
   - If you need more than 1000 OUs, you might be using OUs where tags would be better
   - Consider using account tags for additional categorization

---

## Next Steps

### What Happens After Milestone 1?

**Layman Overview:**
Now that you've built the structure (the filing cabinet), the next steps are:
1. **Put accounts into the OUs** (put files in the folders)
2. **Create security rules** (decide what people can and can't do in each folder)
3. **Test the rules** (make sure the security works)

**Technical Roadmap:**

#### Milestone 2: Account Management and Organization
- Move existing AWS accounts into appropriate OUs
- Create new AWS accounts as needed for each environment
- Set up account naming standards and tagging strategies
- Document account ownership and purposes

**Preparation:**
- Inventory existing AWS accounts
- Determine which OU each account belongs in
- Plan for new account creation if needed
- Review account naming conventions

#### Milestone 3: Service Control Policy (SCP) Implementation
- Export baseline security SCP JSON
- Create SCPs in AWS Organizations
- Attach baseline SCP to Security, Production, Non-Prod, and Sandbox OUs
- Create and attach geo-restriction SCPs
- Create and attach encryption enforcement SCPs

**Reference Your Earlier Milestone List:**
From your project documentation:
1. ✅ Export baseline SCP JSON → `baseline-security-protection.json`
2. Create SCP in AWS Organizations
3. Attach to OUs (Security-OU, Production-OU, Non-production-OU, Sandbox-OU)
4. Add geo-restriction and encryption SCPs
5. Run three SCP enforcement tests
6. Capture screenshots
7. Update documentation (README.md and notes.md)

#### Milestone 4: Testing and Validation
- Test that SCPs prevent prohibited actions
- Verify geo-restrictions work as intended
- Confirm encryption requirements are enforced
- Document test results

#### Milestone 5: Ongoing Governance
- Set up AWS CloudTrail for Organizations
- Enable AWS Config for compliance monitoring
- Configure SCPs for ongoing governance
- Establish change management processes

---

### Immediate Next Actions

**What You Should Do Right Now:**

1. **Take a Screenshot (You Already Did This!)**
   - ✅ Your screenshot shows the completed OU structure
   - This is your proof of completion for Milestone 1

2. **Document What You Built**
   - ✅ You're reading this document - it captures the knowledge
   - Save this guide for reference
   - Share with team members who need to understand the structure

3. **Prepare for Account Placement**
   - List all AWS accounts you currently have
   - Decide which OU each account should go into
   - Plan any new accounts you need to create

4. **Review SCP Strategy**
   - Read up on Service Control Policies
   - Understand the difference between IAM policies and SCPs
   - Review the baseline SCP you'll implement in Milestone 2

5. **Update Your Project Tracker**
   - Mark Milestone 1 as complete
   - Update your notes.md file with completion status
   - Add any lessons learned or questions that came up

---

### Quick Reference: What You Accomplished

**Layman Summary:**
You've successfully set up the organizational structure for your AWS environment. You now have five distinct areas where different types of AWS accounts will live, each serving a specific purpose. This is the foundation for everything else you'll do with AWS Organizations.

**Technical Summary:**
✅ **Milestone 1 Complete**: AWS Organizations Hierarchy Established

**Deliverables Created:**
- ✅ Root organization confirmed (r-im88)
- ✅ 5 Organizational Units created in flat hierarchy
- ✅ DO-NOT-TOUCH OU (ou-im88-16gred4y) - Critical infrastructure
- ✅ Non-production-OU (ou-im88-ozx04ihn) - Dev/test environments
- ✅ Production-OU (ou-im88-v1z00uzh) - Production workloads
- ✅ Sandbox-OU (ou-im88-1r7by4at) - Experimentation
- ✅ Security-OU (ou-im88-o8bz8kx1) - Security tooling

**Architecture Decisions:**
- ✅ Flat hierarchy (all OUs under Root) for simplicity
- ✅ Purpose-based OU segmentation (by environment and function)
- ✅ Clear naming conventions for self-documentation
- ✅ Special-purpose OU (DO-NOT-TOUCH) for critical infrastructure

**Technical Specifications:**
- Organization ID: o-3l9ybracw9
- Root ID: r-im88
- Management Account: 0059-6560-5891
- Region: Global (Organizations is region-independent)
- OU Count: 5
- Hierarchy Depth: 1 level (flat structure)

**Skills Demonstrated:**
- ✅ AWS Console navigation
- ✅ AWS Organizations service usage
- ✅ Organizational Unit creation
- ✅ Hierarchical structure design
- ✅ Cloud governance foundation setup

**Readiness for Next Milestone:**
- ✅ OU structure is in place
- ✅ Ready for account placement
- ✅ Prepared for SCP attachment
- ✅ Foundation set for policy inheritance

---

## Additional Resources

### AWS Documentation
- [AWS Organizations User Guide](https://docs.aws.amazon.com/organizations/latest/userguide/)
- [Best Practices for Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices.html)
- [OU Design Patterns](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html)

### Learning Resources
- AWS Skill Builder: AWS Organizations Course
- AWS Workshops: Multi-Account Strategy
- AWS Prescriptive Guidance: OU Structure Patterns

### Tools
- AWS Organizations Console
- AWS CLI Organizations Commands
- AWS CloudFormation for Organizations (infrastructure as code)

---

## Glossary

**For Beginners:**

- **AWS Organizations**: A service that lets you group multiple AWS accounts together and manage them centrally
- **Organizational Unit (OU)**: A container that groups AWS accounts together - like a folder for organizing files
- **Root**: The top-level container in AWS Organizations - everything else goes inside this
- **Service Control Policy (SCP)**: Rules that limit what actions can be performed in AWS accounts - like parental controls
- **Management Account**: The AWS account that owns and controls the organization - previously called "Master Account"

**Technical Terms:**

- **OU ID**: Unique identifier for an OU (format: `ou-{org-id}-{hash}`)
- **ARN**: Amazon Resource Name - standardized way to identify AWS resources
- **Flat Hierarchy**: Organizational structure where all OUs are at the same level (vs nested/tree structure)
- **Policy Inheritance**: SCPs attached to parent OUs automatically apply to child OUs and accounts
- **Multi-Account Strategy**: Design pattern of using multiple AWS accounts for isolation and governance

---

## Conclusion

Congratulations! You've successfully completed Milestone 1 of your AWS Organizations implementation. You've built a solid, governance-ready organizational structure that will serve as the foundation for implementing comprehensive security controls through Service Control Policies.

**Key Takeaways:**
1. AWS Organizations provides hierarchical account management
2. OUs are logical containers that group accounts by purpose/environment
3. Proper OU design is critical for effective governance
4. Your flat hierarchy with 5 purpose-driven OUs follows industry best practices
5. This structure is now ready for account placement and SCP application

**What Makes This Structure Effective:**
- ✅ Clear separation of concerns (production vs. non-production)
- ✅ Security isolation (dedicated Security-OU)
- ✅ Safe experimentation space (Sandbox-OU)
- ✅ Protected critical infrastructure (DO-NOT-TOUCH)
- ✅ Scalable design (can grow with your organization)

Keep this guide handy as you proceed to the next milestones. The concepts and patterns you've learned here will apply throughout your AWS Organizations journey.

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Milestone:** 1 - AWS Organizations OU Structure Creation  
**Status:** ✅ Complete
