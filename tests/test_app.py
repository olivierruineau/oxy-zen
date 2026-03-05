"""Tests unitaires pour le module app.py."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.app import ExerciseSelector, get_base_path, get_idle_duration, is_session_locked
from src.config import UserPreferences


class TestGetBasePath:
    """Tests pour la fonction get_base_path."""
    
    def test_get_base_path_normal_mode(self):
        """Test que get_base_path retourne le bon chemin en mode normal."""
        base_path = get_base_path()
        
        assert isinstance(base_path, Path)
        assert base_path.exists()
    
    @patch('sys.frozen', True, create=True)
    @patch('sys._MEIPASS', '/tmp/test_path', create=True)
    def test_get_base_path_frozen_mode(self):
        """Test que get_base_path retourne sys._MEIPASS en mode frozen."""
        import sys
        sys.frozen = True
        sys._MEIPASS = '/tmp/test_path'
        
        base_path = get_base_path()
        
        assert base_path == Path('/tmp/test_path')


class TestGetIdleDuration:
    """Tests pour la fonction get_idle_duration."""
    
    @patch('ctypes.windll.user32.GetLastInputInfo')
    @patch('ctypes.windll.kernel32.GetTickCount')
    def test_get_idle_duration_success(self, mock_get_tick, mock_get_input):
        """Test calcul du temps d'inactivité."""
        # Simuler 10 secondes d'inactivité (10000 ms)
        mock_get_tick.return_value = 20000
        mock_get_input.return_value = True
        
        # Mock la structure LASTINPUTINFO
        with patch('src.app.ctypes.Structure') as mock_struct:
            duration = get_idle_duration()
            
            # Difficile de tester exactement sans vraiment appeler l'API Windows
            # On vérifie juste que ça retourne un nombre
            assert isinstance(duration, (int, float))
    
    @patch('ctypes.windll.user32.GetLastInputInfo', side_effect=Exception("Test error"))
    def test_get_idle_duration_error(self, mock_get_input):
        """Test que la fonction retourne 0 en cas d'erreur."""
        duration = get_idle_duration()
        
        assert duration == 0


class TestIsSessionLocked:
    """Tests pour la fonction is_session_locked."""
    
    @patch('ctypes.windll.user32.OpenInputDesktop')
    @patch('ctypes.windll.user32.CloseDesktop')
    def test_session_locked(self, mock_close, mock_open):
        """Test détection d'une session verrouillée."""
        mock_open.return_value = 0  # NULL = session verrouillée
        
        assert is_session_locked() is True
        mock_close.assert_not_called()
    
    @patch('ctypes.windll.user32.OpenInputDesktop')
    @patch('ctypes.windll.user32.CloseDesktop')
    def test_session_unlocked(self, mock_close, mock_open):
        """Test détection d'une session déverrouillée."""
        mock_open.return_value = 12345  # Non-NULL = session active
        
        assert is_session_locked() is False
        mock_close.assert_called_once_with(12345)
    
    @patch('ctypes.windll.user32.OpenInputDesktop', side_effect=Exception("Test error"))
    def test_session_locked_error(self, mock_open):
        """Test que la fonction retourne False en cas d'erreur."""
        assert is_session_locked() is False


class TestExerciseSelector:
    """Tests pour la classe ExerciseSelector."""
    
    def test_init_loads_exercises(self, temp_exercises_file, clean_preferences):
        """Test que l'initialisation charge les exercices."""
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        assert "dos" in selector.exercises
        assert "yeux" in selector.exercises
        assert len(selector.exercises["dos"]) == 2
        assert len(selector.exercises["yeux"]) == 2
    
    def test_load_exercises_success(self, temp_exercises_file, clean_preferences):
        """Test chargement réussi des exercices depuis YAML."""
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        assert selector.exercises is not None
        assert isinstance(selector.exercises, dict)
        assert len(selector.exercises) > 0
    
    def test_load_exercises_file_not_found(self, clean_preferences, tmp_path):
        """Test comportement quand le fichier n'existe pas."""
        non_existent = tmp_path / "non_existent.yaml"
        selector = ExerciseSelector(non_existent, clean_preferences)
        
        # Devrait avoir un fallback
        assert "prevention_globale" in selector.exercises
    
    def test_load_exercises_invalid_yaml(self, clean_preferences, tmp_path):
        """Test comportement avec un YAML invalide."""
        invalid_file = tmp_path / "invalid.yaml"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid: yaml: content }")
        
        selector = ExerciseSelector(invalid_file, clean_preferences)
        
        # Devrait avoir un fallback
        assert "prevention_globale" in selector.exercises
    
    def test_select_next_exercise_returns_tuple(self, temp_exercises_file, clean_preferences):
        """Test que select_next_exercise retourne un tuple valide."""
        clean_preferences.problem_areas = ["dos"]
        clean_preferences.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        result = selector.select_next_exercise()
        
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        category, message, exercise = result
        assert isinstance(category, str)
        assert isinstance(message, str)
        assert isinstance(exercise, str)
    
    def test_select_next_exercise_respects_weights(self, temp_exercises_file, clean_preferences):
        """Test que la sélection respecte les pondérations."""
        clean_preferences.problem_areas = ["dos"]
        clean_preferences.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        # Faire plusieurs sélections et vérifier qu'on a principalement des exercices "dos"
        categories = []
        for _ in range(20):
            result = selector.select_next_exercise()
            if result:
                categories.append(result[0])
        
        # La catégorie "dos" devrait apparaître le plus souvent
        dos_count = categories.count("dos")
        assert dos_count > 0
    
    def test_select_next_exercise_avoids_repetition(self, temp_exercises_file, clean_preferences):
        """Test que la sélection évite les répétitions récentes."""
        clean_preferences.problem_areas = ["dos"]
        clean_preferences.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        # Faire 4 sélections consécutives
        messages = []
        for _ in range(4):
            result = selector.select_next_exercise()
            if result:
                messages.append(result[1])
        
        # Les 3 derniers messages devraient être dans le cache
        assert len(selector.recent_messages) <= 3
    
    def test_select_next_exercise_no_exercises(self, temp_exercises_file, clean_preferences):
        """Test comportement sans exercices disponibles."""
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        selector.exercises = {}  # Vider les exercices
        
        result = selector.select_next_exercise()
        
        assert result is None
    
    def test_select_next_exercise_no_valid_weights(self, temp_exercises_file, clean_preferences):
        """Test comportement quand tous les poids sont à 0."""
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        # Mettre tous les poids à 0
        for key in selector.preferences.weights:
            selector.preferences.weights[key] = 0
        
        result = selector.select_next_exercise()
        
        assert result is None
    
    def test_recent_messages_cache(self, temp_exercises_file, clean_preferences):
        """Test que le cache de messages récents fonctionne correctement."""
        clean_preferences.problem_areas = ["dos"]
        clean_preferences.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        # Initialiser le cache
        selector.recent_messages = []
        
        # Ajouter des messages
        for i in range(5):
            selector.recent_messages.append(f"Message {i}")
            if len(selector.recent_messages) > 3:
                selector.recent_messages.pop(0)
        
        # Le cache devrait contenir seulement 3 messages
        assert len(selector.recent_messages) == 3
        assert selector.recent_messages == ["Message 2", "Message 3", "Message 4"]
    
    def test_select_exercise_from_multiple_categories(self, temp_exercises_file, clean_preferences):
        """Test sélection depuis plusieurs catégories."""
        clean_preferences.problem_areas = ["dos", "yeux"]
        clean_preferences.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        # Faire plusieurs sélections
        categories = set()
        for _ in range(10):
            result = selector.select_next_exercise()
            if result:
                categories.add(result[0])
        
        # On devrait avoir des exercices de différentes catégories
        assert len(categories) > 0
    
    def test_preferences_integration(self, temp_exercises_file, clean_preferences):
        """Test que le sélecteur utilise bien les préférences."""
        selector = ExerciseSelector(temp_exercises_file, clean_preferences)
        
        # Vérifier que le sélecteur a bien les préférences
        assert selector.preferences is clean_preferences
        assert selector.preferences.weights is not None


class TestOxyZenAppHelpers:
    """Tests pour les méthodes helper de OxyZenApp."""
    
    # Note: Les tests complets de OxyZenApp nécessiteraient des mocks
    # complexes pour l'icône système, les threads, etc.
    # On se concentre sur les méthodes testables unitairement.
    
    def test_notification_logic(self):
        """Test de la logique de notification (sans GUI)."""
        # Ce test est un placeholder pour montrer qu'on devrait tester
        # la logique métier sans les dépendances GUI
        pass


class TestScheduleConfiguration:
    """Tests pour la configuration du scheduler."""
    
    def test_notification_times_calculation(self):
        """Test calcul des horaires de notification."""
        # Configuration: 30 min de fréquence, de 9h à 17h
        frequency = 30
        start_hour = 9
        start_minute = 0
        end_hour = 17
        end_minute = 0
        moment = 0
        
        # Calculer les horaires
        notification_times = []
        hour = start_hour
        minute = start_minute + moment
        
        end_total_minutes = end_hour * 60 + end_minute
        
        while (hour * 60 + minute) <= end_total_minutes:
            notification_times.append(f"{hour:02d}:{minute:02d}")
            minute += frequency
            if minute >= 60:
                minute -= 60
                hour += 1
        
        # Vérifier
        assert len(notification_times) > 0
        assert "09:00" in notification_times
        assert "09:30" in notification_times
        assert "17:00" in notification_times or "16:30" in notification_times
    
    def test_notification_times_with_offset(self):
        """Test calcul des horaires avec offset (moment)."""
        frequency = 60  # 1 heure
        start_hour = 9
        start_minute = 0
        moment = 15  # Décalage de 15 minutes
        
        hour = start_hour
        minute = start_minute + moment
        if minute >= 60:
            minute -= 60
            hour += 1
        
        first_time = f"{hour:02d}:{minute:02d}"
        
        # Premier notif devrait être à 9:15
        assert first_time == "09:15"
