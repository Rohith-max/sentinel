# Complete Publishing Guide: PyPI + NPM

## 🐍 PyPI Publishing (Python Package)

### Prerequisites

1. **PyPI Account**: https://pypi.org/account/register/
2. **API Token**: https://pypi.org/manage/account/token/
3. **Build Tools**:

```bash
pip install build twine
```

### Step 1: Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build

# Verify build
ls dist/
# Should show:
# sentinelci-1.0.0-py3-none-any.whl
# sentinelci-1.0.0.tar.gz
```

### Step 2: Test Package

```bash
# Test installation locally
pip install dist/sentinelci-1.0.0-py3-none-any.whl

# Test commands
sci --help
sci onboard
```

### Step 3: Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Enter credentials:
# Username: __token__
# Password: pypi-your-api-token-here
```

### Step 4: Verify Publication

```bash
# Check package page: https://pypi.org/project/sentinelci/

# Test installation from PyPI
pip install sentinelci
sci --help
```

## 📦 NPM Publishing (Node.js Wrapper)

### Prerequisites

1. **NPM Account**: https://www.npmjs.com/signup
2. **NPM CLI**: `npm install -g npm`
3. **Login**: `npm login`

### Step 1: Prepare NPM Package

```bash
# Install dependencies
npm install

# Test the wrapper
node test.js

# Verify package structure
npm pack --dry-run
```

### Step 2: Update Package Files

Make sure these files are ready:
- ✅ `package.json` - Package metadata
- ✅ `README-NPM.md` - NPM-specific documentation  
- ✅ `bin/sci` - CLI executable
- ✅ `bin/sentinelci` - Alternative CLI
- ✅ `index.js` - Main module
- ✅ `install.js` - Installation script
- ✅ `postinstall.js` - Post-install setup

### Step 3: Test NPM Package

```bash
# Test installation locally
npm pack
npm install -g sentinelci-1.0.0.tgz

# Test commands
npx sentinelci --help
npx sentinelci onboard
```

### Step 4: Publish to NPM

```bash
# Login to NPM
npm login

# Publish package
npm publish

# Verify publication
npm info sentinelci
```

### Step 5: Test Published Package

```bash
# Test global installation
npm install -g sentinelci

# Test npx usage
npx sentinelci version
```

## 🚀 Complete Publishing Workflow

### 1. Pre-Publishing Checklist

**Python Package (PyPI):**
- ✅ Version updated in `pyproject.toml`
- ✅ Dependencies are correct
- ✅ README.md is comprehensive
- ✅ LICENSE file exists
- ✅ All tests pass
- ✅ Banner displays correctly

**NPM Package:**
- ✅ Version matches PyPI in `package.json`
- ✅ Node.js dependencies installed
- ✅ CLI executables work
- ✅ Python auto-detection works
- ✅ README-NPM.md is complete

### 2. Publishing Order

**Publish PyPI First:**
```bash
# 1. Build and upload Python package
python -m build
twine upload dist/*
```

**Then Publish NPM:**
```bash
# 2. Publish NPM wrapper (depends on PyPI package)
npm publish
```

### 3. Post-Publishing

**Update Documentation:**
- Update badges in README files
- Create GitHub release with changelog
- Update version references

**Test Both Packages:**
```bash
# Test PyPI
pip install sentinelci
sci onboard

# Test NPM  
npm install -g sentinelci
npx sentinelci onboard
```

## 📊 Package Comparison

| Feature | PyPI Package | NPM Package |
|---------|-------------|-------------|
| **Target Users** | Python developers | JavaScript/Node.js developers |
| **Installation** | `pip install sentinelci` | `npm install -g sentinelci` |
| **Usage** | `sci scan` | `npx sentinelci scan` |
| **Dependencies** | Python 3.11+ | Node.js 16+ + Python 3.11+ |
| **Size** | ~500KB | ~50KB (wrapper only) |
| **Functionality** | Full platform | Wrapper around Python |

## 🔧 Maintenance

### Version Updates

1. **Update Python version** in `pyproject.toml`
2. **Update NPM version** in `package.json` to match
3. **Rebuild and republish both packages**

### Bug Fixes

- **Python bugs**: Fix in Python code, republish PyPI
- **NPM wrapper bugs**: Fix in Node.js code, republish NPM
- **Both**: May need to republish both packages

### Dependencies

- **Python deps**: Update in `pyproject.toml`
- **Node.js deps**: Update in `package.json`

## 🎯 Success Metrics

**PyPI Package:**
- ✅ Installs without errors
- ✅ CLI commands work
- ✅ Banner displays on first run
- ✅ Onboarding wizard completes
- ✅ GitHub integration works

**NPM Package:**
- ✅ Installs Node.js wrapper
- ✅ Auto-detects Python
- ✅ Auto-installs Python package
- ✅ CLI commands proxy correctly
- ✅ Programmatic API works

## 🚨 Troubleshooting

### PyPI Issues

```bash
# Build issues
rm -rf dist/ build/ *.egg-info/
python -m build

# Upload issues  
twine check dist/*
twine upload --verbose dist/*
```

### NPM Issues

```bash
# Package issues
npm pack --dry-run
npm publish --dry-run

# Permission issues
npm login
npm whoami
```

### Cross-Platform Testing

**Windows:**
```cmd
pip install sentinelci
npm install -g sentinelci
```

**macOS:**
```bash
pip3 install sentinelci  
npm install -g sentinelci
```

**Linux:**
```bash
pip3 install sentinelci
npm install -g sentinelci
```

## 🎉 Launch Strategy

1. **Soft Launch**: Publish to test repositories first
2. **Documentation**: Ensure all docs are ready
3. **Community**: Announce on relevant platforms
4. **Monitoring**: Watch for issues and feedback
5. **Iteration**: Quick fixes and improvements

---

**Ready to publish to both PyPI and NPM! 🚀**