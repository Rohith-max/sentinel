"""
Dependency vulnerability scanner
Scans requirements.txt, package.json, etc. for vulnerable dependencies
"""

import re
from pathlib import Path
from typing import List, Dict, Any


# Known vulnerable versions (simplified - in production use a CVE database)
KNOWN_VULNERABILITIES = {
    "requests": {
        "2.6.0": ["CVE-2014-1829", "CVE-2014-1830"],
        "2.5.0": ["CVE-2014-1829"],
    },
    "django": {
        "1.11.0": ["CVE-2019-6975", "CVE-2019-3498"],
        "1.10.0": ["CVE-2017-7233", "CVE-2017-7234"],
    },
    "flask": {
        "0.12.0": ["CVE-2018-1000656"],
        "0.11.0": ["CVE-2018-1000656"],
    },
    "pillow": {
        "5.0.0": ["CVE-2019-16865"],
        "4.0.0": ["CVE-2016-9189"],
    },
    "pyyaml": {
        "3.12": ["CVE-2017-18342"],
        "3.11": ["CVE-2017-18342"],
    },
}


def scan_dependencies(path: str) -> List[Dict[str, Any]]:
    """
    Scan dependency files for vulnerable packages
    
    Args:
        path: File or directory path
    
    Returns:
        List of vulnerability findings
    """
    findings = []
    path_obj = Path(path)
    
    if path_obj.is_file():
        findings.extend(_scan_file(path_obj))
    elif path_obj.is_dir():
        # Scan requirements.txt
        req_file = path_obj / "requirements.txt"
        if req_file.exists():
            findings.extend(_scan_file(req_file))
        
        # Scan package.json
        pkg_file = path_obj / "package.json"
        if pkg_file.exists():
            findings.extend(_scan_npm_packages(pkg_file))
    
    return findings


def _scan_file(file_path: Path) -> List[Dict[str, Any]]:
    """Scan a requirements.txt file"""
    findings = []
    
    try:
        content = file_path.read_text()
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse package==version
            match = re.match(r"([a-zA-Z0-9_-]+)==([0-9.]+)", line)
            if match:
                package, version = match.groups()
                package_lower = package.lower()
                
                if package_lower in KNOWN_VULNERABILITIES:
                    if version in KNOWN_VULNERABILITIES[package_lower]:
                        cves = KNOWN_VULNERABILITIES[package_lower][version]
                        findings.append({
                            "type": "Vulnerable Dependency",
                            "severity": "HIGH",
                            "file": str(file_path),
                            "line_number": line_num,
                            "package": package,
                            "version": version,
                            "cves": cves,
                            "description": f"{package} {version} has known vulnerabilities: {', '.join(cves)}",
                            "remediation": f"Update {package} to the latest secure version",
                        })
    
    except Exception:
        pass
    
    return findings


def _scan_npm_packages(file_path: Path) -> List[Dict[str, Any]]:
    """Scan package.json for vulnerable npm packages"""
    findings = []
    
    try:
        import json
        content = file_path.read_text()
        data = json.loads(content)
        
        dependencies = data.get("dependencies", {})
        dev_dependencies = data.get("devDependencies", {})
        
        all_deps = {**dependencies, **dev_dependencies}
        
        for package, version in all_deps.items():
            # Remove version prefixes like ^, ~, >=
            clean_version = re.sub(r"[^0-9.]", "", version)
            
            # Check for known vulnerabilities (simplified)
            if "express" in package.lower() and clean_version.startswith("3."):
                findings.append({
                    "type": "Vulnerable Dependency",
                    "severity": "HIGH",
                    "file": str(file_path),
                    "line_number": 0,
                    "package": package,
                    "version": version,
                    "cves": ["CVE-2014-6393"],
                    "description": f"{package} {version} has known vulnerabilities",
                    "remediation": f"Update {package} to version 4.x or higher",
                })
    
    except Exception:
        pass
    
    return findings
