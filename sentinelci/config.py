"""
Configuration management for SCI
"""

import os
from pathlib import Path
from typing import Optional
import tomli_w

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import platformdirs


class Config:
    """Manages SCI configuration files"""

    def __init__(self):
        """Initialize config from file or environment"""
        self._load_dotenv_files()
        self.config_dir = Path(platformdirs.user_config_dir("sci", "sci"))
        self.config_file = self.config_dir / "config.toml"
        self.legacy_config_file = (
            Path(platformdirs.user_config_dir("sentinelci", "sentinelci")) / "config.toml"
        )
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file, creating defaults if needed"""
        if self.config_file.exists():
            with open(self.config_file, "rb") as f:
                return tomllib.load(f)
        if self.legacy_config_file.exists():
            with open(self.legacy_config_file, "rb") as f:
                return tomllib.load(f)
        return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            "api": {
                "ai_api_key": None,
                "nvd_api_key": None,
            },
            "git": {
                "github_pat": None,
            },
            "scan": {
                "severity_threshold": "medium",
                "enable_firmware_scanning": True,
                "enable_url_detection": True,
            },
            "output": {
                "format": "terminal",
            },
        }

    def _load_dotenv_files(self) -> None:
        """Load key=value pairs from local .env files into process environment."""
        candidates = [Path.cwd() / ".env", Path.cwd() / ".env.local"]

        for env_path in candidates:
            if not env_path.exists():
                continue

            try:
                for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if not key or key in os.environ:
                        continue

                    os.environ[key] = value
            except OSError:
                continue

    def get(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value"""
        if section not in self._config:
            return default
        return self._config[section].get(key, default)

    def set(self, section: str, key: str, value: str) -> None:
        """Set a configuration value and save to file"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self.save()

    def remove(self, section: str, key: str) -> None:
        """Remove a configuration value and save to file"""
        if section in self._config and key in self._config[section]:
            del self._config[section][key]
            self.save()

    def save(self) -> None:
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "wb") as f:
            tomli_w.dump(self._config, f)

    def get_api_key(self) -> Optional[str]:
        """Get AI API key from config or environment"""
        # Check environment variables first.
        if api_key := os.environ.get("AI_API_KEY"):
            return api_key
        if api_key := os.environ.get("GROQ_API_KEY"):
            return api_key

        # Check config file with backwards compatibility.
        api_key = self.get("api", "ai_api_key")
        if api_key:
            return api_key

        api_key = self.get("api", "anthropic_api_key")
        if api_key:
            return api_key

        return None

    def get_github_pat(self) -> Optional[str]:
        """Get GitHub PAT from config or environment."""
        for env_key in ("GITHUB_PAT", "GH_PAT", "GITHUB_TOKEN"):
            if token := os.environ.get(env_key):
                return token

        token = self.get("git", "github_pat")
        if token:
            return token

        return None

    def get_nvd_api_key(self) -> Optional[str]:
        """Get NVD API key from config or environment."""
        for env_key in ("NVD_API_KEY", "NIST_NVD_API_KEY"):
            if key := os.environ.get(env_key):
                return key

        key = self.get("api", "nvd_api_key")
        if key:
            return key

        return None

    def setup_wizard(self) -> None:
        """Interactive setup wizard for initial configuration"""
        print("\n🔧 SCI Configuration Wizard\n")

        # API Key setup
        current_key = self.get_api_key()
        if current_key:
            prompt = f"Ai Api (current: {current_key[:10]}...): "
        else:
            prompt = "Ai Api (required): "

        api_key = input(prompt).strip()
        if api_key:
            self.set("api", "ai_api_key", api_key)
            print("✓ API key saved")

        # GitHub PAT setup (optional)
        current_pat = self.get_github_pat()
        if current_pat:
            pat_prompt = f"GitHub PAT for sync (optional, current: {current_pat[:6]}...): "
        else:
            pat_prompt = "GitHub PAT for sync (optional): "

        github_pat = input(pat_prompt).strip()
        if github_pat:
            self.set("git", "github_pat", github_pat)
            print("✓ GitHub PAT saved")

        # NVD API Key setup (optional but recommended for higher rate limits)
        current_nvd = self.get_nvd_api_key()
        if current_nvd:
            nvd_prompt = f"NVD API Key (optional, current: {current_nvd[:6]}...): "
        else:
            nvd_prompt = "NVD API Key (optional): "

        nvd_api_key = input(nvd_prompt).strip()
        if nvd_api_key:
            self.set("api", "nvd_api_key", nvd_api_key)
            print("✓ NVD API key saved")

        # Severity threshold
        severity = input("Minimum severity (low/medium/high/critical) [medium]: ").strip()
        if severity and severity in ["low", "medium", "high", "critical"]:
            self.set("scan", "severity_threshold", severity)
            print(f"✓ Severity threshold set to {severity}")

        # Firmware scanning
        firmware = input("Enable firmware CVE scanning (y/n) [y]: ").strip().lower()
        if firmware == "n":
            self.set("scan", "enable_firmware_scanning", "false")
            print("✓ Firmware scanning disabled")

        # URL detection
        urls = input("Enable homograph URL detection (y/n) [y]: ").strip().lower()
        if urls == "n":
            self.set("scan", "enable_url_detection", "false")
            print("✓ URL detection disabled")

        print(f"\n✅ Configuration saved to {self.config_file}\n")

    def configure_onboarding(
        self,
        ai_api_key: Optional[str] = None,
        github_pat: Optional[str] = None,
        nvd_api_key: Optional[str] = None,
        clear_github_pat: bool = False,
        severity: Optional[str] = None,
        enable_firmware: Optional[bool] = None,
        enable_urls: Optional[bool] = None,
    ) -> None:
        """Apply onboarding settings non-interactively."""
        if ai_api_key:
            self.set("api", "ai_api_key", ai_api_key)

        if clear_github_pat:
            if "git" not in self._config:
                self._config["git"] = {}
            self._config["git"].pop("github_pat", None)
            self.save()
        elif github_pat:
            self.set("git", "github_pat", github_pat)

        if nvd_api_key:
            self.set("api", "nvd_api_key", nvd_api_key)

        if severity and severity in ["low", "medium", "high", "critical"]:
            self.set("scan", "severity_threshold", severity)

        if enable_firmware is not None:
            self.set("scan", "enable_firmware_scanning", bool(enable_firmware))

        if enable_urls is not None:
            self.set("scan", "enable_url_detection", bool(enable_urls))

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.get_api_key():
            print("❌ Error: AI API key not configured")
            print("\nRun 'sci config' to set up your API key")
            print("Or set AI_API_KEY (or GROQ_API_KEY) environment variable")
            return False
        return True


def get_config() -> Config:
    """Get or create the global configuration"""
    return Config()
