"""Main window for Rutinkompis."""
import gettext
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf

from . import arasaac
from .tts import speak

_ = gettext.gettext

# Each entry: (emoji_fallback, translated_label, minutes, arasaac_search_term)
ROUTINES = {
    _("Morning"): [
        ("🌅", _("Wake up"), 5, "wake up"),
        ("🚽", _("Go to toilet"), 5, "toilet"),
        ("🪥", _("Brush teeth"), 3, "brush teeth"),
        ("👕", _("Get dressed"), 10, "get dressed"),
        ("🥣", _("Eat breakfast"), 15, "breakfast"),
        ("🎒", _("Pack bag"), 5, "backpack"),
        ("👟", _("Put on shoes"), 3, "shoes"),
    ],
    _("Evening"): [
        ("🍽️", _("Eat dinner"), 20, "dinner"),
        ("🛁", _("Take a bath"), 15, "bath"),
        ("🪥", _("Brush teeth"), 3, "brush teeth"),
        ("📖", _("Read a book"), 15, "read"),
        ("🌙", _("Go to bed"), 5, "sleep"),
    ],
    _("School"): [
        ("📚", _("Take out books"), 3, "books"),
        ("✏️", _("Do exercises"), 20, "write"),
        ("🤚", _("Ask for help"), 2, "help"),
        ("📦", _("Pack up"), 5, "backpack"),
    ],
}


class RutinkompisWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, default_width=480, default_height=700,
                         title=_("Routine Buddy"))
        self.current_routine = list(ROUTINES.keys())[0]
        self.completed_steps = set()
        self.stars = 0
        self._provider = None
        self._build_ui()
        self._start_clock()

    def _get_provider(self):
        if self._provider is None:
            try:
                self._provider = arasaac.get_provider()
            except Exception:
                pass
        return self._provider

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        theme_btn = Gtk.Button(icon_name="weather-clear-night-symbolic",
                               tooltip_text=_("Toggle dark/light theme"))
        theme_btn.connect("clicked", self._toggle_theme)
        header.pack_end(theme_btn)

        menu = Gio.Menu()
        menu.append(_("Export Routine"), "app.export")
        menu.append(_("Preferences"), "app.preferences")
        menu.append(_("Keyboard Shortcuts"), "app.shortcuts")
        menu.append(_("About Routine Buddy"), "app.about")
        menu.append(_("Quit"), "app.quit")
        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        header.pack_end(menu_btn)

        # Stars display
        self.stars_label = Gtk.Label(label="⭐ 0")
        self.stars_label.add_css_class("title-2")
        header.pack_start(self.stars_label)

        # Routine selector
        routine_box = Gtk.Box(spacing=0, halign=Gtk.Align.CENTER)
        routine_box.add_css_class("linked")
        routine_box.set_margin_top(8)
        first = None
        for rname in ROUTINES:
            btn = Gtk.ToggleButton(label=rname)
            if first is None:
                first = btn
                btn.set_active(True)
            else:
                btn.set_group(first)
            btn.connect("toggled", self._on_routine_changed, rname)
            routine_box.append(btn)
        main_box.append(routine_box)

        # Steps list
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.steps_box.set_margin_start(8)
        self.steps_box.set_margin_end(8)
        self.steps_box.set_margin_top(8)
        scrolled.set_child(self.steps_box)
        main_box.append(scrolled)

        # Celebration label
        self.celebration = Gtk.Label(label="")
        self.celebration.add_css_class("title-1")
        self.celebration.set_margin_top(8)
        main_box.append(self.celebration)

        # Progress
        self.progress = Gtk.ProgressBar()
        self.progress.set_margin_start(12)
        self.progress.set_margin_end(12)
        self.progress.set_margin_top(4)
        main_box.append(self.progress)

        # Status
        self.status_label = Gtk.Label(label="", xalign=0)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_bottom(4)
        main_box.append(self.status_label)

        self._populate_steps()

    def _make_icon(self, emoji, arasaac_term):
        """Create icon widget: ARASAAC pictogram if available, else emoji."""
        provider = self._get_provider()
        if provider and arasaac_term:
            try:
                path = provider.get_pictogram(arasaac_term, lang="en", resolution=300)
                if path:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        path, 48, 48, True)
                    image = Gtk.Image.new_from_pixbuf(pixbuf)
                    image.set_pixel_size(48)
                    image.set_margin_start(12)
                    image.set_margin_top(8)
                    image.set_margin_bottom(8)
                    return image
            except Exception:
                pass

        icon = Gtk.Label(label=emoji)
        icon.add_css_class("title-1")
        icon.set_margin_start(12)
        icon.set_margin_top(8)
        icon.set_margin_bottom(8)
        return icon

    def _populate_steps(self):
        child = self.steps_box.get_first_child()
        while child:
            nc = child.get_next_sibling()
            self.steps_box.remove(child)
            child = nc

        self.completed_steps.clear()
        self.celebration.set_label("")
        steps = ROUTINES.get(self.current_routine, [])

        for i, (emoji, name, mins, arasaac_term) in enumerate(steps):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.add_css_class("card")
            row.set_margin_start(4)
            row.set_margin_end(4)
            row.set_margin_top(2)
            row.set_margin_bottom(2)

            icon = self._make_icon(emoji, arasaac_term)
            row.append(icon)

            text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2,
                               hexpand=True)
            text_box.set_margin_top(8)
            text_box.set_margin_bottom(8)
            lbl = Gtk.Label(label=name, xalign=0)
            lbl.add_css_class("title-3")
            text_box.append(lbl)
            time_lbl = Gtk.Label(label=f"{mins} min", xalign=0)
            time_lbl.add_css_class("dim-label")
            text_box.append(time_lbl)
            row.append(text_box)

            speak_btn = Gtk.Button(icon_name="audio-speakers-symbolic")
            speak_btn.add_css_class("flat")
            speak_btn.add_css_class("circular")
            speak_btn.set_tooltip_text(_("Read aloud"))
            speak_btn.connect("clicked", lambda _, n=name: speak(n, "sv"))
            row.append(speak_btn)

            check = Gtk.CheckButton()
            check.set_margin_end(12)
            check.connect("toggled", self._on_step_toggled, i, row)
            row.append(check)

            self.steps_box.append(row)
        self._update_progress()

    def _on_step_toggled(self, check, index, row):
        if check.get_active():
            self.completed_steps.add(index)
            row.set_opacity(0.5)
            self.stars += 1
            self.stars_label.set_label(f"⭐ {self.stars}")
        else:
            self.completed_steps.discard(index)
            row.set_opacity(1.0)
        self._update_progress()

    def _update_progress(self):
        steps = ROUTINES.get(self.current_routine, [])
        total = len(steps)
        done = len(self.completed_steps)
        frac = done / total if total > 0 else 0
        self.progress.set_fraction(frac)
        self.progress.set_text(f"{done}/{total}")
        self.progress.set_show_text(True)

        if done == total and total > 0:
            self.celebration.set_label("🎉 " + _("All done! Great job!") + " ⭐🌟⭐")

    def _on_routine_changed(self, btn, rname):
        if btn.get_active():
            self.current_routine = rname
            self._populate_steps()

    def _toggle_theme(self, btn):
        mgr = Adw.StyleManager.get_default()
        if mgr.get_dark():
            mgr.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def _start_clock(self):
        GLib.timeout_add_seconds(1, self._update_clock)
        self._update_clock()

    def _update_clock(self):
        now = GLib.DateTime.new_now_local()
        self.status_label.set_label(now.format("%Y-%m-%d %H:%M:%S"))
        return True
