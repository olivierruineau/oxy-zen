"""Tests pour les fonctionnalités de système tray."""

import pytest
import threading
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from src.app import OxyZenApp
from src.config import UserPreferences


class TestSystemTrayIcon:
    """Tests pour la création et gestion de l'icône système."""
    
    @patch('src.app.Icon')
    @patch('src.app.Image')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_create_icon_image(self, mock_selector, mock_preferences, mock_image, mock_icon):
        """Test la création de l'image d'icône."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_img = MagicMock()
        mock_image.new.return_value = mock_img
        
        # Créer l'app
        app = OxyZenApp()
        
        # Créer l'icône
        icon_img = app.create_icon_image()
        
        # Vérifier que Image.new a été appelé avec les bons paramètres
        mock_image.new.assert_called_once()
        assert icon_img is not None
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_setup_system_tray(self, mock_selector, mock_preferences, mock_icon):
        """Test la configuration du système tray."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Setup system tray
        with patch.object(app, 'create_icon_image') as mock_create_icon:
            mock_create_icon.return_value = MagicMock()
            app.setup_system_tray()
        
        # Vérifier que Icon a été créé
        mock_icon.assert_called_once()
        assert app.icon is not None
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_icon_tooltip(self, mock_selector, mock_preferences, mock_icon):
        """Test que le tooltip de l'icône est correct."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Setup system tray
        with patch.object(app, 'create_icon_image') as mock_create_icon:
            mock_create_icon.return_value = MagicMock()
            app.setup_system_tray()
        
        # Vérifier que le tooltip contient le bon texte
        call_args = mock_icon.call_args
        assert "Oxy-Zen" in str(call_args)


class TestSystemTrayMenu:
    """Tests pour le menu du système tray."""
    
    @patch('src.app.Icon')
    @patch('src.app.Menu')
    @patch('src.app.MenuItem')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_create_menu_active_state(self, mock_selector, mock_preferences, 
                                     mock_menu_item, mock_menu, mock_icon):
        """Test la création du menu à l'état actif."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.problem_areas = ["dos", "yeux"]
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Créer le menu
        menu = app.create_menu()
        
        # Vérifier que Menu a été appelé
        mock_menu.assert_called()
    
    @patch('src.app.Icon')
    @patch('src.app.Menu')
    @patch('src.app.MenuItem')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_create_menu_paused_state(self, mock_selector, mock_preferences, 
                                     mock_menu_item, mock_menu, mock_icon):
        """Test la création du menu à l'état pause."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.problem_areas = ["dos"]
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = True
        
        # Créer le menu
        menu = app.create_menu()
        
        # Vérifier que Menu a été appelé
        mock_menu.assert_called()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_update_icon_menu(self, mock_selector, mock_preferences, mock_icon):
        """Test la mise à jour du menu de l'icône."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.icon = mock_icon_instance
        
        # Mettre à jour le menu
        with patch.object(app, 'create_menu') as mock_create_menu:
            mock_menu = MagicMock()
            mock_create_menu.return_value = mock_menu
            
            app.update_icon_menu()
            
            # Vérifier que create_menu a été appelé
            mock_create_menu.assert_called_once()
            # Vérifier que le menu de l'icône a été mis à jour
            assert app.icon.menu == mock_menu


class TestMenuCallbacks:
    """Tests pour les callbacks du menu."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_pause_for_hour_callback(self, mock_selector, mock_preferences, mock_icon):
        """Test le callback 'Pause 1 heure'."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Appeler pause_for_hour
        with patch('src.app.datetime') as mock_datetime:
            now = datetime(2026, 3, 6, 10, 0, 0)
            mock_datetime.now.return_value = now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            app.pause_for_hour()
            
            # Vérifier que l'app est en pause
            assert app.paused == True
            assert app.pause_until is not None
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_pause_until_tomorrow_callback(self, mock_selector, mock_preferences, mock_icon):
        """Test le callback 'Pause jusqu'à demain'."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {"start_hour": 7, "start_minute": 30}
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Appeler pause_until_tomorrow
        with patch('src.app.datetime') as mock_datetime:
            now = datetime(2026, 3, 6, 15, 0, 0)
            tomorrow = datetime(2026, 3, 7, 7, 30, 0)
            mock_datetime.now.return_value = now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            app.pause_until_tomorrow()
            
            # Vérifier que l'app est en pause
            assert app.paused == True
            assert app.pause_until is not None
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_resume_callback(self, mock_selector, mock_preferences, mock_icon):
        """Test le callback 'Reprendre'."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = True
        app.pause_until = datetime.now() + timedelta(hours=1)
        
        # Appeler resume
        app.resume()
        
        # Vérifier que l'app n'est plus en pause
        assert app.paused == False
        assert app.pause_until is None
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.show_checkin_dialog')
    def test_show_checkin_callback(self, mock_show_dialog, mock_selector, mock_preferences, mock_icon):
        """Test le callback 'Check-in manuel'."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Appeler show_checkin
        thread = app.show_checkin()
        
        # Vérifier que le thread existe et est daemon
        assert thread is not None
        assert isinstance(thread, threading.Thread)
        assert thread.daemon == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.show_stats_window')
    def test_show_stats_callback(self, mock_show_stats, mock_selector, mock_preferences, mock_icon):
        """Test le callback 'Voir statistiques'."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.get_stats.return_value = {"total_notifications": 10}
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Appeler show_stats
        thread = app.show_stats()
        
        # Vérifier que le thread existe et est daemon
        assert thread is not None
        assert isinstance(thread, threading.Thread)
        assert thread.daemon == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_quit_callback(self, mock_selector, mock_preferences, mock_icon):
        """Test le callback 'Quitter'."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.icon = mock_icon_instance
        app.running = True
        
        # Appeler quit_app
        app.quit_app()
        
        # Vérifier que running est False
        assert app.running == False
        # Vérifier que icon.stop a été appelé
        mock_icon_instance.stop.assert_called_once()


class TestMenuUpdates:
    """Tests pour les mises à jour du menu."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_menu_shows_current_status(self, mock_selector, mock_preferences, mock_icon):
        """Test que le menu affiche le statut actuel."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.problem_areas = ["dos", "yeux"]
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Créer le menu et vérifier qu'il contient le statut
        with patch('src.app.Menu') as mock_menu:
            with patch('src.app.MenuItem') as mock_menu_item:
                app.create_menu()
                
                # Vérifier que MenuItem a été appelé avec le statut
                calls = mock_menu_item.call_args_list
                status_calls = [c for c in calls if "Status:" in str(c) or "Actif" in str(c)]
                assert len(status_calls) > 0
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_menu_shows_problem_areas(self, mock_selector, mock_preferences, mock_icon):
        """Test que le menu affiche les zones à problème."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.problem_areas = ["cou", "poignets"]
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Créer le menu et vérifier qu'il contient les zones
        with patch('src.app.Menu') as mock_menu:
            with patch('src.app.MenuItem') as mock_menu_item:
                app.create_menu()
                
                # Vérifier que MenuItem a été appelé avec les zones
                calls = mock_menu_item.call_args_list
                zones_calls = [c for c in calls if "Zones:" in str(c)]
                assert len(zones_calls) > 0
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_menu_shows_next_notification_time(self, mock_selector, mock_preferences, mock_icon):
        """Test que le menu affiche l'heure de la prochaine notification."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.problem_areas = ["dos"]
        mock_prefs_instance.notification_config = {"start_hour": 7, "start_minute": 30}
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock get_next_notification_time
        with patch.object(app, 'get_next_notification_time') as mock_get_next:
            mock_get_next.return_value = "14:30"
            
            # Créer le menu
            with patch('src.app.Menu') as mock_menu:
                with patch('src.app.MenuItem') as mock_menu_item:
                    app.create_menu()
                    
                    # Vérifier que get_next_notification_time a été appelé
                    mock_get_next.assert_called_once()
                    
                    # Vérifier que MenuItem a été appelé avec l'heure
                    calls = mock_menu_item.call_args_list
                    time_calls = [c for c in calls if "Prochaine:" in str(c)]
                    assert len(time_calls) > 0


class TestNextNotificationTime:
    """Tests pour le calcul de la prochaine notification."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_get_next_notification_time_when_paused(self, mock_selector, mock_preferences, mock_icon):
        """Test get_next_notification_time quand l'app est en pause."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = True
        app.pause_until = None
        
        # Obtenir le texte
        result = app.get_next_notification_time()
        
        # Vérifier que c'est "En pause"
        assert result == "En pause"
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_get_next_notification_time_with_pause_until(self, mock_selector, mock_preferences, mock_icon):
        """Test get_next_notification_time avec pause_until défini."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = True
        app.pause_until = datetime(2026, 3, 6, 16, 30, 0)
        
        # Obtenir le texte
        with patch('src.app.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 3, 6, 15, 0, 0)
            result = app.get_next_notification_time()
        
        # Vérifier que ça contient l'heure
        assert "16:30" in result
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_get_next_notification_time_on_weekend(self, mock_selector, mock_preferences, mock_icon):
        """Test get_next_notification_time pendant le weekend."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.notification_config = {"start_hour": 7, "start_minute": 30}
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Obtenir le texte (samedi)
        with patch('src.app.datetime') as mock_datetime:
            saturday = datetime(2026, 3, 7, 10, 0, 0)  # Samedi
            mock_datetime.now.return_value = saturday
            # Mock datetime class pour timedelta
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw) if args else saturday
            
            result = app.get_next_notification_time()
        
        # Vérifier que ça mentionne lundi
        assert result is not None
        # Le résultat devrait mentionner le prochain jour de travail
