# 🤝 Guide de Contribution - Oxy-Zen

Merci de l'intérêt que vous portez à Oxy-Zen! Ce document vous guide pour contribuer au projet.

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Standards de Code](#standards-de-code)
- [Process de Soumission](#process-de-soumission)
- [Tests](#tests)
- [Rapporter des Bugs](#rapporter-des-bugs)
- [Proposer des Fonctionnalités](#proposer-des-fonctionnalités)

---

## 📜 Code de Conduite

Ce projet adhère à un code de conduite basé sur le respect et l'inclusion. En participant, vous vous engagez à maintenir un environnement accueillant et respectueux pour tous.

**Comportements attendus:**
- ✅ Utiliser un langage accueillant et inclusif
- ✅ Respecter les points de vue et expériences différents
- ✅ Accepter les critiques constructives avec grâce
- ✅ Se concentrer sur ce qui est meilleur pour la communauté

**Comportements inacceptables:**
- ❌ Langage ou imagerie sexualisée
- ❌ Commentaires insultants/dérogatoires, attaques personnelles ou politiques
- ❌ Harcèlement public ou privé
- ❌ Publication d'informations privées d'autrui sans permission

---

## 🚀 Comment Contribuer

### Types de Contributions Bienvenues

**Code:**
- 🐛 Corrections de bugs
- ✨ Nouvelles fonctionnalités
- ♻️ Refactoring
- ⚡ Améliorations de performance

**Documentation:**
- 📝 Amélioration de la documentation
- 🌍 Traductions
- 📖 Tutoriels et guides

**Qualité:**
- 🧪 Ajout de tests
- 🔍 Revue de code
- 🐛 Rapport de bugs détaillés

---

## 🛠️ Configuration de l'Environnement

### Prérequis

- **Python 3.12+** (recommandé: 3.12 ou 3.13)
- **Windows 10/11** (actuellement Windows-only)
- **uv** (gestionnaire de paquets moderne)
- **Git** pour le contrôle de version

### Installation

1. **Cloner le repository**
   ```powershell
   git clone https://github.com/olivierruineau/oxy-zen.git
   cd oxy-zen
   ```

2. **Installer les dépendances**
   ```powershell
   uv sync
   ```

3. **Activer l'environnement virtuel**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. **Vérifier l'installation**
   ```powershell
   python -m pytest
   ```

### Structure du Projet

```
oxy-zen/
├── src/                    # Code source principal
│   ├── app.py             # Application principale
│   ├── config.py          # Gestion configuration
│   ├── constants.py       # Constantes
│   ├── logging_config.py  # Configuration logging
│   ├── security.py        # Validation sécurité
│   ├── managers/          # Managers modulaires
│   │   ├── icon_manager.py
│   │   ├── notification_manager.py
│   │   └── schedule_manager.py
│   └── ui/                # Interfaces utilisateur
│       ├── base_window.py
│       ├── checkin_window.py
│       ├── notification_config_window.py
│       └── stats_window.py
├── tests/                 # Suite de tests
├── data/                  # Données (exercices.yaml)
├── scripts/               # Scripts build et utilitaires
└── docs/                  # Documentation
```

---

## 📐 Standards de Code

### Style Python

Nous suivons **PEP 8** avec quelques adaptations:

- **Longueur de ligne:** 100 caractères max (flexible pour lisibilité)
- **Indentation:** 4 espaces (pas de tabs)
- **Quotes:** Simple quotes `'...'` par défaut, double `"..."` pour strings avec apostrophes
- **Type hints:** Utilisez les annotations de type autant que possible

**Exemple:**
```python
def send_notification(
    self, 
    category: str, 
    message: str, 
    exercise: str
) -> None:
    """
    Envoie une notification Windows.
    
    Args:
        category: Catégorie de l'exercice
        message: Message sarcastique
        exercise: Instructions d'exercice
    """
    logger.info(f"Sending notification: {category}")
    # Implementation...
```

### Naming Conventions

- **Classes:** `PascalCase` (ex: `OxyZenApp`, `CheckInWindow`)
- **Fonctions/méthodes:** `snake_case` (ex: `send_notification`, `get_idle_duration`)
- **Constantes:** `UPPER_SNAKE_CASE` (ex: `IDLE_THRESHOLD_SECONDS`, `MAX_RECENT_MESSAGES`)
- **Variables privées:** préfixe `_` (ex: `self._lock`, `_state_lock`)

### Logging

**Pas de `print()` dans le code!** Utilisez le système de logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug info for development")
logger.info("General information")
logger.warning("Something unexpected")
logger.error("Error occurred", exc_info=True)
```

### Docstrings

Utilisez le style **Google** pour les docstrings:

```python
def validate_exercises_schema(data: dict) -> bool:
    """
    Valide le schéma du fichier exercises.yaml.
    
    Args:
        data: Dictionnaire chargé depuis yaml.safe_load()
        
    Returns:
        True si le schéma est valide
        
    Raises:
        ValidationError: Si le schéma est invalide
        
    Example:
        >>> with open('exercises.yaml') as f:
        ...     data = yaml.safe_load(f)
        >>> validate_exercises_schema(data)
        True
    """
    # Implementation...
```

---

## 📤 Process de Soumission

### 1. Créer une Issue (Recommandé)

Avant de coder, créez une issue pour discuter de votre contribution:

- **Bug Report:** Décrivez le problème, steps to reproduce, comportement attendu
- **Feature Request:** Décrivez la fonctionnalité, cas d'utilisation, bénéfices

### 2. Fork et Branch

```powershell
# Fork le repo sur GitHub, puis:
git clone https://github.com/YOUR_USERNAME/oxy-zen.git
cd oxy-zen
git remote add upstream https://github.com/olivierruineau/oxy-zen.git

# Créer une branche pour votre feature/fix
git checkout -b feature/analytics-dashboard
# ou
git checkout -b fix/notification-bug
```

**Naming de branches:**
- `feature/` pour nouvelles fonctionnalités
- `fix/` pour corrections de bugs
- `docs/` pour documentation
- `refactor/` pour refactoring

### 3. Coder et Tester

```powershell
# Faire vos modifications
# ...

# Exécuter les tests
python -m pytest

# Vérifier la couverture
python -m pytest --cov=src --cov-report=html

# Vérifier le code
python -m pylint src/
```

### 4. Commit

Utilisez des messages de commit clairs et descriptifs:

```
<type>: <description courte>

<description détaillée optionnelle>

<footer optionnel avec références issues>
```

**Types:**
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage (pas de changement de code)
- `refactor:` refactoring
- `test:` ajout/modification tests
- `chore:` tâches maintenance

**Exemples:**
```
feat: add analytics dashboard with exercise statistics

Implement basic analytics showing:
- Exercise distribution by category
- Temporal trends over 7/30/90 days
- Interactive charts with matplotlib

Closes #42

---

fix: prevent race condition in pause/resume

Add threading.Lock() to protect shared state access
between schedule loop and menu callbacks.

Fixes #38
```

### 5. Push et Pull Request

```powershell
git push origin feature/analytics-dashboard
```

Créez une Pull Request sur GitHub avec:

**Titre clair:**
```
feat: Add analytics dashboard
```

**Description détaillée:**
```markdown
## Description
Implémente un dashboard d'analytics montrant les statistiques d'exercices.

## Changes
- ✨ Nouveau module `src/analytics.py`
- ✨ Nouvelle fenêtre `src/ui/analytics_window.py`
- 📊 Graphiques avec matplotlib (distribution, trends)
- 🧪 20 nouveaux tests

## Screenshots
[Ajouter captures d'écran si pertinent]

## Checklist
- [x] Tests ajoutés et passants
- [x] Documentation mise à jour
- [x] Code suit les standards du projet
- [x] Pas de régression (tous tests passent)
- [x] Couverture de tests maintenue/améliorée

## Related Issues
Closes #42
```

### 6. Code Review

- Répondez aux commentaires de review constructivement
- Faites les changements demandés
- Push les updates (automatiquement mis à jour dans la PR)

### 7. Merge

Une fois approuvée, votre PR sera mergée par un mainteneur!

---

## 🧪 Tests

### Exécuter les Tests

```powershell
# Tous les tests
python -m pytest

# Tests spécifiques
python -m pytest tests/test_app.py
python -m pytest tests/test_app.py::test_send_notification

# Avec couverture
python -m pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html

# Verbose
python -m pytest -v
```

### Écrire des Tests

**Structure:**
```python
# tests/test_feature.py
import pytest
from unittest.mock import Mock, patch
from src.app import OxyZenApp

def test_feature_behavior():
    """Test que la feature se comporte correctement."""
    # Arrange
    app = OxyZenApp()
    
    # Act
    result = app.some_method()
    
    # Assert
    assert result == expected_value
    
@patch('src.app.winotify.Notification')
def test_feature_with_mock(mock_notification):
    """Test avec mock pour dépendances externes."""
    # Arrange
    mock_notification.return_value = Mock()
    app = OxyZenApp()
    
    # Act
    app.send_notification("category", "message", "exercise")
    
    # Assert
    mock_notification.assert_called_once()
```

**Guidelines:**
- Un test = une assertion principale
- Noms de tests descriptifs: `test_send_notification_when_idle_logs_info`
- Mock les dépendances externes (filesystem, Windows API, notifications)
- Testez les edge cases et error conditions
- Visez 75%+ de couverture pour nouveau code

---

## 🐛 Rapporter des Bugs

### Avant de Rapporter

1. ✅ Vérifiez que vous utilisez la dernière version
2. ✅ Cherchez dans les issues existantes (ouvertes et fermées)
3. ✅ Reproduisez le bug dans un environnement propre

### Template de Bug Report

```markdown
**Description**
Description claire et concise du bug.

**Steps to Reproduce**
1. Lancer l'application
2. Cliquer sur '...'
3. Faire '...'
4. Voir l'erreur

**Comportement Attendu**
Ce qui devrait se passer normalement.

**Comportement Actuel**
Ce qui se passe actuellement (incluant messages d'erreur).

**Screenshots**
Si applicable, ajouter captures d'écran.

**Environnement**
- OS: Windows 11 [e.g. Build 22000]
- Python: 3.12.1
- Version Oxy-Zen: 0.2.0

**Logs**
```
[Copier logs pertinents depuis ~/.oxy-zen/app.log]
```

**Contexte Additionnel**
Toute autre information utile.
```

---

## ✨ Proposer des Fonctionnalités

### Template de Feature Request

```markdown
**Problème à Résoudre**
Description du problème utilisateur que cette feature résoudrait.
Ex: "Je ne peux pas visualiser mes progrès sur le long terme"

**Solution Proposée**
Description claire de la feature souhaitée.
Ex: "Un dashboard analytics avec graphiques montrant l'évolution"

**Alternatives Considérées**
Autres solutions envisagées.

**Bénéfices**
- Bénéfice utilisateur 1
- Bénéfice utilisateur 2

**Complexité Estimée**
- [ ] Simple (1-3 jours)
- [ ] Moyenne (1-2 semaines)
- [ ] Complexe (3+ semaines)

**Mockups/Wireframes**
Si disponibles, ajouter designs ou croquis.
```

---

## 📚 Ressources Utiles

### Documentation
- [README.md](README.md) - Introduction et installation
- [ROADMAP.md](ROADMAP.md) - Plan d'évolution du projet
- [SECURITY_REVIEW.md](SECURITY_REVIEW.md) - Revue de sécurité
- [TODO.md](TODO.md) - Tâches en cours et futures
- [docs/architecture.md](docs/architecture.md) - Architecture technique

### Liens Externes
- [PEP 8 - Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [pytest Documentation](https://docs.pytest.org/)

---

## ❓ Questions?

- 💬 **Discussions GitHub:** Pour questions générales
- 🐛 **Issues GitHub:** Pour bugs et features
- 📧 **Email:** [À définir si souhaité]

---

## 🙏 Remerciements

Merci à tous les contributeurs qui rendent Oxy-Zen meilleur!

---

*Document vivant - dernière mise à jour: 6 mars 2026*
