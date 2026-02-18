# Rutinkompis

Step-by-step visual routine guides for children with autism.

![Screenshot](screenshots/screenshot.png)

## Features

Create and follow routines (morning, evening, school). Each step has image + text + timer. Mark steps complete. Star rewards for motivation.

## Requirements

- Python 3.10+
- GTK4 / libadwaita
- PyGObject

## Installation

```bash
# Install dependencies (Fedora/RHEL)
sudo dnf install python3-gobject gtk4 libadwaita

# Install dependencies (Debian/Ubuntu)
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Run from source
PYTHONPATH=src python3 -c "from rutinkompis.main import main; main()"
```

## License

GPL-3.0-or-later

## Author

Daniel Nylander

## Links

- [GitHub](https://github.com/yeager/rutinkompis)
- [Issues](https://github.com/yeager/rutinkompis/issues)
- [Translations](https://app.transifex.com/danielnylander/rutinkompis)
