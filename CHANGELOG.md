# Changelog

Toutes les modifications notables du projet Oxy-Zen seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Phase 4: Build & CI/CD (Mars 2026) ✅

#### Ajouté
- **Version Info**: Création de `version_info.txt` pour les métadonnées Windows de l'exécutable
  - Informations de version (0.1.0)
  - Copyright et description
  - Intégration avec PyInstaller dans `build.spec`

- **Dependency Scanning**: Configuration Dependabot pour la surveillance automatique des dépendances
  - `.github/dependabot.yml` configuré pour pip et GitHub Actions
  - Vérifications hebdomadaires le lundi matin
  - Groupement automatique des mises à jour mineures/patch

- **Security Audit**: Nouveau job `security` dans le workflow CI
  - Utilise `pip-audit` pour détecter les vulnérabilités
  - Rapport JSON généré et uploadé comme artifact
  - Affichage clair des vulnérabilités trouvées

- **CI Matrix**: Tests sur plusieurs configurations
  - Python 3.12 et 3.13
  - Windows Server 2019 et 2022
  - Total: 4 combinaisons testées par push

#### Amélioré
- **CI Workflow**: `continue-on-error` ajouté pour rendre CODECOV_TOKEN vraiment optionnel
- **Coverage Reports**: Uploadés uniquement pour Python 3.12 sur Windows 2022 (configuration de référence)
- **PR Comments**: Incluent maintenant la version Python et OS testés

### Phase 3: Tests (Mars 2026) ✅

#### Ajouté
- **Suite de tests complète**: 220 tests (+85 nouveaux tests)
  - `tests/test_ui.py`: 20 tests pour les composants UI
  - `tests/test_system_tray.py`: 18 tests pour l'icône système
  - `tests/test_notifications.py`: 17 tests pour les notifications
  - `tests/test_schedule.py`: 17 tests pour le planning
  - `tests/test_threads.py`: 13 tests pour la gestion des threads

#### Amélioré
- **Coverage**: Augmenté de 56% à 75% (+19 points de pourcentage)
  - src/app.py: 87%
  - src/config.py: 98%
  - src/ui/checkin_window.py: 88%
  - src/ui/notification_config_window.py: 99%

#### Corrigé
- Stratégies de mocking pour tkinter, pystray, winotify
- Gestion des threads dans les tests
- Structure des données pour StatsWindow
- Fonctions show_checkin() et show_stats() retournent maintenant le thread

### Phase 2: Qualité du Code (Mars 2026) ✅

#### Ajouté
- **Logging System**: Configuration centralisée dans `src/logging_config.py`
  - Rotation automatique des logs (5MB)
  - Stockage dans `~/.oxy-zen/app.log`
  - Remplacement de tous les `print()` par `logger`

- **Constants**: Extraction dans `src/constants.py`
  - Valeurs configurables centralisées
  - Documentation des constantes

- **Managers**: Structure modulaire créée
  - `src/managers/schedule_manager.py`
  - `src/managers/notification_manager.py`
  - `src/managers/icon_manager.py`

- **Base Window**: Classe de base pour les fenêtres UI dans `src/ui/base_window.py`

#### Amélioré
- **Exception Handling**: Gestion d'erreurs plus spécifique et logging avec `exc_info=True`

### Phase 1: Sécurité (Mars 2026) ✅

#### Ajouté
- **Path Validation**: Protection contre les attaques path traversal dans `src/security.py`
  - Validation des chemins de fichiers
  - Logging des tentatives suspectes

- **YAML Schema Validation**: Validation du schéma des exercices
  - Fonction `validate_exercises_schema()`
  - Messages d'erreur clairs

- **Thread Safety**: Protection des accès concurrents
  - `threading.Lock()` pour `self.paused`, `self.last_notification`, `self.exercise_history`
  - Tests de concurrence ajoutés

- **Input Validation**: Validation UI pour `NotificationConfigWindow`
  - Vérification des heures (0-23) et minutes (0-59)
  - Validation que start_time < end_time

- **Atomic Config Write**: Écriture sécurisée de la configuration
  - Write to temp file + atomic rename
  - Nettoyage en cas d'erreur

## [0.1.0] - Version initiale

### Ajouté
- Application de rappels d'exercices adaptatifs
- Sélection d'exercices pondérée selon les préférences
- Système de notifications Windows
- Icône système avec menu contextuel
- Interface de check-in pour signaler les problèmes
- Statistiques d'utilisation
- Configuration des notifications (fréquence, horaires)
- Détection d'inactivité et sessions verrouillées
- Exclusion des weekends
- Build avec PyInstaller pour exécutable standalone
