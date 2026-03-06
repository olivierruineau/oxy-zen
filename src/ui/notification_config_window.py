"""Fenêtre de configuration des notifications pour Oxy-Zen."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict

class NotificationConfigWindow:
    """Fenêtre pour configurer les notifications."""
    FREQUENCIES = [
        ("Toutes les 30 minutes", 30),
        ("Toutes les heures", 60),
        ("Toutes les 2 heures", 120),
        ("Jamais", 0),
    ]
    MOMENTS = [
        ("À l'heure pile (ex: 10:00)", 0),
        ("À +7 min (ex: 10:07)", 7),
        ("À +15 min (ex: 10:15)", 15),
        ("À +23 min (ex: 10:23)", 23),
    ]
    HOURS = list(range(0, 24))
    MINUTES = [0, 15, 30, 45]

    def __init__(self, current_config: Dict, on_save: Callable[[Dict], None]):
        self.current_config = current_config or {}
        self.on_save = on_save
        self.root = tk.Tk()
        self.root.title("Configuration des notifications")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        self.frequency_var = tk.IntVar(value=self.current_config.get("frequency", 30))
        self.moment_var = tk.IntVar(value=self.current_config.get("moment", 0))
        self.start_hour_var = tk.IntVar(value=self.current_config.get("start_hour", 7))
        self.start_minute_var = tk.IntVar(value=self.current_config.get("start_minute", 30))
        self.end_hour_var = tk.IntVar(value=self.current_config.get("end_hour", 16))
        self.end_minute_var = tk.IntVar(value=self.current_config.get("end_minute", 0))
        self.build_ui()
        self.center_window()
        self.root.mainloop()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Fréquence
        ttk.Label(frame, text="Fréquence des notifications :", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        for label, value in self.FREQUENCIES:
            ttk.Radiobutton(frame, text=label, variable=self.frequency_var, value=value).pack(anchor=tk.W)
        
        # Moment
        ttk.Label(frame, text="\nMoment d'envoi :", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        for label, value in self.MOMENTS:
            ttk.Radiobutton(frame, text=label, variable=self.moment_var, value=value).pack(anchor=tk.W)
        
        # Horaires de travail
        ttk.Label(frame, text="\nHoraires de travail :", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # Heure de début
        start_frame = ttk.Frame(frame)
        start_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(start_frame, text="Début:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Spinbox(start_frame, from_=0, to=23, textvariable=self.start_hour_var, width=5).pack(side=tk.LEFT)
        ttk.Label(start_frame, text="h").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(start_frame, from_=0, to=45, increment=15, textvariable=self.start_minute_var, width=5).pack(side=tk.LEFT)
        ttk.Label(start_frame, text="min").pack(side=tk.LEFT, padx=5)
        
        # Heure de fin
        end_frame = ttk.Frame(frame)
        end_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(end_frame, text="Fin:     ").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Spinbox(end_frame, from_=0, to=23, textvariable=self.end_hour_var, width=5).pack(side=tk.LEFT)
        ttk.Label(end_frame, text="h").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(end_frame, from_=0, to=45, increment=15, textvariable=self.end_minute_var, width=5).pack(side=tk.LEFT)
        ttk.Label(end_frame, text="min").pack(side=tk.LEFT, padx=5)
        
        # Bouton enregistrer
        save_btn = ttk.Button(frame, text="Enregistrer", command=self.save)
        save_btn.pack(pady=20)

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def save(self):
        # Récupération des valeurs
        start_hour = self.start_hour_var.get()
        start_minute = self.start_minute_var.get()
        end_hour = self.end_hour_var.get()
        end_minute = self.end_minute_var.get()
        
        # Validation des heures (0-23)
        if not (0 <= start_hour <= 23):
            messagebox.showerror(
                "Erreur de validation",
                f"L'heure de début ({start_hour}) doit être entre 0 et 23."
            )
            return
        
        if not (0 <= end_hour <= 23):
            messagebox.showerror(
                "Erreur de validation",
                f"L'heure de fin ({end_hour}) doit être entre 0 et 23."
            )
            return
        
        # Validation des minutes (0-59)
        if not (0 <= start_minute <= 59):
            messagebox.showerror(
                "Erreur de validation",
                f"Les minutes de début ({start_minute}) doivent être entre 0 et 59."
            )
            return
        
        if not (0 <= end_minute <= 59):
            messagebox.showerror(
                "Erreur de validation",
                f"Les minutes de fin ({end_minute}) doivent être entre 0 et 59."
            )
            return
        
        # Validation que l'heure de début est avant l'heure de fin
        start_total_minutes = start_hour * 60 + start_minute
        end_total_minutes = end_hour * 60 + end_minute
        
        if start_total_minutes >= end_total_minutes:
            messagebox.showerror(
                "Erreur de validation",
                f"L'heure de début ({start_hour:02d}:{start_minute:02d}) doit être avant l'heure de fin ({end_hour:02d}:{end_minute:02d})."
            )
            return
        
        # Si toutes les validations passent, enregistrer la configuration
        config = {
            "frequency": self.frequency_var.get(),
            "moment": self.moment_var.get(),
            "start_hour": start_hour,
            "start_minute": start_minute,
            "end_hour": end_hour,
            "end_minute": end_minute,
        }
        self.on_save(config)
        self.root.destroy()

def show_notification_config_window(current_config: Dict, on_save: Callable[[Dict], None]):
    NotificationConfigWindow(current_config, on_save)
