---
name: pyinstaller-packaging
description: Explains how PyInstaller is used to bundle Everscript into standalone executables via make.py and everscript.spec, handling dependencies and CI/CD.
---

# PyInstaller Packaging & Distribution

To allow romhackers and community modders to compile Everscript without requiring a local Python installation or virtual environment, the project uses **PyInstaller** to package the entire compiler into standalone single-file executables.

---

## 1. Why PyInstaller is Used

- **Zero-Dependency Execution:** Bundles the Python runtime, bytecode interpreter, and all external dependencies (`rply`, `numpy`, `injector`, `ujson`, `ips_util`) into a single executable.
- **Multi-Platform Support:** Distributes binaries for **macOS** (`dist/everscript_mac`), **Linux** (`dist/everscript`), and **Windows** (`dist/everscript.exe`).

---

## 2. Configuration & Build Files

### 2.1 `everscript.spec`
The PyInstaller specification file controls how dependencies and assets are bundled:
```python
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['everscript.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['rply', 'numpy', 'injector', 'ujson', 'ips_util'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='everscript',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
```

### 2.2 `make.py`
A simple wrapper script that launches PyInstaller using the repository's `.spec` file:
```python
import subprocess
subprocess.run(["pyinstaller", "--clean", "everscript.spec"])
```

---

## 3. How to Build Locally

To compile a standalone binary on your local machine:
```bash
# Ensure virtualenv is active and dependencies are installed
.venv/bin/pip install -r requirements.txt

# Run the build script
.venv/bin/python3 make.py
```

The resulting binary is written to `dist/everscript` (or `dist/everscript_mac`).

### Verifying the Packaged Binary:
Run the standalone binary directly on a sample script without invoking Python:
```bash
./dist/everscript_mac in/practice/main.evs
```
Confirm that:
1. `out/everscript.ips` is successfully created.
2. No `ModuleNotFoundError` or hidden import warnings are thrown.

---

## 4. GitHub Actions CI/CD Workflows

Automated builds are configured in:
- `.github/workflows/pyinstaller-linux.yml`: Runs on `ubuntu-latest`, packages the Linux executable, and uploads release artifacts.
- `.github/workflows/pyinstaller-windows.yml`: Runs on `windows-latest`, generates `everscript.exe`, and uploads release artifacts.
