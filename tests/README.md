# Tests pour Oxy-Zen

## Vue d'ensemble

Ce projet utilise `pytest` pour les tests unitaires et d'intégration, avec `pytest-cov` pour mesurer la couverture de code.

## Structure des tests

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures partagées
├── test_config.py                 # Tests pour UserPreferences
├── test_app.py                    # Tests pour ExerciseSelector et utilitaires
├── test_app_extended.py           # Tests pour OxyZenApp
└── test_integration.py            # Tests d'intégration
```

## Lancer les tests

### Installation des dépendances
```bash
uv sync --all-groups
```

### Exécuter tous les tests
```bash
uv run pytest
```

### Exécuter avec couverture
```bash
uv run pytest --cov=src --cov-report=term-missing
```

### Générer un rapport HTML de couverture
```bash
uv run pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

### Exécuter tests spécifiques
```bash
# Un fichier
uv run pytest tests/test_config.py

# Une classe
uv run pytest tests/test_config.py::TestUserPreferences

# Un test spécifique
uv run pytest tests/test_config.py::TestUserPreferences::test_calculate_weights
```

## Couverture actuelle

- **Total : ~55-60%**
- `src/config.py` : 97%
- `src/app.py` : 72%
- `src/ui/*` : 15-20% (modules UI difficiles à tester automatiquement)

### Zones non couvertes

Les modules UI (`checkin_window.py`, `notification_config_window.py`, `stats_window.py`) ont une couverture faible car ils dépendent de Tkinter et nécessitent une interface graphique. Ces modules devraient être testés manuellement.

Autres zones non couvertes :
- Gestion des erreurs rares (fichiers corrompus, etc.)
- Flux complexes de l'interface système (pystray, icônes)
- Boucle principale de scheduling

## CI/CD avec GitHub Actions

Les tests s'exécutent automatiquement sur chaque Pull Request vers `main` ou `master`.

Le workflow `.github/workflows/tests.yml` :
- Installe les dépendances avec `uv`
- Exécute tous les tests
- Génère un rapport de couverture
- Vérifie que la couverture est entre 60% et 80%
- Poste un commentaire sur la PR avec les résultats

## Tests principaux

### Tests unitaires (`test_config.py`)
- Calcul des poids selon les zones à problème (algorithme 70/30)
- Sauvegarde et chargement de la configuration
- Gestion de l'historique des exercices
- Gestion des statistiques

### Tests unitaires (`test_app.py`)
- Chargement des exercices depuis YAML
- Sélection d'exercices selon la pondération
- Évitement des répétitions
- Détection d'inactivité et session verrouillée

### Tests d'intégration (`test_integration.py`)
- Workflow complet : configuration → sélection → statistiques
- Persistence des données après redémarrage
- Influence des poids sur la distribution des sélections
- Gestion de multiples check-ins
- Cas limites (aucune zone, toutes les zones, etc.)

## Stratégie de test

1. **Tests unitaires** : Testent les fonctions/méthodes individuelles en isolation
2. **Tests d'intégration** : Testent les interactions entre composants
3. **Fixtures** : Données de test réutilisables (exercices, configurations temporaires)
4. **Mocking** : Pour isoler les dépendances externes (notifications Windows, API système)

## Conventions

- Noms de tests : `test_<fonctionnalité>_<scénario>`
- Classes de tests : `Test<NomClasse>`
- Utiliser `pytest.mark.skip` pour les tests nécessitant une intervention manuelle
- Documenter les tests complexes avec des docstrings

## Ajout de nouveaux tests

1. Identifier la fonctionnalité à tester
2. Créer/utiliser des fixtures appropriées dans `conftest.py`
3. Écrire le test dans le fichier correspondant
4. Vérifier que le test passe : `uv run pytest tests/test_<fichier>.py -v`
5. Vérifier l'impact sur la couverture

## Rapports de bugs

Si un test échoue :
1. Lire le message d'erreur complet
2. Vérifier les logs capturés
3. Exécuter le test isolément avec `-v` pour plus de détails
4. Utiliser `pytest --pdb` pour déboguer interactivement
