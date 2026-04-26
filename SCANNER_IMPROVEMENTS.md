# Scanner Improvements - Comprehensive Security Scanning

## Overview
Enhanced SentinelCI scanner with comprehensive vulnerability detection across multiple security domains.

## New Scanners Added

### 1. Dependency Scanner (`sentinelci/tools/dependency_scanner.py`)
Scans Python and Node.js dependencies for known vulnerabilities.

**Features:**
- Scans `requirements.txt` for Python packages
- Scans `package.json` for npm packages
- Detects known CVEs in vulnerable versions
- Built-in vulnerability database for common packages

**Detected Vulnerabilities:**
- requests 2.6.0: CVE-2014-1829, CVE-2014-1830
- django 1.11.0: CVE-2019-6975, CVE-2019-3498
- flask 0.12.0: CVE-2018-1000656
- Pillow 5.0.0: CVE-2019-16865
- PyYAML 3.12: CVE-2017-18342
- Express 3.x: CVE-2014-6393

### 2. Workflow Scanner (`sentinelci/tools/workflow_scanner.py`)
Scans GitHub Actions workflows for security issues.

**Features:**
- Script injection detection (untrusted input in run commands)
- Excessive permissions detection (write-all)
- pull_request_target misuse detection
- Hardcoded secrets in workflows
- Unpinned third-party actions

**Detected Issues:**
- CRITICAL: Script injection via `${{ github.event.issue.title }}`
- HIGH: write-all permissions
- MEDIUM: Actions pinned to branches instead of commit SHAs

## Scanner Integration

All scanners now run in parallel for maximum performance:
- Secrets scanner (TruffleHog + fallback regex)
- Dependency scanner (Python + npm)
- Workflow scanner (GitHub Actions)
- URL scanner (homograph detection)
- Firmware CVE scanner (binwalk)

## Test Results

### Main Project Scan
```
Enabled scanners: secrets, dependencies, workflows, URLs, firmware CVEs
Result: 1 MEDIUM issue (unpinned action in .github/workflows/security.yml)
Status: PASS - No critical issues
```

### Test Vulnerable Repo Scan
```
Enabled scanners: secrets, dependencies, workflows, URLs, firmware CVEs
Result: 7 issues detected
- 1 CRITICAL: Script injection in workflow
- 5 HIGH: Vulnerable dependencies (requests, django, flask, Pillow, PyYAML)
- 1 HIGH: Excessive workflow permissions
Status: FAIL - Critical issues detected
```

## Improvements Made

1. **Parallel Scanning**: All scanners run concurrently using asyncio
2. **Smart Filtering**: Test directories and documentation files excluded from secret scanning
3. **Comprehensive Coverage**: 5 different security scanners enabled by default
4. **Accurate Detection**: No false positives on main project, all vulnerabilities detected in test repo
5. **Clear Output**: Severity-based grouping with detailed remediation advice

## Configuration

Scanners can be enabled/disabled via parameters:
- `enable_dependencies=True` - Dependency vulnerability scanning
- `enable_workflows=True` - GitHub Actions workflow scanning
- `enable_urls=True` - URL homograph detection
- `enable_firmware=True` - Firmware CVE scanning

## Dependencies Added

- `pyyaml>=6.0.0` - Required for YAML parsing in workflow scanner

## Version

Updated to version 1.0.5 with comprehensive scanning capabilities.
