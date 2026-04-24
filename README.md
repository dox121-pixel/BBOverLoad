# BBOverLoad

A toolkit for decompiling mobile game APKs into editable, recompilable projects.

BBOverLoad wraps industry-standard tools ([apktool](https://apktool.org/) and [jadx](https://github.com/skylot/jadx)) behind a clean Python CLI so you can:

- **Decompile** any APK into editable smali + resources (via apktool) or readable Java source code (via jadx).
- **Recompile** a modified smali/resource project back into a new APK (via apktool).
- **Sign** the rebuilt APK with a debug or custom keystore so it can be installed on a device or emulator.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Command Reference](#command-reference)
5. [Project Layout](#project-layout)
6. [Contributing](#contributing)
7. [License](#license)

---

## Requirements

| Dependency | Purpose |
|---|---|
| Python ≥ 3.8 | Runs the CLI |
| Java ≥ 11 (JDK) | Required by apktool and jadx |
| [apktool](https://apktool.org/) | Smali decompile / recompile |
| [jadx](https://github.com/skylot/jadx) | Java source decompile |
| Android SDK `build-tools` (optional) | Provides `zipalign` and `apksigner` |

Install Java-based tools automatically with the provided helper script (see [Installation](#installation)).

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dox121-pixel/BBOverLoad.git
cd BBOverLoad
```

### 2. Install Python dependencies

```bash
pip install -e .
```

### 3. Install apktool and jadx

```bash
bash scripts/install_tools.sh
```

This script downloads the latest stable releases of apktool and jadx into `~/.bboverload/tools/` and adds wrapper scripts to `~/.local/bin/` (Linux/macOS).

---

## Quick Start

```bash
# Decompile an APK to smali + resources (apktool)
bboverload decompile game.apk

# Decompile an APK to Java source (jadx)
bboverload decompile --mode java game.apk

# Edit files inside output/game/ ...

# Recompile the modified project back to an APK
bboverload recompile output/game/

# Sign the rebuilt APK with the built-in debug key
bboverload sign output/game/dist/game.apk
```

---

## Command Reference

### `bboverload decompile`

```
bboverload decompile [OPTIONS] APK_PATH

Options:
  --mode [smali|java]   Decompile mode (default: smali)
  --output DIR          Output directory (default: output/<apk_stem>/)
  --no-res              Skip resource decoding (smali mode only)
  --help                Show this message and exit.
```

### `bboverload recompile`

```
bboverload recompile [OPTIONS] PROJECT_DIR

Options:
  --output DIR          Where to place the rebuilt APK (default: <PROJECT_DIR>/dist/)
  --help                Show this message and exit.
```

### `bboverload sign`

```
bboverload sign [OPTIONS] APK_PATH

Options:
  --keystore FILE       Path to a .jks / .keystore file (default: debug key)
  --alias TEXT          Key alias (default: androiddebugkey)
  --storepass TEXT      Keystore password (default: android)
  --keypass TEXT        Key password (default: android)
  --output FILE         Output signed APK path (default: <APK_PATH>_signed.apk)
  --help                Show this message and exit.
```

---

## Project Layout

```
BBOverLoad/
├── bboverload/
│   ├── __init__.py       Package metadata
│   ├── cli.py            Entry-point (click)
│   ├── decompile.py      Decompilation logic (apktool / jadx)
│   ├── recompile.py      Recompilation logic (apktool)
│   └── sign.py           APK signing logic (jarsigner / apksigner)
├── scripts/
│   └── install_tools.sh  Downloads apktool + jadx
├── tests/
│   ├── test_decompile.py
│   ├── test_recompile.py
│   └── test_sign.py
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

---

## Contributing

Pull requests are welcome! Please open an issue first if you want to discuss a large change.

1. Fork the repo and create your feature branch: `git checkout -b feature/my-feature`
2. Commit your changes: `git commit -m 'Add my feature'`
3. Push to the branch: `git push origin feature/my-feature`
4. Open a pull request.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
