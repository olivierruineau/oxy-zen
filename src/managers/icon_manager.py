"""Gestionnaire de l'icône système pour Oxy-Zen."""

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from typing import Callable, Optional, List
from src import constants
from src.logging_config import get_logger

logger = get_logger(__name__)


class IconManager:
    """Gère l'icône système et son menu."""
    
    def __init__(self):
        """Initialise le gestionnaire d'icône."""
        self.icon: Optional[Icon] = None
    
    def create_icon_image(self) -> Image.Image:
        """
        Crée une image d'icône simple.
        
        Returns:
            Image PIL pour l'icône
        """
        # Créer une image avec un cercle et "OZ"
        img = Image.new('RGB', (constants.ICON_SIZE, constants.ICON_SIZE), color='#3498db')
        draw = ImageDraw.Draw(img)
        
        # Cercle blanc
        margin = constants.ICON_SIZE // 8
        draw.ellipse([margin, margin, constants.ICON_SIZE - margin, constants.ICON_SIZE - margin], 
                     fill='white', outline='#2980b9', width=3)
        
        # Texte "OZ"
        text_x = constants.ICON_SIZE // 3
        text_y = constants.ICON_SIZE // 4
        draw.text((text_x, text_y), "OZ", fill='#3498db')
        
        return img
    
    def create_menu(
        self,
        paused: bool,
        problem_areas: List[str],
        next_notif_text: str,
        has_last_notification: bool,
        trigger_callback: Callable,
        snooze_callback: Callable,
        checkin_callback: Callable,
        stats_callback: Callable,
        config_callback: Callable,
        pause_hour_callback: Callable,
        pause_tomorrow_callback: Callable,
        resume_callback: Callable,
        quit_callback: Callable
    ) -> Menu:
        """
        Crée le menu de l'icône système.
        
        Args:
            paused: Si l'application est en pause
            problem_areas: Liste des zones à problème
            next_notif_text: Texte de la prochaine notification
            has_last_notification: Si une dernière notification existe (pour snooze)
            trigger_callback: Callback pour déclencher une notification
            snooze_callback: Callback pour snooze
            checkin_callback: Callback pour check-in
            stats_callback: Callback pour statistiques
            config_callback: Callback pour configuration
            pause_hour_callback: Callback pour pause 1h
            pause_tomorrow_callback: Callback pour pause jusqu'à demain
            resume_callback: Callback pour reprendre
            quit_callback: Callback pour quitter
            
        Returns:
            Menu pystray configuré
        """
        status = "⏸️ EN PAUSE" if paused else "✅ Actif"
        areas = ", ".join(problem_areas) if problem_areas else "Aucune"
        
        return Menu(
            MenuItem(f"Status: {status}", None, enabled=False),
            MenuItem(f"Zones: {areas}", None, enabled=False),
            MenuItem(next_notif_text, None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Déclencher notification", lambda: trigger_callback()),
            MenuItem("Snooze 5 min", lambda: snooze_callback(), enabled=has_last_notification),
            MenuItem("Check-in manuel", lambda: checkin_callback()),
            MenuItem("Voir statistiques", lambda: stats_callback()),
            MenuItem("Configurer notifications", lambda: config_callback()),
            Menu.SEPARATOR,
            MenuItem("Pause 1 heure", lambda: pause_hour_callback(), enabled=not paused),
            MenuItem("Pause jusqu'à demain", lambda: pause_tomorrow_callback(), enabled=not paused),
            MenuItem("Reprendre", lambda: resume_callback(), enabled=paused),
            Menu.SEPARATOR,
            MenuItem("Quitter", quit_callback)
        )
    
    def setup_icon(self, menu: Menu):
        """
        Configure l'icône dans la barre système.
        
        Args:
            menu: Menu à attacher à l'icône
        """
        icon_image = self.create_icon_image()
        
        self.icon = Icon(
            "Oxy-Zen",
            icon_image,
            "Oxy-Zen - Rappels d'exercices",
            menu=menu
        )
        logger.info("Icône système configurée")
    
    def update_menu(self, menu: Menu):
        """
        Met à jour le menu de l'icône.
        
        Args:
            menu: Nouveau menu
        """
        if self.icon:
            self.icon.menu = menu
    
    def run(self):
        """Lance l'icône système (bloquant)."""
        if self.icon:
            self.icon.run()
    
    def stop(self):
        """Arrête l'icône système."""
        if self.icon:
            self.icon.stop()
            logger.info("Icône système arrêtée")
