"""Configuration centralisée du système de logging pour Oxy-Zen."""

import logging
import logging.handlers
from pathlib import Path
import os
from . import constants


def setup_logging(log_level: str = constants.DEFAULT_LOG_LEVEL) -> logging.Logger:
    """
    Configure le système de logging avec rotation automatique.
    
    Args:
        log_level: Niveau de logging ("DEBUG", "INFO", "WARNING", "ERROR")
        
    Returns:
        Logger racine configuré
    """
    # Créer le répertoire de logs
    log_dir = Path.home() / ".oxy-zen"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    
    # Configurer le logger racine
    logger = logging.getLogger("oxy_zen")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Éviter les handlers dupliqués si setup_logging est appelé plusieurs fois
    if logger.handlers:
        return logger
    
    # Handler avec rotation (5MB max, 3 fichiers de backup)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=constants.LOG_FILE_MAX_BYTES,
        backupCount=constants.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Handler console (moins verbeux)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format détaillé pour le fichier
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Format simplifié pour la console
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("="*50)
    logger.info("Système de logging initialisé")
    logger.info(f"Fichier de log: {log_file}")
    logger.info(f"Niveau: {log_level}")
    logger.info("="*50)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtient un logger pour un module spécifique.
    
    Args:
        name: Nom du module (généralement __name__)
        
    Returns:
        Logger configuré pour ce module
    """
    return logging.getLogger(f"oxy_zen.{name}")
