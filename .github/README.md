# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the SentinelCI project.

## 🚀 Workflows Overview

### 1. **publish.yml** - Automated Publishing
**Trigger**: Release creation or manual dispatch
**Purpose**: Publishes packages to PyPI and NPM

**Features:**
- ✅ Builds Python package with proper validation
- ✅ Publishes to PyPI using trusted publishing
- ✅ Waits for PyPI availability before NPM publish
- ✅ Publishes NPM wrapper package
- ✅ Creates GitHub release with installation instructions

**Required Secrets:**
- `PYPI_API_TOKEN` - PyPI API token for publishing
- `NPM_TOKEN` - NPM authentication token

### 2. **ci.yml** - Continuous Integration
**Trigger**: Push to main branches, PRs
**Purpose**: Tests packages across multiple environments

**Features:**
- ✅ Tests Python package on Ubuntu, Windows, macOS
- ✅ Tests Python versions 3.11 and 3.12
- ✅ Tests NPM wrapper on multiple Node.js versions
- ✅ Runs linting, type checking, and security scans
- ✅ Builds and validates both packages
- ✅ Self-scans with SentinelCI

### 3. **security.yml** - Security Scanning
**Trigger**: Push, PRs, daily schedule
**Purpose**: Comprehensive security analysis

**Features:**
- ✅ Secret detection with TruffleHog
- ✅ Python dependency scanning with Safety
- ✅ Code security analysis with Bandit and Semgrep
- ✅ NPM audit for Node.js dependencies
- ✅ CodeQL analysis for code vulnerabilities
- ✅ Self-scanning with SentinelCI
- ✅ Consolidated security reporting

### 4. **dependencies.yml** - Dependency Management
**Trigger**: Weekly schedule, manual dispatch
**Purpose**: Automated dependency updates

**Features:**
- ✅ Updates Python dependencies weekly
- ✅ Updates NPM dependencies with security fixes
- ✅ Creates PRs for dependency updates
- ✅ Maintains version constraints

### 5. **docs.yml** - Documentation
**Trigger**: Documentation changes
**Purpose**: Validates and maintains documentation

**Features:**
- ✅ Markdown linting
- ✅ Link validation
- ✅ Badge updates
- ✅ Documentation consistency checks

## 🔧 Setup Instructions

### 1. Repository Secrets

Add these secrets in GitHub repository settings:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Required Secrets:**
- `PYPI_API_TOKEN`: Your PyPI API token (get from https://pypi.org/manage/account/token/)
- `NPM_TOKEN`: Your NPM authentication token (get from https://www.npmjs.com/settings/tokens)

### 2. PyPI Trusted Publishing (Recommended)

For enhanced security, set up PyPI trusted publishing:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **PyPI Project Name**: `sentinelci`
   - **Owner**: `your-github-username`
   - **Repository**: `sentinelci`
   - **Workflow**: `publish.yml`
   - **Environment**: `release`

### 3. Environment Protection

Create a `release` environment with protection rules:

1. Go to `Settings → Environments → New environment`
2. Name: `release`
3. Add protection rules:
   - ✅ Required reviewers (recommended)
   - ✅ Wait timer (optional)
   - ✅ Deployment branches (main/master only)

## 📦 Publishing Process

### Automated Release (Recommended)

1. **Create a Release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Release**:
   - Go to GitHub → Releases → Create new release
   - Tag: `v1.0.0`
   - Title: `Release v1.0.0`
   - Description: Release notes
   - Publish release

3. **Automatic Publishing**:
   - Workflow triggers automatically
   - Publishes to PyPI first
   - Then publishes to NPM
   - Updates release with package links

### Manual Publishing

Use workflow dispatch for manual control:

1. Go to `Actions → Publish to PyPI and NPM`
2. Click `Run workflow`
3. Enter version number (e.g., `1.0.0`)
4. Click `Run workflow`

## 🔍 Monitoring

### Workflow Status

Monitor workflow status in the Actions tab:
- ✅ Green: All checks passed
- ❌ Red: Failures need attention
- 🟡 Yellow: In progress

### Security Reports

Security scan results are available as artifacts:
- Download from completed workflow runs
- Review security-reports.zip for detailed analysis
- Check CodeQL results in Security tab

### Package Status

After successful publishing:
- **PyPI**: https://pypi.org/project/sentinelci/
- **NPM**: https://www.npmjs.com/package/sentinelci
- **GitHub**: Release page with installation instructions

## 🛠️ Troubleshooting

### Common Issues

**PyPI Publishing Fails:**
- Check PYPI_API_TOKEN is valid
- Verify package name is available
- Ensure version number is incremented

**NPM Publishing Fails:**
- Check NPM_TOKEN is valid
- Verify NPM package name is available
- Ensure PyPI package is published first

**Tests Fail:**
- Check Python/Node.js version compatibility
- Verify all dependencies are properly specified
- Review test logs for specific errors

### Debug Mode

Enable debug logging by adding to workflow:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

## 📊 Workflow Metrics

Track workflow performance:
- **Build Time**: Typically 5-10 minutes
- **Test Coverage**: Cross-platform compatibility
- **Security Scans**: Daily automated scanning
- **Dependency Updates**: Weekly automation

## 🎯 Best Practices

1. **Version Management**: Use semantic versioning (x.y.z)
2. **Testing**: All workflows include comprehensive testing
3. **Security**: Multiple security scanning tools integrated
4. **Documentation**: Keep workflows documented and updated
5. **Monitoring**: Regular review of workflow results

---

**Workflows are production-ready and follow GitHub Actions best practices! 🚀**