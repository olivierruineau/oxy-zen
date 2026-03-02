"""Fenêtre de check-in pour identifier les zones à problème."""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable


class CheckInWindow:
    """Fenêtre de questionnaire pour identifier les besoins actuels."""
    
    def __init__(self, callback: Callable[[List[str]], None], current_areas: List[str] = None):
        """
        Initialise la fenêtre de check-in.
        
        Args:
            callback: Fonction à appeler avec la liste des zones sélectionnées
            current_areas: Zones déjà sélectionnées (pour pré-cocher)
        """
        self.callback = callback
        self.current_areas = current_areas or []
        self.result = None
        
        # Créer la fenêtre
        self.root = tk.Tk()
        self.root.title("Oxy-Zen Check-In 🧘")
        self.root.geometry("350x500")
        self.root.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables pour les checkboxes
        self.check_vars = {}
        
        # Construire l'interface
        self.build_ui()
        
        # Gérer la fermeture avec la croix
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Raccourcis clavier
        self.root.bind('<Escape>', lambda e: self.cancel())
        self.root.bind('<Return>', lambda e: self.validate())
        
        # Focus sur la fenêtre
        self.root.focus_force()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
    
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
        
        # Titre avec style
        title_label = tk.Label(
            main_frame,
            text="Alors, qu'est-ce qui coince\naujourd'hui? 🤔",
            font=("Segoe UI", 14, "bold"),
            fg="#2c3e50",
            justify=tk.CENTER
        )
        title_label.pack(pady=(0, 15))
        
        # Sous-titre
        subtitle_label = tk.Label(
            main_frame,
            text="Coche les zones qui te posent problème :",
            font=("Segoe UI", 9),
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Frame pour les checkboxes
        check_frame = ttk.Frame(main_frame)
        check_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Options avec émojis
        options = [
            ("dos", "🦴 Dos / Lombaires"),
            ("yeux", "👀 Yeux / Fatigue oculaire"),
            ("jambes", "🦵 Jambes / Circulation"),
            ("posture", "🧍 Posture / Nuque"),
            ("respiration", "😮‍💨 Respiration / Stress"),
            ("fatigue_generale", "🥱 Fatigue générale"),
        ]
        
        # Créer les checkboxes
        for key, label in options:
            var = tk.BooleanVar(value=key in self.current_areas)
            self.check_vars[key] = var
            
            cb = tk.Checkbutton(
                check_frame,
                text=label,
                variable=var,
                font=("Segoe UI", 10),
                anchor="w",
                pady=5,
                command=self.toggle_problem_area
            )
            cb.pack(fill=tk.X)
        
        # Séparateur
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)
        
        # Option "Aucun souci"
        self.no_problem_var = tk.BooleanVar(value=len(self.current_areas) == 0)
        no_problem_cb = tk.Checkbutton(
            main_frame,
            text="✅ Tout va bien (RAS)",
            variable=self.no_problem_var,
            font=("Segoe UI", 10, "italic"),
            command=self.toggle_no_problem
        )
        no_problem_cb.pack(pady=(0, 15))
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Bouton Annuler
        cancel_btn = tk.Button(
            button_frame,
            text="Annuler",
            command=self.cancel,
            font=("Segoe UI", 9),
            bg="#ecf0f1",
            fg="#2c3e50",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        # Bouton Valider
        validate_btn = tk.Button(
            button_frame,
            text="Valider",
            command=self.validate,
            font=("Segoe UI", 9, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        )
        validate_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Effet hover sur les boutons
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#d5dbdb"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#ecf0f1"))
        validate_btn.bind("<Enter>", lambda e: validate_btn.config(bg="#2980b9"))
        validate_btn.bind("<Leave>", lambda e: validate_btn.config(bg="#3498db"))
    
    def toggle_no_problem(self):
        """Gère l'exclusivité mutuelle avec "Aucun souci"."""
        if self.no_problem_var.get():
            # Décocher toutes les autres options
            for var in self.check_vars.values():
                var.set(False)
    
    def toggle_problem_area(self):
        """Décoche 'Tout va bien' si une zone à problème est cochée."""
        # Si au moins une zone est cochée, décocher "Tout va bien"
        if any(var.get() for var in self.check_vars.values()):
            self.no_problem_var.set(False)
    
    def validate(self):
        """Valide et retourne les zones sélectionnées."""
        # Si "Aucun souci" est coché, retourner une liste vide
        if self.no_problem_var.get():
            self.result = []
        else:
            # Collecter les zones cochées
            self.result = [
                key for key, var in self.check_vars.items() 
                if var.get()
            ]
        
        # Appeler le callback avec le résultat
        if self.callback:
            self.callback(self.result)
        
        # Fermer la fenêtre
        self.root.quit()
        self.root.destroy()
    
    def cancel(self):
        """Annule et ferme la fenêtre sans sauvegarder."""
        self.result = None
        self.root.quit()
        self.root.destroy()
    
    def show(self):
        """Affiche la fenêtre et attend la réponse."""
        self.root.mainloop()
        return self.result


def show_checkin_dialog(callback: Callable[[List[str]], None], current_areas: List[str] = None) -> List[str]:
    """
    Fonction helper pour afficher le dialog de check-in.
    
    Args:
        callback: Fonction à appeler avec les résultats
        current_areas: Zones actuellement sélectionnées
    
    Returns:
        Liste des zones sélectionnées ou None si annulé
    """
    window = CheckInWindow(callback, current_areas)
    return window.show()
