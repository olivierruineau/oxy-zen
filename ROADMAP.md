# 🗺️ Roadmap Oxy-Zen - Plan d'Évolution

> Dernière mise à jour : 6 mars 2026

## 📊 Vue d'ensemble

Ce document trace le plan d'évolution d'Oxy-Zen pour améliorer la documentation et ajouter de nouvelles fonctionnalités.

**Statut actuel :** Version 0.2.0 - Fondations solides établies ✅
- ✅ ~3000+ lignes de code
- ✅ Couverture tests : 75% (objectif atteint!)
- ✅ 220 tests tous passants
- ✅ CI/CD avec matrix tests (Python 3.12/3.13, Windows 2019/2022)
- ✅ Sécurité: 0 vulnérabilités critiques, dependabot + pip-audit actifs
- ✅ Architecture modulaire avec managers
- ✅ Logging centralisé et constantes extraites
- ✅ Thread safety et validation d'entrées

**Phases complétées:**
- ✅ Phase 1: Sécurisation & Stabilité (Thread safety, validation, atomic writes, path validation)
- ✅ Phase 2: Qualité du Code (Logging, constants, managers, base window, exception handling)
- ✅ Phase 3: Tests & Couverture (75% coverage, tests UI/system tray/notifications/schedule/threads)
- ✅ Phase 4: Build & Déploiement (Version info, dependabot, security audit, CI matrix)

---

## 📚 Phase 5: Documentation & Professionnalisation (Actuelle)

**Objectif :** Documentation complète et professionnalisation du projet

### 5.1 Fichiers légaux et contribution (Priorité: 🟠 HAUTE)
- [ ] Créer `LICENSE` (suggestion: MIT)
- [ ] Créer `CONTRIBUTING.md` avec guidelines
- [ ] Mettre à jour `CHANGELOG.md` avec historique complet
- [ ] Créer `CODE_OF_CONDUCT.md` (si projet devient public)
- [ ] Mettre à jour `README.md` avec liens vers ces fichiers

**Bénéfice :** Professionnalise le projet, facilite contributions futures

### 5.2 Documentation architecture (Priorité: 🟡 MOYENNE)
- [ ] Créer `docs/architecture.md`
- [ ] Diagrammes de composants (architecture actuelle avec managers)
- [ ] Schémas flux de données (lifecycle notification, check-in, etc.)
- [ ] Documenter décisons techniques et compromis
- [ ] Documenter structure du projet

**Bénéfice :** Facilite onboarding futurs développeurs, maintenance long terme

### 5.3 Préparation internationalisation (Priorité: 🟢 BASSE)
- [ ] Créer `src/i18n/` directory
- [ ] Créer `src/i18n/fr_FR.py` avec strings actuelles
- [ ] Extraire strings hardcodées de `src/ui/*.py`
- [ ] Documenter process traduction
- [ ] Préparer structure pour futures langues (EN, ES, etc.)

**Bénéfice :** Infrastructure prête pour support multi-langues

### 5.4 Documentation API avec Sphinx (Priorité: 🟢 BASSE)
- [ ] Installer et configurer Sphinx
- [ ] Créer `docs/conf.py` et structure Sphinx
- [ ] Configurer autodoc pour générer docs depuis docstrings
- [ ] Review et améliorer qualité des docstrings
- [ ] Setup GitHub Pages pour publier docs
- [ ] Automatiser build docs dans CI

**Bénéfice :** Documentation API professionnelle, recherchable

### 5.5 Créer icône professionnel (Priorité: 🟡 MOYENNE)
- [ ] Créer ou commander `assets/icon.ico` professionnel
- [ ] Multiple résolutions (16x16, 32x32, 48x48, 256x256)
- [ ] Intégrer dans `build.spec`
- [ ] Vérifier affichage dans explorateur Windows et barre des tâches

**Bénéfice :** Aspect professionnel de l'application

### ✅ Critères de succès Phase 5
- [ ] LICENSE et CONTRIBUTING.md présents
- [ ] CHANGELOG.md mis à jour avec historique complet
- [ ] Architecture documentée dans docs/
- [ ] Structure i18n en place (même si une seule langue)
- [ ] Icône professionnel intégré

---

## 🚀 Phase 6: Nouvelles Fonctionnalités (Futur)

**Pré-requis :** Phase 5 complétée (Phases 1-4 déjà ✅)

### Option A: Analytics & Insights 📊 (Recommandé en priorité)
- [ ] Créer dashboard avec graphiques interactifs
- [ ] Choisir librairie: matplotlib (simple) ou plotly (interactif)
- [ ] Créer `src/analytics.py` pour calculs statistiques
- [ ] Créer `src/ui/analytics_window.py` pour affichage
- [ ] Implémenter trends exercices par catégorie
- [ ] Rapport hebdomadaire/mensuel automatique
- [ ] Export données vers CSV/JSON pour analyse externe
- [ ] Graphiques: distribution exercices, évolution temporelle, heatmap horaire

**Nouveau module :** `src/analytics.py`, `src/ui/analytics_window.py`
**Effort estimé :** 2-3 semaines
**Bénéfice :** Visualisation progrès, motivation utilisateur++

### Option B: Éditeur d'exercices intégré 🎨
- [ ] Créer éditeur YAML intégré avec syntax highlighting
- [ ] Validation en temps réel du schéma
- [ ] Import/export profils d'exercices
- [ ] Support images/GIFs dans notifications (via chemins)
- [ ] Templates exercices partagés (marketplace?)
- [ ] Preview exercice avant sauvegarde
- [ ] Gestion versions (rollback si mauvaise config)

**Nouveau module :** `src/ui/exercise_editor.py`
**Effort estimé :** 2-3 semaines
**Bénéfice :** Personnalisation avancée sans éditer YAML manuellement

### Option C: Intégration smartwatch/fitness trackers ⌚
- [ ] Créer API REST locale avec FastAPI
- [ ] Intégration Fitbit API
- [ ] Intégration Apple Health/Google Fit
- [ ] Ajuster intensité exercices basé sur heart rate
- [ ] Sync automatique données activité physique
- [ ] Alertes si inactivité détectée par wearable
- [ ] Dashboard unified: app + wearable data

**Nouveau module :** `src/api/`, intégrations tierces
**Effort estimé :** 3-4 semaines
**Bénéfice :** Recommandations intelligentes basées sur données réelles
**Note :** Nécessite expertise APIs tierces et OAuth

### Option D: Support multi-plateforme 🖥️
- [ ] Abstraire code platform-specific dans `src/platform/`
- [ ] Implémenter `src/platform/windows.py` (migration code actuel)
- [ ] Implémenter `src/platform/macos.py` (notifications natives macOS)
- [ ] Implémenter `src/platform/linux.py` (libnotify)
- [ ] Adapter system tray pour chaque OS
- [ ] CI matrix: Windows/macOS/Linux × Python 3.12/3.13
- [ ] Build séparés pour chaque plateforme
- [ ] Documentation installation par OS

**Nouveau module :** `src/platform/`
**Effort estimé :** 4-6 semaines
**Bénéfice :** Audience élargie (macOS, Linux)
**Note :** Refactoring majeur, nécessite VMs de test

### Option E: Mode équipe & gamification 👥
- [ ] Backend cloud (Firebase/Supabase?) pour sync
- [ ] Mode équipe: challenges hebdomadaires
- [ ] Stats anonymes comparées (leaderboard équipe)
- [ ] Système de badges/achievements
- [ ] Streaks de jours consécutifs
- [ ] Notifications push pour encouragement
- [ ] Dashboard administrateur pour équipe
- [ ] Export analytics équipe pour RH

**Nouveau module :** `src/cloud/`, backend séparé
**Effort estimé :** 6-8 semaines
**Bénéfice :** Engagement++, adoption entreprise
**Note :** Requiert infrastructure cloud, coûts récurrents, RGPD

---

## 📈 Métriques de Succès Globales

### Sécurité ✅
- ✅ 0 vulnérabilités critiques
- ✅ 0 vulnérabilités moyennes (toutes résolues Phase 1)
- ✅ Dependabot actif et monitore
- ✅ pip-audit dans CI
- 🎯 Score A+ maintenu dans futurs audits

### Qualité ✅
- ✅ 75% couverture tests (objectif atteint!)
- ✅ 220 tests passants
- ✅ 0 `print()` statements (tout loggé)
- ✅ Architecture modulaire (managers prêts)
- ✅ Constantes extraites
- ✅ Exception handling robuste

### Tests ✅
- ✅ UI tests (20 tests)
- ✅ System tray tests (18 tests)
- ✅ Notification tests (17 tests)
- ✅ Schedule tests (17 tests)
- ✅ Thread tests (13 tests)
- ✅ CI passe sur matrix Python 3.12/3.13 × Windows 2019/2022

### Build & CI/CD ✅
- ✅ PyInstaller build fonctionnel
- ✅ Version info intégré
- ✅ CI/CD avec matrix tests
- ✅ Dependabot configuré
- ✅ Security audit automatique
- 🎯 Code signing (optionnel, coût ~400€/an)

### Documentation
- ✅ README complet avec exemples
- ✅ ROADMAP à jour
- ✅ SECURITY_REVIEW complet
- ✅ TODO.md structuré
- 🎯 LICENSE (Phase 5.1)
- 🎯 CONTRIBUTING.md (Phase 5.1)
- 🎯 CHANGELOG.md mis à jour (Phase 5.1)
- 🎯 Architecture docs (Phase 5.2)
- 🎯 API docs Sphinx (Phase 5.4)

---

## 🗓️ Timeline Révisée

| Phase | Durée | Statut | Complétée |
|-------|-------|--------|-----------|
| Phase 1: Sécurité | 1-2 semaines | ✅ Complété | Mars 2026 |
| Phase 2: Qualité | 2-3 semaines | ✅ Complété | Mars 2026 |
| Phase 3: Tests | 1-2 semaines | ✅ Complété | Mars 2026 |
| Phase 4: Build | 1 semaine | ✅ Complété | Mars 2026 |
| **Phase 5: Documentation** | **1-2 semaines** | **⏳ Actuelle** | **-** |
| Phase 6: Features | 2-8 semaines (variable) | 🔮 À planifier | - |

---

## 🎯 Prochaines Actions Recommandées

### Court terme (Cette semaine)
1. ✅ Créer `LICENSE` (MIT recommandé)
2. ✅ Créer `CONTRIBUTING.md`
3. ✅ Mettre à jour `CHANGELOG.md` historique complet
4. 🎨 Commander/créer icône professionnel

### Moyen terme (Ce mois)
1. 📚 Documenter architecture dans `docs/architecture.md`
2. 🌍 Préparer structure i18n (extraction strings)
3. 📖 Setup Sphinx pour API docs (optionnel)

### Long terme (Prochains mois)
1. Phase 6 Option A: Dashboard Analytics (suggéré en priorité)
2. Phase 6 Option B: Éditeur exercices
3. Considérer Options C/D/E selon besoins/feedback

---

## 📝 Notes Importantes

- ✅ **Phases 1-4 complétées** : Fondations solides établies
- 🎯 **Focus Phase 5** : Documentation et professionnalisation
- 🚀 **Phase 6 flexible** : Choisir features selon priorités utilisateur
- 💡 **Analytics (Option A)** recommandé comme première feature
- 🌍 **Multi-platform (Option D)** si audience internationale
- 👥 **Mode équipe (Option E)** si adoption entreprise visée

---

*Roadmap vivante - mise à jour: 6 mars 2026*
*Version 0.2.0 - Fondations complètes ✅*
