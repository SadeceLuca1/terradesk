"""
TerraDesk Installer
Bağımlılıkları kurar ve oyunu başlatmaya hazırlar.
"""

import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

REQUIRED = [
    "pygame-ce>=2.5.0",
    "pywin32>=305",
]

TITLE = "TerraDesk Kurulum"

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITLE)
        self.resizable(False, False)
        self.geometry("480x320")
        self.configure(bg="#1a1a2e")
        self._center()
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 480) // 2
        y = (sh - 320) // 2
        self.geometry(f"480x320+{x}+{y}")

    def _build_ui(self):
        # Başlık
        tk.Label(self, text="🌍 TerraDesk", font=("Segoe UI", 22, "bold"),
                 fg="#e8d5b7", bg="#1a1a2e").pack(pady=(24, 4))
        tk.Label(self, text="Desktop Village Simulation", font=("Segoe UI", 10),
                 fg="#8899aa", bg="#1a1a2e").pack()

        # Durum etiketi
        self.status_var = tk.StringVar(value="Kuruluma başlamak için düğmeye basın.")
        tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 9),
                 fg="#ccddee", bg="#1a1a2e", wraplength=440).pack(pady=(20, 6))

        # Progress bar
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#0f3460",
                        background="#e94560", thickness=18)
        self.progress = ttk.Progressbar(self, length=420, mode="determinate",
                                        style="TProgressbar")
        self.progress.pack(pady=4)

        # Log kutusu
        self.log = tk.Text(self, height=4, width=56, font=("Consolas", 8),
                           bg="#0f0f1a", fg="#aaffaa", relief="flat",
                           state="disabled", bd=0)
        self.log.pack(padx=20, pady=(8, 0))

        # Buton
        self.btn = tk.Button(self, text="  Kur  ", font=("Segoe UI", 11, "bold"),
                             bg="#e94560", fg="white", relief="flat",
                             activebackground="#c73652", cursor="hand2",
                             command=self._start_install, padx=16, pady=6)
        self.btn.pack(pady=14)

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    def _start_install(self):
        self.btn.configure(state="disabled", text="Kuruluyor…")
        threading.Thread(target=self._run_install, daemon=True).start()

    def _run_install(self):
        total = len(REQUIRED) + 1   # +1 pip upgrade
        done  = 0

        # pip yükselt
        self._set_status("pip güncelleniyor…")
        self._run(["python", "-m", "pip", "install", "--upgrade", "pip", "-q"])
        done += 1
        self.progress["value"] = int(done / total * 100)

        # Paketleri kur
        for pkg in REQUIRED:
            self._set_status(f"Kuruluyor: {pkg}")
            ok = self._run(["python", "-m", "pip", "install", pkg, "-q"])
            done += 1
            self.progress["value"] = int(done / total * 100)
            if not ok:
                self.after(0, self._failed, pkg)
                return

        self.after(0, self._done)

    def _run(self, cmd):
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
            if proc.stdout.strip():
                self.after(0, self._log, proc.stdout.strip()[-120:])
            if proc.returncode != 0:
                self.after(0, self._log, f"HATA: {proc.stderr.strip()[-120:]}")
                return False
            return True
        except Exception as e:
            self.after(0, self._log, str(e))
            return False

    def _done(self):
        self.progress["value"] = 100
        self._set_status("✅ Kurulum tamamlandı!")
        self._log("Oyunu başlatmak için: python main.py")
        self.btn.configure(state="normal", text="  Kapat  ",
                           command=self.destroy, bg="#2ecc71")

    def _failed(self, pkg):
        self._set_status(f"❌ Kurulum başarısız: {pkg}")
        self.btn.configure(state="normal", text="  Tekrar Dene  ",
                           command=self._retry)

    def _retry(self):
        self.progress["value"] = 0
        self.btn.configure(state="disabled", text="Kuruluyor…")
        threading.Thread(target=self._run_install, daemon=True).start()


def main():
    # Python sürüm kontrolü
    if sys.version_info < (3, 11):
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Python Sürümü Hatalı",
                f"Python 3.11 veya üzeri gerekli.\n"
                f"Mevcut sürüm: {sys.version}\n\n"
                "https://www.python.org/downloads/ adresinden güncelleyin."
            )
        except Exception:
            pass
        sys.exit(1)

    app = InstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()