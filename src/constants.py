"""Constantes globales pour l'application Oxy-Zen."""

# Seuils et limites
IDLE_THRESHOLD_SECONDS = 300  # 5 minutes
"""Durée d'inactivité (en secondes) avant de considérer l'utilisateur absent."""

MAX_RECENT_MESSAGES = 3
"""Nombre de messages récents à garder en cache pour éviter les répétitions."""

MAX_SELECTION_ATTEMPTS = 10
"""Nombre maximum de tentatives pour sélectionner un exercice non-récent."""

MAX_EXERCISE_HISTORY = 20
"""Nombre maximum d'exercices à garder dans l'historique."""

# Configuration par défaut
DEFAULT_NOTIFICATION_FREQUENCY = 30  # minutes
"""Fréquence par défaut des notifications (en minutes)."""

DEFAULT_NOTIFICATION_MOMENT = 0  # minutes
"""Décalage par défaut du moment d'envoi (en minutes)."""

DEFAULT_START_HOUR = 7
"""Heure de début par défaut des notifications."""

DEFAULT_START_MINUTE = 30
"""Minute de début par défaut des notifications."""

DEFAULT_END_HOUR = 16
"""Heure de fin par défaut des notifications."""

DEFAULT_END_MINUTE = 0
"""Minute de fin par défaut des notifications."""

# Timings
SNOOZE_DURATION_SECONDS = 300  # 5 minutes
"""Durée du snooze (en secondes)."""

SCHEDULE_CHECK_INTERVAL = 60  # secondes
"""Intervalle de vérification du scheduler (en secondes)."""

# Poids de pondération
PROBLEM_AREAS_WEIGHT = 0.7
"""Pourcentage du poids total pour les zones à problème."""

PREVENTION_WEIGHT = 0.3
"""Pourcentage du poids pour la prévention globale."""

RESIDUAL_WEIGHT = 0.01
"""Poids résiduel pour les catégories non-problème."""

# Check-in
CHECKIN_HOUR_MIN = 10
"""Heure minimale pour le check-in quotidien."""

CHECKIN_HOUR_MAX = 13
"""Heure maximale pour le check-in quotidien."""

# Jours de la semaine
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

WEEKEND_DAYS = [SATURDAY, SUNDAY]
"""Jours de weekend."""

WEEKDAYS = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY]
"""Jours de semaine."""

# Logging
DEFAULT_LOG_LEVEL = "INFO"
"""Niveau de log par défaut."""

LOG_FILE_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
"""Taille maximale du fichier de log avant rotation."""

LOG_BACKUP_COUNT = 3
"""Nombre de fichiers de backup pour les logs."""

# Icon système
ICON_SIZE = 64
"""Taille de l'icône système (en pixels)."""

ICON_BACKGROUND_COLOR = (0, 128, 128)
"""Couleur de fond de l'icône (RGB)."""

ICON_TEXT_COLOR = (255, 255, 255)
"""Couleur du texte de l'icône (RGB)."""
