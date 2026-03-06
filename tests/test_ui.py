"""Tests unitaires pour les composants UI."""

import pytest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock, call
from src.ui.checkin_window import CheckInWindow
from src.ui.stats_window import StatsWindow
from src.ui.notification_config_window import NotificationConfigWindow


class TestCheckInWindow:
    """Tests pour CheckInWindow."""
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_checkin_window_init(self, mock_tk, mock_bool_var):
        """Test l'initialisation de CheckInWindow."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        callback = Mock()
        
        window = CheckInWindow(callback)
        
        # Vérifier que le callback est stocké
        assert window.callback == callback
        
        # Vérifier que la fenêtre root a été configurée
        mock_root.title.assert_called_once_with("Oxy-Zen Check-In 🧘")
        # geometry est appelé deux fois (initial + centrage)
        assert mock_root.geometry.call_count >= 1
        assert mock_root.geometry.call_args_list[0] == (('350x500',),)
        mock_root.resizable.assert_called_once_with(False, False)
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_checkin_window_init_with_current_areas(self, mock_tk, mock_bool_var):
        """Test l'initialisation avec des zones déjà sélectionnées."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        callback = Mock()
        current_areas = ["dos", "cou"]
        
        window = CheckInWindow(callback, current_areas=current_areas)
        
        assert window.current_areas == current_areas
        assert window.callback == callback
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_checkin_window_validate_with_selections(self, mock_tk, mock_bool_var):
        """Test la validation avec des sélections."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        callback = Mock()
        
        window = CheckInWindow(callback)
        
        # Mocker no_problem_var pour qu'il retourne False
        mock_no_problem = MagicMock()
        mock_no_problem.get.return_value = False
        window.no_problem_var = mock_no_problem
        
        # Simuler des sélections avec des mocks
        mock_var_dos = MagicMock()
        mock_var_dos.get.return_value = True
        mock_var_cou = MagicMock()
        mock_var_cou.get.return_value = False
        mock_var_yeux = MagicMock()
        mock_var_yeux.get.return_value = True
        
        window.check_vars = {
            "dos": mock_var_dos,
            "cou": mock_var_cou,
            "yeux": mock_var_yeux,
        }
        
        # Appeler validate
        window.validate()
        
        # Vérifier que le callback est appelé avec les bonnes valeurs
        callback.assert_called_once_with(["dos", "yeux"])
        
        # Vérifier que la fenêtre est fermée (quit au lieu de destroy)
        mock_root.quit.assert_called_once()
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_checkin_window_cancel(self, mock_tk, mock_bool_var):
        """Test l'annulation de la fenêtre."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        callback = Mock()
        
        window = CheckInWindow(callback)
        window.cancel()
        
        # Vérifier que le callback n'a pas été appelé
        callback.assert_not_called()
        
        # Vérifier que la fenêtre est détruite
        mock_root.destroy.assert_called_once()
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_checkin_window_center_window(self, mock_tk, mock_bool_var):
        """Test le centrage de la fenêtre."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Configurer les mocks pour simuler les dimensions de l'écran
        mock_root.winfo_screenwidth.return_value = 1920
        mock_root.winfo_screenheight.return_value = 1080
        mock_root.winfo_width.return_value = 350
        mock_root.winfo_height.return_value = 500
        
        callback = Mock()
        window = CheckInWindow(callback)
        
        # Vérifier que geometry est appelé pour centrer
        # (1920 // 2) - (350 // 2) = 785
        # (1080 // 2) - (500 // 2) = 290
        calls = mock_root.geometry.call_args_list
        # Le dernier appel devrait être pour centrer
        assert len(calls) >= 2  # Au moins l'appel initial + le centrage
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_checkin_window_keyboard_shortcuts(self, mock_tk, mock_bool_var):
        """Test les raccourcis clavier."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        callback = Mock()
        
        window = CheckInWindow(callback)
        
        # Vérifier que les raccourcis sont enregistrés
        bind_calls = mock_root.bind.call_args_list
        
        # Chercher les bindings pour Escape et Return
        bound_keys = [call[0][0] for call in bind_calls]
        assert '<Escape>' in bound_keys
        assert '<Return>' in bound_keys


class TestStatsWindow:
    """Tests pour StatsWindow."""
    
    @patch('tkinter.Tk')
    def test_stats_window_init(self, mock_tk):
        """Test l'initialisation de StatsWindow."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        stats = {
            "total_notifications": 100,
            "total_completed": 75,
            "total_checkins": 10,
            "completion_rate": 75.0,
            "favorite_categories": ["dos", "yeux"],
            "problem_areas": ["dos", "yeux"],
            "recent_exercises": [],
        }
        
        window = StatsWindow(stats)
        
        # Vérifier que les stats sont stockées
        assert window.stats == stats
        
        # Vérifier que la fenêtre root a été configurée
        mock_root.title.assert_called_once_with("Oxy-Zen - Statistiques 📊")
        # geometry est appelé deux fois (initial + centrage)
        assert mock_root.geometry.call_count >= 1
        assert mock_root.geometry.call_args_list[0] == (('400x550',),)
        mock_root.resizable.assert_called_once_with(False, False)
    
    @patch('tkinter.Tk')
    def test_stats_window_display_with_data(self, mock_tk):
        """Test l'affichage avec des données."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        stats = {
            "total_notifications": 50,
            "total_completed": 40,
            "total_checkins": 5,
            "completion_rate": 80.0,
            "exercises_by_category": {"dos": 15, "yeux": 10, "cou": 8},
            "best_streak": 7,
            "problem_areas": ["dos"],
            "recent_exercises": [],
        }
        
        window = StatsWindow(stats)
        
        # Vérifier que la fenêtre est créée sans erreur
        assert window.stats == stats
        mock_root.title.assert_called_once()
    
    @patch('tkinter.Tk')
    def test_stats_window_close(self, mock_tk):
        """Test la fermeture de la fenêtre."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        stats = {"total_notifications": 0, "total_checkins": 0, "problem_areas": [], "recent_exercises": []}
        window = StatsWindow(stats)
        window.close()
        
        # Vérifier que la fenêtre est détruite
        mock_root.destroy.assert_called_once()
    
    @patch('tkinter.Tk')
    def test_stats_window_center_window(self, mock_tk):
        """Test le centrage de la fenêtre."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Configurer les mocks pour simuler les dimensions de l'écran
        mock_root.winfo_screenwidth.return_value = 1920
        mock_root.winfo_screenheight.return_value = 1080
        mock_root.winfo_width.return_value = 400
        mock_root.winfo_height.return_value = 550
        
        stats = {"total_notifications": 0, "total_checkins": 0, "problem_areas": [], "recent_exercises": []}
        window = StatsWindow(stats)
        
        # Vérifier que geometry est appelé
        calls = mock_root.geometry.call_args_list
        # Au moins l'appel initial + le centrage
        assert len(calls) >= 2


class TestNotificationConfigWindow:
    """Tests pour NotificationConfigWindow."""
    
    @patch('tkinter.IntVar')
    @patch('tkinter.Tk')
    def test_notification_config_window_init(self, mock_tk, mock_int_var):
        """Test l'initialisation de NotificationConfigWindow."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Mock mainloop pour ne pas bloquer
        mock_root.mainloop = Mock()
        
        current_config = {
            "frequency": 60,
            "moment": 7,
            "start_hour": 8,
            "start_minute": 0,
            "end_hour": 17,
            "end_minute": 0,
        }
        on_save = Mock()
        
        window = NotificationConfigWindow(current_config, on_save)
        
        # Vérifier que la config est stockée
        assert window.current_config == current_config
        assert window.on_save == on_save
        
        # Vérifier que la fenêtre root a été configurée
        mock_root.title.assert_called_once_with("Configuration des notifications")
        # geometry est appelé deux fois (initial + centrage)
        assert mock_root.geometry.call_count >= 1
        assert mock_root.geometry.call_args_list[0] == (('450x500',),)
        mock_root.resizable.assert_called_once_with(False, False)
    
    @patch('tkinter.IntVar')
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.showerror')
    def test_notification_config_window_validation_invalid_hours(self, mock_showerror, mock_tk, mock_int_var):
        """Test la validation avec des heures invalides."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_root.mainloop = Mock()
        
        current_config = {
            "frequency": 30,
            "start_hour": 10,
            "end_hour": 8,  # Fin avant début
        }
        on_save = Mock()
        
        window = NotificationConfigWindow(current_config, on_save)
        
        # Définir des valeurs invalides
        window.start_hour_var.get = Mock(return_value=10)
        window.end_hour_var.get = Mock(return_value=8)
        window.start_minute_var.get = Mock(return_value=0)
        window.end_minute_var.get = Mock(return_value=0)
        
        # Appeler save
        window.save()
        
        # Vérifier qu'une erreur est affichée
        mock_showerror.assert_called_once()
        
        # Vérifier que on_save n'a pas été appelé
        on_save.assert_not_called()
    
    @patch('tkinter.IntVar')
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.showerror')
    def test_notification_config_window_validation_same_time(self, mock_showerror, mock_tk, mock_int_var):
        """Test la validation avec même heure de début et fin."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_root.mainloop = Mock()
        
        current_config = {"frequency": 30}
        on_save = Mock()
        
        window = NotificationConfigWindow(current_config, on_save)
        
        # Définir la même heure
        window.start_hour_var.get = Mock(return_value=9)
        window.end_hour_var.get = Mock(return_value=9)
        window.start_minute_var.get = Mock(return_value=0)
        window.end_minute_var.get = Mock(return_value=0)
        
        # Appeler save
        window.save()
        
        # Vérifier qu'une erreur est affichée
        mock_showerror.assert_called_once()
        
        # Vérifier que on_save n'a pas été appelé
        on_save.assert_not_called()
    
    @patch('src.ui.notification_config_window.messagebox')
    @patch('tkinter.IntVar')
    @patch('tkinter.Tk')
    def test_notification_config_window_save_valid(self, mock_tk, mock_int_var, mock_messagebox):
        """Test l'enregistrement avec des valeurs valides."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_root.mainloop = Mock()
        
        current_config = {"frequency": 30}
        on_save = Mock()
        
        window = NotificationConfigWindow(current_config, on_save)
        
        # Créer des mocks pour les IntVar qui retournent des valeurs valides
        mock_freq_var = MagicMock()
        mock_freq_var.get.return_value = 60
        mock_moment_var = MagicMock()
        mock_moment_var.get.return_value = 7
        mock_start_hour_var = MagicMock()
        mock_start_hour_var.get.return_value = 8
        mock_start_minute_var = MagicMock()
        mock_start_minute_var.get.return_value = 30
        mock_end_hour_var = MagicMock()
        mock_end_hour_var.get.return_value = 17
        mock_end_minute_var = MagicMock()
        mock_end_minute_var.get.return_value = 0
        
        window.frequency_var = mock_freq_var
        window.moment_var = mock_moment_var
        window.start_hour_var = mock_start_hour_var
        window.start_minute_var = mock_start_minute_var
        window.end_hour_var = mock_end_hour_var
        window.end_minute_var = mock_end_minute_var
        
        # Appeler save
        window.save()
        
        # Vérifier que on_save a été appelé avec la bonne config
        expected_config = {
            "frequency": 60,
            "moment": 7,
            "start_hour": 8,
            "start_minute": 30,
            "end_hour": 17,
            "end_minute": 0,
        }
        on_save.assert_called_once_with(expected_config)
        
        # Vérifier que la fenêtre est détruite
        mock_root.destroy.assert_called_once()
    
    @patch('tkinter.IntVar')
    @patch('tkinter.Tk')
    def test_notification_config_window_default_values(self, mock_tk, mock_int_var):
        """Test les valeurs par défaut."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_root.mainloop = Mock()
        
        current_config = {}  # Pas de config
        on_save = Mock()
        
        window = NotificationConfigWindow(current_config, on_save)
        
        # Vérifier que les valeurs par défaut sont utilisées
        # Les valeurs par défaut sont définies dans le constructeur
        assert window.current_config == {}


class TestUIIntegration:
    """Tests d'intégration pour les composants UI."""
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_multiple_windows_can_coexist(self, mock_tk, mock_bool_var):
        """Test que plusieurs fenêtres peuvent coexister."""
        mock_roots = [MagicMock() for _ in range(3)]
        mock_tk.side_effect = mock_roots
        
        # Créer plusieurs fenêtres
        callback1 = Mock()
        window1 = CheckInWindow(callback1)
        
        stats = {"total_notifications": 10, "total_checkins": 2, "problem_areas": [], "recent_exercises": []}
        window2 = StatsWindow(stats)
        
        # Vérifier que les fenêtres sont indépendantes
        assert window1.root != window2.root
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_window_focus_and_topmost(self, mock_tk, mock_bool_var):
        """Test que les fenêtres demandent le focus et sont topmost."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        callback = Mock()
        window = CheckInWindow(callback)
        
        # Vérifier que focus_force est appelé
        mock_root.focus_force.assert_called_once()
        mock_root.lift.assert_called_once()
        
        # Vérifier que topmost est géré
        topmost_calls = [call for call in mock_root.attributes.call_args_list 
                        if '-topmost' in str(call)]
        assert len(topmost_calls) >= 1


# Tests smoke pour tous les dialogs
class TestSmokeTests:
    """Tests smoke pour vérifier que tous les dialogs peuvent être créés."""
    
    @patch('tkinter.BooleanVar')
    @patch('tkinter.Tk')
    def test_smoke_checkin_window(self, mock_tk, mock_bool_var):
        """Test smoke pour CheckInWindow."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        try:
            window = CheckInWindow(Mock())
            assert window is not None
        except Exception as e:
            pytest.fail(f"CheckInWindow smoke test failed: {e}")
    
    @patch('tkinter.Tk')
    def test_smoke_stats_window(self, mock_tk):
        """Test smoke pour StatsWindow."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        try:
            window = StatsWindow({"total_notifications": 0, "total_checkins": 0, "problem_areas": [], "recent_exercises": []})
            assert window is not None
        except Exception as e:
            pytest.fail(f"StatsWindow smoke test failed: {e}")
    
    @patch('tkinter.IntVar')
    @patch('tkinter.Tk')
    def test_smoke_notification_config_window(self, mock_tk, mock_int_var):
        """Test smoke pour NotificationConfigWindow."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_root.mainloop = Mock()
        
        try:
            window = NotificationConfigWindow({}, Mock())
            assert window is not None
        except Exception as e:
            pytest.fail(f"NotificationConfigWindow smoke test failed: {e}")
