"""Rutinkompis - Step-by-step visual routine guides."""
import json
import sys
import gettext
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

from rutinkompis import __version__
from rutinkompis.window import RutinkompisWindow

TEXTDOMAIN = "rutinkompis"
gettext.textdomain(TEXTDOMAIN)
_ = gettext.gettext

APP_ID = "se.yeager.rutinkompis"
CONFIG_DIR = Path(GLib.get_user_config_dir()) / "rutinkompis"


def _load_settings():
    path = CONFIG_DIR / "settings.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_settings(settings):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / "settings.json").write_text(
        json.dumps(settings, indent=2, ensure_ascii=False))


class RutinkompisApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.settings = _load_settings()

    def do_activate(self):
        win = self.props.active_window or RutinkompisWindow(application=self)
        self._apply_theme()
        win.present()
        if not self.settings.get("welcome_shown"):
            self._show_welcome(win)

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._setup_actions()

    def _apply_theme(self):
        theme = self.settings.get("theme", "system")
        mgr = Adw.StyleManager.get_default()
        schemes = {
            "light": Adw.ColorScheme.FORCE_LIGHT,
            "dark": Adw.ColorScheme.FORCE_DARK,
            "system": Adw.ColorScheme.DEFAULT,
        }
        mgr.set_color_scheme(schemes.get(theme, Adw.ColorScheme.DEFAULT))

    def _setup_actions(self):
        for name, cb, accel in [
            ("quit", lambda *_: self.quit(), ["<Control>q"]),
            ("about", self._on_about, ["F1"]),
            ("shortcuts", self._on_shortcuts, ["<Control>slash"]),
            ("preferences", self._on_preferences, ["<Control>comma"]),
            ("export", self._on_export, ["<Control>e"]),
        ]:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", cb)
            self.add_action(action)
            if accel:
                self.set_accels_for_action(f"app.{name}", accel)

    # ── Welcome Dialog ───────────────────────────────────────

    def _show_welcome(self, win):
        dialog = Adw.Dialog()
        dialog.set_title(_("Welcome"))
        dialog.set_content_width(420)
        dialog.set_content_height(480)

        page = Adw.StatusPage()
        page.set_icon_name("rutinkompis")
        page.set_title(_("Welcome to Rutinkompis"))
        page.set_description(_(
            "Follow step-by-step routines with pictures.\n\n"
            "✓ Visual guides for daily tasks\n"
            "✓ Check off each step as you go\n"
            "✓ Search 13,000+ ARASAAC pictograms\n"
            "✓ Customizable routines"
        ))

        btn = Gtk.Button(label=_("Get Started"))
        btn.add_css_class("suggested-action")
        btn.add_css_class("pill")
        btn.set_halign(Gtk.Align.CENTER)
        btn.set_margin_top(12)
        btn.connect("clicked", self._on_welcome_close, dialog)
        page.set_child(btn)

        box = Adw.ToolbarView()
        hb = Adw.HeaderBar()
        hb.set_show_title(False)
        box.add_top_bar(hb)
        box.set_content(page)
        dialog.set_child(box)
        dialog.present(win)

    def _on_welcome_close(self, btn, dialog):
        self.settings["welcome_shown"] = True
        _save_settings(self.settings)
        dialog.close()

    # ── Preferences ──────────────────────────────────────────

    def _on_preferences(self, *_):
        prefs = Adw.PreferencesDialog()
        prefs.set_title(_("Preferences"))

        basic = Adw.PreferencesPage()
        basic.set_title(_("General"))
        basic.set_icon_name("preferences-system-symbolic")

        appearance = Adw.PreferencesGroup()
        appearance.set_title(_("Appearance"))

        theme_row = Adw.ComboRow()
        theme_row.set_title(_("Theme"))
        theme_row.set_subtitle(_("Choose light, dark, or follow system"))
        theme_row.set_model(Gtk.StringList.new(
            [_("System"), _("Light"), _("Dark")]))
        cur = {"system": 0, "light": 1, "dark": 2}.get(
            self.settings.get("theme", "system"), 0)
        theme_row.set_selected(cur)
        theme_row.connect("notify::selected", self._on_theme_changed)
        appearance.add(theme_row)

        size_row = Adw.ComboRow()
        size_row.set_title(_("Icon Size"))
        size_row.set_subtitle(_("Size of pictogram icons"))
        size_row.set_model(Gtk.StringList.new(
            [_("Small"), _("Medium"), _("Large")]))
        cur_size = {"small": 0, "medium": 1, "large": 2}.get(
            self.settings.get("icon_size", "medium"), 1)
        size_row.set_selected(cur_size)
        size_row.connect("notify::selected", self._on_icon_size_changed)
        appearance.add(size_row)

        basic.add(appearance)
        prefs.add(basic)

        # Advanced
        advanced = Adw.PreferencesPage()
        advanced.set_title(_("Advanced"))
        advanced.set_icon_name("applications-engineering-symbolic")

        cache_group = Adw.PreferencesGroup()
        cache_group.set_title(_("ARASAAC Cache"))
        cache_dir = Path(GLib.get_user_cache_dir()) / "arasaac"
        cache_size = sum(f.stat().st_size for f in cache_dir.glob("*")
                         if f.is_file()) if cache_dir.exists() else 0
        cache_row = Adw.ActionRow()
        cache_row.set_title(_("Cached pictograms"))
        cache_row.set_subtitle(f"{cache_size / (1024*1024):.1f} MB")
        clear_btn = Gtk.Button(label=_("Clear"))
        clear_btn.add_css_class("destructive-action")
        clear_btn.set_valign(Gtk.Align.CENTER)
        clear_btn.connect("clicked", self._on_clear_cache, cache_row)
        cache_row.add_suffix(clear_btn)
        cache_group.add(cache_row)
        advanced.add(cache_group)

        debug_group = Adw.PreferencesGroup()
        debug_group.set_title(_("Developer"))
        debug_row = Adw.SwitchRow()
        debug_row.set_title(_("Debug mode"))
        debug_row.set_subtitle(_("Show extra logging in terminal"))
        debug_row.set_active(self.settings.get("debug", False))
        debug_row.connect("notify::active", self._on_debug_changed)
        debug_group.add(debug_row)
        advanced.add(debug_group)

        prefs.add(advanced)
        prefs.present(self.props.active_window)

    def _on_theme_changed(self, row, *_):
        themes = {0: "system", 1: "light", 2: "dark"}
        self.settings["theme"] = themes.get(row.get_selected(), "system")
        _save_settings(self.settings)
        self._apply_theme()

    def _on_icon_size_changed(self, row, *_):
        sizes = {0: "small", 1: "medium", 2: "large"}
        self.settings["icon_size"] = sizes.get(row.get_selected(), "medium")
        _save_settings(self.settings)

    def _on_clear_cache(self, btn, row):
        cache_dir = Path(GLib.get_user_cache_dir()) / "arasaac"
        if cache_dir.exists():
            for f in cache_dir.glob("*"):
                if f.is_file():
                    f.unlink()
        row.set_subtitle("0.0 MB")
        btn.set_sensitive(False)
        btn.set_label(_("Cleared"))

    def _on_debug_changed(self, row, *_):
        self.settings["debug"] = row.get_active()
        _save_settings(self.settings)

    # ── Export ────────────────────────────────────────────────

    def _on_export(self, *_):
        win = self.props.active_window
        if win and hasattr(win, 'steps'):
            from rutinkompis.export import show_export_dialog
            show_export_dialog(win, win.steps,
                               routine_name=getattr(win, 'routine_name', ''),
                               status_callback=getattr(win, '_set_status', None))

    # ── About ────────────────────────────────────────────────

    def _on_about(self, *_):
        about = Adw.AboutDialog(
            application_name=_("Rutinkompis"),
            application_icon="rutinkompis",
            version=__version__,
            developer_name="Daniel Nylander",
            website="https://github.com/yeager/rutinkompis",
            issue_url="https://github.com/yeager/rutinkompis/issues",
            support_url="https://www.autismappar.se",
            translate_url="https://app.transifex.com/danielnylander/rutinkompis",
            license_type=Gtk.License.GPL_3_0,
            developers=["Daniel Nylander <daniel@danielnylander.se>"],
            documenters=["Daniel Nylander"],
            artists=[_("ARASAAC pictograms (https://arasaac.org)")],
            copyright="© 2026 Daniel Nylander",
            comments=_(
                "Step-by-step visual routine guides with pictogram support "
                "for children with autism and language disorders.\n\n"
                "Part of the Autismappar suite — free tools for "
                "communication and daily structure."
            ),
            debug_info=f"Version: {__version__}\n"
                       f"GTK: {Gtk.get_major_version()}.{Gtk.get_minor_version()}\n"
                       f"Adwaita: {Adw.get_major_version()}.{Adw.get_minor_version()}\n"
                       f"Python: {sys.version}",
            debug_info_filename="rutinkompis-debug-info.txt",
        )
        about.add_link(_("Autismappar"), "https://www.autismappar.se")
        about.present(self.props.active_window)

    # ── Shortcuts ────────────────────────────────────────────

    def _on_shortcuts(self, *_):
        builder = Gtk.Builder()
        builder.add_from_string('''
        <interface>
          <object class="GtkShortcutsWindow" id="shortcuts">
            <property name="modal">true</property>
            <child>
              <object class="GtkShortcutsSection">
                <child>
                  <object class="GtkShortcutsGroup">
                    <property name="title" translatable="yes">General</property>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title" translatable="yes">Export</property>
                        <property name="accelerator">&lt;Control&gt;e</property>
                      </object>
                    </child>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title" translatable="yes">Preferences</property>
                        <property name="accelerator">&lt;Control&gt;comma</property>
                      </object>
                    </child>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title" translatable="yes">Keyboard Shortcuts</property>
                        <property name="accelerator">&lt;Control&gt;slash</property>
                      </object>
                    </child>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title" translatable="yes">About</property>
                        <property name="accelerator">F1</property>
                      </object>
                    </child>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title" translatable="yes">Quit</property>
                        <property name="accelerator">&lt;Control&gt;q</property>
                      </object>
                    </child>
                  </object>
                </child>
              </object>
            </child>
          </object>
        </interface>''')
        win = builder.get_object("shortcuts")
        win.set_transient_for(self.props.active_window)
        win.present()


def main():
    app = RutinkompisApp()
    app.run(sys.argv)
