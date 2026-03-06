"""Gestionnaire de notifications pour Oxy-Zen."""

from pathlib import Path
from winotify import Notification, audio
from typing import Tuple, Optional
from src.logging_config import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Gère l'envoi de notifications Windows."""
    
    def __init__(self):
        """Initialise le gestionnaire de notifications."""
        self._last_notification: Optional[Tuple[str, str, str]] = None
    
    @property
    def last_notification(self) -> Optional[Tuple[str, str, str]]:
        """Retourne la dernière notification envoyée."""
        return self._last_notification
    
    def send_notification(self, category: str, message: str, exercise: str) -> bool:
        """
        Envoie une notification Windows.
        
        Args:
            category: Catégorie de l'exercice
            message: Message de la notification
            exercise: Instructions de l'exercice
            
        Returns:
            True si la notification a été envoyée avec succès, False sinon
        """
        try:
            # Sauvegarder pour le snooze
            self._last_notification = (category, message, exercise)
            
            notif = Notification(
                app_id="Oxy-Zen",
                title=message,
                msg=exercise,
                duration="long",
                icon=str(Path(__file__).parent.parent / "icon.png") if (Path(__file__).parent.parent / "icon.png").exists() else ""
            )
            
            # Son plus audible pour attirer l'attention
            notif.set_audio(audio.Reminder, loop=False)
            
            # Afficher
            notif.show()
            
            logger.info(f"Notification envoyée: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur notification: {e}", exc_info=True)
            return False
