"""Tests unitaires pour le module config.py."""

import pytest
import json
from datetime import datetime
from pathlib import Path
from src.config import UserPreferences


class TestUserPreferences:
    """Tests pour la classe UserPreferences."""
    
    def test_init_default_values(self, clean_preferences):
        """Test que l'initialisation crée les valeurs par défaut."""
        prefs = clean_preferences
        
        assert prefs.problem_areas == []
        assert prefs.last_checkin == ""
        assert prefs.weights != {}
        assert prefs.stats["total_notifications"] == 0
        assert prefs.stats["total_checkins"] == 0
        assert prefs.notification_config["frequency"] == 30
    
    def test_calculate_weights_no_problems(self, clean_preferences):
        """Test calcul des poids sans problèmes identifiés."""
        prefs = clean_preferences
        prefs.problem_areas = []
        prefs.calculate_weights()
        
        # Prevention globale devrait avoir le poids maximum
        assert prefs.weights["prevention_globale"] == 1.0
        
        # Toutes les catégories devraient avoir des petits poids
        for cat in UserPreferences.CATEGORIES:
            assert prefs.weights[cat] == 0.1
    
    def test_calculate_weights_with_problems(self, clean_preferences):
        """Test calcul des poids avec des zones à problème."""
        prefs = clean_preferences
        prefs.problem_areas = ["dos", "yeux"]
        prefs.calculate_weights()
        
        # Les zones à problème devraient avoir 70% / 2 = 35% chacune
        assert prefs.weights["dos"] == pytest.approx(0.7 / 2)
        assert prefs.weights["yeux"] == pytest.approx(0.7 / 2)
        
        # Prevention globale devrait avoir 30%
        assert prefs.weights["prevention_globale"] == 0.3
        
        # Les autres catégories devraient avoir un poids résiduel
        assert prefs.weights["jambes"] == 0.01
        assert prefs.weights["posture"] == 0.01
    
    def test_calculate_weights_single_problem(self, clean_preferences):
        """Test calcul des poids avec une seule zone à problème."""
        prefs = clean_preferences
        prefs.problem_areas = ["dos"]
        prefs.calculate_weights()
        
        # La zone à problème devrait avoir 70%
        assert prefs.weights["dos"] == 0.7
        
        # Prevention globale devrait avoir 30%
        assert prefs.weights["prevention_globale"] == 0.3
    
    def test_save_and_load(self, clean_preferences, temp_config_dir):
        """Test sauvegarde et chargement de la configuration."""
        prefs = clean_preferences
        prefs.problem_areas = ["dos", "yeux"]
        prefs.notification_config["frequency"] = 45
        prefs.stats["total_notifications"] = 10
        prefs.save()
        
        # Vérifier que le fichier existe
        assert prefs.CONFIG_FILE.exists()
        
        # Créer une nouvelle instance pour charger
        prefs2 = UserPreferences()
        
        assert prefs2.problem_areas == ["dos", "yeux"]
        assert prefs2.notification_config["frequency"] == 45
        assert prefs2.stats["total_notifications"] == 10
    
    def test_update_problem_areas(self, clean_preferences):
        """Test mise à jour des zones à problème."""
        prefs = clean_preferences
        prefs.update_problem_areas(["dos", "jambes"])
        
        assert prefs.problem_areas == ["dos", "jambes"]
        assert prefs.last_checkin != ""
        assert prefs.stats["total_checkins"] == 1
        
        # Vérifier que les poids ont été recalculés
        assert prefs.weights["dos"] > 0
        assert prefs.weights["jambes"] > 0
    
    def test_update_problem_areas_filters_invalid(self, clean_preferences):
        """Test que update_problem_areas filtre les catégories invalides."""
        prefs = clean_preferences
        prefs.update_problem_areas(["dos", "invalid_category", "yeux"])
        
        # Seules les catégories valides devraient être conservées
        assert prefs.problem_areas == ["dos", "yeux"]
    
    def test_increment_notification_count(self, clean_preferences):
        """Test incrémentation du compteur de notifications."""
        prefs = clean_preferences
        initial_count = prefs.stats["total_notifications"]
        
        prefs.increment_notification_count()
        assert prefs.stats["total_notifications"] == initial_count + 1
        
        prefs.increment_notification_count()
        assert prefs.stats["total_notifications"] == initial_count + 2
    
    def test_add_exercise_to_history(self, clean_preferences):
        """Test ajout d'exercice à l'historique."""
        prefs = clean_preferences
        
        prefs.add_exercise_to_history("dos", "Test message")
        
        assert len(prefs.stats["exercises_done"]) == 1
        assert prefs.stats["exercises_done"][0]["category"] == "dos"
        assert prefs.stats["exercises_done"][0]["message"] == "Test message"
        assert "timestamp" in prefs.stats["exercises_done"][0]
    
    def test_add_exercise_to_history_limit(self, clean_preferences):
        """Test que l'historique est limité à 20 entrées."""
        prefs = clean_preferences
        
        # Ajouter 25 exercices
        for i in range(25):
            prefs.add_exercise_to_history("dos", f"Test {i}")
        
        # Vérifier qu'on a seulement les 20 derniers
        assert len(prefs.stats["exercises_done"]) == 20
        assert prefs.stats["exercises_done"][-1]["message"] == "Test 24"
        assert prefs.stats["exercises_done"][0]["message"] == "Test 5"
    
    def test_update_notification_config(self, clean_preferences):
        """Test mise à jour de la configuration des notifications."""
        prefs = clean_preferences
        
        new_config = {
            "frequency": 60,
            "start_hour": 8,
            "end_hour": 17
        }
        prefs.update_notification_config(new_config)
        
        assert prefs.notification_config["frequency"] == 60
        assert prefs.notification_config["start_hour"] == 8
        assert prefs.notification_config["end_hour"] == 17
        # Les autres valeurs devraient être conservées
        assert prefs.notification_config["moment"] == 0
    
    def test_get_stats_summary(self, clean_preferences):
        """Test récupération du résumé des statistiques."""
        prefs = clean_preferences
        prefs.problem_areas = ["dos"]
        prefs.stats["total_notifications"] = 5
        prefs.stats["total_checkins"] = 2
        prefs.add_exercise_to_history("dos", "Test 1")
        prefs.add_exercise_to_history("yeux", "Test 2")
        
        summary = prefs.get_stats_summary()
        
        assert summary["total_notifications"] == 5
        assert summary["total_checkins"] == 2
        assert summary["problem_areas"] == ["dos"]
        assert len(summary["recent_exercises"]) == 2
    
    def test_needs_initial_checkin(self, clean_preferences):
        """Test détection du besoin de check-in initial."""
        prefs = clean_preferences
        
        # Par défaut, devrait nécessiter un check-in
        assert prefs.needs_initial_checkin() is True
        
        # Après un check-in, devrait retourner False
        prefs.update_problem_areas(["dos"])
        assert prefs.needs_initial_checkin() is False
    
    def test_config_persistence(self, clean_preferences, temp_config_dir):
        """Test que la configuration persiste correctement."""
        # Première instance
        prefs1 = clean_preferences
        prefs1.problem_areas = ["dos", "yeux"]
        prefs1.stats["total_notifications"] = 42
        prefs1.save()
        
        # Deuxième instance qui devrait charger les mêmes données
        prefs2 = UserPreferences()
        
        assert prefs2.problem_areas == prefs1.problem_areas
        assert prefs2.stats["total_notifications"] == 42
        assert prefs2.weights == prefs1.weights
    
    def test_load_corrupted_config(self, clean_preferences, temp_config_dir):
        """Test que l'app continue de fonctionner avec un fichier config corrompu."""
        prefs = clean_preferences
        
        # Écrire un fichier JSON invalide
        with open(prefs.CONFIG_FILE, 'w') as f:
            f.write("{ invalid json }")
        
        # Créer une nouvelle instance qui devrait charger les valeurs par défaut
        prefs2 = UserPreferences()
        
        assert prefs2.problem_areas == []
        assert prefs2.stats["total_notifications"] == 0
    
    def test_categories_constant(self):
        """Test que les catégories sont bien définies."""
        expected_categories = ["dos", "yeux", "jambes", "posture", "respiration", "fatigue_generale"]
        
        assert UserPreferences.CATEGORIES == expected_categories
