"""Preferences dialog for Sablenda."""

import wx

from ..i18n import get_i18n
from ..settings import Settings


class PreferencesDialog(wx.Dialog):
    """Dialog for configuring application preferences."""

    def __init__(self, parent: wx.Window, settings: Settings) -> None:
        """
        Initialize the preferences dialog.

        Args:
            parent: Parent window
            settings: Current settings object
        """
        i18n = get_i18n()
        super().__init__(
            parent,
            title=i18n.translate("preferences-title"),
            style=wx.DEFAULT_DIALOG_STYLE,
        )

        self.settings = settings
        self._create_ui()
        self.Fit()
        self.Centre()

    def _create_ui(self) -> None:
        """Create the dialog UI."""
        i18n = get_i18n()

        # Main panel
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Language selection
        language_box = wx.StaticBoxSizer(wx.VERTICAL, panel, i18n.translate("preferences-language-label"))

        self.language_choice = wx.Choice(panel)
        self.language_choice.Append(i18n.translate("preferences-language-auto"), "auto")
        self.language_choice.Append(i18n.translate("preferences-language-en"), "en")
        self.language_choice.Append(i18n.translate("preferences-language-fr"), "fr")

        # Select current language
        current_lang = self.settings.language
        if current_lang == "auto":
            self.language_choice.SetSelection(0)
        elif current_lang == "en":
            self.language_choice.SetSelection(1)
        elif current_lang == "fr":
            self.language_choice.SetSelection(2)

        language_box.Add(self.language_choice, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(language_box, 0, wx.EXPAND | wx.ALL, 10)

        # Buttons
        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(panel, wx.ID_OK, i18n.translate("btn-ok"))
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(panel, wx.ID_CANCEL, i18n.translate("btn-cancel"))
        button_sizer.AddButton(cancel_button)

        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(sizer)

        # Bind events
        ok_button.Bind(wx.EVT_BUTTON, self._on_ok)

    def _on_ok(self, event: wx.Event) -> None:
        """Handle OK button click."""
        # Get selected language
        selection = self.language_choice.GetSelection()
        lang_data = self.language_choice.GetClientData(selection)

        if lang_data:
            self.settings.language = lang_data  # type: ignore

        self.EndModal(wx.ID_OK)

    def get_settings(self) -> Settings:
        """Get the updated settings."""
        return self.settings
