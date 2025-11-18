# 🚀 Complete Step-by-Step Guide: Setup GitHub Actions Playwright CI/CD

## ✅ What's Already Done

I've already created the necessary files:
- ✅ `.github/workflows/ci.yml` - Main workflow file
- ✅ `GITHUB_ACTIONS_PLAYWRIGHT_SETUP.md` - Detailed documentation

## 📋 Step-by-Step Setup Instructions

### **Step 1: Verify Files Exist**

Check that the workflow file exists:
\`\`\`bash
ls -la .github/workflows/ci.yml
\`\`\`

Expected output: File should exist with ~170 lines.

---

### **Step 2: Review the Workflow File (Optional)**

Open and review the workflow:
\`\`\`bash
cat .github/workflows/ci.yml
\`\`\`

Or view in your editor:
- File: `.github/workflows/ci.yml`

---

### **Step 3: Commit and Push to GitHub**

\`\`\`bash
# Stage the workflow file
git add .github/workflows/ci.yml
git add GITHUB_ACTIONS_PLAYWRIGHT_SETUP.md

# Commit
git commit -m "Add GitHub Actions CI/CD with Playwright tests"

# Push to GitHub
git push origin main
# Or if pushing to a different branch:
# git push origin develop
\`\`\`

**Note**: Replace `main` with your branch name if different.

---

### **Step 4: Verify GitHub Actions Triggered**

1. Go to your GitHub repository on GitHub.com
2. Click the **"Actions"** tab (top navigation)
3. You should see:
   - A workflow run starting (yellow/orange icon)
   - Job names: "Backend Tests", "Frontend Tests", "Test Report Summary"

---

### **Step 5: Monitor Workflow Execution**

Click on the workflow run to see:
- **Backend Tests job**: 
  - Setting up Python
  - Installing dependencies
  - Installing Playwright
  - Running tests
- **Frontend Tests job**:
  - Setting up Node.js
  - Installing dependencies
  - Installing Playwright browsers
  - Running tests

---

### **Step 6: Download Test Reports**

After workflow completes:

1. **Click on the completed workflow run**
2. **Scroll down to "Artifacts" section**
3. **Download artifacts**:
   - `backend-test-reports` - Backend test reports
   - `frontend-test-reports` - Frontend test reports
   - `test-reports-consolidated` - All reports together

4. **Extract the zip file**
5. **Open `table-report.html` in your browser**

---

## 🔧 If Something Goes Wrong

### **Issue: Workflow not triggering**

**Check**:
- File location: `.github/workflows/ci.yml` (must be exact)
- File syntax: Check YAML is valid
- Branch name: Workflow triggers on `main` and `develop`

**Fix**:
\`\`\`bash
# Check file exists
ls -la .github/workflows/ci.yml

# Validate YAML syntax (if you have yamllint)
yamllint .github/workflows/ci.yml
\`\`\`

---

### **Issue: Playwright installation fails**

**Error**: `playwright: command not found` or `Browser not found`

**Solution**: The workflow already includes Playwright installation. If it fails:
1. Check GitHub Actions logs
2. Verify `requirements.txt` includes `playwright`
3. Verify `frontend/package.json` includes `@playwright/test`

---

### **Issue: Services not ready**

**Error**: `Connection refused` to PostgreSQL or Dgraph

**Solution**: The workflow includes health checks. If it fails:
1. Check service container logs in GitHub Actions
2. Verify service images are correct
3. Check service health check commands

---

### **Issue: Tests fail**

**Solutions**:
- Check test logs in GitHub Actions output
- Download artifacts to see detailed reports
- Review error messages in `table-report.html`
- Run tests locally first to debug

---

## 📊 What the Workflow Does

### **Backend Tests Job**

1. ✅ Sets up Python 3.10
2. ✅ Caches pip dependencies
3. ✅ Installs system dependencies
4. ✅ Installs Python packages from `requirements.txt`
5. ✅ **Installs Playwright** (`playwright install chromium`)
6. ✅ **Installs Playwright system dependencies** (`playwright install-deps`)
7. ✅ Starts PostgreSQL service
8. ✅ Starts Dgraph service
9. ✅ Waits for services to be ready
10. ✅ Runs E2E tests (mock mode)
11. ✅ Runs API tests
12. ✅ Runs Performance tests
13. ✅ Uploads test reports

### **Frontend Tests Job**

1. ✅ Sets up Node.js 20
2. ✅ Caches npm dependencies
3. ✅ Installs npm packages (`npm ci`)
4. ✅ **Installs Playwright browsers** (`npx playwright install --with-deps chromium`)
5. ✅ Builds frontend (`npm run build`)
6. ✅ Runs Playwright tests (`npm run test:e2e`)
7. ✅ Uploads test reports

---

## 🎯 Quick Commands

### **Check Workflow File**
\`\`\`bash
cat .github/workflows/ci.yml | head -20
\`\`\`

### **View Workflow Status (after pushing)**
\`\`\`bash
# Using GitHub CLI (if installed)
gh workflow list
gh run list

# Or visit: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
\`\`\`

### **Re-run Failed Workflow**
1. Go to GitHub Actions tab
2. Click on failed workflow
3. Click "Re-run all jobs" button

---

## ✅ Verification Checklist

Before pushing, verify:

- [ ] File exists: `.github/workflows/ci.yml`
- [ ] YAML syntax is valid (no errors)
- [ ] `backend/requirements.txt` includes `playwright`
- [ ] `frontend/package.json` includes `@playwright/test`
- [ ] Test files exist in `backend/tests/` and `frontend/tests/`
- [ ] You have push access to GitHub repository

---

## 🚀 After Setup

Once workflow is running:

1. **Monitor first run** - Watch for any errors
2. **Download reports** - Verify test reports are generated
3. **Check execution time** - Should be 5-15 minutes total
4. **Set up notifications** (optional) - GitHub can email on failures

---

## 📚 Additional Resources

- Full documentation: `GITHUB_ACTIONS_PLAYWRIGHT_SETUP.md`
- GitHub Actions docs: https://docs.github.com/en/actions
- Playwright docs: https://playwright.dev/

---

## 🎉 That's It!

Once you push the workflow file, GitHub Actions will automatically:
- Run tests on every push to `main`/`develop`
- Run tests on every pull request
- Generate and upload test reports
- Allow manual triggering

**You're all set!** 🚀
