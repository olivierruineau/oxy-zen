"""Gestionnaire de planification pour Oxy-Zen."""

import random
import schedule
from typing import List, Callable
from src import constants
from src.logging_config import get_logger

logger = get_logger(__name__)


class ScheduleManager:
    """Gère la planification des tâches (notifications et check-ins)."""
    
    def __init__(self, notification_config: dict, notification_callback: Callable, checkin_callback: Callable):
        """
        Initialise le gestionnaire de planification.
        
        Args:
            notification_config: Configuration des notifications
            notification_callback: Fonction à appeler pour les notifications
            checkin_callback: Fonction à appeler pour les check-ins
        """
        self.notification_config = notification_config
        self.notification_callback = notification_callback
        self.checkin_callback = checkin_callback
        self.notification_jobs: List = []
    
    def setup_schedule(self):
        """Configure les tâches planifiées."""
        # Récupérer les paramètres de configuration
        frequency = self.notification_config.get("frequency", constants.DEFAULT_NOTIFICATION_FREQUENCY)
        moment = self.notification_config.get("moment", constants.DEFAULT_NOTIFICATION_MOMENT)
        start_hour = self.notification_config.get("start_hour", constants.DEFAULT_START_HOUR)
        start_minute = self.notification_config.get("start_minute", constants.DEFAULT_START_MINUTE)
        end_hour = self.notification_config.get("end_hour", constants.DEFAULT_END_HOUR)
        end_minute = self.notification_config.get("end_minute", constants.DEFAULT_END_MINUTE)
        
        # Si fréquence = 0 (Jamais), ne rien programmer
        if frequency == 0:
            logger.warning("Notifications désactivées")
            return
        
        # Notifications entre les horaires configurés, lun-ven
        notification_times = []
        hour = start_hour
        minute = start_minute + moment  # Appliquer l'offset
        if minute >= 60:
            minute -= 60
            hour += 1
        
        end_total_minutes = end_hour * 60 + end_minute
        
        while (hour * 60 + minute) <= end_total_minutes:
            time_str = f"{hour:02d}:{minute:02d}"
            notification_times.append(time_str)
            job = schedule.every().day.at(time_str).do(self.notification_callback)
            self.notification_jobs.append(job)
            
            # Incrémenter selon la fréquence configurée
            minute += frequency
            if minute >= 60:
                minute -= 60
                hour += 1
        
        # Check-in quotidien une fois par jour (heure aléatoire entre 10h et 14h)
        checkin_hour = random.randint(constants.CHECKIN_HOUR_MIN, constants.CHECKIN_HOUR_MAX)
        checkin_minute = random.randint(0, 59)
        checkin_time = f"{checkin_hour:02d}:{checkin_minute:02d}"
        schedule.every().day.at(checkin_time).do(self.checkin_callback)
        
        logger.info(f"Notifications programmées: {', '.join(notification_times)}")
        logger.info(f"Check-in quotidien: {checkin_time}")
    
    def clear_schedule(self):
        """Efface tous les jobs planifiés."""
        schedule.clear()
        self.notification_jobs.clear()
    
    def reconfigure(self, notification_config: dict):
        """
        Reconfigure le scheduler avec une nouvelle configuration.
        
        Args:
            notification_config: Nouvelle configuration des notifications
        """
        self.notification_config = notification_config
        self.clear_schedule()
        self.setup_schedule()
        logger.info("Horaires de notification mis à jour")
