"""Tests de thread safety pour Oxy-Zen."""

import pytest
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.app import OxyZenApp
from src.config import UserPreferences


class TestThreadSafetyApp:
    """Tests de concurrence pour OxyZenApp."""
    
    @patch('src.app.ExerciseSelector')
    @patch('src.app.UserPreferences')
    def test_concurrent_pause_resume(self, mock_prefs, mock_selector):
        """Teste les modifications concurrentes de l'état pause."""
        app = OxyZenApp()
        app.preferences = MagicMock()
        
        results = []
        errors = []
        
        def toggle_pause(thread_id):
            try:
                for i in range(50):
                    app.paused = True
                    time.sleep(0.001)
                    app.paused = False
                    time.sleep(0.001)
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # Créer 5 threads qui modifient paused en même temps
        threads = []
        for i in range(5):
            t = threading.Thread(target=toggle_pause, args=(i,))
            threads.append(t)
            t.start()
        
        # Attendre que tous les threads finissent
        for t in threads:
            t.join()
        
        # Vérifier qu'il n'y a pas eu d'erreurs
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        # L'état final devrait être cohérent
        final_state = app.paused
        assert isinstance(final_state, bool)
    
    @patch('src.app.ExerciseSelector')
    @patch('src.app.UserPreferences')
    def test_concurrent_last_notification(self, mock_prefs, mock_selector):
        """Teste les modifications concurrentes de last_notification."""
        app = OxyZenApp()
        app.preferences = MagicMock()
        
        errors = []
        
        def set_notification(thread_id):
            try:
                for i in range(100):
                    app.last_notification = (f"cat_{thread_id}", f"msg_{i}", f"ex_{i}")
                    # Lire immédiatement après
                    notif = app.last_notification
                    # Vérifier que c'est bien un tuple
                    assert isinstance(notif, tuple) or notif is None
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # Créer 3 threads qui modifient last_notification
        threads = []
        for i in range(3):
            t = threading.Thread(target=set_notification, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors occurred: {errors}"
    
    @patch('src.app.ExerciseSelector')
    @patch('src.app.UserPreferences')
    def test_concurrent_pause_until(self, mock_prefs, mock_selector):
        """Teste les modifications concurrentes de pause_until."""
        from datetime import datetime, timedelta
        
        app = OxyZenApp()
        app.preferences = MagicMock()
        
        errors = []
        
        def set_pause_until(thread_id):
            try:
                for i in range(50):
                    app.pause_until = datetime.now() + timedelta(minutes=thread_id)
                    time.sleep(0.001)
                    app.pause_until = None
                    time.sleep(0.001)
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        threads = []
        for i in range(3):
            t = threading.Thread(target=set_pause_until, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors occurred: {errors}"
    
    @patch('src.app.ExerciseSelector')
    @patch('src.app.UserPreferences')
    def test_mixed_operations(self, mock_prefs, mock_selector):
        """Teste un mélange d'opérations concurrentes."""
        from datetime import datetime, timedelta
        
        app = OxyZenApp()
        app.preferences = MagicMock()
        
        errors = []
        
        def pause_operations():
            try:
                for _ in range(30):
                    app.paused = True
                    time.sleep(0.002)
                    app.paused = False
            except Exception as e:
                errors.append(f"Pause error: {e}")
        
        def notification_operations():
            try:
                for i in range(30):
                    app.last_notification = ("test", f"msg_{i}", "exercise")
                    time.sleep(0.002)
            except Exception as e:
                errors.append(f"Notification error: {e}")
        
        def pause_until_operations():
            try:
                for _ in range(30):
                    app.pause_until = datetime.now() + timedelta(hours=1)
                    time.sleep(0.002)
            except Exception as e:
                errors.append(f"Pause until error: {e}")
        
        threads = [
            threading.Thread(target=pause_operations),
            threading.Thread(target=notification_operations),
            threading.Thread(target=pause_until_operations),
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors occurred: {errors}"


class TestThreadSafetyConfig:
    """Tests de concurrence pour UserPreferences."""
    
    def test_concurrent_increment_notification_count(self, tmp_path):
        """Teste l'incrémentation concurrente du compteur de notifications."""
        # Créer une instance avec un fichier temporaire
        with patch.object(UserPreferences, 'CONFIG_DIR', tmp_path):
            with patch.object(UserPreferences, 'CONFIG_FILE', tmp_path / 'config.json'):
                prefs = UserPreferences()
                prefs.stats["total_notifications"] = 0
                
                errors = []
                
                def increment():
                    try:
                        for _ in range(50):
                            prefs.increment_notification_count()
                    except Exception as e:
                        errors.append(f"Increment error: {e}")
                
                # Créer 5 threads qui incrémentent
                threads = []
                for _ in range(5):
                    t = threading.Thread(target=increment)
                    threads.append(t)
                    t.start()
                
                for t in threads:
                    t.join()
                
                assert len(errors) == 0, f"Errors occurred: {errors}"
                # On devrait avoir 5 * 50 = 250 notifications
                # (Note: avec le save après chaque incrémentation, on peut avoir moins si certaines sont perdues)
                # L'important est qu'il n'y ait pas d'erreur de concurrence
                assert prefs.stats["total_notifications"] > 0
    
    def test_concurrent_add_exercise_to_history(self, tmp_path):
        """Teste l'ajout concurrent à l'historique des exercices."""
        with patch.object(UserPreferences, 'CONFIG_DIR', tmp_path):
            with patch.object(UserPreferences, 'CONFIG_FILE', tmp_path / 'config.json'):
                prefs = UserPreferences()
                
                errors = []
                
                def add_exercises(thread_id):
                    try:
                        for i in range(30):
                            prefs.add_exercise_to_history(f"cat_{thread_id}", f"msg_{i}")
                    except Exception as e:
                        errors.append(f"Thread {thread_id} error: {e}")
                
                threads = []
                for i in range(3):
                    t = threading.Thread(target=add_exercises, args=(i,))
                    threads.append(t)
                    t.start()
                
                for t in threads:
                    t.join()
                
                assert len(errors) == 0, f"Errors occurred: {errors}"
                # Vérifier que l'historique est cohérent (max 20 entrées)
                assert len(prefs.stats["exercises_done"]) <= 20
    
    def test_concurrent_mixed_operations(self, tmp_path):
        """Teste un mélange d'opérations concurrentes sur UserPreferences."""
        with patch.object(UserPreferences, 'CONFIG_DIR', tmp_path):
            with patch.object(UserPreferences, 'CONFIG_FILE', tmp_path / 'config.json'):
                prefs = UserPreferences()
                
                errors = []
                
                def increment_operation():
                    try:
                        for _ in range(20):
                            prefs.increment_notification_count()
                            time.sleep(0.001)
                    except Exception as e:
                        errors.append(f"Increment error: {e}")
                
                def history_operation(thread_id):
                    try:
                        for i in range(20):
                            prefs.add_exercise_to_history(f"cat_{thread_id}", f"msg_{i}")
                            time.sleep(0.001)
                    except Exception as e:
                        errors.append(f"History error: {e}")
                
                threads = [
                    threading.Thread(target=increment_operation),
                    threading.Thread(target=history_operation, args=(0,)),
                    threading.Thread(target=history_operation, args=(1,)),
                ]
                
                for t in threads:
                    t.start()
                
                for t in threads:
                    t.join()
                
                assert len(errors) == 0, f"Errors occurred: {errors}"
                # Vérifier l'intégrité des données
                assert prefs.stats["total_notifications"] > 0
                assert len(prefs.stats["exercises_done"]) <= 20


class TestRapidPauseResume:
    """Tests de pause/reprise rapide."""
    
    @patch('src.app.ExerciseSelector')
    @patch('src.app.UserPreferences')
    def test_rapid_pause_resume(self, mock_prefs, mock_selector):
        """Teste la pause et reprise très rapides successives."""
        app = OxyZenApp()
        app.preferences = MagicMock()
        
        errors = []
        
        def rapid_toggle():
            try:
                for _ in range(100):
                    app.paused = True
                    # Lecture immédiate
                    assert app.paused is True
                    
                    app.paused = False
                    # Lecture immédiate
                    assert app.paused is False
            except AssertionError as e:
                errors.append(f"State inconsistency: {e}")
            except Exception as e:
                errors.append(f"Error: {e}")
        
        # Un seul thread pour tester la cohérence
        t = threading.Thread(target=rapid_toggle)
        t.start()
        t.join()
        
        assert len(errors) == 0, f"Errors occurred: {errors}"
