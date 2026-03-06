# ✅ TODO - Oxy-Zen

> Dernière mise à jour : 6 mars 2026
> 
> Checklist de suivi pour les améliorations du projet

---

## 🔥 Actions Immédiates (Cette Semaine)

### Thread Safety (CRITIQUE) ✅
- [x] Ajouter `threading.Lock()` dans `OxyZenApp.__init__()`
- [x] Créer property pour `self.paused` avec lock
- [x] Protéger `self.last_notification` avec lock
- [x] Protéger `self.exercise_history` avec lock
- [x] Review tous les accès multi-threads
- [x] Ajouter tests de concurrence
- [x] Tester pause/reprise rapide

### Validation Input UI (CRITIQUE) ✅
- [x] Ajouter validation dans `NotificationConfigWindow.save()`
- [x] Vérifier `start_hour < end_hour`
- [x] Valider heures 0-23
- [x] Valider minutes 0-59
- [x] Tester avec inputs invalides
- [x] Afficher message erreur user-friendly

### Atomic Config Write (CRITIQUE) ✅
- [x] Implémenter write to temp file
- [x] Implémenter atomic rename
- [x] Ajouter cleanup sur erreur
- [x] Tester avec kill process pendant save
- [x] Vérifier config pas corrompue

---

## 📋 Phase 1: Sécurité (Semaine 1-2)

### Path Validation
- [ ] Créer constante `ALLOWED_DATA_DIR`
- [ ] Valider `exercises_file` dans répertoire autorisé
- [ ] Rejeter path traversal attempts
- [ ] Logger tentatives suspectes
- [ ] Ajouter tests

### YAML Schema Validation
- [ ] Définir schéma attendu
- [ ] Créer fonction `validate_exercises_schema()`
- [ ] Valider après `yaml.safe_load()`
- [ ] Message erreur clair si invalide
- [ ] Documenter schéma dans README

---

## 🔧 Phase 2: Qualité Code (Semaine 3-5)

### Logging System
- [ ] Créer `src/logging_config.py`
- [ ] Configurer file handler (`~/.oxy-zen/app.log`)
- [ ] Configurer log rotation (5MB)
- [ ] Remplacer `print()` dans `src/app.py`
- [ ] Remplacer `print()` dans `src/config.py`
- [ ] Remplacer `print()` dans `src/ui/checkin_window.py`
- [ ] Remplacer `print()` dans `src/ui/stats_window.py`
- [ ] Remplacer `print()` dans `src/ui/notification_config_window.py`
- [ ] Configurer niveaux (DEBUG dev, INFO prod)
- [ ] Tester logs générés

### Constants Extraction
- [ ] Créer `src/constants.py`
- [ ] Extraire `IDLE_THRESHOLD_SECONDS = 300`
- [ ] Extraire `MAX_RECENT_MESSAGES = 3`
- [ ] Extraire `MAX_SELECTION_ATTEMPTS = 10`
- [ ] Extraire `MAX_EXERCISE_HISTORY = 20`
- [ ] Extraire autres magic numbers
- [ ] Remplacer hardcoded values
- [ ] Documenter constantes

### Refactoring OxyZenApp
- [ ] Créer `src/managers/__init__.py`
- [ ] Créer `src/managers/schedule_manager.py`
- [ ] Créer `src/managers/notification_manager.py`
- [ ] Créer `src/managers/icon_manager.py`
- [ ] Migrer logique scheduling
- [ ] Migrer logique notifications
- [ ] Migrer logique system tray
- [ ] Implémenter dependency injection
- [ ] Mettre à jour `OxyZenApp`
- [ ] Mettre à jour tests
- [ ] Vérifier tout fonctionne

### Base Window Class
- [ ] Créer `src/ui/base_window.py`
- [ ] Extraire `center_window()` commun
- [ ] Extraire config window commune
- [ ] Refactor `CheckInWindow` hériter `BaseWindow`
- [ ] Refactor `StatsWindow` hériter `BaseWindow`
- [ ] Refactor `NotificationConfigWindow` hériter `BaseWindow`
- [ ] Tester tous dialogs

### Better Exception Handling
- [ ] Identifier tous `except Exception`
- [ ] Remplacer par exceptions spécifiques
- [ ] Ajouter logging avec `exc_info=True`
- [ ] Stratégies recovery cohérentes
- [ ] Documenter exceptions possibles

---

## 🧪 Phase 3: Tests (Semaine 6-7)

### UI Tests
- [ ] Créer `tests/test_ui.py`
- [ ] Setup mocks pour `tkinter`
- [ ] Test `CheckInWindow` init
- [ ] Test `CheckInWindow` callbacks
- [ ] Test `StatsWindow` display
- [ ] Test `NotificationConfigWindow` validation
- [ ] Tests smoke pour tous dialogs

### System Tray Tests
- [ ] Mock `pystray` library
- [ ] Test menu creation
- [ ] Test menu callbacks
- [ ] Test menu updates
- [ ] Test pause/resume via menu

### Notification Tests
- [ ] Mock `winotify.Notification`
- [ ] Test messages corrects envoyés
- [ ] Test snooze functionality
- [ ] Test notification failure handling

### Schedule Tests
- [ ] Test détection weekend
- [ ] Test validation heures travail
- [ ] Test idle detection
- [ ] Test edge cases (minuit, DST)

### Thread Tests
- [ ] Test création threads
- [ ] Test cleanup threads
- [ ] Test interruption propre
- [ ] Test synchronisation

### Coverage Goals
- [ ] Atteindre 75% coverage globale
- [ ] HTML coverage report à jour
- [ ] CI passe avec nouveau threshold
- [ ] Aucune régression

---

## 📦 Phase 4: Build (Semaine 8)

### Code Signing (Optionnel)
- [ ] Obtenir certificat code signing
- [ ] Configurer dans `build.spec`
- [ ] Modifier `scripts/build.bat`
- [ ] Tester signature
- [ ] Vérifier pas de warning Windows

### Version Info & Icon
- [ ] Créer `version_info.txt`
- [ ] Créer/obtenir `assets/icon.ico`
- [ ] Modifier `build.spec` ligne 59
- [ ] Modifier `build.spec` ligne 60
- [ ] Build et vérifier icône visible

### Dependency Scanning
- [ ] Créer `.github/dependabot.yml`
- [ ] Configurer pip ecosystem
- [ ] Schedule weekly checks
- [ ] Ajouter job `pip-audit` dans CI
- [ ] Configurer alertes GitHub
- [ ] Tester avec vulnérabilité test

### CI Matrix
- [ ] Modifier `.github/workflows/tests.yml`
- [ ] Ajouter matrix Python [3.12, 3.13]
- [ ] Ajouter matrix Windows [2019, 2022]
- [ ] Rendre CODECOV_TOKEN optionnel
- [ ] Vérifier tous jobs passent

---

## 📚 Phase 5: Documentation (Semaine 9)

### Legal & Contributing
- [ ] Créer `LICENSE` (MIT suggéré)
- [ ] Créer `CONTRIBUTING.md`
- [ ] Créer `CHANGELOG.md`
- [ ] Créer `CODE_OF_CONDUCT.md`
- [ ] Mettre à jour `README.md` avec liens

### Architecture
- [ ] Créer `docs/` directory
- [ ] Créer `docs/architecture.md`
- [ ] Créer diagramme composants
- [ ] Créer schéma flux de données
- [ ] Documenter décisions techniques
- [ ] Documenter structure projet

### Internationalization Prep
- [ ] Créer `src/i18n/` directory
- [ ] Créer `src/i18n/fr_FR.py`
- [ ] Extraire strings de `CheckInWindow`
- [ ] Extraire strings de `StatsWindow`
- [ ] Extraire strings de `NotificationConfigWindow`
- [ ] Documenter process i18n

### API Documentation
- [ ] Installer Sphinx
- [ ] Créer `docs/conf.py`
- [ ] Configurer autodoc
- [ ] Générer docs depuis docstrings
- [ ] Review docstrings qualité
- [ ] Setup GitHub Pages
- [ ] Publier docs

---

## 🚀 Phase 6: Features (Future)

### Analytics Dashboard
- [ ] Design mockups
- [ ] Choisir lib graphiques (matplotlib/plotly)
- [ ] Créer `src/analytics.py`
- [ ] Créer `src/ui/analytics_window.py`
- [ ] Implémenter trends par catégorie
- [ ] Rapport hebdomadaire
- [ ] Rapport mensuel
- [ ] Export CSV/JSON
- [ ] Tests

### Exercise Editor
- [ ] Design UI
- [ ] Créer `src/ui/exercise_editor.py`
- [ ] YAML syntax highlighting
- [ ] Validation en temps réel
- [ ] Import/export profils
- [ ] Templates exercices
- [ ] Support images
- [ ] Tests

### Multi-Platform
- [ ] Abstraire platform-specific code
- [ ] Créer `src/platform/` module
- [ ] Implémenter macOS notifications
- [ ] Implémenter Linux notifications
- [ ] CI pour 3 plateformes
- [ ] Tests par plateforme

---

## 📊 Métriques de Progrès

### Sécurité
- [x] Vulnérabilités critiques: 0/0 ✅
- [ ] Vulnérabilités moyennes: 0/3 (0%)
- [ ] Vulnérabilités faibles: 0/5 (0%)

### Tests
- [x] Coverage actuelle: ~60%
- [ ] Coverage cible: 75%
- [ ] UI tests: 0%
- [ ] System tray tests: 0%
- [ ] Notification tests: 0%

### Code Quality
- [ ] Logging implementé: 0%
- [ ] Constants extracted: 0%
- [ ] Refactoring done: 0%
- [ ] Exception handling: 0%

### Documentation
- [x] README: ✅
- [ ] License: ❌
- [ ] Contributing: ❌
- [ ] Changelog: ❌
- [ ] Architecture: ❌
- [ ] API docs: ❌

### Build
- [x] CI/CD: ✅
- [ ] Code signing: ❌
- [ ] Dependency scanning: ❌
- [ ] CI matrix: ❌

---

## 📅 Timeline

| Phase | Début | Fin | Statut |
|-------|-------|-----|--------|
| Phase 1 | - | - | ⏳ À planifier |
| Phase 2 | - | - | ⏳ À planifier |
| Phase 3 | - | - | ⏳ À planifier |
| Phase 4 | - | - | ⏳ À planifier |
| Phase 5 | - | - | ⏳ À planifier |
| Phase 6 | - | - | 🔮 Future |

---

## 🎯 Sprint Actuel

**Sprint :** Planification
**Dates :** -
**Objectif :** Préparer Phase 1

### Cette Semaine
- [ ] Review complet de cette TODO
- [ ] Setup development environment
- [ ] Décider date début Phase 1
- [ ] Commit initial des documents (ROADMAP, SECURITY_REVIEW, TODO)

---

## 📝 Notes

- Phases 1-3 sont **bloquantes** avant features
- Code signing optionnel pour usage personnel
- Estimer ~2h pour chaque task moyenne
- Tasks grandes à décomposer si besoin
- Update ce doc après chaque completion

---

*Checklist vivante - cocher au fur et à mesure*
