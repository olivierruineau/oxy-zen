# Changelog

Toutes les modifications notables du projet Oxy-Zen seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Phase 5: Documentation & Professionnalisation (Mars 2026) 🚧 En cours

#### Ajouté
- **License MIT**: Ajout du fichier `LICENSE` pour clarifier les droits d'utilisation
- **Guide de Contribution**: Création de `CONTRIBUTING.md` avec guidelines complètes
  - Standards de code et conventions de nommage
  - Process de soumission de PR
  - Guide d'écriture de tests
  - Templates pour bug reports et feature requests

#### À venir
- Architecture détaillée dans `docs/architecture.md`
- Icône professionnel pour l'application
- Structure d'internationalisation (i18n)
- Documentation API avec Sphinx (optionnel)

---

## [0.2.0] - 2026-03-06

**Release majeure: Fondations solides ✅**

Cette version marque l'achèvement des Phases 1-4 du projet avec des améliorations majeures en sécurité, qualité de code, tests et CI/CD. Le projet passe d'une base fonctionnelle à une application professionnelle prête pour la production.

**Statistiques:**
- 📊 Coverage: 75% (de 56% initial, +19 points)
- 🧪 Tests: 220 (de ~85 initiaux, +135 tests)
- 🔒 Sécurité: 0 vulnérabilités critiques/moyennes (note A+)
- 📦 Build: Exécutable Windows optimisé avec metadata

### 🔒 Sécurité (Phase 1)

#### Ajouté
- **Path Validation**: Protection contre attaques path traversal dans `src/security.py`
  - Validation stricte des chemins de fichiers
  - Constante `ALLOWED_DATA_DIR` pour restreindre accès
  - Logging des tentatives suspectes
  - Tests de sécurité complets

- **YAML Schema Validation**: Validation robuste du schéma des exercices
  - Fonction `validate_exercises_schema()` avec vérification complète
  - Messages d'erreur clairs et actionnables
  - Protection contre fichiers YAML malformés

- **Thread Safety**: Protection complète des accès concurrents
  - `threading.Lock()` pour tous les états partagés
  - Properties thread-safe pour `paused`, `last_notification`, `exercise_history`
  - 13 tests de concurrence couvrant race conditions
  - Gestion sécurisée pause/reprise

- **Input Validation UI**: Validation stricte des entrées utilisateur
  - Vérification des heures (0-23) et minutes (0-59)
  - Validation que `start_time < end_time`
  - Messages d'erreur user-friendly
  - Prévention de configurations invalides

- **Atomic Config Write**: Écriture sécurisée de la configuration
  - Write to temp file + atomic `os.replace()`
  - Rollback automatique en cas d'erreur
  - Protection contre corruption lors de crashes
  - Tests de robustesse avec kill process simulé

#### Corrigé
- Race conditions potentielles dans accès multi-threads
- Risques de corruption de fichier config
- Possibilité de configurations UI invalides

### ♻️ Qualité du Code (Phase 2)

#### Ajouté
- **Logging System**: Configuration centralisée professionnelle
  - Module `src/logging_config.py` avec configuration complète
  - Rotation automatique des logs (5MB max)
  - Stockage dans `~/.oxy-zen/app.log`
  - Niveaux appropriés (DEBUG dev, INFO prod)
  - 100% des `print()` remplacés par `logger`

- **Constants**: Extraction de toutes les valeurs magiques
  - Module `src/constants.py` centralisé
  - Documentation complète de chaque constante
  - Facilite maintenance et configuration
  - Constantes: `IDLE_THRESHOLD_SECONDS`, `MAX_RECENT_MESSAGES`, etc.

- **Architecture Modulaire**: Structure avec managers
  - `src/managers/schedule_manager.py` - Gestion du planning
  - `src/managers/notification_manager.py` - Gestion notifications
  - `src/managers/icon_manager.py` - Gestion icône système
  - Séparation des responsabilités
  - Prêt pour injection de dépendances futures

- **Base Window Class**: Classe de base pour fenêtres UI
  - `src/ui/base_window.py` avec fonctionnalités communes
  - Méthode `center_window()` réutilisable
  - Configuration fenêtre cohérente
  - Réduction duplication de code

#### Amélioré
- **Exception Handling**: Gestion d'erreurs professionnelle
  - Exceptions spécifiques plutôt que `except Exception` générique
  - Logging avec `exc_info=True` pour stack traces complètes
  - Stratégies de recovery cohérentes
  - Documentation des exceptions possibles

### 🧪 Tests & Couverture (Phase 3)

#### Ajouté
- **Suite de tests massive**: 220 tests (+135 nouveaux)
  - `tests/test_ui.py`: 20 tests pour composants UI
  - `tests/test_system_tray.py`: 18 tests pour icône système
  - `tests/test_notifications.py`: 17 tests pour notifications
  - `tests/test_schedule.py`: 17 tests pour planning
  - `tests/test_threads.py`: 13 tests pour gestion threads
  - `tests/test_thread_safety.py`: Tests de concurrence
  - `tests/test_atomic_config_write.py`: Tests d'écriture atomique
  - `tests/test_security.py`: Tests de validation sécurité

#### Amélioré
- **Coverage**: Bond de 56% à 75% (+19 points)
  - `src/app.py`: 87% coverage
  - `src/config.py`: 98% coverage
  - `src/ui/checkin_window.py`: 88% coverage
  - `src/ui/notification_config_window.py`: 99% coverage
  - `src/ui/stats_window.py`: 93% coverage
  - HTML coverage report maintenu à jour

#### Corrigé
- Stratégies de mocking pour tkinter, pystray, winotify
- Gestion propre des threads dans les tests
- Structure des données pour StatsWindow
- `show_checkin()` et `show_stats()` retournent thread pour tests

### 📦 Build & CI/CD (Phase 4)
- **Version Info**: Création de `version_info.txt` pour les métadonnées Windows de l'exécutable
  - Informations de version (0.1.0)
  - Copyright et description
  - Intégration avec PyInstaller dans `build.spec`

---

## [0.1.0] - 2026-02 (Date approximative)

**Release initiale: MVP fonctionnel ✅**

Première version fonctionnelle de l'application avec toutes les fonctionnalités de base.

### Ajouté
- **Core Features**: Fonctionnalités principales
  - Application de rappels d'exercices adaptatifs
  - Sélection d'exercices pondérée 70/30 selon préférences utilisateur
  - Système de notifications Windows (winotify)
  - Icône système avec menu contextuel complet
  - Détection d'inactivité avec Windows API
  - Détection de sessions verrouillées

- **UI**: Interfaces utilisateur
  - Fenêtre de check-in quotidien pour signaler problèmes
  - Fenêtre de statistiques d'utilisation
  - Fenêtre de configuration des notifications
  - Design cohérent avec centrage automatique

- **Configuration**: Système de configuration
  - Stockage dans `~/.oxy-zen/config.json`
  - Préférences utilisateur persistantes
  - Historique des exercices
  - Compteurs de notifications

- **Data**: Données d'exercices
  - Fichier `data/exercises.yaml` avec exercices par catégorie
  - Messages sarcastiques motivants
  - Instructions d'exercices détaillées
  - Catégories: dos, yeux, jambes, posture, respiration, fatigue

- **Intelligence**: Logique d'adaptation
  - Pondération 70% exercices ciblés / 30% prévention
  - Anti-répétition des messages récents
  - Exclusion automatique des weekends
  - Respect des horaires de travail configurés

- **Build**: Packaging
  - PyInstaller configuré pour exécutable standalone Windows
  - Script `scripts/build.bat` pour build automatisé
  - Nettoyage automatique des builds précédents
  - Exécutable sans dépendances Python externes

- **Tests**: Suite de tests initiale
  - ~85 tests couvrant fonctionnalités principales
  - 56% de couverture de code
  - Tests pour app, config, UI basiques

### Technique
- Python 3.12+
- Architecture monolithique fonctionnelle
- Dépendances: winotify, schedule, pystray, pillow, pyyaml
- Windows-only (Windows API pour idle detection)

---

## [0.0.1] - 2026-01 (Date approximative)

**Prototype initial 🧪**

Premier prototype de travail avec fonctionnalités minimales.

### Ajouté
- Structure de base du projet
- Notification simple toutes les X minutes
- Exercices hardcodés
- Tests basiques

---

*Pour voir le détail de l'architecture et des décisions techniques, consultez [docs/architecture.md](docs/architecture.md)*

*Ce changelog suit les principes de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/) et [Semantic Versioning](https://semver.org/lang/fr/)*
