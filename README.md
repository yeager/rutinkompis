# Rutinkompis

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/yeager/rutinkompis/releases)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Transifex](https://img.shields.io/badge/Transifex-Translate-green.svg)](https://www.transifex.com/danielnylander/rutinkompis/)

Step-by-step visual routine guides with ARASAAC pictograms — GTK4/Adwaita.

> **For:** Children with autism, ADHD, or intellectual disabilities who benefit from visual step-by-step routine guides with pictogram support.

![Screenshot](screenshots/main.png)

## Features

- **Visual routines** — step-by-step guides with images
- **ARASAAC pictograms** — automatic download of free symbols
- **Checkable steps** — mark steps as done
- **Custom routines** — create your own sequences
- **Timer support** — time limits per step
- **Dark/light theme** toggle

## Installation

### Debian/Ubuntu

```bash
echo "deb [signed-by=/usr/share/keyrings/yeager-keyring.gpg] https://yeager.github.io/debian-repo stable main" | sudo tee /etc/apt/sources.list.d/yeager.list
curl -fsSL https://yeager.github.io/debian-repo/yeager-keyring.gpg | sudo tee /usr/share/keyrings/yeager-keyring.gpg > /dev/null
sudo apt update && sudo apt install rutinkompis
```

### Fedora/openSUSE

```bash
sudo dnf config-manager --add-repo https://yeager.github.io/rpm-repo/yeager.repo
sudo dnf install rutinkompis
```

### From source

```bash
git clone https://github.com/yeager/rutinkompis.git
cd rutinkompis && pip install -e .
rutinkompis
```

## ARASAAC Attribution

Pictographic symbols © Gobierno de Aragón, created by Sergio Palao for [ARASAAC](https://arasaac.org), distributed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Translation

Help translate on [Transifex](https://www.transifex.com/danielnylander/rutinkompis/).

## License

GPL-3.0-or-later — see [LICENSE](LICENSE) for details.

## Author

**Daniel Nylander** — [danielnylander.se](https://danielnylander.se)
