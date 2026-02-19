# Rutinkompis

Step-by-step visual routine guides for children with autism.

> **Målgrupp / Target audience:** Barn och vuxna med autism, ADHD, intellektuell
> funktionsnedsättning och andra kognitiva funktionsnedsättningar som behöver
> steg-för-steg visuellt stöd för dagliga rutiner. Perfekt för morgonrutiner,
> kvällsrutiner och skolrutiner. Även användbart i LSS-verksamhet och habilitering.
>
> **For:** Children and adults with autism spectrum disorder (ASD), ADHD, intellectual
> disabilities, and other cognitive disabilities who need step-by-step visual routine
> guides. Perfect for morning routines, evening routines, and school routines. Also
> useful in disability services and rehabilitation settings.

![Screenshot](screenshots/screenshot.png)

## Features

- Create and follow routines (morning, evening, school)
- Each step has image + text + timer
- Mark steps complete with visual feedback
- Star rewards for motivation
- Dark/light theme toggle

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
