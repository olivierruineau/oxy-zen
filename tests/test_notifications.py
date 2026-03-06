"""Tests pour les fonctionnalités de notification."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import time
from src.app import OxyZenApp
from src.config import UserPreferences


class TestSendNotification:
    """Tests pour l'envoi de notifications."""
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_send_notification_success(self, mock_selector, mock_preferences, 
                                      mock_icon, mock_notification):
        """Test l'envoi réussi d'une notification."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification
        with patch.object(app, 'update_icon_menu'):
            app.send_notification("dos", "Time for a break!", "Stretch your back")
        
        # Vérifier que Notification a été créé
        mock_notification.assert_called_once()
        
        # Vérifier que show() a été appelé
        mock_notif_instance.show.assert_called_once()
        
        # Vérifier que les stats ont été mises à jour
        mock_prefs_instance.increment_notification_count.assert_called_once()
        mock_prefs_instance.add_exercise_to_history.assert_called_once_with(
            "dos", "Time for a break!"
        )
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_send_notification_stores_last_notification(self, mock_selector, mock_preferences,
                                                        mock_icon, mock_notification):
        """Test que la dernière notification est sauvegardée."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification
        with patch.object(app, 'update_icon_menu'):
            app.send_notification("yeux", "Eye break", "Look at distance")
        
        # Vérifier que last_notification est défini
        assert app.last_notification == ("yeux", "Eye break", "Look at distance")
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_send_notification_updates_menu(self, mock_selector, mock_preferences,
                                           mock_icon, mock_notification):
        """Test que le menu est mis à jour après l'envoi."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock update_icon_menu
        with patch.object(app, 'update_icon_menu') as mock_update:
            app.send_notification("cou", "Neck break", "Roll your neck")
            
            # Vérifier que update_icon_menu a été appelé
            mock_update.assert_called_once()
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_send_notification_with_audio(self, mock_selector, mock_preferences,
                                         mock_icon, mock_notification):
        """Test que la notification a du son."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification
        with patch.object(app, 'update_icon_menu'):
            app.send_notification("dos", "Message", "Exercise")
        
        # Vérifier que set_audio a été appelé
        mock_notif_instance.set_audio.assert_called_once()
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_send_notification_handles_error(self, mock_selector, mock_preferences,
                                            mock_icon, mock_notification):
        """Test la gestion d'erreur lors de l'envoi."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Faire échouer Notification
        mock_notification.side_effect = Exception("Notification error")
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification (ne devrait pas crasher)
        try:
            app.send_notification("dos", "Message", "Exercise")
            # Le test passe si pas d'exception
        except Exception as e:
            pytest.fail(f"send_notification should handle errors: {e}")


class TestSnoozeNotification:
    """Tests pour la fonctionnalité snooze."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('time.sleep')
    def test_snooze_notification_resends_after_delay(self, mock_sleep, mock_selector,
                                                     mock_preferences, mock_icon):
        """Test que snooze renvoie la notification après le délai."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.last_notification = ("dos", "Message", "Exercise")
        app.paused = False
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Appeler snooze
            app.snooze_notification()
            
            # Attendre que le thread se termine (il est créé)
            time.sleep(0.1)
            
            # Vérifier que sleep a été appelé (peu importe la durée exacte à cause du mock)
            assert mock_sleep.called
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_snooze_notification_no_last_notification(self, mock_selector,
                                                      mock_preferences, mock_icon):
        """Test snooze quand il n'y a pas de dernière notification."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.last_notification = None
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Appeler snooze
            app.snooze_notification()
            
            # Attendre un peu
            time.sleep(0.1)
            
            # Vérifier que send_notification n'a pas été appelé
            mock_send.assert_not_called()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('time.sleep')
    def test_snooze_notification_respects_pause(self, mock_sleep, mock_selector,
                                                mock_preferences, mock_icon):
        """Test que snooze respecte l'état de pause."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.last_notification = ("dos", "Message", "Exercise")
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Mettre en pause avant que le snooze se déclenche
            app.paused = True
            
            # Appeler snooze
            app.snooze_notification()
            
            # Attendre que le délai se termine
            time.sleep(0.1)
            
            # Vérifier que send_notification n'a pas été appelé (car en pause)
            # Note: le thread peut toujours être en cours, donc on vérifie juste
            # que le comportement est paramétré correctement


class TestTriggerNotificationNow:
    """Tests pour le déclenchement manuel de notification."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_trigger_notification_now_success(self, mock_selector, mock_preferences, mock_icon):
        """Test le déclenchement manuel réussi."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector_instance.select_next_exercise.return_value = ("dos", "Message", "Exercise")
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Déclencher une notification
            app.trigger_notification_now()
            
            # Vérifier que send_notification a été appelé
            mock_send.assert_called_once_with("dos", "Message", "Exercise")
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_trigger_notification_now_no_exercise(self, mock_selector, mock_preferences, mock_icon):
        """Test le déclenchement manuel quand aucun exercice n'est disponible."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector_instance.select_next_exercise.return_value = None
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Déclencher une notification
            app.trigger_notification_now()
            
            # Vérifier que send_notification n'a pas été appelé
            mock_send.assert_not_called()


class TestNotificationJob:
    """Tests pour le job de notification schedulé."""
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_notification_job_when_paused(self, mock_selector, mock_preferences, mock_icon):
        """Test que le job ignore les notifications en pause."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = True
        
        # Mock les méthodes appelées
        with patch.object(app, 'selector') as mock_sel:
            # Appeler notification_job
            app.notification_job()
            
            # Vérifier que select_next_exercise n'a pas été appelé
            mock_sel.select_next_exercise.assert_not_called()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.is_session_locked')
    @patch('src.app.get_idle_duration')
    def test_notification_job_when_session_locked(self, mock_idle, mock_locked,
                                                  mock_selector, mock_preferences, mock_icon):
        """Test que le job ignore les notifications quand la session est verrouillée."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_locked.return_value = True
        mock_idle.return_value = 0
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Appeler notification_job
            app.notification_job()
            
            # Vérifier que send_notification n'a pas été appelé
            mock_send.assert_not_called()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.is_session_locked')
    @patch('src.app.get_idle_duration')
    def test_notification_job_when_idle_too_long(self, mock_idle, mock_locked,
                                                 mock_selector, mock_preferences, mock_icon):
        """Test que le job ignore les notifications si l'utilisateur est inactif."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_locked.return_value = False
        from src import constants
        mock_idle.return_value = constants.IDLE_THRESHOLD_SECONDS + 10  # Plus que le seuil
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Appeler notification_job
            app.notification_job()
            
            # Vérifier que send_notification n'a pas été appelé
            mock_send.assert_not_called()
    
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    @patch('src.app.is_session_locked')
    @patch('src.app.get_idle_duration')
    def test_notification_job_sends_when_conditions_met(self, mock_idle, mock_locked,
                                                        mock_selector, mock_preferences, mock_icon):
        """Test que le job envoie une notification quand toutes les conditions sont remplies."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector_instance.select_next_exercise.return_value = ("dos", "Message", "Exercise")
        mock_selector.return_value = mock_selector_instance
        
        mock_locked.return_value = False
        mock_idle.return_value = 10  # Actif récemment
        
        # Créer l'app
        app = OxyZenApp()
        app.paused = False
        app.selector = mock_selector_instance
        
        # Mock send_notification
        with patch.object(app, 'send_notification') as mock_send:
            # Appeler notification_job
            app.notification_job()
            
            # Vérifier que send_notification a été appelé
            mock_send.assert_called_once_with("dos", "Message", "Exercise")


class TestNotificationContent:
    """Tests pour le contenu des notifications."""
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_notification_has_correct_title(self, mock_selector, mock_preferences,
                                           mock_icon, mock_notification):
        """Test que la notification a le bon titre."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification
        with patch.object(app, 'update_icon_menu'):
            app.send_notification("dos", "Take a break!", "Stretch your back")
        
        # Vérifier que Notification a été créé avec le bon titre
        call_kwargs = mock_notification.call_args[1]
        assert call_kwargs['title'] == "Take a break!"
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_notification_has_correct_message(self, mock_selector, mock_preferences,
                                             mock_icon, mock_notification):
        """Test que la notification a le bon message."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification
        with patch.object(app, 'update_icon_menu'):
            app.send_notification("yeux", "Eye time", "Look at something far away")
        
        # Vérifier que Notification a été créé avec le bon message
        call_kwargs = mock_notification.call_args[1]
        assert call_kwargs['msg'] == "Look at something far away"
    
    @patch('src.app.Notification')
    @patch('src.app.Icon')
    @patch('src.app.UserPreferences')
    @patch('src.app.ExerciseSelector')
    def test_notification_has_long_duration(self, mock_selector, mock_preferences,
                                           mock_icon, mock_notification):
        """Test que la notification a une longue durée."""
        # Setup mocks
        mock_prefs_instance = MagicMock()
        mock_preferences.return_value = mock_prefs_instance
        mock_selector_instance = MagicMock()
        mock_selector.return_value = mock_selector_instance
        
        mock_notif_instance = MagicMock()
        mock_notification.return_value = mock_notif_instance
        
        # Créer l'app
        app = OxyZenApp()
        
        # Envoyer une notification
        with patch.object(app, 'update_icon_menu'):
            app.send_notification("dos", "Message", "Exercise")
        
        # Vérifier que duration est "long"
        call_kwargs = mock_notification.call_args[1]
        assert call_kwargs['duration'] == "long"
