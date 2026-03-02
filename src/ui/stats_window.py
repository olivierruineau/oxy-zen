"""Fenêtre de statistiques pour Oxy-Zen."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict


class StatsWindow:
    """Fenêtre d'affichage des statistiques d'utilisation."""
    
    def __init__(self, stats: Dict):
        """
        Initialise la fenêtre de statistiques.
        
        Args:
            stats: Dictionnaire des statistiques à afficher
        """
        self.stats = stats
        
        # Créer la fenêtre
        self.root = tk.Tk()
        self.root.title("Oxy-Zen - Statistiques 📊")
        self.root.geometry("400x550")
        self.root.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Construire l'interface
        self.build_ui()
        
        # Gérer la fermeture avec la croix
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        # Raccourcis clavier
        self.root.bind('<Escape>', lambda e: self.close())
        
        # Focus sur la fenêtre
        self.root.focus_force()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def build_ui(self):
        """Construit l'interface utilisateur."""
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="📊 Ton bilan Oxy-Zen",
            font=("Segoe UI", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # Section statistiques globales
        stats_frame = tk.Frame(main_frame, bg="#ecf0f1", relief=tk.FLAT)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Notifications envoyées
        notif_label = tk.Label(
            stats_frame,
            text=f"🔔 Notifications envoyées : {self.stats['total_notifications']}",
            font=("Segoe UI", 11),
            bg="#ecf0f1",
            anchor="w",
            pady=8,
            padx=15
        )
        notif_label.pack(fill=tk.X)
        
        # Check-ins effectués
        checkin_label = tk.Label(
            stats_frame,
            text=f"✅ Check-ins effectués : {self.stats['total_checkins']}",
            font=("Segoe UI", 11),
            bg="#ecf0f1",
            anchor="w",
            pady=8,
            padx=15
        )
        checkin_label.pack(fill=tk.X)
        
        # Dernier check-in
        last_checkin = self.format_datetime(self.stats.get('last_checkin', ''))
        last_label = tk.Label(
            stats_frame,
            text=f"🕐 Dernier check-in : {last_checkin}",
            font=("Segoe UI", 11),
            bg="#ecf0f1",
            anchor="w",
            pady=8,
            padx=15
        )
        last_label.pack(fill=tk.X)
        
        # Section zones ciblées
        if self.stats['problem_areas']:
            areas_title = tk.Label(
                main_frame,
                text="🎯 Zones ciblées actuellement :",
                font=("Segoe UI", 12, "bold"),
                fg="#34495e",
                anchor="w"
            )
            areas_title.pack(fill=tk.X, pady=(10, 5))
            
            areas_frame = tk.Frame(main_frame, bg="#e8f5e9")
            areas_frame.pack(fill=tk.X, pady=(0, 15))
            
            area_names = {
                "dos": "🦴 Dos",
                "yeux": "👀 Yeux",
                "jambes": "🦵 Jambes",
                "posture": "🧍 Posture",
                "respiration": "😮‍💨 Respiration",
                "fatigue_generale": "🥱 Fatigue générale"
            }
            
            for area in self.stats['problem_areas']:
                area_label = tk.Label(
                    areas_frame,
                    text=area_names.get(area, area),
                    font=("Segoe UI", 10),
                    bg="#e8f5e9",
                    anchor="w",
                    pady=4,
                    padx=15
                )
                area_label.pack(fill=tk.X)
        else:
            no_problem_label = tk.Label(
                main_frame,
                text="✨ Aucun problème identifié\nTu gères comme un(e) chef! 💪",
                font=("Segoe UI", 11, "italic"),
                fg="#27ae60",
                justify=tk.CENTER
            )
            no_problem_label.pack(pady=15)
        
        # Section exercices récents
        recent_title = tk.Label(
            main_frame,
            text="📝 Exercices récents :",
            font=("Segoe UI", 12, "bold"),
            fg="#34495e",
            anchor="w"
        )
        recent_title.pack(fill=tk.X, pady=(10, 5))
        
        # Frame avec scrollbar pour les exercices récents
        recent_frame = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=1)
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        if self.stats['recent_exercises']:
            for exercise in self.stats['recent_exercises']:
                time_str = self.format_time(exercise['timestamp'])
                cat = exercise['category']
                msg = exercise['message']
                
                ex_label = tk.Label(
                    recent_frame,
                    text=f"{time_str} - {msg[:40]}...",
                    font=("Segoe UI", 9),
                    bg="white",
                    anchor="w",
                    pady=4,
                    padx=10,
                    fg="#7f8c8d"
                )
                ex_label.pack(fill=tk.X)
        else:
            empty_label = tk.Label(
                recent_frame,
                text="Aucun exercice pour le moment",
                font=("Segoe UI", 9, "italic"),
                bg="white",
                fg="#95a5a6",
                pady=20
            )
            empty_label.pack()
        
        # Bouton Fermer
        close_btn = tk.Button(
            main_frame,
            text="Fermer",
            command=self.close,
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        close_btn.pack(pady=(10, 0))
        
        # Effet hover
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#2980b9"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#3498db"))
    
    def format_datetime(self, iso_string: str) -> str:
        """Formate une date ISO en format lisible."""
        if not iso_string:
            return "Jamais"
        
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%d/%m/%Y à %H:%M")
        except:
            return iso_string
    
    def format_time(self, iso_string: str) -> str:
        """Formate une date ISO en heure simple."""
        if not iso_string:
            return ""
        
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%H:%M")
        except:
            return iso_string
    
    def close(self):
        """Ferme la fenêtre."""
        self.root.quit()
        self.root.destroy()
    
    def show(self):
        """Affiche la fenêtre."""
        self.root.mainloop()


def show_stats_window(stats: Dict):
    """
    Fonction helper pour afficher la fenêtre de statistiques.
    
    Args:
        stats: Dictionnaire des statistiques
    """
    window = StatsWindow(stats)
    window.show()
