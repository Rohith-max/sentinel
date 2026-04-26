# Testing SentinelCI Against Real CI/CD Pipelines

This guide will help you set up test repositories with intentionally vulnerable CI/CD pipelines to test SentinelCI's capabilities.

## Quick Start: 3-Step Testing

### Step 1: Create a Test Repository

```bash
# Create a new test repo on GitHub
# Go to https://github.com/new
# Name it: sentinelci-test
# Make it public or private
# Initialize with README

# Clone it locally
git clone https://github.com/YOUR_USERNAME/sentinelci-test.git
cd sentinelci-test
```

### Step 2: Add Vulnerable Workflows

Copy the vulnerable workflows from this guide (see below) into `.github/workflows/`

### Step 3: Scan with SentinelCI

```bash
# Scan the repository
sci scan

# Or scan via GitHub integration
sci github repos
# Select your test repo → "Run AI Security Analysis"
```

---

## Sample Vulnerable Workflows

### 1. Basic Vulnerable Workflow (Easy)

Create `.github/workflows/vulnerable-basic.yml`:

```yaml
name: Vulnerable Basic CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    # VULNERABILITY: Excessive permissions
    permissions: write-all
    
    steps:
    - uses: actions/checkout@v3
    
    # VULNERABILITY: Unpinned action version
    - name: Setup Node
      uses: actions/setup-node@v3
      
    # VULNERABILITY: Hardcoded secret
    - name: Deploy
      run: |
        echo "API_KEY=sk_live_1234567890abcdef" >> $GITHUB_ENV
        npm run deploy
      env:
        DATABASE_PASSWORD: "admin123"
        
    # VULNERABILITY: Command injection risk
    - name: Run tests
      run: npm test -- ${{ github.event.head_commit.message }}
```

**Issues SentinelCI will detect:**
- ✓ Excessive permissions (`write-all`)
- ✓ Unpinned action versions
- ✓ Hardcoded secrets
- ✓ Command injection vulnerability

---

### 2. Advanced Vulnerable Workflow (Medium)

Create `.github/workflows/vulnerable-advanced.yml`:

```yaml
name: Vulnerable Advanced CI

on:
  pull_request_target:  # VULNERABILITY: Dangerous trigger
    types: [opened, synchronize]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout PR code
      uses: actions/checkout@v3
      with:
        # VULNERABILITY: Checking out untrusted PR code
        ref: ${{ github.event.pull_request.head.sha }}
    
    # VULNERABILITY: Script injection
    - name: Comment on PR
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: 'Thanks for the PR: ${{ github.event.pull_request.title }}'
          })
    
    # VULNERABILITY: Exposing secrets in logs
    - name: Debug
      run: |
        echo "Secret: ${{ secrets.DEPLOY_TOKEN }}"
        printenv | grep -i secret
        
  deploy:
    needs: security-scan
    runs-on: ubuntu-latest
    
    # VULNERABILITY: No environment protection
    steps:
    - uses: actions/checkout@v3
    
    # VULNERABILITY: Using deprecated action
    - name: Deploy to production
      uses: actions/aws/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
```

**Issues SentinelCI will detect:**
- ✓ Dangerous `pull_request_target` trigger
- ✓ Script injection vulnerabilities
- ✓ Secrets exposed in logs
- ✓ No environment protection for production
- ✓ Deprecated actions

---

### 3. Supply Chain Attack Workflow (Hard)

Create `.github/workflows/vulnerable-supply-chain.yml`:

```yaml
name: Vulnerable Supply Chain

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    # VULNERABILITY: Unpinned third-party action
    - name: Checkout
      uses: actions/checkout@main
      
    # VULNERABILITY: Untrusted action from unknown source
    - name: Run security scan
      uses: random-user/security-scanner@latest
      
    # VULNERABILITY: Installing packages without verification
    - name: Install dependencies
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        pip install -r requirements.txt --no-verify
        
    # VULNERABILITY: Downloading and executing script
    - name: Setup environment
      run: |
        curl https://raw.githubusercontent.com/unknown/repo/main/setup.sh | bash
        
    # VULNERABILITY: Using self-hosted runner without isolation
    - name: Build on self-hosted
      runs-on: self-hosted
      run: |
        docker build -t myapp .
        docker push myregistry/myapp:latest
```

**Issues SentinelCI will detect:**
- ✓ Unpinned actions using branch names
- ✓ Third-party actions from untrusted sources
- ✓ Downloading and executing remote scripts
- ✓ Self-hosted runner security risks
- ✓ No package verification

---

## Testing Scenarios

### Scenario 1: Local Scanning

```bash
# Navigate to your test repo
cd sentinelci-test

# Run basic scan
sci scan

# Run with AI analysis
sci scan --format json --output results.json

# Scan only workflows
sci scan --path .github/workflows/
```

### Scenario 2: GitHub Integration

```bash
# List your repositories
sci github repos

# Select your test repo and choose:
# 1. "Analyze Security Configuration" - Quick overview
# 2. "Run AI Security Analysis" - Detailed AI analysis
# 3. "Autonomous Agent" - Auto-fix vulnerabilities
```

### Scenario 3: Autonomous Remediation

```bash
# Run autonomous agent
sci github repos
# Select test repo → "Autonomous Agent (Full Automation)"

# The agent will:
# 1. Detect all vulnerabilities
# 2. Create a remediation plan
# 3. Ask for your approval
# 4. Fix issues automatically
# 5. Create a PR with fixes
```

---

## Creating Your Own Test Repository

### Step-by-Step Setup

1. **Create repository:**
   ```bash
   mkdir sentinelci-test
   cd sentinelci-test
   git init
   ```

2. **Add vulnerable code:**
   ```bash
   # Create a file with hardcoded secrets
   echo 'API_KEY="sk_live_1234567890"' > config.py
   echo 'DATABASE_URL="postgresql://admin:password123@localhost/db"' >> config.py
   ```

3. **Add vulnerable workflows:**
   ```bash
   mkdir -p .github/workflows
   # Copy one of the vulnerable workflows above
   ```

4. **Add dependencies with known vulnerabilities:**
   ```bash
   # Create requirements.txt with old versions
   echo "requests==2.6.0" > requirements.txt
   echo "django==1.11.0" >> requirements.txt
   echo "flask==0.12.0" >> requirements.txt
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add vulnerable code for testing"
   git remote add origin https://github.com/YOUR_USERNAME/sentinelci-test.git
   git push -u origin main
   ```

6. **Scan with SentinelCI:**
   ```bash
   sci scan
   ```

---

## Expected Results

### What SentinelCI Should Detect

**Secrets:**
- Hardcoded API keys
- Database credentials
- AWS access keys
- GitHub tokens

**CI/CD Issues:**
- Excessive permissions
- Unpinned action versions
- Script injection vulnerabilities
- Dangerous workflow triggers
- Secrets in logs

**Dependencies:**
- Vulnerable package versions
- Outdated dependencies
- Known CVEs

**Code Issues:**
- SQL injection patterns
- Command injection risks
- Insecure configurations

---

## Testing Checklist

- [ ] Local file scanning works
- [ ] GitHub repository scanning works
- [ ] AI analysis provides insights
- [ ] Autonomous agent creates fixes
- [ ] Pull requests are generated
- [ ] Issues are created for tracking
- [ ] Secrets are detected
- [ ] Workflow vulnerabilities found
- [ ] Dependency issues identified
- [ ] Fix suggestions are accurate

---

## Advanced Testing

### Test with Real Projects

1. **Fork a popular open-source project**
2. **Scan it with SentinelCI:**
   ```bash
   sci github repos
   # Select the forked repo
   ```

3. **Compare results with:**
   - GitHub's Dependabot
   - Snyk
   - CodeQL

### Test Autonomous Fixes

1. **Create a branch:**
   ```bash
   git checkout -b test-autonomous-fixes
   ```

2. **Run autonomous agent:**
   ```bash
   sci github repos
   # Select repo → "Autonomous Agent"
   ```

3. **Review the PR created by SentinelCI**

4. **Verify fixes are correct**

---

## Troubleshooting Tests

### No Issues Found?

Make sure your test files have actual vulnerabilities:
```bash
# Check if workflows exist
ls -la .github/workflows/

# Check if secrets are in code
grep -r "API_KEY\|PASSWORD\|SECRET" .

# Verify SentinelCI is scanning correctly
sci scan --verbose
```

### Too Many False Positives?

Adjust severity threshold:
```bash
sci scan --severity high
```

### Agent Not Creating PRs?

Check GitHub permissions:
```bash
sci github auth
# Make sure your PAT has 'repo' scope
```

---

## Sample Test Repository

I've created a complete test repository template:

```bash
# Clone the test template
git clone https://github.com/sentinelci/test-vulnerable-repo.git
cd test-vulnerable-repo

# Scan it
sci scan

# Expected: 15+ vulnerabilities detected
```

---

## Next Steps

1. **Start with Basic Workflow** - Test detection capabilities
2. **Try Autonomous Agent** - Test auto-remediation
3. **Create Custom Tests** - Add your own vulnerable patterns
4. **Compare Tools** - Test against other security scanners
5. **Report Issues** - Help improve SentinelCI

---

## Need Help?

- **Documentation**: Check `AUTONOMOUS_AGENT_GUIDE.md`
- **Examples**: See `examples/github_integration_demo.py`
- **Issues**: https://github.com/sentinelci/sentinelci/issues

Happy testing! 🔒
