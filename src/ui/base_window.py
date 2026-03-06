"""Classe de base pour les fenêtres tkinter de l'application Oxy-Zen."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple


class BaseWindow:
    """
    Classe de base pour toutes les fenêtres de l'application.
    
    Fournit des fonctionnalités communes:
    - Centrage automatique de la fenêtre
    - Configuration standard de la fenêtre
    - Gestion des raccourcis clavier
    - Focus et positionnement au premier plan
    """
    
    def __init__(
        self,
        title: str,
        width: int = 400,
        height: int = 500,
        resizable: bool = False,
        escape_closes: bool = True
    ):
        """
        Initialise la fenêtre de base.
        
        Args:
            title: Titre de la fenêtre
            width: Largeur de la fenêtre (défaut: 400px)
            height: Hauteur de la fenêtre (défaut: 500px)
            resizable: Si la fenêtre est redimensionnable (défaut: False)
            escape_closes: Si Escape ferme la fenêtre (défaut: True)
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable, resizable)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Configurer les raccourcis clavier si demandé
        if escape_closes:
            self.root.bind('<Escape>', lambda e: self.close())
        
        # Focus et positioning au premier plan
        self.root.focus_force()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # Gérer la fermeture avec la croix
        self.root.protocol("WM_DELETE_WINDOW", self.close)
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_main_frame(self, padding: str = "20") -> ttk.Frame:
        """
        Crée et retourne un frame principal avec padding.
        
        Args:
            padding: Padding du frame (défaut: "20")
            
        Returns:
            Frame principal configuré
        """
        main_frame = ttk.Frame(self.root, padding=padding)
        main_frame.pack(fill=tk.BOTH, expand=True)
        return main_frame
    
    def create_title_label(
        self,
        parent: tk.Widget,
        text: str,
        font_size: int = 14,
        color: str = "#2c3e50"
    ) -> tk.Label:
        """
        Crée un label de titre styled.
        
        Args:
            parent: Widget parent
            text: Texte du titre
            font_size: Taille de la police (défaut: 14)
            color: Couleur du texte (défaut: #2c3e50)
            
        Returns:
            Label de titre configuré
        """
        label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", font_size, "bold"),
            fg=color,
            justify=tk.CENTER
        )
        return label
    
    def close(self):
        """Ferme la fenêtre. Peut être surchargé par les classes filles."""
        self.root.destroy()
    
    def run(self):
        """Lance la boucle principale de la fenêtre."""
        self.root.mainloop()
    
    def build_ui(self):
        """
        Construit l'interface utilisateur.
        
        Cette méthode doit être implémentée par les classes filles.
        """
        raise NotImplementedError("Les classes filles doivent implémenter build_ui()")
