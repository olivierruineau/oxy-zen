"""Tests pour NotificationConfigWindow avec focus sur la validation des inputs."""

import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.ui.notification_config_window import NotificationConfigWindow


class TestNotificationConfigWindowValidation:
    """Tests de validation pour NotificationConfigWindow."""

    @pytest.fixture
    def mock_on_save(self):
        """Mock pour le callback on_save."""
        return Mock()

    @pytest.fixture
    def window(self, mock_on_save):
        """Crée une fenêtre de configuration pour les tests."""
        # Mock complet de tk.Tk et tk.IntVar pour éviter l'initialisation réelle de tkinter
        with patch('tkinter.Tk') as mock_tk_class, \
             patch('tkinter.IntVar') as mock_intvar_class, \
             patch.object(NotificationConfigWindow, 'build_ui'), \
             patch.object(NotificationConfigWindow, 'center_window'):
            
            # Setup mock root
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            
            # Setup mock IntVar pour qu'il retourne un objet avec get/set
            def create_mock_intvar(value=0):
                mock_var = MagicMock()
                mock_var._value = value
                mock_var.get.return_value = value
                def set_value(v):
                    mock_var._value = v
                    mock_var.get.return_value = v
                mock_var.set.side_effect = set_value
                return mock_var
            
            mock_intvar_class.side_effect = create_mock_intvar
            
            config = {
                "frequency": 30,
                "moment": 0,
                "start_hour": 9,
                "start_minute": 0,
                "end_hour": 17,
                "end_minute": 0,
            }
            window = NotificationConfigWindow(config, mock_on_save)
            yield window
            # Pas besoin de destroy avec un mock

    def test_valid_configuration_saves_successfully(self, window, mock_on_save):
        """Test qu'une configuration valide est enregistrée correctement."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(0)
        window.end_hour_var.set(17)
        window.end_minute_var.set(30)
        
        # Act
        window.save()
        
        # Assert
        mock_on_save.assert_called_once()
        config = mock_on_save.call_args[0][0]
        assert config["start_hour"] == 9
        assert config["start_minute"] == 0
        assert config["end_hour"] == 17
        assert config["end_minute"] == 30

    def test_start_hour_below_0_shows_error(self, window, mock_on_save):
        """Test qu'une heure de début < 0 affiche une erreur."""
        # Arrange
        window.start_hour_var.set(-1)
        window.start_minute_var.set(0)
        window.end_hour_var.set(17)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "heure de début" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 23" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_start_hour_above_23_shows_error(self, window, mock_on_save):
        """Test qu'une heure de début > 23 affiche une erreur."""
        # Arrange
        window.start_hour_var.set(24)
        window.start_minute_var.set(0)
        window.end_hour_var.set(17)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "heure de début" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 23" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_end_hour_below_0_shows_error(self, window, mock_on_save):
        """Test qu'une heure de fin < 0 affiche une erreur."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(0)
        window.end_hour_var.set(-1)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "heure de fin" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 23" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_end_hour_above_23_shows_error(self, window, mock_on_save):
        """Test qu'une heure de fin > 23 affiche une erreur."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(0)
        window.end_hour_var.set(24)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "heure de fin" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 23" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_start_minute_below_0_shows_error(self, window, mock_on_save):
        """Test que des minutes de début < 0 affichent une erreur."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(-1)
        window.end_hour_var.set(17)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "minutes de début" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 59" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_start_minute_above_59_shows_error(self, window, mock_on_save):
        """Test que des minutes de début > 59 affichent une erreur."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(60)
        window.end_hour_var.set(17)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "minutes de début" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 59" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_end_minute_below_0_shows_error(self, window, mock_on_save):
        """Test que des minutes de fin < 0 affichent une erreur."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(0)
        window.end_hour_var.set(17)
        window.end_minute_var.set(-1)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "minutes de fin" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 59" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_end_minute_above_59_shows_error(self, window, mock_on_save):
        """Test que des minutes de fin > 59 affichent une erreur."""
        # Arrange
        window.start_hour_var.set(9)
        window.start_minute_var.set(0)
        window.end_hour_var.set(17)
        window.end_minute_var.set(60)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "minutes de fin" in mock_error.call_args[0][1].lower()
        assert "entre 0 et 59" in mock_error.call_args[0][1]
        mock_on_save.assert_not_called()

    def test_start_time_equals_end_time_shows_error(self, window, mock_on_save):
        """Test que start_time == end_time affiche une erreur."""
        # Arrange
        window.start_hour_var.set(10)
        window.start_minute_var.set(30)
        window.end_hour_var.set(10)
        window.end_minute_var.set(30)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "avant" in mock_error.call_args[0][1].lower()
        mock_on_save.assert_not_called()

    def test_start_time_after_end_time_shows_error(self, window, mock_on_save):
        """Test que start_time > end_time affiche une erreur."""
        # Arrange
        window.start_hour_var.set(17)
        window.start_minute_var.set(0)
        window.end_hour_var.set(9)
        window.end_minute_var.set(0)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "avant" in mock_error.call_args[0][1].lower()
        mock_on_save.assert_not_called()

    def test_start_hour_equals_end_hour_but_start_minute_after_end_minute_shows_error(self, window, mock_on_save):
        """Test que 10:45 > 10:30 affiche une erreur."""
        # Arrange
        window.start_hour_var.set(10)
        window.start_minute_var.set(45)
        window.end_hour_var.set(10)
        window.end_minute_var.set(30)
        
        # Act
        with patch('tkinter.messagebox.showerror') as mock_error:
            window.save()
        
        # Assert
        mock_error.assert_called_once()
        assert "avant" in mock_error.call_args[0][1].lower()
        mock_on_save.assert_not_called()

    def test_start_hour_equals_end_hour_but_start_minute_before_end_minute_succeeds(self, window, mock_on_save):
        """Test que 10:15 < 10:30 réussit."""
        # Arrange
        window.start_hour_var.set(10)
        window.start_minute_var.set(15)
        window.end_hour_var.set(10)
        window.end_minute_var.set(30)
        
        # Act
        window.save()
        
        # Assert
        mock_on_save.assert_called_once()
        config = mock_on_save.call_args[0][0]
        assert config["start_hour"] == 10
        assert config["start_minute"] == 15
        assert config["end_hour"] == 10
        assert config["end_minute"] == 30

    def test_boundary_values_0_and_23_are_valid(self, window, mock_on_save):
        """Test que les valeurs limites 0 et 23 sont valides pour les heures."""
        # Arrange
        window.start_hour_var.set(0)
        window.start_minute_var.set(0)
        window.end_hour_var.set(23)
        window.end_minute_var.set(59)
        
        # Act
        window.save()
        
        # Assert
        mock_on_save.assert_called_once()
        config = mock_on_save.call_args[0][0]
        assert config["start_hour"] == 0
        assert config["start_minute"] == 0
        assert config["end_hour"] == 23
        assert config["end_minute"] == 59
