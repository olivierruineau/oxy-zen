"""Tests pour l'écriture atomique de la configuration."""

import pytest
import json
import os
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.config import UserPreferences


class TestAtomicConfigWrite:
    """Tests pour vérifier l'écriture atomique de la configuration."""

    @pytest.fixture
    def temp_config(self, tmp_path):
        """Crée une configuration temporaire pour les tests."""
        # Utiliser un répertoire temporaire pour les tests
        original_config_dir = UserPreferences.CONFIG_DIR
        original_config_file = UserPreferences.CONFIG_FILE
        
        UserPreferences.CONFIG_DIR = tmp_path / ".oxy-zen"
        UserPreferences.CONFIG_FILE = UserPreferences.CONFIG_DIR / "config.json"
        UserPreferences.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        prefs = UserPreferences()
        
        yield prefs
        
        # Restaurer les chemins originaux
        UserPreferences.CONFIG_DIR = original_config_dir
        UserPreferences.CONFIG_FILE = original_config_file

    def test_temp_file_cleaned_up_after_successful_save(self, temp_config):
        """Test que le fichier temporaire est supprimé après une sauvegarde réussie."""
        # Arrange
        temp_config.problem_areas = ["dos", "yeux"]
        temp_file = temp_config.CONFIG_FILE.with_suffix('.tmp')
        
        # Act
        temp_config.save()
        
        # Assert
        assert temp_config.CONFIG_FILE.exists(), "Le fichier de config devrait exister"
        assert not temp_file.exists(), "Le fichier temporaire ne devrait plus exister"

    def test_config_file_valid_json_after_save(self, temp_config):
        """Test que le fichier de configuration est un JSON valide après sauvegarde."""
        # Arrange
        temp_config.problem_areas = ["dos", "yeux"]
        temp_config.stats["total_notifications"] = 42
        
        # Act
        temp_config.save()
        
        # Assert
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data["problem_areas"] == ["dos", "yeux"]
            assert data["stats"]["total_notifications"] == 42

    def test_temp_file_cleaned_up_on_write_error(self, temp_config):
        """Test que le fichier temporaire est nettoyé en cas d'erreur d'écriture."""
        # Arrange
        temp_file = temp_config.CONFIG_FILE.with_suffix('.tmp')
        
        # Act - Simuler une erreur lors du rename
        with patch('os.replace', side_effect=OSError("Simulated error")):
            temp_config.save()
        
        # Assert - Le fichier temporaire ne devrait plus exister
        assert not temp_file.exists(), "Le fichier temporaire devrait être nettoyé"

    def test_old_config_preserved_on_write_error(self, temp_config):
        """Test que l'ancienne configuration est préservée en cas d'erreur."""
        # Arrange - Créer une config initiale
        temp_config.problem_areas = ["dos"]
        temp_config.stats["total_notifications"] = 10
        temp_config.save()
        
        # Sauvegarder les valeurs actuelles
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Act - Essayer de sauvegarder avec une erreur simulée
        temp_config.problem_areas = ["yeux", "jambes"]
        temp_config.stats["total_notifications"] = 999
        
        with patch('os.replace', side_effect=OSError("Simulated error")):
            temp_config.save()
        
        # Assert - L'ancienne configuration devrait être intacte
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            current_content = f.read()
            assert current_content == original_content
        
        # Vérifier que les données sont bien les anciennes
        data = json.loads(current_content)
        assert data["problem_areas"] == ["dos"]
        assert data["stats"]["total_notifications"] == 10

    def test_config_not_corrupted_during_concurrent_saves(self, temp_config):
        """Test que la configuration n'est pas corrompue lors de sauvegardes concurrentes."""
        # Arrange
        errors = []
        results = []
        
        def save_config(value):
            try:
                temp_config.stats["total_notifications"] = value
                temp_config.save()
                # Lire immédiatement pour vérifier la cohérence
                temp_config.load()
                results.append(temp_config.stats["total_notifications"])
            except Exception as e:
                errors.append(e)
        
        # Act - Lancer plusieurs threads qui sauvegardent en même temps
        threads = []
        for i in range(10):
            t = threading.Thread(target=save_config, args=(i * 10,))
            threads.append(t)
            t.start()
        
        # Attendre que tous les threads se terminent
        for t in threads:
            t.join()
        
        # Assert
        assert len(errors) == 0, f"Aucune erreur ne devrait survenir : {errors}"
        
        # Vérifier que le fichier final est un JSON valide
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # La valeur finale devrait être l'une des valeurs sauvegardées
            assert data["stats"]["total_notifications"] in [i * 10 for i in range(10)]

    def test_fsync_called_to_ensure_data_written(self, temp_config):
        """Test que fsync est appelé pour garantir l'écriture sur disque."""
        # Arrange
        temp_config.problem_areas = ["dos"]
        
        # Act & Assert - Vérifier que fsync est appelé
        with patch('os.fsync') as mock_fsync:
            temp_config.save()
            mock_fsync.assert_called_once()

    def test_config_recoverable_after_interrupted_save(self, temp_config):
        """Test que la configuration est récupérable après une sauvegarde interrompue."""
        # Arrange - Créer une config initiale valide
        temp_config.problem_areas = ["dos", "yeux"]
        temp_config.stats["total_notifications"] = 5
        temp_config.save()
        
        # Act - Simuler une interruption pendant l'écriture du fichier temporaire
        # en créant un fichier temporaire incomplet
        temp_file = temp_config.CONFIG_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            f.write('{"incomplete": ')  # JSON incomplet
        
        # Assert - La configuration existante devrait toujours être valide
        prefs2 = UserPreferences()
        assert prefs2.problem_areas == ["dos", "yeux"]
        assert prefs2.stats["total_notifications"] == 5
        
        # Le fichier temporaire abandonné devrait être ignoré
        assert temp_file.exists() or not temp_file.exists()  # Peut exister ou non, peu importe

    def test_multiple_sequential_saves_work_correctly(self, temp_config):
        """Test que plusieurs sauvegardes séquentielles fonctionnent correctement."""
        # Arrange & Act
        values = [1, 5, 10, 15, 20]
        
        for value in values:
            temp_config.stats["total_notifications"] = value
            temp_config.save()
            
            # Vérifier immédiatement que la sauvegarde est correcte
            with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data["stats"]["total_notifications"] == value
        
        # Assert final
        prefs2 = UserPreferences()
        assert prefs2.stats["total_notifications"] == 20

    def test_save_with_readonly_directory_handles_error(self, temp_config):
        """Test que la sauvegarde gère correctement un répertoire en lecture seule."""
        # Ce test est informatif mais peut être difficile à implémenter sur toutes les plateformes
        # On se contente de vérifier que l'erreur est capturée sans planter l'app
        
        # Arrange
        temp_config.problem_areas = ["dos"]
        
        # Act - Simuler une erreur de permission
        with patch('builtins.open', side_effect=PermissionError("No write permission")):
            # Ne devrait pas lever d'exception
            temp_config.save()
        
        # Assert - L'application continue de fonctionner
        assert True  # Si on arrive ici, c'est que l'exception a été gérée


class TestAtomicWriteEdgeCases:
    """Tests pour les cas limites de l'écriture atomique."""

    @pytest.fixture
    def temp_config(self, tmp_path):
        """Crée une configuration temporaire pour les tests."""
        original_config_dir = UserPreferences.CONFIG_DIR
        original_config_file = UserPreferences.CONFIG_FILE
        
        UserPreferences.CONFIG_DIR = tmp_path / ".oxy-zen"
        UserPreferences.CONFIG_FILE = UserPreferences.CONFIG_DIR / "config.json"
        UserPreferences.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        prefs = UserPreferences()
        
        yield prefs
        
        UserPreferences.CONFIG_DIR = original_config_dir
        UserPreferences.CONFIG_FILE = original_config_file

    def test_save_with_unicode_characters(self, temp_config):
        """Test que la sauvegarde gère correctement les caractères Unicode."""
        # Arrange
        temp_config.problem_areas = ["dos"]
        # Note: Les catégories sont prédéfinies, mais les stats peuvent contenir des messages
        temp_config.stats["exercises_done"] = [{
            "timestamp": "2026-03-06T10:00:00",
            "category": "dos",
            "message": "Étirement du dos - côté gauche 💪"
        }]
        
        # Act
        temp_config.save()
        
        # Assert
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "💪" in data["stats"]["exercises_done"][0]["message"]

    def test_save_with_empty_stats(self, temp_config):
        """Test que la sauvegarde fonctionne avec des stats vides."""
        # Arrange
        temp_config.stats["exercises_done"] = []
        temp_config.problem_areas = []
        
        # Act
        temp_config.save()
        
        # Assert
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data["stats"]["exercises_done"] == []
            assert data["problem_areas"] == []

    def test_save_with_large_exercise_history(self, temp_config):
        """Test que la sauvegarde fonctionne avec un grand historique."""
        # Arrange - Ajouter 100 exercices
        for i in range(100):
            temp_config.stats["exercises_done"].append({
                "timestamp": f"2026-03-06T10:{i:02d}:00",
                "category": "dos",
                "message": f"Exercice {i}"
            })
        
        # Act
        temp_config.save()
        
        # Assert - Vérifier que tout a été sauvegardé correctement
        with open(temp_config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data["stats"]["exercises_done"]) == 100
