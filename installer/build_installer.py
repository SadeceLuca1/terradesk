"""
TerraDesk – Windows Installer Builder
Checks for Inno Setup, then compiles TerraDesk_Setup.exe
Run: python installer/build_installer.py
"""
import os, sys, subprocess, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISS  = os.path.join(ROOT, "installer", "terradesk_setup.iss")
ISCC_PATHS = [
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
    r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    r"C:\Program Files\Inno Setup 5\ISCC.exe",
]

print("=" * 60)
print("  TerraDesk – Windows Installer Builder")
print("=" * 60)

# 1. Check EXE exists
exe = os.path.join(ROOT, "dist", "TerraDesk.exe")
if not os.path.exists(exe):
    print("ERROR: dist/TerraDesk.exe not found.")
    print("Run:  python scripts/build_exe.py  first.")
    sys.exit(1)
print(f"[OK] Found {os.path.getsize(exe)//1024//1024} MB EXE")

# 2. Create release dir
os.makedirs(os.path.join(ROOT, "release"), exist_ok=True)

# 3. Find Inno Setup
iscc = None
for p in ISCC_PATHS:
    if os.path.exists(p):
        iscc = p
        break

if iscc is None:
    print()
    print("Inno Setup not found on this machine.")
    print()
    print("Inno Setup'ı buradan ücretsiz indir ve kur:")
    print("  https://jrsoftware.org/isdl.php")
    print()
    print("Kurduktan sonra bu scripti tekrar çalıştır:")
    print("  python installer/build_installer.py")
    print()
    print("Alternatif: installer/terradesk_setup.iss dosyasını")
    print("Inno Setup IDE'sinde aç ve Compile et.")
    sys.exit(0)

print(f"[OK] Inno Setup: {iscc}")

# 4. Compile
print("\nCompiling installer...")
result = subprocess.run([iscc, ISS], capture_output=True, text=True, cwd=ROOT)
print(result.stdout)
if result.returncode != 0:
    print("FAIL:", result.stderr)
    sys.exit(1)

# 5. Report
out = os.path.join(ROOT, "release", "TerraDesk_Setup.exe")
if os.path.exists(out):
    mb = os.path.getsize(out) / 1024 / 1024
    print(f"\nSUCCESS!")
    print(f"  Installer: {out}")
    print(f"  Size: {mb:.1f} MB")
    print("\nUpload 'release/TerraDesk_Setup.exe' to your GitHub release!")
else:
    print("WARNING: Output file not found, check Inno Setup output above.")
