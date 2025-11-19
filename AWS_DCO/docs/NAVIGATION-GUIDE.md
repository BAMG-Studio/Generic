# AWS Organizations Navigation Guide

## Quick Navigation Reference

This guide provides multiple paths to reach the AWS Organizations console from the main AWS Console.

---

## Method 1: Using the Search Box (Fastest - 5 seconds)

### Step-by-Step Instructions

**Starting Point:** AWS Console Home Page

1. **Locate the Search Box**
   - Look at the very top of the AWS Console
   - Find the search bar (has a magnifying glass 🔍 icon)
   - You'll see placeholder text: "Search"
   - Keyboard shortcut visible: `[Alt+S]`

2. **Activate Search**
   - **Mouse**: Click inside the search box
   - **Keyboard**: Press `Alt+S` (or `Option+S` on Mac)

3. **Type Your Search**
   - Type: `organizations` (lowercase is fine)
   - As you type, a dropdown menu appears

4. **Select the Service**
   - Look for the "Services" section in the dropdown
   - Find "AWS Organizations" with the Organizations icon
   - Click on "AWS Organizations"

5. **Arrival**
   - The AWS Organizations console loads
   - You'll see the "AWS accounts" page by default
   - Breadcrumb confirms: "AWS Organizations > AWS accounts"

**Time Required:** ~5 seconds  
**Clicks Required:** 2 clicks  
**Best For:** Experienced users who know the service name

---

## Method 2: Using the Services Menu (Traditional - 10-15 seconds)

### Step-by-Step Instructions

**Starting Point:** AWS Console Home Page

1. **Open the Services Menu**
   - **Option A**: Click the hamburger menu icon (☰) at the top-left
   - **Option B**: Click "Services" in the top navigation bar
   - A sidebar or dropdown appears

2. **Navigate to Category**
   - Scroll through the category list
   - Find "Management & Governance" category
   - Click on "Management & Governance"

3. **Find AWS Organizations**
   - Within the Management & Governance section
   - Services are listed alphabetically
   - Scroll to find "AWS Organizations"
   - Click on "AWS Organizations"

4. **Arrival**
   - AWS Organizations console opens
   - Default view: "AWS accounts" page

**Time Required:** ~10-15 seconds  
**Clicks Required:** 3 clicks  
**Best For:** First-time users exploring AWS services, learning where services are categorized

---

## Method 3: Using Favorites/Recently Visited (2 seconds)

### Setting Up Favorites

1. **Add to Favorites**
   - When on the AWS Organizations page
   - Look for the star icon (⭐) near the service name
   - Click the star to add to favorites
   - The star fills in (becomes solid)

2. **Access via Favorites**
   - Click the hamburger menu (☰)
   - "Favorites" section appears at the top
   - "AWS Organizations" is listed
   - Click to open

### Recently Visited Services

- After visiting AWS Organizations once:
  - It appears in your "Recently visited" list
  - Found in the hamburger menu (☰) under "Recently visited"
  - Click to quickly navigate back

**Time Required:** ~2 seconds  
**Clicks Required:** 2 clicks  
**Best For:** Regular users who frequently access Organizations

---

## Method 4: Direct URL (Instant)

### URL Formats

**Console URL:**
```
https://console.aws.amazon.com/organizations/v2/home
```

**Deep Link to AWS Accounts:**
```
https://console.aws.amazon.com/organizations/v2/home/accounts
```

**Deep Link to Policies:**
```
https://console.aws.amazon.com/organizations/v2/home/policies
```

### Usage Instructions

1. **Bookmark the URL**
   - Copy the Organizations console URL
   - Add to browser bookmarks
   - Name it clearly: "AWS Organizations Console"

2. **Create Browser Shortcuts**
   - Chrome/Edge: Drag URL to bookmarks bar
   - Firefox: Star icon → Choose folder → Done

3. **Direct Navigation**
   - Paste URL in browser address bar
   - Press Enter
   - (You must be logged into AWS Console first)

**Time Required:** Instant  
**Clicks Required:** 0 (if logged in)  
**Best For:** Power users, automation scripts, saved workflows

---

## Method 5: AWS CloudShell Quick Command

### For Technical Users

If you're in AWS CloudShell or have AWS CLI configured:

```bash
# Open Organizations console in browser (macOS/Linux)
open "https://console.aws.amazon.com/organizations/v2/home"

# Windows
start "https://console.aws.amazon.com/organizations/v2/home"

# Or use AWS CLI to verify you can access Organizations
aws organizations describe-organization
```

---

## Console Layout Reference

### What You See Upon Arrival

```
┌─────────────────────────────────────────────────────────────┐
│ AWS Console Top Bar                                         │
│  [☰] [AWS Logo] [Search: Alt+S] ... [Account ID] [Region]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AWS Organizations > AWS accounts          [Hierarchy][List]│
│                                                             │
│  ┌──────────────┐  ┌───────────────────────────────────┐  │
│  │              │  │                                     │  │
│  │ Left Sidebar │  │      Main Content Area             │  │
│  │              │  │                                     │  │
│  │ - AWS accounts  │  [Organizational structure displayed] │
│  │ - Invitations   │                                     │  │
│  │ - Multi-party   │                                     │  │
│  │ - Services      │                                     │  │
│  │ - Policies      │                                     │  │
│  │ - Settings      │                                     │  │
│  │ - Get started   │                                     │  │
│  │                │  │                                     │  │
│  └──────────────┘  └───────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements Visible

**Top Navigation Bar:**
- AWS logo (home button)
- Search box with `[Alt+S]` shortcut
- Help icon (?)
- Notifications bell icon
- Settings gear icon
- Region selector (shows "Global" for Organizations)
- Account ID and user info

**Breadcrumb Trail:**
- Shows current location: "AWS Organizations > AWS accounts"
- Click any part to navigate up the hierarchy

**Left Sidebar Sections:**
1. **AWS accounts** ← Default landing page
2. **Invitations** - Manage organization invitations
3. **Multi-party approval** - Configure approval workflows
4. **Services** - Enable AWS services across organization
5. **Policies** - Manage SCPs, tag policies, etc.
6. **Settings** - Organization-wide settings
7. **Get started** - Tutorials and quick starts

**Main Content Area:**
- Displays based on left sidebar selection
- For "AWS accounts": Shows organizational hierarchy
- Toggle between "Hierarchy" view and "List" view
- Search box to filter accounts/OUs

**Bottom of Sidebar:**
- **Organization ID**: `o-3l9ybracw9` (example from screenshot)
- Useful for API calls and support tickets

---

## Navigation Verification Checklist

Use this checklist to confirm you've reached the correct page:

- [ ] Service name shows "AWS Organizations" in breadcrumb
- [ ] Left sidebar shows Organizations-specific menu items
- [ ] Organization ID is displayed (format: `o-xxxxxxxxx`)
- [ ] Region shows "Global" (Organizations is not region-specific)
- [ ] "Hierarchy" or "List" view toggle is visible
- [ ] Root organizational unit is visible in structure

If all items are checked, you're in the right place!

---

## Troubleshooting Navigation Issues

### Issue: "Service is not available in this region"

**Cause:** AWS Organizations is a global service  
**Solution:** Ignore region selector - Organizations works from any region view

### Issue: Search doesn't show Organizations

**Possible Causes:**
1. Typing error - try "org" or "organization"
2. Service not available to your account type
3. Browser cache issue

**Solutions:**
1. Clear search and retype
2. Try Method 2 (Services menu) instead
3. Clear browser cache (Ctrl+Shift+Delete)

### Issue: Organizations console shows "Create an organization"

**Meaning:** Organizations is not yet enabled  
**Action:** 
- This is normal for new AWS accounts
- Click "Create organization" to set up Organizations
- Follow the setup wizard

### Issue: Access Denied / Permission Error

**Cause:** Insufficient IAM permissions  
**Required Permissions:**
- `organizations:DescribeOrganization`
- `organizations:ListRoots`
- Must be in management account

**Solution:**
- Contact your AWS administrator
- Request Organizations read access
- Verify you're in the correct AWS account

---

## Region Considerations

### Why Organizations Shows "Global"

**Layman Explanation:**
Unlike EC2 or S3 which exist in specific regions (like us-east-1 or eu-west-1), AWS Organizations manages your entire AWS organization across all regions. That's why you see "Global" in the region selector.

**Technical Explanation:**
- AWS Organizations is a **global service** with a single control plane
- Organizational structure, OUs, and SCPs are **region-independent**
- The Organizations API endpoint is global: `organizations.us-east-1.amazonaws.com`
- While the API endpoint uses us-east-1, the service itself is globally replicated
- Changes to organization structure are eventually consistent across all regions

### What This Means for You

- You can access Organizations from any region view in the console
- The region selector doesn't affect Organizations functionality
- OUs and SCPs apply globally to all regions by default
- If you want region-specific controls, use SCP conditions (covered in later milestones)

---

## Keyboard Shortcuts

Speed up your navigation with these shortcuts:

| Shortcut | Action | Context |
|----------|--------|---------|
| `Alt+S` (Win/Linux) | Open search box | Any AWS Console page |
| `Option+S` (Mac) | Open search box | Any AWS Console page |
| `Ctrl+K` | Open command palette | Modern AWS Console |
| `?` | Show help | Any AWS Console page |
| `Esc` | Close dropdown/modal | When dropdown is open |

---

## Mobile App Navigation

### AWS Console Mobile App

**Available On:**
- iOS (App Store)
- Android (Google Play)

**To Access Organizations:**
1. Open AWS Console app
2. Log in with your credentials
3. Tap the menu icon (☰)
4. Scroll to "Management & Governance"
5. Tap "AWS Organizations"

**Note:** Mobile app has limited Organizations functionality
- View organizational structure: ✅
- Create OUs: ❌ (use web console)
- Attach SCPs: ❌ (use web console)
- View account details: ✅

**Best Practice:** Use mobile for viewing only, perform administrative tasks on desktop

---

## Navigation Best Practices

### For Beginners

1. **Start with Search** (Method 1)
   - Fastest way to find any service
   - Reduces confusion about service categories
   - Works consistently across all AWS services

2. **Bookmark the Console**
   - Save Organizations URL for quick access
   - Create a "AWS Admin" bookmark folder
   - Include other frequently-used services

3. **Learn the Breadcrumb**
   - Always check breadcrumb to confirm location
   - Use breadcrumb to navigate back

### For Regular Users

1. **Add to Favorites**
   - Star AWS Organizations for quick access
   - Organize favorites by workflow (Security, Cost, Compute, etc.)

2. **Use Multiple Browser Tabs**
   - Keep Organizations in one tab
   - Open IAM in another
   - Use CloudTrail in a third
   - Quickly switch between related services

3. **Create Browser Profiles**
   - Separate browser profile for AWS work
   - Keeps AWS sessions isolated
   - Prevents accidental logout from personal browsing

### For Power Users

1. **Direct URLs**
   - Use bookmarked deep links
   - Skip navigation entirely
   - Create URL shortcuts for specific tasks

2. **Browser Extensions**
   - AWS Extend Switch Roles extension (Chrome/Firefox)
   - Quickly switch between accounts
   - Manage multiple Organizations

3. **CLI Integration**
   - Use AWS CLI for verification
   - Script common tasks
   - Combine console and CLI workflows

---

## Navigation Flowchart

```
                    START
                      |
                      v
        ┌─────────────────────────┐
        │ Are you logged into     │
        │ AWS Console?            │
        └─────────────────────────┘
                 |         |
                No        Yes
                 |         |
                 v         v
         ┌───────────┐   ┌──────────────────────┐
         │ Log in at │   │ Choose navigation    │
         │ console.  │   │ method:              │
         │ aws.com   │   │ 1. Search (fastest)  │
         └───────────┘   │ 2. Services menu     │
                         │ 3. Favorites         │
                         │ 4. Direct URL        │
                         └──────────────────────┘
                                   |
                                   v
                    ┌──────────────────────────┐
                    │ AWS Organizations        │
                    │ console loaded?          │
                    └──────────────────────────┘
                             |         |
                           Yes        No
                             |         |
                             v         v
                    ┌──────────┐  ┌─────────────────┐
                    │ SUCCESS  │  │ Troubleshoot:   │
                    │ Begin    │  │ - Check perms   │
                    │ work     │  │ - Verify account│
                    └──────────┘  │ - Clear cache   │
                                  └─────────────────┘
```

---

## Navigation Time Comparison

| Method | Time | Clicks | Skill Level | When to Use |
|--------|------|--------|-------------|-------------|
| Search box | 5s | 2 | Beginner+ | Daily work |
| Services menu | 15s | 3 | Beginner | Learning phase |
| Favorites | 2s | 2 | Intermediate | Regular access |
| Direct URL | 0s | 0 | Advanced | Automation/bookmarks |
| CloudShell | 3s | 1 | Advanced | CLI workflows |

---

## Summary

You now have **5 different methods** to navigate to AWS Organizations:

1. ⚡ **Search Box** - Fastest for most users
2. 📂 **Services Menu** - Best for exploration
3. ⭐ **Favorites** - Best for frequent use
4. 🔗 **Direct URL** - Best for bookmarks
5. 💻 **CloudShell** - Best for CLI integration

**Recommended Approach:**
- **Week 1-2**: Use Services Menu to learn where Organizations lives
- **Week 3+**: Switch to Search Box for speed
- **Month 2+**: Add to Favorites or bookmark direct URL

**Navigation is now muscle memory** - you should be able to reach Organizations in under 5 seconds!

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Purpose:** Navigation reference for AWS Organizations console access
