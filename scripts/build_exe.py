#!/usr/bin/env python3
"""
TerraDesk – Build Script
Compiles main.py into a single-file Windows executable via PyInstaller.
Run from the project root:
    python scripts/build_exe.py
"""

import subprocess
import sys
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

print("=" * 60)
print("  TerraDesk – EXE Builder")
print("=" * 60)

# 1. Smoke-test first
print("\n[1/3] Running headless smoke-test...")
result = subprocess.run(
    [sys.executable, "main.py", "--test-engine"],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("FAIL: smoke-test failed")
    print(result.stdout)
    print(result.stderr)
    sys.exit(1)
print("  PASS:", result.stdout.strip())

# 2. Build EXE
print("\n[2/3] Building EXE with PyInstaller...")
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--noconsole",
    "--name", "TerraDesk",
    "--distpath", "dist",
    "--workpath", "build",
    "--specpath", ".",
    "--hidden-import", "pygame",
    "--hidden-import", "pygame.font",
    "--hidden-import", "pygame.mixer",
    "main.py",
]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
if result.returncode != 0:
    print("FAIL: PyInstaller failed")
    print(result.stderr[-2000:])
    sys.exit(1)

# 3. Report
exe_path = os.path.join(ROOT, "dist", "TerraDesk.exe")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"\n[3/3] SUCCESS!")
    print(f"  EXE: {exe_path}")
    print(f"  Size: {size_mb:.1f} MB")
else:
    print("\n[3/3] WARNING: EXE not found at expected path")
    print("  Check the dist/ folder manually")

print("\nDone. Upload dist/TerraDesk.exe to your GitHub release.")