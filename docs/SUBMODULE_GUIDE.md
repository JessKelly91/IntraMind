# IntraMind Git Submodule Management Guide

> Complete guide to working with Git submodules in the IntraMind platform

**Last Updated**: November 6, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Understanding Submodules](#understanding-submodules)
3. [Initial Setup](#initial-setup)
4. [Daily Workflows](#daily-workflows)
5. [Making Changes](#making-changes)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

### Why Submodules?

IntraMind uses Git submodules to manage independent microservices, providing:

- **Independent Development**: Each service has its own repository and lifecycle
- **Version Control**: Pin specific versions of each service
- **Team Isolation**: Teams can work on services independently
- **Flexible Deployment**: Deploy services individually or together
- **Clear Boundaries**: Enforces microservices architecture

### IntraMind Repository Structure

```
IntraMind/                              (Main Platform Repository)
├── .gitmodules                         # Submodule configuration
├── docker-compose.yml                  # Platform orchestration
├── README.md                           # Platform documentation
├── docs/                               # Platform-wide documentation
│
├── vector-db-service/                  # Submodule → ai-vector-db-practice
│   ├── .git                            # Separate git repository
│   ├── README.md                       # Service-specific docs
│   └── ...
│
├── api-gateway/                        # Submodule → intramind-api-gateway
│   ├── .git                            # Separate git repository
│   ├── README.md                       # Service-specific docs
│   └── ...
│
└── ai-agent/                           # Submodule → intramind-ai-agent
    ├── .git                            # Separate git repository
    ├── README.md                       # Service-specific docs
    └── ...
```

### Submodule Repositories

| Service | Repository | Purpose |
|---------|-----------|---------|
| **vector-db-service** | [ai-vector-db-practice](https://github.com/JessKelly91/ai-vector-db-practice) | gRPC vector database service |
| **api-gateway** | [intramind-api-gateway](https://github.com/JessKelly91/intramind-api-gateway) | REST API gateway |
| **ai-agent** | [intramind-ai-agent](https://github.com/JessKelly91/intramind-ai-agent) | AI agent with LangGraph |

---

## Understanding Submodules

### How Submodules Work

A Git submodule is a reference to a specific commit in another repository:

```bash
# .gitmodules file
[submodule "api-gateway"]
    path = api-gateway
    url = https://github.com/JessKelly91/intramind-api-gateway.git
```

**Key Concepts:**

1. **Pointer Not Copy**: The main repo stores a commit SHA, not the full code
2. **Separate History**: Each submodule has its own git history
3. **Explicit Updates**: Submodules don't auto-update when their repos change
4. **Detached HEAD**: Submodules default to detached HEAD state

### Visual Representation

```
Main Repo (IntraMind)
├── commit abc123  ──→  vector-db-service @ commit def456
├── commit abc124  ──→  vector-db-service @ commit def789  (updated reference)
└── commit abc125  ──→  vector-db-service @ commit def789  (same reference)
```

---

## Initial Setup

### Clone Repository with Submodules

**Method 1: Clone with Submodules (Recommended)**

```bash
# Clone main repo and initialize all submodules in one command
git clone --recurse-submodules https://github.com/JessKelly91/IntraMind.git
cd IntraMind

# Verify submodules are initialized
ls -la vector-db-service/
ls -la api-gateway/
ls -la ai-agent/
```

**Method 2: Clone Then Initialize Submodules**

```bash
# Clone main repo first
git clone https://github.com/JessKelly91/IntraMind.git
cd IntraMind

# Initialize and update submodules
git submodule init
git submodule update

# Or in one command:
git submodule update --init --recursive
```

### Verify Setup

```bash
# Check submodule status
git submodule status

# Output should show commit SHAs (no '-' or '+' prefix):
#  4139471784aee6b28a267c50254ba5346642a211 ai-agent (heads/main)
#  5aa237075c1e8cec3dd6645f97f9d09120d5bfdc api-gateway (heads/main)
#  adda26a53bdef7a71523231e02d2695739694d62 vector-db-service (heads/main)

# Check each submodule has content
ls -la vector-db-service/
ls -la api-gateway/
ls -la ai-agent/
```

---

## Daily Workflows

### Pulling Latest Changes

**Scenario**: You're starting work and need the latest code.

```bash
# Update main repo and all submodules to latest
git pull --recurse-submodules

# Alternative (more explicit):
git pull                              # Update main repo
git submodule update --remote         # Update all submodules to latest
```

**What this does:**
- Updates main repository to latest commit
- Updates submodule references to the commits currently tracked
- Does NOT automatically pull latest from submodule origins

### Updating to Latest Submodule Versions

**Scenario**: A teammate updated a submodule, and you want their changes.

```bash
# Fetch latest submodule changes
git submodule update --remote --merge

# Or for a specific submodule:
git submodule update --remote --merge api-gateway

# Commit the updated submodule reference in main repo
git add api-gateway
git commit -m "Update api-gateway submodule to latest"
git push
```

### Checking Submodule Status

```bash
# See which commit each submodule is on
git submodule status

# Detailed status for all submodules
git submodule foreach 'git status'

# Check for uncommitted changes in submodules
git submodule foreach 'git diff'
```

---

## Making Changes

### Workflow Overview

```
1. Navigate into submodule directory
2. Checkout a branch (escape detached HEAD)
3. Make changes and commit
4. Push to submodule's origin
5. Return to main repo
6. Commit updated submodule reference
7. Push main repo
```

### Step-by-Step Example

**Scenario**: You need to fix a bug in the API Gateway.

#### Step 1: Navigate to Submodule

```bash
cd api-gateway
```

#### Step 2: Checkout a Branch

```bash
# Check current status
git status
# You'll likely see: "HEAD detached at <commit>"

# Checkout main branch
git checkout main

# Or create a new feature branch
git checkout -b fix/search-bug

# Pull latest changes
git pull origin main
```

#### Step 3: Make Your Changes

```bash
# Make code changes
nano src/IntraMind.ApiGateway/Controllers/SearchController.cs

# Check what changed
git status
git diff
```

#### Step 4: Commit in Submodule

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Fix search endpoint null reference bug

- Add null check for query parameter
- Return 400 Bad Request for empty queries
- Add unit tests for edge cases"
```

#### Step 5: Push Submodule Changes

```bash
# Push to the submodule's origin
git push origin main

# Or if on feature branch:
git push origin fix/search-bug
```

#### Step 6: Return to Main Repo

```bash
# Go back to main repo root
cd ..

# Check status (should show api-gateway modified)
git status
```

#### Step 7: Update Submodule Reference

```bash
# Stage the updated submodule reference
git add api-gateway

# Commit the reference update
git commit -m "Update api-gateway submodule

Updated to include:
- Search endpoint bug fix
- Additional validation
- New unit tests"

# Push main repo
git push origin main
```

### Visual Workflow

```
┌─────────────────────────────────────────┐
│ Main Repo (IntraMind)                   │
│                                         │
│  git add api-gateway                    │  ← Step 7: Commit submodule reference
│  git commit -m "Update api-gateway"     │
│  git push                               │
└────────────────┬────────────────────────┘
                 │
                 │ Points to
                 ▼
┌─────────────────────────────────────────┐
│ Submodule (api-gateway)                 │
│                                         │
│  cd api-gateway                         │  ← Step 1: Navigate
│  git checkout main                      │  ← Step 2: Checkout branch
│  # Make changes                         │  ← Step 3: Edit code
│  git add . && git commit                │  ← Step 4: Commit
│  git push origin main                   │  ← Step 5: Push to origin
└─────────────────────────────────────────┘
```

---

## Common Tasks

### Add a New Submodule

**Scenario**: Adding a new service to the platform.

```bash
# Add new submodule
git submodule add https://github.com/JessKelly91/intramind-new-service.git new-service

# This creates:
# - new-service/ directory with cloned repo
# - Entry in .gitmodules file

# Commit the addition
git add .gitmodules new-service
git commit -m "Add new-service submodule"
git push
```

### Remove a Submodule

**Scenario**: Deprecating a service.

```bash
# 1. Deinitialize submodule
git submodule deinit -f api-gateway

# 2. Remove from .git/modules
rm -rf .git/modules/api-gateway

# 3. Remove submodule directory
git rm -f api-gateway

# 4. Commit the removal
git commit -m "Remove api-gateway submodule"
git push
```

### Change Submodule URL

**Scenario**: Repository was moved or renamed.

```bash
# Edit .gitmodules file
nano .gitmodules

# Update URL:
[submodule "api-gateway"]
    path = api-gateway
    url = https://github.com/NewOrg/intramind-api-gateway.git  # New URL

# Sync the configuration
git submodule sync

# Update submodule
git submodule update --remote

# Commit changes
git add .gitmodules
git commit -m "Update api-gateway submodule URL"
git push
```

### Reset Submodule to Tracked Commit

**Scenario**: You made changes in a submodule you don't want to keep.

```bash
# Reset submodule to the commit tracked by main repo
git submodule update --init api-gateway

# Or reset all submodules:
git submodule update --init --recursive
```

### View Submodule Diff

**Scenario**: See what changed in a submodule between commits.

```bash
# See submodule commit range change
git diff main..feature-branch

# See detailed changes within submodule
git diff main..feature-branch --submodule=diff

# See submodule log
cd api-gateway
git log --oneline
```

### Update All Submodules to Latest

**Scenario**: You want all services on their latest main branches.

```bash
# Update all submodules to latest from their tracked branches
git submodule update --remote --merge

# Check what changed
git submodule status

# Commit updated references
git add .
git commit -m "Update all submodules to latest versions"
git push
```

---

## Troubleshooting

### Problem: Submodule Directory is Empty

**Symptoms**: After clone, submodule directories exist but are empty.

**Cause**: Submodules weren't initialized.

**Solution**:
```bash
# Initialize and populate submodules
git submodule update --init --recursive

# Verify
ls -la api-gateway/
```

### Problem: Detached HEAD State

**Symptoms**: Running `git status` in submodule shows "HEAD detached at...".

**Cause**: Normal behavior! Submodules default to detached HEAD.

**Solution** (if you want to make changes):
```bash
cd api-gateway
git checkout main  # Or your desired branch
```

**Note**: Detached HEAD is fine if you're just reading code.

### Problem: Submodule Has Uncommitted Changes

**Symptoms**: `git status` shows "modified: api-gateway (modified content)".

**Solution 1: Commit the Changes**

```bash
cd api-gateway
git add .
git commit -m "Your changes"
git push origin main

# Return to main repo and update reference
cd ..
git add api-gateway
git commit -m "Update api-gateway submodule"
```

**Solution 2: Discard the Changes**

```bash
cd api-gateway
git checkout .  # Discard all changes
git clean -fd   # Remove untracked files

# Or reset to tracked commit
cd ..
git submodule update --init api-gateway
```

### Problem: Merge Conflict in Submodule

**Symptoms**: Git shows conflict in submodule reference.

**Solution**:
```bash
# Check submodule status
git submodule status

# Go into submodule
cd api-gateway

# Checkout the desired branch
git checkout main
git pull origin main

# Return to main repo
cd ..

# Stage the resolution
git add api-gateway

# Complete the merge
git commit
```

### Problem: "reference is not a tree" Error

**Symptoms**: `git submodule update` fails with this error.

**Cause**: Main repo references a commit that doesn't exist in the submodule.

**Solution**:
```bash
# Fetch all commits in submodule
cd api-gateway
git fetch origin
git checkout <commit-sha>  # The commit main repo wants

# Or update to latest
git checkout main
git pull origin main

# Return and update reference
cd ..
git add api-gateway
git commit -m "Fix submodule reference"
```

### Problem: Permission Denied (SSH)

**Symptoms**: Can't clone/update submodules with SSH errors.

**Solution**:
```bash
# Option 1: Use HTTPS instead of SSH
# Edit .gitmodules:
[submodule "api-gateway"]
    url = https://github.com/JessKelly91/intramind-api-gateway.git

git submodule sync
git submodule update --init

# Option 2: Set up SSH keys
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add to GitHub: Settings → SSH and GPG keys
```

---

## Best Practices

### Do's ✅

1. **Always Work on a Branch in Submodules**
   ```bash
   cd api-gateway
   git checkout -b feature/new-endpoint
   # Make changes
   ```

2. **Pull Before Making Changes**
   ```bash
   git pull --recurse-submodules
   ```

3. **Commit Submodule Reference Updates**
   ```bash
   git add api-gateway
   git commit -m "Update api-gateway to v1.2.0"
   ```

4. **Use Descriptive Commit Messages**
   ```bash
   git commit -m "Update api-gateway submodule

   - Added new search endpoint
   - Fixed pagination bug
   - Updated API documentation"
   ```

5. **Check Submodule Status Regularly**
   ```bash
   git submodule status
   git submodule foreach 'git status'
   ```

6. **Test After Submodule Updates**
   ```bash
   docker-compose up --build
   # Run integration tests
   ```

### Don'ts ❌

1. **Don't Forget to Push Submodule Changes First**
   ```bash
   # Wrong order:
   cd ..
   git push  # Main repo pushed, but submodule changes not pushed!

   # Correct order:
   cd api-gateway
   git push origin main  # Push submodule first
   cd ..
   git push              # Then push main repo
   ```

2. **Don't Make Changes in Detached HEAD**
   ```bash
   # Check first!
   git status  # If detached, checkout a branch
   git checkout main
   ```

3. **Don't Commit Broken Submodule References**
   ```bash
   # Test before committing:
   cd api-gateway
   git log -1  # Verify commit exists
   cd ..
   git add api-gateway
   git commit
   ```

4. **Don't Ignore Submodule Conflicts**
   ```bash
   # Resolve properly, don't just accept one side blindly
   ```

5. **Don't Mix Submodule and Main Repo Changes**
   ```bash
   # Keep separate:
   # Commit 1: Submodule changes
   # Commit 2: Main repo changes including updated submodule reference
   ```

### Workflow Checklist

**Before Starting Work:**
- [ ] `git pull --recurse-submodules`
- [ ] `git submodule status` (verify everything is up to date)
- [ ] Navigate to submodule and checkout working branch

**While Working:**
- [ ] Make changes in submodule
- [ ] Test changes locally
- [ ] Commit and push submodule changes first

**After Completing Work:**
- [ ] Return to main repo
- [ ] Update submodule reference with `git add <submodule>`
- [ ] Commit reference update to main repo
- [ ] Push main repo
- [ ] Verify with `git submodule status`

---

## Quick Reference

### Essential Commands

| Task | Command |
|------|---------|
| **Clone with submodules** | `git clone --recurse-submodules <url>` |
| **Initialize submodules** | `git submodule update --init --recursive` |
| **Update submodules to latest** | `git submodule update --remote --merge` |
| **Check submodule status** | `git submodule status` |
| **Run command in all submodules** | `git submodule foreach '<command>'` |
| **Pull main + submodules** | `git pull --recurse-submodules` |
| **Add new submodule** | `git submodule add <url> <path>` |
| **Remove submodule** | `git submodule deinit -f <path> && git rm -f <path>` |
| **Reset submodule** | `git submodule update --init <path>` |

### One-Liners

```bash
# Check all submodules for uncommitted changes
git submodule foreach 'git status --short'

# Pull latest for all submodules
git submodule foreach 'git pull origin main'

# Show commits in each submodule
git submodule foreach 'git log --oneline -5'

# Clean all submodules
git submodule foreach 'git clean -fd'

# See outdated submodules
git submodule foreach 'git remote update && git status -uno'
```

---

## Additional Resources

- [Official Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub: Working with Submodules](https://github.blog/2016-02-01-working-with-submodules/)
- [Atlassian: Git Submodules](https://www.atlassian.com/git/tutorials/git-submodule)

---

## Support

For issues specific to IntraMind submodules:

1. Check this guide first
2. Review [PROJECT_ROADMAP.md](./PROJECT_ROADMAP.md) for current status
3. Check individual service READMEs:
   - [vector-db-service/README.md](../vector-db-service/README.md)
   - [api-gateway/README.md](../api-gateway/README.md)
   - [ai-agent/README.md](../ai-agent/README.md)

---

**Last Updated**: November 6, 2025
**Maintained By**: IntraMind Development Team
