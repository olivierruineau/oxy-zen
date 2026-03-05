"""Configuration et fixtures pytest pour les tests Oxy-Zen."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock
from src.config import UserPreferences


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Crée un répertoire de config temporaire pour les tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        # Monkey-patch le répertoire de config
        monkeypatch.setattr(UserPreferences, 'CONFIG_DIR', temp_path)
        monkeypatch.setattr(UserPreferences, 'CONFIG_FILE', temp_path / "config.json")
        yield temp_path


@pytest.fixture
def clean_preferences(temp_config_dir):
    """Retourne une instance UserPreferences avec un répertoire temporaire."""
    return UserPreferences()


@pytest.fixture
def sample_exercises():
    """Retourne un dictionnaire d'exercices de test."""
    return {
        "dos": [
            {"message": "Test dos 1", "exercise": "Exercice dos 1"},
            {"message": "Test dos 2", "exercise": "Exercice dos 2"},
        ],
        "yeux": [
            {"message": "Test yeux 1", "exercise": "Exercice yeux 1"},
            {"message": "Test yeux 2", "exercise": "Exercice yeux 2"},
        ],
        "jambes": [
            {"message": "Test jambes 1", "exercise": "Exercice jambes 1"},
        ],
        "prevention_globale": [
            {"message": "Test prévention 1", "exercise": "Exercice prévention 1"},
            {"message": "Test prévention 2", "exercise": "Exercice prévention 2"},
        ]
    }


@pytest.fixture
def temp_exercises_file(tmp_path, sample_exercises):
    """Crée un fichier YAML d'exercices temporaire."""
    exercises_file = tmp_path / "exercises.yaml"
    with open(exercises_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_exercises, f)
    return exercises_file


@pytest.fixture
def mock_notification():
    """Mock pour les notifications Windows."""
    return Mock()


@pytest.fixture
def mock_icon():
    """Mock pour l'icône système."""
    return Mock()
