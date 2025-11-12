"""Internationalization support for Sablenda using Fluent."""

import locale
from datetime import date, time
from pathlib import Path
from typing import Any

from babel.dates import format_date
from fluent.runtime import FluentLocalization, FluentResourceLoader

from sablenda.settings import Settings


class I18n:
    """Handles translations and locale-specific formatting."""

    def __init__(self, settings: Settings) -> None:
        """Initialize I18n with the given settings."""
        self.settings = settings
        self._l18n = None
        self._current_locale = self._determine_locale()
        self._load_translations()

    def _determine_locale(self) -> str:
        """Determine which locale to use based on settings."""
        if self.settings.language == "auto":
            # Get system locale
            try:
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    # Extract language code (e.g., "fr_FR" -> "fr")
                    lang = system_locale.split('_')[0].lower()
                    if lang in ('en', 'fr'):
                        return lang
            except Exception:
                pass
            # Default to English if unable to detect
            return "en"
        else:
            return self.settings.language

    def _load_translations(self) -> None:
        """Load Fluent translation files."""
        loader = FluentResourceLoader("locales/{locale}")
        self._l10n = FluentLocalization([self._current_locale, "en"], ["main.ftl"], loader)

    def translate(self, *args, **kwargs: Any) -> str:
        """Translate a message key with optional parameters.

        Returns:
            The translated string

        """
        return self._l10n.format_value(*args, kwargs)

    def get_current_locale(self) -> str:
        """Get the current locale code."""
        return self._current_locale

    def set_locale(self, locale_code: str) -> None:
        """Set the current locale."""
        if locale_code in self._bundles:
            self._current_locale = locale_code

    def format_date_full(
        self, date_obj: date, capitalize: bool = False
    ) -> str:
        """Format a date in the full format for the current locale.

        Uses Babel's CLDR data for proper locale-specific formatting.
        Capitalizes the first letter for UI presentation (labels/headers).
        English: "monday, November 4, 2025"
        French: "lundi 4 novembre 2025"
        If `capitalize` is True, capitalize the return string.

        """
        formatted = format_date(date_obj, format='full', locale=self._current_locale)

        if capitalize:
            formatted = (
                formatted[0].upper() + formatted[1:]
                if formatted
                else formatted
            )

        return formatted

    def format_date_dialog_title(self, date_obj: date) -> str:
        """Format a date for dialog titles.

        Uses Babel's CLDR data for proper locale-specific formatting.
        English: "monday, November 4, 2025"
        French: "lundi 4 novembre 2025"

        """
        formatted = format_date(date_obj, format='full', locale=self._current_locale)
        return formatted

    def format_month_year(self, month: int, year: int) -> str:
        """Format month and year for calendar header.

        Uses Babel's CLDR data for proper locale-specific formatting.
        Capitalizes the first letter for UI presentation (calendar header).
        English: "November 2025"
        French: "Novembre 2025"

        """
        # Create a date object for the first day of the month
        date_obj = date(year, month, 1)
        # Use a custom pattern that only shows month and year
        formatted = format_date(date_obj, format='MMMM y', locale=self._current_locale)

        return formatted[0].upper() + formatted[1:] if formatted else formatted


# Global instance (will be initialized in main)
_i18n_instance: I18n | None = None


def init_i18n(settings: Settings) -> I18n:
    """Initialize the global I18n instance."""
    global _i18n_instance
    _i18n_instance = I18n(settings)
    return _i18n_instance


def get_i18n() -> I18n:
    """Get the global I18n instance."""
    if _i18n_instance is None:
        raise RuntimeError("I18n not initialized. Call init_i18n() first.")
    return _i18n_instance


def translate(*args, **kwargs: Any) -> str:
    """Convenience function to translate a message."""
    return get_i18n().translate(*args, **kwargs)


def _(*args, **kwargs: Any) -> str:
    """Short alias for translate()."""
    return translate(*args, **kwargs)
