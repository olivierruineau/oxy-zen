# 🗺️ Roadmap Oxy-Zen - Plan d'Évolution

> Dernière mise à jour : 6 mars 2026

## 📊 Vue d'ensemble

Ce document trace le plan d'évolution d'Oxy-Zen pour améliorer la sécurité, la qualité du code, et ajouter de nouvelles fonctionnalités.

**Statut actuel :** Version stable avec bonne base technique
- ✅ ~2500 lignes de code
- ✅ Couverture tests : 54-80%
- ✅ CI/CD fonctionnel
- ⚠️ Quelques risques de sécurité moyens
- ⚠️ Dette technique à adresser

---

## 🎯 Phase 1: Sécurisation & Stabilité (1-2 semaines)

**Objectif :** Éliminer les risques de sécurité et les problèmes de stabilité

### 1.1 Résoudre les problèmes de concurrence
- [ ] Ajouter `threading.Lock()` dans `src/app.py`
- [ ] Protéger `self.paused` avec lock
- [ ] Protéger `self.last_notification` avec lock
- [ ] Envelopper modifications d'état dans `with self._state_lock:`
- [ ] Tester scénarios pause/reprise rapides
- [ ] Ajouter tests de concurrence (multiple threads)

**Fichiers concernés :** `src/app.py` (lignes 172, 335, 349)
**Priorité :** 🔴 CRITIQUE
**Risque :** Race conditions → crashes imprévisibles

### 1.2 Valider les entrées utilisateur
- [ ] Ajouter validation dans `NotificationConfigWindow.save()`
- [ ] Vérifier `start_hour < end_hour`
- [ ] Valider plages horaires (0-23h, 0-59min)
- [ ] Valider intervalles > 0
- [ ] Afficher messages d'erreur clairs
- [ ] Ajouter tests de validation

**Fichiers concernés :** `src/ui/notification_config_window.py`
**Priorité :** 🔴 CRITIQUE
**Risque :** Config invalide → crash au démarrage

### 1.3 Sécuriser l'écriture de configuration
- [ ] Implémenter écriture atomique (temp + rename)
- [ ] Ajouter gestion d'erreur pour cleanup
- [ ] Tester corruption sur crash simulé
- [ ] Ajouter tests d'écriture atomique

**Fichiers concernés :** `src/config.py` (ligne 76-77)
**Priorité :** 🔴 CRITIQUE
**Risque :** Corruption config si crash pendant écriture

### 1.4 Valider les chemins de fichiers
- [ ] Valider `exercises_file` dans répertoire attendu
- [ ] Rejeter chemins absolus arbitraires
- [ ] Ajouter constante `ALLOWED_DATA_DIR`
- [ ] Tester path traversal attempts

**Fichiers concernés :** `src/app.py` (lignes 79-90)
**Priorité :** 🟠 HAUTE
**Risque :** Faible actuellement, prévention path traversal

### 1.5 Ajouter validation schéma YAML
- [ ] Définir schéma attendu pour `exercises.yaml`
- [ ] Valider structure après `yaml.safe_load()`
- [ ] Fail fast avec message clair
- [ ] Documenter schéma dans README

**Fichiers concernés :** `src/app.py` (ligne 91), `data/exercises.yaml`
**Priorité :** 🟠 HAUTE

### ✅ Critères de succès Phase 1
- [ ] Tous les tests de concurrence passent
- [ ] Validation UI empêche configs invalides
- [ ] Config non corrompue après crash
- [ ] Aucune vulnérabilité moyenne ou plus

---

## 🔧 Phase 2: Qualité du Code (2-3 semaines)

**Objectif :** Améliorer la maintenabilité et réduire la dette technique

### 2.1 Implémenter système de logging
- [ ] Créer `src/logging_config.py`
- [ ] Configurer logger avec rotation (5MB)
- [ ] Remplacer `print()` dans `src/app.py`
- [ ] Remplacer `print()` dans `src/config.py`
- [ ] Remplacer `print()` dans `src/ui/*.py`
- [ ] Ajouter niveaux: DEBUG (dev), INFO (prod)
- [ ] Log file: `~/.oxy-zen/app.log`

**Fichiers concernés :** Tous les fichiers `.py`
**Priorité :** 🟠 HAUTE

### 2.2 Extraire constantes magiques
- [ ] Créer `src/constants.py`
- [ ] `IDLE_THRESHOLD_SECONDS = 300`
- [ ] `MAX_RECENT_MESSAGES = 3`
- [ ] `MAX_SELECTION_ATTEMPTS = 10`
- [ ] `MAX_EXERCISE_HISTORY = 20`
- [ ] Remplacer hardcoded values

**Fichiers concernés :** `src/app.py` (189, 140, 132), `src/config.py` (126)
**Priorité :** 🟡 MOYENNE

### 2.3 Refactoriser classe OxyZenApp
- [ ] Créer `src/managers/schedule_manager.py`
- [ ] Créer `src/managers/notification_manager.py`
- [ ] Créer `src/managers/icon_manager.py`
- [ ] Migrer logique depuis `OxyZenApp`
- [ ] Implémenter injection de dépendances
- [ ] Mettre à jour tests
- [ ] OxyZenApp devient orchestrateur

**Fichiers concernés :** `src/app.py` (lignes 157-587)
**Priorité :** 🟡 MOYENNE
**Bénéfice :** Testabilité ++, maintenabilité ++

### 2.4 Créer classe de base pour fenêtres UI
- [ ] Créer `src/ui/base_window.py`
- [ ] Extraire `center_window()` commun
- [ ] Extraire configuration window commune
- [ ] Hériter dans `CheckInWindow`
- [ ] Hériter dans `StatsWindow`
- [ ] Hériter dans `NotificationConfigWindow`

**Fichiers concernés :** `src/ui/*.py`
**Priorité :** 🟡 MOYENNE
**Bénéfice :** -50 lignes duplication

### 2.5 Améliorer gestion d'exceptions
- [ ] Remplacer `except Exception` par exceptions spécifiques
- [ ] Stratégies de recovery cohérentes
- [ ] Logger stack traces complets
- [ ] Documenter exceptions possibles

**Fichiers concernés :** Tous fichiers avec error handling
**Priorité :** 🟡 MOYENNE

### ✅ Critères de succès Phase 2
- [ ] Aucun `print()` restant (sauf argparse help)
- [ ] Logs générés correctement
- [ ] Managers testables indépendamment
- [ ] Code review réussi

---

## 🧪 Phase 3: Tests & Couverture (1-2 semaines)

**Objectif :** Augmenter couverture de 60% à 75%+

### 3.1 Tester composants UI
- [ ] Créer `tests/test_ui.py`
- [ ] Mock `tkinter` objects
- [ ] Test `CheckInWindow` création
- [ ] Test `StatsWindow` affichage
- [ ] Test `NotificationConfigWindow` validation
- [ ] Smoke tests pour catch obvious bugs

**Priorité :** 🟠 HAUTE
**Objectif couverture :** +5% (UI coverage)

### 3.2 Tester intégration system tray
- [ ] Mock `pystray` dans tests
- [ ] Test création menu
- [ ] Test callbacks menu
- [ ] Test updates menu
- [ ] Test pause/resume via menu

**Priorité :** 🟡 MOYENNE
**Objectif couverture :** +3%

### 3.3 Tester envoi notifications
- [ ] Mock `winotify.Notification`
- [ ] Vérifier messages corrects
- [ ] Test snooze functionality
- [ ] Test notification failure handling

**Priorité :** 🟠 HAUTE
**Objectif couverture :** +4%

### 3.4 Tester logique de scheduling
- [ ] Tests détection weekend
- [ ] Tests validation heures travail
- [ ] Tests idle detection complète
- [ ] Tests edge cases (minuit, DST)

**Priorité :** 🟡 MOYENNE
**Objectif couverture :** +3%

### 3.5 Tests de thread management
- [ ] Test création/cleanup threads
- [ ] Test interruption propre
- [ ] Test synchronisation

**Priorité :** 🟡 MOYENNE
**Objectif couverture :** +2%

### ✅ Critères de succès Phase 3
- [ ] Couverture ≥ 75%
- [ ] CI passe avec nouvelle couverture
- [ ] Aucune régression tests existants
- [ ] Coverage report HTML à jour

---

## 📦 Phase 4: Build & Déploiement (1 semaine)

**Objectif :** Professionnaliser le build et la distribution

### 4.1 Ajouter code signing Windows
- [ ] Obtenir certificat (DigiCert/Sectigo)
- [ ] Configurer `codesign_identity` dans `build.spec`
- [ ] Signer executable dans `scripts/build.bat`
- [ ] Tester signature sur Windows propre
- [ ] Vérifier pas de warning "Unknown Publisher"

**Fichiers concernés :** `build.spec` (ligne 58), `scripts/build.bat`
**Priorité :** 🟡 MOYENNE (optionnel usage perso)
**Coût :** ~300-500€/an

### 4.2 Ajouter version info & icône
- [ ] Créer `version_info.txt` avec metadata
- [ ] Créer `assets/icon.ico` professionnel
- [ ] Modifier `build.spec` ligne 59-60
- [ ] Vérifier icône visible dans explorateur

**Fichiers concernés :** `build.spec`
**Priorité :** 🟢 BASSE

### 4.3 Activer dependency scanning
- [ ] Créer `.github/dependabot.yml`
- [ ] Ajouter job `pip-audit` dans CI
- [ ] Configurer alertes CVEs
- [ ] Tester avec vulnérabilité connue

**Fichiers concernés :** `.github/workflows/tests.yml`, `.github/dependabot.yml`
**Priorité :** 🟠 HAUTE

### 4.4 Améliorer CI matrix
- [ ] Tester Python [3.12, 3.13]
- [ ] Tester Windows [2019, 2022]
- [ ] Rendre `CODECOV_TOKEN` optionnel
- [ ] Paralléliser jobs si possible

**Fichiers concernés :** `.github/workflows/tests.yml`
**Priorité :** 🟡 MOYENNE

### ✅ Critères de succès Phase 4
- [ ] Executable signé vérifié (si applicable)
- [ ] Icône visible partout
- [ ] Dependabot actif
- [ ] CI tests sur toutes matrices

---

## 📚 Phase 5: Documentation (1 semaine)

**Objectif :** Documentation complète et professionnelle

### 5.1 Ajouter fichiers légaux & contribution
- [ ] Créer `LICENSE` (suggestion: MIT)
- [ ] Créer `CONTRIBUTING.md`
- [ ] Créer `CHANGELOG.md`
- [ ] Créer `CODE_OF_CONDUCT.md` (si public)
- [ ] Mettre à jour `README.md` avec liens

**Priorité :** 🟡 MOYENNE

### 5.2 Créer documentation architecture
- [ ] Créer `docs/architecture.md`
- [ ] Diagramme composants (post-refactoring)
- [ ] Schémas flux de données
- [ ] Documenter décisions techniques

**Priorité :** 🟡 MOYENNE

### 5.3 Extraire strings UI (i18n prep)
- [ ] Créer `src/i18n/fr_FR.py`
- [ ] Extraire strings de `src/ui/*.py`
- [ ] Préparer structure i18n future
- [ ] Documenter process traduction

**Priorité :** 🟢 BASSE

### 5.4 Générer documentation API
- [ ] Setup Sphinx dans `docs/`
- [ ] Configurer autodoc
- [ ] Générer depuis docstrings
- [ ] Publier sur GitHub Pages

**Priorité :** 🟢 BASSE

### ✅ Critères de succès Phase 5
- [ ] Tous fichiers légaux présents
- [ ] Architecture documentée
- [ ] Sphinx build sans erreurs
- [ ] Pas de hardcoded strings UI

---

## 🚀 Phase 6: Nouvelles Fonctionnalités (Futur)

**Pré-requis :** Phases 1-5 complétées

### Option A: Analytics & Insights 📊
- [ ] Dashboard avec graphiques (matplotlib/plotly)
- [ ] Trends exercices par catégorie
- [ ] Rapport hebdomadaire/mensuel
- [ ] Export données CSV/JSON

**Nouveau module :** `src/analytics.py`, `src/ui/analytics_window.py`
**Effort :** 2-3 semaines
**Priorité :** 🟢 Suggérée en priorité

### Option B: Personnalisation avancée 🎨
- [ ] Éditeur YAML intégré
- [ ] Import/export profils exercices
- [ ] Support images/vidéos dans notifications
- [ ] Templates exercices partagés

**Nouveau module :** `src/ui/exercise_editor.py`
**Effort :** 2-3 semaines
**Priorité :** 🟢 Seconde priorité

### Option C: Intégration smartwatch/fitness ⌚
- [ ] API REST locale (FastAPI)
- [ ] Integration Fitbit/Apple Health
- [ ] Ajuster intensité basé sur heart rate
- [ ] Sync automatique données santé

**Nouveau module :** `src/api/`
**Effort :** 3-4 semaines
**Priorité :** 🟡 Expertise requise

### Option D: Multi-plateforme 🖥️
- [ ] Support macOS (notifications natives)
- [ ] Support Linux (libnotify)
- [ ] Abstraire platform-specific code
- [ ] CI pour 3 plateformes

**Nouveau module :** `src/platform/`
**Effort :** 4-6 semaines
**Priorité :** 🟡 Refactoring majeur

### Option E: Intelligence sociale 👥
- [ ] Mode équipe: challenges
- [ ] Stats anonymes partagées
- [ ] Gamification (badges/achievements)
- [ ] Leaderboard

**Nouveau module :** `src/cloud/` (backend requis)
**Effort :** 6-8 semaines
**Priorité :** 🟢 Dépend infrastructure cloud

---

## 📈 Métriques de Succès

### Sécurité
- ✅ 0 vulnérabilités critiques (atteint)
- 🎯 0 vulnérabilités moyennes (Phase 1)
- 🎯 Score A+ dans audits automatisés

### Qualité
- ✅ 60% couverture tests (actuel)
- 🎯 75% couverture tests (Phase 3)
- 🎯 0 `print()` statements (Phase 2)
- 🎯 Architecture modulaire (Phase 2)

### Documentation
- ✅ README complet (actuel)
- 🎯 Documentation API (Phase 5)
- 🎯 Guides contribution (Phase 5)
- 🎯 Architecture documentée (Phase 5)

### Build
- ✅ CI/CD fonctionnel (actuel)
- 🎯 Code signing (Phase 4)
- 🎯 Dependency scanning (Phase 4)
- 🎯 Multi-Python/Windows tests (Phase 4)

---

## 🗓️ Timeline Estimée

| Phase | Durée | Date début | Date fin |
|-------|-------|------------|----------|
| Phase 1 | 1-2 semaines | - | - |
| Phase 2 | 2-3 semaines | - | - |
| Phase 3 | 1-2 semaines | - | - |
| Phase 4 | 1 semaine | - | - |
| Phase 5 | 1 semaine | - | - |
| **Total** | **6-9 semaines** | - | - |

> **Note :** Phase 6 à planifier après completion des phases 1-5

---

## 🎯 Prochaines Actions

1. **Immédiat :** Commencer Phase 1.1 (thread safety)
2. **Cette semaine :** Compléter Phase 1
3. **Ce mois :** Phases 1-3 (sécurité + qualité + tests)
4. **Prochain mois :** Phases 4-5 (build + docs)

---

## 📝 Notes

- Phases 1-3 sont **bloquantes** avant nouvelles features
- Code signing (Phase 4.1) optionnel pour usage personnel
- Multi-plateforme (Option D) = refactoring significatif
- Prioriser qualité sur rapidité

---

*Roadmap vivante - mettre à jour régulièrement*
