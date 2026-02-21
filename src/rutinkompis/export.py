"""Export/print functionality for Rutinkompis."""

import csv
import io
import json
from datetime import datetime

import gettext
_ = gettext.gettext

from rutinkompis import __version__

APP_LABEL = _("Routine Buddy")
AUTHOR = "Daniel Nylander"
WEBSITE = "www.autismappar.se"

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib


def routine_to_csv(steps, routine_name=""):
    """Export routine steps as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([_("Step"), _("Activity"), _("Duration (min)"), _("Completed")])
    for i, (emoji, name, mins, term) in enumerate(steps, 1):
        writer.writerow([i, name, mins, _("No")])
    writer.writerow([])
    writer.writerow([f"{APP_LABEL} v{__version__} — {WEBSITE}"])
    return output.getvalue()


def routine_to_json(steps, routine_name=""):
    """Export routine steps as JSON."""
    data = {
        "app": APP_LABEL,
        "version": __version__,
        "author": AUTHOR,
        "exported": datetime.now().isoformat(),
        "routine": routine_name,
        "steps": [
            {"step": i + 1, "name": name, "emoji": emoji, "minutes": mins}
            for i, (emoji, name, mins, term) in enumerate(steps)
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def routine_to_pdf(steps, routine_name, output_path):
    """Export routine as visual A4 PDF with step numbers."""
    try:
        import cairo
    except ImportError:
        try:
            import cairocffi as cairo
        except ImportError:
            return False

    width, height = 595, 842
    surface = cairo.PDFSurface(output_path, width, height)
    ctx = cairo.Context(surface)

    ctx.set_font_size(24)
    ctx.move_to(40, 50)
    ctx.show_text(routine_name or _("My Routine"))

    ctx.set_font_size(12)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.move_to(40, 70)
    ctx.show_text(datetime.now().strftime("%Y-%m-%d"))
    ctx.set_source_rgb(0, 0, 0)

    y = 100
    row_h = 70

    for i, (emoji, name, mins, term) in enumerate(steps, 1):
        if y + row_h > height - 40:
            surface.show_page()
            y = 40

        # Step number circle
        ctx.set_source_rgb(0.2, 0.5, 0.9)
        ctx.arc(60, y + 30, 18, 0, 6.283)
        ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_font_size(16)
        ctx.move_to(54 if i < 10 else 48, y + 36)
        ctx.show_text(str(i))
        ctx.set_source_rgb(0, 0, 0)

        # Emoji
        ctx.set_font_size(22)
        ctx.move_to(90, y + 35)
        ctx.show_text(emoji)

        # Name
        ctx.set_font_size(18)
        ctx.move_to(125, y + 28)
        ctx.show_text(name)

        # Duration
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.move_to(125, y + 48)
        ctx.show_text(_("%d min") % mins)
        ctx.set_source_rgb(0, 0, 0)

        # Checkbox
        ctx.set_line_width(1.5)
        ctx.rectangle(510, y + 15, 22, 22)
        ctx.stroke()

        # Separator
        ctx.set_source_rgb(0.9, 0.9, 0.9)
        ctx.set_line_width(0.5)
        ctx.move_to(40, y + row_h - 4)
        ctx.line_to(width - 40, y + row_h - 4)
        ctx.stroke()
        ctx.set_source_rgb(0, 0, 0)

        y += row_h

    # Footer
    ctx.set_font_size(9)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.move_to(40, height - 20)
    ctx.show_text(f"{APP_LABEL} v{__version__} — {WEBSITE} — {datetime.now().strftime('%Y-%m-%d')}")

    surface.finish()
    return True


def show_export_dialog(window, steps, routine_name="", status_callback=None):
    """Show export dialog."""
    dialog = Adw.AlertDialog.new(
        _("Export Routine"),
        _("Choose export format:")
    )
    dialog.add_response("cancel", _("Cancel"))
    dialog.add_response("csv", _("CSV"))
    dialog.add_response("json", _("JSON"))
    dialog.add_response("pdf", _("PDF"))
    dialog.set_default_response("pdf")
    dialog.set_close_response("cancel")
    dialog.connect("response", _on_export_response, window, steps, routine_name, status_callback)
    dialog.present(window)


def _on_export_response(dialog, response, window, steps, routine_name, status_callback):
    if response == "cancel":
        return
    if response == "csv":
        content = routine_to_csv(steps, routine_name)
        _save_text(window, content, "csv", status_callback)
    elif response == "json":
        content = routine_to_json(steps, routine_name)
        _save_text(window, content, "json", status_callback)
    elif response == "pdf":
        _save_pdf(window, steps, routine_name, status_callback)


def _save_text(window, content, ext, status_callback):
    fd = Gtk.FileDialog.new()
    fd.set_title(_("Save Export"))
    fd.set_initial_name(f"rutinkompis_{datetime.now().strftime('%Y%m%d')}.{ext}")
    fd.save(window, None, _on_text_done, content, ext, status_callback)


def _on_text_done(fd, result, content, ext, status_callback):
    try:
        gfile = fd.save_finish(result)
    except GLib.Error:
        return
    try:
        with open(gfile.get_path(), "w") as f:
            f.write(content)
        if status_callback:
            status_callback(_("Exported %s") % ext.upper())
    except Exception as e:
        if status_callback:
            status_callback(_("Export error: %s") % str(e))


def _save_pdf(window, steps, routine_name, status_callback):
    fd = Gtk.FileDialog.new()
    fd.set_title(_("Save PDF"))
    fd.set_initial_name(f"rutinkompis_{datetime.now().strftime('%Y%m%d')}.pdf")
    fd.save(window, None, _on_pdf_done, steps, routine_name, status_callback)


def _on_pdf_done(fd, result, steps, routine_name, status_callback):
    try:
        gfile = fd.save_finish(result)
    except GLib.Error:
        return
    try:
        ok = routine_to_pdf(steps, routine_name, gfile.get_path())
        if ok and status_callback:
            status_callback(_("PDF exported"))
        elif not ok and status_callback:
            status_callback(_("PDF export requires pycairo"))
    except Exception as e:
        if status_callback:
            status_callback(_("Export error: %s") % str(e))
