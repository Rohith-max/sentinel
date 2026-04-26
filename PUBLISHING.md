# Publishing SentinelCI to PyPI

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **API Token**: Generate token at https://pypi.org/manage/account/token/
3. **Build Tools**: Install build dependencies

```bash
pip install build twine
```

## Publishing Steps

### 1. Prepare Release

```bash
# Update version in pyproject.toml if needed
# Current version: 1.0.0

# Clean previous builds
rm -rf dist/ build/ *.egg-info/
```

### 2. Build Package

```bash
# Build source distribution and wheel
python -m build

# Verify build
ls dist/
# Should show:
# sentinelci-1.0.0-py3-none-any.whl
# sentinelci-1.0.0.tar.gz
```

### 3. Test Package Locally

```bash
# Install in test environment
pip install dist/sentinelci-1.0.0-py3-none-any.whl

# Test installation
sci --help
sci onboard
```

### 4. Upload to Test PyPI (Optional)

```bash
# Upload to test PyPI first
twine upload --repository testpypi dist/*

# Test install from test PyPI
pip install --index-url https://test.pypi.org/simple/ sentinelci
```

### 5. Upload to Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Enter your PyPI credentials or use API token
# Username: __token__
# Password: pypi-your-api-token-here
```

### 6. Verify Publication

```bash
# Check package page
# https://pypi.org/project/sentinelci/

# Test installation
pip install sentinelci
sci --help
```

## Post-Publication

### Update Documentation

1. Update README badges with correct PyPI links
2. Update installation instructions
3. Create release notes

### Create GitHub Release

```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Create release on GitHub with:
# - Release notes
# - Binary attachments
# - Changelog
```

### Monitor

1. Check PyPI download statistics
2. Monitor GitHub issues for installation problems
3. Update documentation based on user feedback

## Package Structure

```
sentinelci/
├── pyproject.toml          # Package configuration
├── README.md              # Package description
├── LICENSE                # MIT license
├── MANIFEST.in           # Include/exclude files
├── sentinelci/           # Main package
│   ├── __init__.py
│   ├── cli.py           # Main CLI entry point
│   ├── cli_new.py       # Modern CLI with onboarding
│   ├── core/            # Core modules
│   ├── output/          # Output formatters
│   └── tools/           # Security tools
└── tests/               # Test suite
```

## Entry Points

The package provides two CLI entry points:

```bash
sci --help          # Main command
sentinelci --help   # Alternative command
```

Both point to `sentinelci.cli:main`

## Dependencies

All dependencies are properly specified in `pyproject.toml`:

- **Core**: click, typer, rich, requests
- **AI**: groq (with fallback support for OpenAI/Anthropic)
- **Config**: platformdirs, tomli-w
- **UI**: questionary

## Version Management

Update version in `pyproject.toml`:

```toml
[project]
version = "1.0.1"  # Increment as needed
```

Follow semantic versioning:
- **1.0.0**: Major release
- **1.0.1**: Bug fixes
- **1.1.0**: New features
- **2.0.0**: Breaking changes

## Troubleshooting

### Build Issues

```bash
# Clear cache and rebuild
pip cache purge
rm -rf dist/ build/ *.egg-info/
python -m build
```

### Upload Issues

```bash
# Check credentials
twine check dist/*

# Use API token instead of password
# Username: __token__
# Password: pypi-AgEIcHlwaS5vcmc...
```

### Installation Issues

```bash
# Check package integrity
pip install --force-reinstall sentinelci

# Verify entry points
which sci
sci --version
```

## Success Criteria

✅ Package builds without errors
✅ All dependencies resolve correctly  
✅ CLI commands work after installation
✅ Onboarding wizard completes successfully
✅ GitHub integration functions properly
✅ AI analysis works with provided API keys
✅ Documentation is accurate and complete

## Next Steps After Publishing

1. **Announce**: Social media, dev communities
2. **Document**: Create comprehensive docs site
3. **Integrate**: Add to CI/CD marketplaces
4. **Extend**: Plugin system for custom rules
5. **Scale**: Performance optimizations for large repos