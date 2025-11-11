"""User settings management for Sablenda."""

import json
from pathlib import Path
from typing import Literal

# Type for language setting
LanguageSetting = Literal["auto", "en", "fr"]


class Settings:
    """Manages user settings for the application."""

    def __init__(self) -> None:
        """Initialize settings with defaults."""
        self.language: LanguageSetting = "auto"
        self.version: str = "1.0"

    def to_dict(self) -> dict[str, str]:
        """Convert settings to dictionary."""
        return {
            "language": self.language,
            "version": self.version,
        }

    def from_dict(self, data: dict[str, str]) -> None:
        """Load settings from dictionary."""
        self.language = data.get("language", "auto")  # type: ignore
        self.version = data.get("version", "1.0")

        # Validate language setting
        if self.language not in ("auto", "en", "fr"):
            self.language = "auto"


def get_settings_path() -> Path:
    """Get the path to the settings file."""
    import os

    if os.name == 'nt':
        # Windows: Use APPDATA
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            settings_dir = Path(appdata) / 'sablenda'
        else:
            settings_dir = Path.home() / 'AppData' / 'Roaming' / 'sablenda'
    else:
        # Unix-like: Use XDG_CONFIG_HOME or ~/.config
        config_home = os.environ.get('XDG_CONFIG_HOME', '')
        if config_home:
            settings_dir = Path(config_home) / 'sablenda'
        else:
            settings_dir = Path.home() / '.config' / 'sablenda'

    # Ensure directory exists
    settings_dir.mkdir(parents=True, exist_ok=True)

    return settings_dir / 'settings.json'


def load_settings() -> Settings:
    """Load settings from disk, or create defaults if not found."""
    settings = Settings()
    settings_path = get_settings_path()

    try:
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                settings.from_dict(data)
    except Exception:
        # If there's any error reading settings, use defaults
        pass

    return settings


def save_settings(settings: Settings) -> None:
    """Save settings to disk."""
    settings_path = get_settings_path()

    try:
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception:
        # Silently fail if we can't save settings
        pass
