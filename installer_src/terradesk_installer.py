"""
TerraDesk Windows Installer
Self-contained: extracts TerraDesk.exe, creates shortcuts, registers uninstaller.
Compiled with PyInstaller: the main EXE is embedded as data via --add-data.
"""
import sys, os, shutil, ctypes, winreg, threading, time

# ── Embedded EXE path (PyInstaller temp dir) ─────────────────────────────────
def _resource(relative_path: str) -> str:
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

APP_NAME     = "TerraDesk"
APP_VERSION  = "1.0.0"
APP_EXE      = "TerraDesk.exe"
PUBLISHER    = "SadeceLuca1"
INSTALL_DIR  = os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), APP_NAME)
UNINSTALL_KEY = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"

# ── Helpers ───────────────────────────────────────────────────────────────────
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)

def create_shortcut(target: str, shortcut_path: str, icon: str = None, description: str = ""):
    """Create a .lnk Windows shortcut using COM."""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        sc = shell.CreateShortCut(shortcut_path)
        sc.Targetpath = target
        sc.WorkingDirectory = os.path.dirname(target)
        sc.Description = description
        if icon:
            sc.IconLocation = icon
        sc.save()
    except ImportError:
        # Fallback: use PowerShell
        ps = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "{target}"; '
            f'$s.WorkingDirectory = "{os.path.dirname(target)}"; '
            f'$s.Save()'
        )
        os.system(f'powershell -Command "{ps}"')

def register_uninstaller(install_dir: str, uninstaller: str):
    """Write to Windows registry so it appears in Add/Remove Programs."""
    try:
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, UNINSTALL_KEY)
        winreg.SetValueEx(key, "DisplayName",        0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion",     0, winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher",          0, winreg.REG_SZ, PUBLISHER)
        winreg.SetValueEx(key, "InstallLocation",    0, winreg.REG_SZ, install_dir)
        winreg.SetValueEx(key, "UninstallString",    0, winreg.REG_SZ, f'"{uninstaller}" /uninstall')
        winreg.SetValueEx(key, "DisplayIcon",        0, winreg.REG_SZ, os.path.join(install_dir, APP_EXE))
        winreg.SetValueEx(key, "URLInfoAbout",       0, winreg.REG_SZ, "https://github.com/SadeceLuca1/terradesk")
        winreg.SetValueEx(key, "NoModify",           0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair",           0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Registry warning: {e}")
        return False

def unregister_uninstaller():
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, UNINSTALL_KEY)
    except Exception:
        pass


# ── GUI Installer ─────────────────────────────────────────────────────────────
def run_installer_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title(f"{APP_NAME} Setup")
    root.geometry("520x380")
    root.resizable(False, False)
    root.configure(bg="#1a1c24")

    # Icon
    try:
        ico = _resource("icon.ico")
        if os.path.exists(ico):
            root.iconbitmap(ico)
    except Exception:
        pass

    # Header
    header = tk.Frame(root, bg="#12141e", height=80)
    header.pack(fill="x")
    tk.Label(header, text="TerraDesk", font=("Segoe UI", 22, "bold"),
             fg="#5aaeff", bg="#12141e").pack(pady=(16, 2))
    tk.Label(header, text="A Living World. Your World.",
             font=("Segoe UI", 10), fg="#8899bb", bg="#12141e").pack()

    # Body
    body = tk.Frame(root, bg="#1a1c24", padx=24, pady=16)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=f"Install Location:", font=("Segoe UI", 9),
             fg="#aabbcc", bg="#1a1c24", anchor="w").pack(fill="x")

    dir_var = tk.StringVar(value=INSTALL_DIR)
    dir_entry = tk.Entry(body, textvariable=dir_var, font=("Segoe UI", 9),
                         bg="#252836", fg="#dde3f0", insertbackground="white",
                         relief="flat", bd=4)
    dir_entry.pack(fill="x", pady=(4, 12))

    desktop_var = tk.BooleanVar(value=True)
    start_var   = tk.BooleanVar(value=True)
    startup_var = tk.BooleanVar(value=False)

    for text, var in [
        ("Create Desktop shortcut", desktop_var),
        ("Add to Start Menu",       start_var),
        ("Launch at Windows startup", startup_var),
    ]:
        cb = tk.Checkbutton(body, text=text, variable=var,
                            font=("Segoe UI", 9), fg="#ccd3e8", bg="#1a1c24",
                            selectcolor="#252836", activebackground="#1a1c24",
                            activeforeground="#ffffff")
        cb.pack(anchor="w", pady=1)

    # Progress
    prog_frame = tk.Frame(body, bg="#1a1c24")
    prog_frame.pack(fill="x", pady=(12, 0))
    status_var = tk.StringVar(value="Ready to install.")
    tk.Label(prog_frame, textvariable=status_var, font=("Segoe UI", 9),
             fg="#8899bb", bg="#1a1c24", anchor="w").pack(fill="x")
    progress = ttk.Progressbar(prog_frame, length=460, mode="determinate")
    progress.pack(fill="x", pady=4)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TProgressbar", troughcolor="#252836", background="#5aaeff")

    # Buttons
    btn_frame = tk.Frame(root, bg="#12141e", height=52)
    btn_frame.pack(fill="x", side="bottom")

    def do_install():
        install_dir = dir_var.get().strip()
        btn_install.config(state="disabled")
        btn_cancel.config(state="disabled")

        def install_thread():
            steps = [
                ("Creating install directory...", 20),
                ("Copying TerraDesk.exe...",      55),
                ("Creating shortcuts...",          75),
                ("Registering uninstaller...",     90),
                ("Done!",                         100),
            ]
            try:
                # Step 1
                status_var.set(steps[0][0]); progress["value"] = 5; root.update()
                os.makedirs(install_dir, exist_ok=True)
                time.sleep(0.3)
                progress["value"] = steps[0][1]; root.update()

                # Step 2 – copy main EXE
                status_var.set(steps[1][0]); root.update()
                src_exe = _resource(APP_EXE)
                dst_exe = os.path.join(install_dir, APP_EXE)
                shutil.copy2(src_exe, dst_exe)
                # Copy icon if present
                src_ico = _resource("icon.ico")
                if os.path.exists(src_ico):
                    shutil.copy2(src_ico, os.path.join(install_dir, "icon.ico"))
                progress["value"] = steps[1][1]; root.update()

                # Step 3 – shortcuts
                status_var.set(steps[2][0]); root.update()
                if desktop_var.get():
                    desktop = os.path.join(os.environ.get("USERPROFILE",""), "Desktop")
                    create_shortcut(dst_exe, os.path.join(desktop, f"{APP_NAME}.lnk"),
                                    dst_exe, "TerraDesk – Village Simulation")
                if start_var.get():
                    start = os.path.join(os.environ.get("APPDATA",""),
                                         "Microsoft","Windows","Start Menu","Programs")
                    os.makedirs(start, exist_ok=True)
                    create_shortcut(dst_exe, os.path.join(start, f"{APP_NAME}.lnk"),
                                    dst_exe, "TerraDesk – Village Simulation")
                if startup_var.get():
                    startup = os.path.join(os.environ.get("APPDATA",""),
                                           "Microsoft","Windows","Start Menu",
                                           "Programs","Startup")
                    os.makedirs(startup, exist_ok=True)
                    create_shortcut(dst_exe, os.path.join(startup, f"{APP_NAME}.lnk"))
                progress["value"] = steps[2][1]; root.update()

                # Step 4 – registry
                status_var.set(steps[3][0]); root.update()
                # Copy installer itself as uninstaller
                uninstaller = os.path.join(install_dir, f"{APP_NAME}_Uninstall.exe")
                try:
                    shutil.copy2(sys.executable, uninstaller)
                except Exception:
                    uninstaller = dst_exe
                register_uninstaller(install_dir, uninstaller)
                progress["value"] = steps[3][1]; root.update()

                # Done
                status_var.set(steps[4][0])
                progress["value"] = 100; root.update()
                time.sleep(0.5)

                result = messagebox.askyesno(
                    "Installation Complete",
                    f"TerraDesk has been installed!\n\nLaunch TerraDesk now?",
                    icon="info"
                )
                if result:
                    os.startfile(dst_exe)
                root.destroy()

            except Exception as exc:
                status_var.set(f"Error: {exc}")
                btn_install.config(state="normal")
                btn_cancel.config(state="normal")
                messagebox.showerror("Install Error", str(exc))

        threading.Thread(target=install_thread, daemon=True).start()

    btn_install = tk.Button(btn_frame, text="Install", width=14,
                            font=("Segoe UI", 10, "bold"),
                            bg="#3a7bcc", fg="white", relief="flat",
                            activebackground="#4a8bdc", cursor="hand2",
                            command=do_install)
    btn_install.pack(side="right", padx=(8, 16), pady=10)

    btn_cancel = tk.Button(btn_frame, text="Cancel", width=10,
                           font=("Segoe UI", 10), bg="#2a2d3e", fg="#aabbcc",
                           relief="flat", activebackground="#3a3d4e",
                           cursor="hand2", command=root.destroy)
    btn_cancel.pack(side="right", padx=4, pady=10)

    root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "/uninstall" in sys.argv:
        # Uninstall mode
        if not is_admin():
            run_as_admin()
        try:
            install_dir = INSTALL_DIR
            # Try to get from registry
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, UNINSTALL_KEY)
                install_dir, _ = winreg.QueryValueEx(key, "InstallLocation")
                winreg.CloseKey(key)
            except Exception:
                pass
            # Remove shortcuts
            for loc in [
                os.path.join(os.environ.get("USERPROFILE",""), "Desktop"),
                os.path.join(os.environ.get("APPDATA",""), "Microsoft","Windows","Start Menu","Programs"),
                os.path.join(os.environ.get("APPDATA",""), "Microsoft","Windows","Start Menu","Programs","Startup"),
            ]:
                lnk = os.path.join(loc, f"{APP_NAME}.lnk")
                if os.path.exists(lnk):
                    os.remove(lnk)
            unregister_uninstaller()
            # Remove install dir (delayed – can't delete while running)
            bat = os.path.join(os.environ.get("TEMP",""), "terradesk_uninstall.bat")
            with open(bat, "w") as f:
                f.write(f'@echo off\ntimeout /t 2 /nobreak >nul\nrmdir /s /q "{install_dir}"\ndel "%~f0"\n')
            os.startfile(bat)
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, f"Uninstall error: {e}", "TerraDesk", 0x10)
    else:
        # Install mode
        if not is_admin():
            run_as_admin()
        run_installer_gui()