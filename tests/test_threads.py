"""Tests pour les fonctionnalités de threading."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import threading
import time
from src.app import OxyZenApp
from src.config import UserPreferences


class TestThreadCreation:
    """Tests pour la création de threads."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.show_checkin_dialog')
    def test_show_checkin_creates_thread(self, mock_dialog, mock_selector,
                                        mock_preferences, mock_icon):
        """Test que show_checkin crée un thread."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Appeler show_checkin
        result = app.show_checkin()
        
        # Vérifier qu'un thread est retourné
        assert isinstance(result, threading.Thread)
        
        # Vérifier que le thread est daemon
        assert result.daemon == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.show_stats_window')
    def test_show_stats_creates_thread(self, mock_stats_window, mock_selector,
                                      mock_preferences, mock_icon):
        """Test que show_stats crée un thread."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.get_stats.return_value = {"total_notifications": 10}
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Appeler show_stats
        result = app.show_stats()
        
        # Vérifier qu'un thread est retourné
        assert isinstance(result, threading.Thread)
        
        # Vérifier que le thread est daemon
        assert result.daemon == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('threading.Thread')
    def test_snooze_creates_thread(self, mock_thread_class, mock_selector,
                                   mock_preferences, mock_icon):
        """Test que snooze_notification crée un thread."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        # Créer l'app
        app = OxyZenApp()
        app.last_notification = ("dos", "Message", "Exercise")
        
        # Appeler snooze_notification
        app.snooze_notification()
        
        # Vérifier qu'un thread a été créé
        mock_thread_class.assert_called()
        
        # Vérifier que le thread est démarré
        mock_thread.start.assert_called_once()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_schedule_thread_created_on_run(self, mock_selector, mock_preferences, mock_icon):
        """Test que le schedule_thread est créé lors de run."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_prefs_instance.needs_initial_checkin.return_value = False
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_icon_instance = MagicMock()
        mock_icon.return_value = mock_icon_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mocker self.icon pour éviter AttributeError
        app.icon = MagicMock()
        
        # Mock les méthodes pour éviter le blocage
        with patch.object(app, 'setup_schedule'):
            with patch.object(app, 'setup_system_tray'):
                # Appeler run
                app.run()
                
                # Vérifier que schedule_thread existe et a été créé
                assert app.schedule_thread is not None
                assert isinstance(app.schedule_thread, threading.Thread)


class TestThreadCleanup:
    """Tests pour le nettoyage des threads."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_quit_app_stops_running(self, mock_selector, mock_preferences, mock_icon):
        """Test que quit_app arrête l'application."""
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
        
        # Vérifier que icon.stop() a été appelé
        mock_icon_instance.stop.assert_called_once()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_schedule_loop_stops_when_not_running(self, mock_selector, mock_preferences, mock_icon):
        """Test que schedule_loop s'arrête quand running est False."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.running = False  # Déjà arrêté
        
        # Mock les méthodes appelées dans schedule_loop
        with patch('src.app.schedule.run_pending'):
            with patch.object(app, 'update_icon_menu'):
                with patch('time.sleep'):
                    # Appeler schedule_loop (devrait s'arrêter immédiatement)
                    app.schedule_loop()
                    
                    # Si on arrive ici, c'est que la boucle s'est terminée correctement


class TestThreadInterruption:
    """Tests pour l'interruption propre des threads."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_schedule_loop_can_be_interrupted(self, mock_selector, mock_preferences, mock_icon):
        """Test que schedule_loop peut être interrompu."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.running = True
        
        # Sauvegarder le vrai time.sleep pour l'utiliser dans le mock
        real_sleep = time.sleep
        
        # Mock les méthodes appelées dans schedule_loop
        with patch('src.app.schedule.run_pending'):
            with patch.object(app, 'update_icon_menu'):
                with patch('time.sleep') as mock_sleep:
                    # Faire en sorte que le sleep arrête l'app après 2 appels
                    call_count = [0]
                    
                    def stop_after_calls(duration):
                        call_count[0] += 1
                        if call_count[0] >= 2:
                            app.running = False
                        # Utiliser le vrai sleep pour éviter la récursion
                        real_sleep(0.01)
                    
                    mock_sleep.side_effect = stop_after_calls
                    
                    # Appeler schedule_loop (devrait s'arrêter rapidement)
                    app.schedule_loop()
                    
                    # Vérifier que running est False
                    assert app.running == False


class TestThreadSynchronization:
    """Tests pour la synchronisation des threads."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_paused_property_thread_safe(self, mock_selector, mock_preferences, mock_icon):
        """Test que la propriété paused est thread-safe."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Fonction qui modifie paused plusieurs fois
        def toggle_pause():
            for _ in range(100):
                app.paused = not app.paused
        
        # Créer plusieurs threads qui modifient paused
        threads = []
        for _ in range(5):
            t = threading.Thread(target=toggle_pause, daemon=True)
            threads.append(t)
            t.start()
        
        # Attendre que tous les threads se terminent
        for t in threads:
            t.join(timeout=2)
        
        # Vérifier que paused est soit True soit False (pas corrompu)
        assert isinstance(app.paused, bool)
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_last_notification_property_thread_safe(self, mock_selector, mock_preferences, mock_icon):
        """Test que la propriété last_notification est thread-safe."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Fonction qui modifie last_notification plusieurs fois
        def set_notification():
            for i in range(100):
                app.last_notification = (f"cat{i}", f"msg{i}", f"ex{i}")
        
        # Créer plusieurs threads qui modifient last_notification
        threads = []
        for _ in range(5):
            t = threading.Thread(target=set_notification, daemon=True)
            threads.append(t)
            t.start()
        
        # Attendre que tous les threads se terminent
        for t in threads:
            t.join(timeout=2)
        
        # Vérifier que last_notification est soit None soit un tuple valide
        assert app.last_notification is None or (
            isinstance(app.last_notification, tuple) and len(app.last_notification) == 3
        )
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_concurrent_pause_and_resume(self, mock_selector, mock_preferences, mock_icon):
        """Test la pause et reprise concurrentes."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock update_icon_menu pour éviter les erreurs
        with patch.object(app, 'update_icon_menu'):
            # Fonction qui pause
            def pause_app():
                for _ in range(50):
                    app.pause_for_hour()
                    time.sleep(0.001)
            
            # Fonction qui reprend
            def resume_app():
                for _ in range(50):
                    app.resume()
                    time.sleep(0.001)
            
            # Créer des threads concurrents
            pause_thread = threading.Thread(target=pause_app, daemon=True)
            resume_thread = threading.Thread(target=resume_app, daemon=True)
            
            pause_thread.start()
            resume_thread.start()
            
            # Attendre que les threads se terminent
            pause_thread.join(timeout=2)
            resume_thread.join(timeout=2)
            
            # Vérifier que l'app est dans un état cohérent
            assert isinstance(app.paused, bool)


class TestDaemonThreads:
    """Tests pour vérifier que les threads sont des daemons."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.show_checkin_dialog')
    def test_checkin_thread_is_daemon(self, mock_dialog, mock_selector, mock_preferences, mock_icon):
        """Test que le thread de check-in est daemon."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Appeler show_checkin
        thread = app.show_checkin()
        
        # Vérifier que le thread est daemon
        assert thread.daemon == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.show_stats_window')
    def test_stats_thread_is_daemon(self, mock_stats, mock_selector, mock_preferences, mock_icon):
        """Test que le thread de stats est daemon."""
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
        
        # Vérifier que le thread est daemon
        assert thread.daemon == True
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_snooze_thread_is_daemon(self, mock_selector, mock_preferences, mock_icon):
        """Test que le thread de snooze est daemon."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.last_notification = ("dos", "Message", "Exercise")
        
        # Capturer le thread créé
        created_thread = None
        original_thread = threading.Thread
        
        def capture_thread(*args, **kwargs):
            nonlocal created_thread
            created_thread = original_thread(*args, **kwargs)
            return created_thread
        
        # Mock Thread pour capturer
        with patch('threading.Thread', side_effect=capture_thread):
            # Appeler snooze_notification
            app.snooze_notification()
            
            # Attendre un peu pour que le thread soit créé
            time.sleep(0.05)
            
            # Vérifier que le thread est daemon
            if created_thread:
                assert created_thread.daemon == True


class TestScheduleLoop:
    """Tests spécifiques pour la boucle du scheduler."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.schedule.run_pending')
    @patch('time.sleep')
    def test_schedule_loop_calls_run_pending(self, mock_sleep, mock_run_pending,
                                            mock_selector, mock_preferences, mock_icon):
        """Test que schedule_loop appelle schedule.run_pending."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Faire en sorte que la boucle s'exécute 2 fois puis s'arrête
        call_count = [0]
        
        def stop_after_two(duration):
            call_count[0] += 1
            if call_count[0] >= 2:
                app.running = False
        
        mock_sleep.side_effect = stop_after_two
        
        # Mock update_icon_menu
        with patch.object(app, 'update_icon_menu'):
            # Mock datetime pour simuler un jour de semaine
            with patch('src.app.datetime') as mock_datetime:
                monday = datetime(2026, 3, 9, 10, 0, 0)  # Lundi
                mock_datetime.now.return_value = monday
                
                # Appeler schedule_loop
                app.schedule_loop()
        
        # Vérifier que run_pending a été appelé
        assert mock_run_pending.call_count >= 2
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.schedule.run_pending')
    @patch('time.sleep')
    def test_schedule_loop_updates_menu(self, mock_sleep, mock_run_pending,
                                       mock_selector, mock_preferences, mock_icon):
        """Test que schedule_loop met à jour le menu."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Faire en sorte que la boucle s'exécute 2 fois puis s'arrête
        call_count = [0]
        
        def stop_after_two(duration):
            call_count[0] += 1
            if call_count[0] >= 2:
                app.running = False
        
        mock_sleep.side_effect = stop_after_two
        
        # Mock update_icon_menu
        with patch.object(app, 'update_icon_menu') as mock_update:
            # Mock datetime pour simuler un jour de semaine
            with patch('src.app.datetime') as mock_datetime:
                monday = datetime(2026, 3, 9, 10, 0, 0)  # Lundi
                mock_datetime.now.return_value = monday
                
                # Appeler schedule_loop
                app.schedule_loop()
        
        # Vérifier que update_icon_menu a été appelé
        assert mock_update.call_count >= 2
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.schedule.run_pending')
    @patch('time.sleep')
    def test_schedule_loop_skips_weekend(self, mock_sleep, mock_run_pending,
                                        mock_selector, mock_preferences, mock_icon):
        """Test que schedule_loop ne traite pas les jobs le weekend."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Faire en sorte que la boucle s'exécute 2 fois puis s'arrête
        call_count = [0]
        
        def stop_after_two(duration):
            call_count[0] += 1
            if call_count[0] >= 2:
                app.running = False
        
        mock_sleep.side_effect = stop_after_two
        
        # Mock update_icon_menu
        with patch.object(app, 'update_icon_menu'):
            # Mock datetime pour simuler un samedi
            with patch('src.app.datetime') as mock_datetime:
                saturday = datetime(2026, 3, 7, 10, 0, 0)  # Samedi
                mock_datetime.now.return_value = saturday
                
                # Appeler schedule_loop
                app.schedule_loop()
        
        # Vérifier que run_pending n'a PAS été appelé (weekend)
        mock_run_pending.assert_not_called()
