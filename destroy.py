import customtkinter as ctk
import os
import ctypes
import subprocess
import threading
import sys
import winreg
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# --- SİSTEM AYARLARI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ShadowProtocolUltimate(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SHADOW PROTOCOL // v8.0 ABSOLUTE")
        self.geometry("800x780")
        self.lang = "TR"
        
        # X Butonuna basınca tepsiyi gizle
        self.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)

        # Dil Sözlüğü
        self.text_data = {
            "TR": {
                "header": "SHADOW PROTOCOL: ABSOLUTE CONTROL",
                "warning": "⚠️ KRİTİK: Sistem arızalarından kullanıcı sorumludur. Bu araç Görev Zamanlayıcı kullanarak UAC engelini aşar. Sistem Geri Yükleme noktası almayı unutmayın!",
                "btn_ghost": "PROTOKOLÜ ŞİMDİ ÇALIŞTIR",
                "btn_lang": "LANG: ENGLISH",
                "check_tele": "Telemetri Servislerini Kökten Kapat",
                "check_pre": "Prefetch Dosyalarını Temizle",
                "check_log": "Windows Olay Loglarını Sıfırla",
                "check_ps": "PowerShell Komut Geçmişini Sil",
                "check_start": "Bilgisayar Açıldığında Başlat (UAC Bypass)",
                "check_autoclean": "Açılışta Otomatik Temizle",
                "console": "Sistem aktif. Komut bekleniyor...",
                "status": "DURUM: HAZIR"
            },
            "EN": {
                "header": "SHADOW PROTOCOL: ABSOLUTE CONTROL",
                "warning": "⚠️ CRITICAL: User is responsible for failures. This tool uses Task Scheduler to bypass UAC. Don't forget to create a Restore Point!",
                "btn_ghost": "EXECUTE PROTOCOL NOW",
                "btn_lang": "DİL: TÜRKÇE",
                "check_tele": "Disable Telemetry Services",
                "check_pre": "Wipe Prefetch Files",
                "check_log": "Reset System Event Logs",
                "check_ps": "Clear PowerShell History",
                "check_start": "Run at Startup (UAC Bypass)",
                "check_autoclean": "Auto-Clean on Startup",
                "console": "System active. Awaiting commands...",
                "status": "STATUS: READY"
            }
        }

        # Değişkenler
        self.check_telemetry = ctk.BooleanVar(value=True)
        self.check_prefetch = ctk.BooleanVar(value=True)
        self.check_logs = ctk.BooleanVar(value=True)
        self.check_ps_history = ctk.BooleanVar(value=True)
        self.check_startup = ctk.BooleanVar(value=False)
        self.check_autoclean = ctk.BooleanVar(value=False)

        self.setup_ui()
        self.create_tray_icon()

        # Otomatik Temizleme Kontrolü
        if "--auto" in sys.argv:
            self.withdraw()
            threading.Thread(target=self.run_tasks, daemon=True).start()

    def setup_ui(self):
        # UI Elemanları
        self.header_label = ctk.CTkLabel(self, text=self.text_data[self.lang]["header"], font=("Impact", 32), text_color="#FF0000")
        self.header_label.pack(pady=(20, 5))

        self.warn_frame = ctk.CTkFrame(self, fg_color="#220000", border_color="#FF0000", border_width=1)
        self.warn_frame.pack(pady=10, padx=20, fill="x")
        self.warning_label = ctk.CTkLabel(self.warn_frame, text=self.text_data[self.lang]["warning"], font=("Arial", 11, "bold"), text_color="#FFCC00", wraplength=700)
        self.warning_label.pack(pady=10)

        self.opt_frame = ctk.CTkFrame(self)
        self.opt_frame.pack(pady=10, padx=20, fill="x")

        self.c1 = ctk.CTkCheckBox(self.opt_frame, text=self.text_data[self.lang]["check_tele"], variable=self.check_telemetry)
        self.c1.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.c2 = ctk.CTkCheckBox(self.opt_frame, text=self.text_data[self.lang]["check_pre"], variable=self.check_prefetch)
        self.c2.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        self.c3 = ctk.CTkCheckBox(self.opt_frame, text=self.text_data[self.lang]["check_log"], variable=self.check_logs)
        self.c3.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.c4 = ctk.CTkCheckBox(self.opt_frame, text=self.text_data[self.lang]["check_ps"], variable=self.check_ps_history)
        self.c4.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.c5 = ctk.CTkCheckBox(self.opt_frame, text=self.text_data[self.lang]["check_start"], variable=self.check_startup, command=self.toggle_startup)
        self.c5.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.c6 = ctk.CTkCheckBox(self.opt_frame, text=self.text_data[self.lang]["check_autoclean"], variable=self.check_autoclean, command=self.toggle_startup)
        self.c6.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        self.ghost_btn = ctk.CTkButton(self, text=self.text_data[self.lang]["btn_ghost"], fg_color="#550000", hover_color="#BB0000", height=50, width=400, font=("Arial", 16, "bold"), command=self.execute_protocol)
        self.ghost_btn.pack(pady=10)

        self.console = ctk.CTkTextbox(self, height=200, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.console.pack(pady=20, padx=20, fill="both", expand=True)
        self.log(self.text_data[self.lang]["console"])

        self.lang_btn = ctk.CTkButton(self, text=self.text_data[self.lang]["btn_lang"], width=120, command=self.toggle_language)
        self.lang_btn.place(x=20, y=730)

    def log(self, msg):
        self.console.insert("end", f"\n> {msg}")
        self.console.see("end")

    def toggle_language(self):
        self.lang = "EN" if self.lang == "TR" else "TR"
        # Arayüz metinlerini güncelle
        self.header_label.configure(text=self.text_data[self.lang]["header"])
        self.warning_label.configure(text=self.text_data[self.lang]["warning"])
        self.ghost_btn.configure(text=self.text_data[self.lang]["btn_ghost"])
        self.lang_btn.configure(text=self.text_data[self.lang]["btn_lang"])
        self.c1.configure(text=self.text_data[self.lang]["check_tele"])
        self.c2.configure(text=self.text_data[self.lang]["check_pre"])
        self.c3.configure(text=self.text_data[self.lang]["check_log"])
        self.c4.configure(text=self.text_data[self.lang]["check_ps"])
        self.c5.configure(text=self.text_data[self.lang]["check_start"])
        self.c6.configure(text=self.text_data[self.lang]["check_autoclean"])

    # --- TRAY (SAĞ ALT) MANTIĞI ---
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        d = ImageDraw.Draw(image)
        d.polygon([(32, 10), (10, 54), (54, 54)], fill=(255, 0, 0)) # Kırmızı üçgen
        menu = (item('Göster (Show)', self.show_window), item('Kapat (Exit)', self.quit_app))
        self.icon = pystray.Icon("ZeroTrace", image, "Shadow Protocol", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def minimize_to_tray(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()

    def quit_app(self):
        self.icon.stop()
        self.destroy()
        sys.exit()

    # --- UAC BYPASS VE STARTUP MANTIĞI (GÖREV ZAMANLAYICI) ---
    def toggle_startup(self):
        app_name = "ShadowProtocol"
        script_path = os.path.abspath(__file__)
        python_exe = sys.executable
        
        # EXE olup olmadığını kontrol et
        full_path = sys.executable if getattr(sys, 'frozen', False) else f'{python_exe} "{script_path}"'
        cmd_args = "--auto" if self.check_autoclean.get() else ""
        
        if self.check_startup.get():
            # Görev Zamanlayıcıya 'rl highest' (En yüksek yetki) ile ekle
            task_cmd = f'schtasks /create /tn "{app_name}" /tr "{full_path} {cmd_args}" /sc onlogon /rl highest /f'
            result = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("BAŞLANGIÇ GÖREVİ AKTİF (UAC BYPASS OK).")
            else:
                self.log("HATA: Görev oluşturulamadı!")
        else:
            subprocess.run(f'schtasks /delete /tn "{app_name}" /f', shell=True, capture_output=True)
            self.log("BAŞLANGIÇ GÖREVİ İPTAL EDİLDİ.")

    # --- TEMİZLİK PROTOKOLÜ ---
    def execute_protocol(self):
        threading.Thread(target=self.run_tasks).start()

    def run_tasks(self):
        if self.check_telemetry.get():
            self.log("Servisler donduruluyor...")
            subprocess.run("sc stop DiagTrack", shell=True, capture_output=True)
            subprocess.run("sc config DiagTrack start= disabled", shell=True, capture_output=True)

        if self.check_prefetch.get():
            self.log("Prefetch temizleniyor...")
            subprocess.run(r'del /q /f /s "C:\Windows\Prefetch\*.*"', shell=True, capture_output=True)

        if self.check_logs.get():
            self.log("Loglar imha ediliyor...")
            subprocess.run('for /F "tokens=*" %1 in (\'wevtutil el\') do wevtutil cl "%1"', shell=True)

        if self.check_ps_history.get():
            self.log("PowerShell geçmişi siliniyor...")
            path = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt")
            if os.path.exists(path):
                try: os.remove(path)
                except: pass

        self.log("--- İŞLEM TAMAMLANDI ---")

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = ShadowProtocolUltimate()
        app.mainloop()
    else:
        ctypes.windll.user32.MessageBoxW(0, "YÖNETİCİ YETKİSİ GEREKLİ!", "ERİŞİM REDDEDİLDİ", 0x10)