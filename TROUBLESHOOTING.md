# Troubleshooting Guide

## Command Not Found: `sci`

### Problem
After installing `sentinelci`, the `sci` command is not recognized.

### Solution

The Python Scripts directory is not in your system PATH. Here's how to fix it:

#### Windows

1. **Find the Scripts directory:**
   When you install with `pip install sentinelci`, look for a warning message like:
   ```
   WARNING: The scripts sci.exe and sentinelci.exe are installed in 'C:\Users\...\Scripts' which is not on PATH.
   ```

2. **Add to PATH temporarily (current session):**
   ```powershell
   $env:PATH += ";C:\Users\YourName\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_xxx\LocalCache\local-packages\Python311\Scripts"
   ```

3. **Add to PATH permanently:**
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", select "Path" and click "Edit"
   - Click "New" and add the Scripts directory path
   - Click "OK" on all dialogs
   - Restart your terminal

4. **Alternative: Use full path:**
   ```powershell
   C:\Users\YourName\AppData\Local\Packages\...\Scripts\sci.exe --help
   ```

#### macOS/Linux

1. **Add to your shell profile:**
   ```bash
   # For bash (~/.bashrc):
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc

   # For zsh (~/.zshrc):
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Verify installation:**
   ```bash
   which sci
   sci --version
   ```

#### Using NPM Instead

If PATH configuration is too complex, use the NPM package:

```bash
npm install -g sentinelci
npx sentinelci --help
```

The NPM wrapper handles PATH automatically.

## Python Version Issues

### Problem
Error: `sentinelci requires Python 3.11+`

### Solution
Install Python 3.11 or higher:

**Windows:**
- Download from https://python.org/downloads/
- Or use Microsoft Store: `winget install Python.Python.3.11`

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

## Dependency Installation Failures

### Problem
Errors during `pip install sentinelci`

### Solution

1. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install with verbose output:**
   ```bash
   pip install sentinelci --verbose
   ```

3. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install sentinelci
   ```

## GitHub Authentication Issues

### Problem
`ERROR: Not authenticated` or `403 Forbidden`

### Solution

1. **Create GitHub Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (for private repos) or `public_repo` (for public only)
   - Copy the token

2. **Configure SentinelCI:**
   ```bash
   sci github setup
   # Paste your token when prompted
   ```

3. **Or set environment variable:**
   ```bash
   export GITHUB_PAT="your_token_here"
   ```

## AI API Issues

### Problem
`ERROR: AI API key not configured`

### Solution

1. **Get an API key:**
   - **Groq (Recommended - Free):** https://console.groq.com/keys
   - **OpenAI:** https://platform.openai.com/api-keys
   - **Anthropic:** https://console.anthropic.com/

2. **Configure via wizard:**
   ```bash
   sci onboard
   ```

3. **Or set environment variable:**
   ```bash
   export GROQ_API_KEY="your_key_here"
   # or
   export OPENAI_API_KEY="your_key_here"
   ```

## Permission Errors

### Problem
`PermissionError` or `Access Denied` when scanning

### Solution

1. **Run with appropriate permissions:**
   ```bash
   # Windows (as Administrator if needed):
   sci scan

   # Linux/macOS:
   sudo sci scan  # Only if scanning system directories
   ```

2. **Check file permissions:**
   ```bash
   ls -la  # Check if you have read access to files
   ```

## Import Errors

### Problem
`ModuleNotFoundError: No module named 'sentinelci'`

### Solution

1. **Verify installation:**
   ```bash
   pip show sentinelci
   ```

2. **Reinstall:**
   ```bash
   pip uninstall sentinelci
   pip install sentinelci
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.11+
   ```

## Getting Help

If you're still experiencing issues:

1. **Check version:**
   ```bash
   sci version
   ```

2. **Enable verbose output:**
   ```bash
   sci scan --verbose
   ```

3. **Report issue:**
   - GitHub Issues: https://github.com/sentinelci/sentinelci/issues
   - Include: OS, Python version, error message, and steps to reproduce

## Quick Verification

Test if everything is working:

```bash
# Check installation
sci --version

# Test basic scan
sci scan --help

# Verify GitHub auth (if configured)
sci github auth

# Run a test scan
sci scan --path . --no-ai
```

If all commands work, you're good to go!
