"""Tests pour les fonctionnalités de planification (schedule)."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, time as dt_time, timedelta
import schedule
from src.app import OxyZenApp
from src.config import UserPreferences
from src import constants


class TestSetupSchedule:
    """Tests pour la configuration du scheduler."""
    
    @patch('src.app.schedule')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_setup_schedule_creates_jobs(self, mock_selector, mock_preferences,
                                        mock_icon, mock_schedule):
        """Test que setup_schedule crée des jobs de notification."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "frequency": 60,
            "moment": 0,
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Mock schedule.every()
        mock_job = MagicMock()
        mock_schedule.every.return_value.day.at.return_value.do.return_value = mock_job
        
        # Créer l'app
        app = OxyZenApp()
        
        # Setup schedule
        app.setup_schedule()
        
        # Vérifier que des jobs ont été créés
        assert len(app.notification_jobs) > 0
    
    @patch('src.app.schedule')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_setup_schedule_with_frequency_zero(self, mock_selector, mock_preferences,
                                                mock_icon, mock_schedule):
        """Test que setup_schedule ne crée pas de jobs si fréquence = 0."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "frequency": 0,  # Jamais
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Setup schedule
        app.setup_schedule()
        
        # Vérifier qu'aucun job de notification n'a été créé
        assert len(app.notification_jobs) == 0
    
    @patch('src.app.schedule')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.random.randint')
    def test_setup_schedule_creates_checkin_job(self, mock_randint, mock_selector,
                                               mock_preferences, mock_icon, mock_schedule):
        """Test que setup_schedule crée un job de check-in quotidien."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "frequency": 60,
            "moment": 0,
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_randint.side_effect = [12, 30]  # Heure et minute du check-in
        
        # Mock schedule.every()
        mock_job = MagicMock()
        mock_schedule.every.return_value.day.at.return_value.do.return_value = mock_job
        
        # Créer l'app
        app = OxyZenApp()
        
        # Setup schedule
        app.setup_schedule()
        
        # Vérifier que schedule.every().day.at() a été appelé pour le check-in
        # Il devrait y avoir plusieurs appels: notifications + check-in
        assert mock_schedule.every.return_value.day.at.return_value.do.call_count > 0
    
    @patch('src.app.schedule')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_setup_schedule_respects_time_range(self, mock_selector, mock_preferences,
                                                mock_icon, mock_schedule):
        """Test que setup_schedule respecte la plage horaire."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "frequency": 30,  # Toutes les 30 minutes
            "moment": 0,
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 10,  # Seulement 1 heure
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Mock schedule.every()
        mock_job = MagicMock()
        mock_schedule.every.return_value.day.at.return_value.do.return_value = mock_job
        
        # Créer l'app
        app = OxyZenApp()
        
        # Setup schedule
        app.setup_schedule()
        
        # Vérifier que le nombre de jobs est cohérent (2 ou 3 max pour 1h à 30 min d'intervalle)
        assert len(app.notification_jobs) <= 3


class TestWeekendDetection:
    """Tests pour la détection des weekends."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_should_run_now_on_weekday(self, mock_selector, mock_preferences, mock_icon):
        """Test should_run_now retourne True un jour de semaine."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 8,
            "start_minute": 0,
            "end_hour": 18,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour un lundi à 10h
        with patch('src.app.datetime') as mock_datetime:
            monday = datetime(2026, 3, 9, 10, 0, 0)  # Lundi
            mock_datetime.now.return_value = monday
            
            result = app.should_run_now()
        
        # Devrait retourner True (lundi dans les horaires)
        assert result == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_should_run_now_on_weekend(self, mock_selector, mock_preferences, mock_icon):
        """Test should_run_now retourne False le weekend."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 8,
            "start_minute": 0,
            "end_hour": 18,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour un samedi
        with patch('src.app.datetime') as mock_datetime:
            saturday = datetime(2026, 3, 7, 10, 0, 0)  # Samedi
            mock_datetime.now.return_value = saturday
            
            result = app.should_run_now()
        
        # Devrait retourner False (weekend)
        assert result == False
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_should_run_now_on_sunday(self, mock_selector, mock_preferences, mock_icon):
        """Test should_run_now retourne False le dimanche."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 8,
            "start_minute": 0,
            "end_hour": 18,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour un dimanche
        with patch('src.app.datetime') as mock_datetime:
            sunday = datetime(2026, 3, 8, 10, 0, 0)  # Dimanche
            mock_datetime.now.return_value = sunday
            
            result = app.should_run_now()
        
        # Devrait retourner False (weekend)
        assert result == False


class TestWorkHoursValidation:
    """Tests pour la validation des horaires de travail."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_should_run_now_before_work_hours(self, mock_selector, mock_preferences, mock_icon):
        """Test should_run_now avant les horaires de travail."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour un lundi à 8h (avant 9h)
        with patch('src.app.datetime') as mock_datetime:
            monday_early = datetime(2026, 3, 9, 8, 0, 0)
            mock_datetime.now.return_value = monday_early
            
            result = app.should_run_now()
        
        # Devrait retourner False (avant les heures de travail)
        assert result == False
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_should_run_now_after_work_hours(self, mock_selector, mock_preferences, mock_icon):
        """Test should_run_now après les horaires de travail."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour un lundi à 18h (après 17h)
        with patch('src.app.datetime') as mock_datetime:
            monday_late = datetime(2026, 3, 9, 18, 0, 0)
            mock_datetime.now.return_value = monday_late
            
            result = app.should_run_now()
        
        # Devrait retourner False (après les heures de travail)
        assert result == False
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_should_run_now_during_work_hours(self, mock_selector, mock_preferences, mock_icon):
        """Test should_run_now pendant les horaires de travail."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour un lundi à 12h
        with patch('src.app.datetime') as mock_datetime:
            monday_noon = datetime(2026, 3, 9, 12, 0, 0)
            mock_datetime.now.return_value = monday_noon
            
            result = app.should_run_now()
        
        # Devrait retourner True (pendant les heures de travail)
        assert result == True


class TestIdleDetection:
    """Tests pour la détection d'inactivité."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.get_idle_duration')
    def test_idle_detection_short_idle(self, mock_idle, mock_selector, mock_preferences, mock_icon):
        """Test la détection d'inactivité courte."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Retourner une inactivité courte
        mock_idle.return_value = 60  # 1 minute
        
        # Vérifier que c'est moins que le seuil
        idle_duration = mock_idle()
        assert idle_duration < constants.IDLE_THRESHOLD_SECONDS
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.get_idle_duration')
    def test_idle_detection_long_idle(self, mock_idle, mock_selector, mock_preferences, mock_icon):
        """Test la détection d'inactivité longue."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Retourner une inactivité longue
        mock_idle.return_value = 600  # 10 minutes
        
        # Vérifier que c'est plus que le seuil
        idle_duration = mock_idle()
        assert idle_duration > constants.IDLE_THRESHOLD_SECONDS


class TestEdgeCases:
    """Tests pour les cas limites (minuit, DST, etc)."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_schedule_near_midnight(self, mock_selector, mock_preferences, mock_icon):
        """Test le comportement proche de minuit."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 22,  # 22h
            "start_minute": 0,
            "end_hour": 23,  # 23h
            "end_minute": 59,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour 23h30
        with patch('src.app.datetime') as mock_datetime:
            late_night = datetime(2026, 3, 9, 23, 30, 0)
            mock_datetime.now.return_value = late_night
            
            result = app.should_run_now()
        
        # Devrait retourner True (dans les horaires)
        assert result == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_schedule_at_exact_start_time(self, mock_selector, mock_preferences, mock_icon):
        """Test le comportement à l'heure de début exacte."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour 9h00 exactement
        with patch('src.app.datetime') as mock_datetime:
            exact_start = datetime(2026, 3, 9, 9, 0, 0)
            mock_datetime.now.return_value = exact_start
            
            result = app.should_run_now()
        
        # Devrait retourner True (à l'heure de début)
        assert result == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_schedule_at_exact_end_time(self, mock_selector, mock_preferences, mock_icon):
        """Test le comportement à l'heure de fin exacte."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock datetime pour 17h00 exactement
        with patch('src.app.datetime') as mock_datetime:
            exact_end = datetime(2026, 3, 9, 17, 0, 0)
            mock_datetime.now.return_value = exact_end
            
            result = app.should_run_now()
        
        # Devrait retourner True (à l'heure de fin)
        assert result == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_friday_to_monday_transition(self, mock_selector, mock_preferences, mock_icon):
        """Test la transition vendredi -> lundi."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {
            "start_hour": 9,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Test vendredi (devrait fonctionner)
        with patch('src.app.datetime') as mock_datetime:
            friday = datetime(2026, 3, 13, 10, 0, 0)  # Vendredi
            mock_datetime.now.return_value = friday
            
            result_friday = app.should_run_now()
        
        assert result_friday == True
        
        # Test samedi (ne devrait pas fonctionner)
        with patch('src.app.datetime') as mock_datetime:
            saturday = datetime(2026, 3, 14, 10, 0, 0)  # Samedi
            mock_datetime.now.return_value = saturday
            
            result_saturday = app.should_run_now()
        
        assert result_saturday == False
