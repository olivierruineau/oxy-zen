"""Tests d'intégration pour Oxy-Zen."""

import pytest
import yaml
import json
from pathlib import Path
from src.app import ExerciseSelector
from src.config import UserPreferences


class TestEndToEndWorkflow:
    """Tests du workflow complet de l'application."""
    
    def test_complete_user_workflow(self, temp_config_dir, temp_exercises_file):
        """Test du workflow complet : config -> sélection -> stats."""
        # 1. Créer des préférences
        prefs = UserPreferences()
        
        # 2. Faire un check-in initial
        prefs.update_problem_areas(["dos", "yeux"])
        
        # 3. Créer un sélecteur
        selector = ExerciseSelector(temp_exercises_file, prefs)
        
        # 4. Sélectionner quelques exercices
        for i in range(5):
            result = selector.select_next_exercise()
            assert result is not None
            category, message, exercise = result
            
            # Enregistrer dans les stats
            prefs.increment_notification_count()
            prefs.add_exercise_to_history(category, message)
        
        # 5. Vérifier les stats
        summary = prefs.get_stats_summary()
        assert summary["total_notifications"] == 5
        assert summary["total_checkins"] == 1
        assert len(summary["recent_exercises"]) == 5
        
        # 6. Changer les zones à problème
        prefs.update_problem_areas(["jambes"])
        
        # 7. Vérifier que les poids ont changé
        assert prefs.weights["jambes"] > prefs.weights["dos"]
        assert summary["total_checkins"] == 1  # pas encore incrémenté car on n'a pas rechargé
        
        # Recharger le summary
        summary2 = prefs.get_stats_summary()
        assert summary2["total_checkins"] == 2


class TestConfigurationPersistence:
    """Tests de persistence de la configuration."""
    
    def test_config_survives_restart(self, temp_config_dir, temp_exercises_file):
        """Test que la configuration persiste après un 'restart' de l'app."""
        # Session 1
        prefs1 = UserPreferences()
        prefs1.update_problem_areas(["dos", "yeux"])
        prefs1.increment_notification_count()
        prefs1.increment_notification_count()
        prefs1.add_exercise_to_history("dos", "Test exercise 1")
        prefs1.notification_config["frequency"] = 45
        prefs1.save()
        
        # Session 2 (simuler un redémarrage)
        prefs2 = UserPreferences()
        
        # Vérifier que tout a été chargé correctement
        assert prefs2.problem_areas == ["dos", "yeux"]
        assert prefs2.stats["total_notifications"] == 2
        assert prefs2.notification_config["frequency"] == 45
        assert len(prefs2.stats["exercises_done"]) == 1
        
        # Créer un nouveau sélecteur avec les préférences chargées
        selector = ExerciseSelector(temp_exercises_file, prefs2)
        
        # Vérifier que la sélection fonctionne
        result = selector.select_next_exercise()
        assert result is not None


class TestWeightCalculationIntegration:
    """Tests d'intégration pour le calcul des poids."""
    
    def test_weight_distribution_affects_selection(self, temp_config_dir, temp_exercises_file, sample_exercises):
        """Test que les poids influencent vraiment la sélection."""
        # Ajouter plus d'exercices pour avoir des stats significatives
        exercises = sample_exercises.copy()
        exercises["dos"] = [{"message": f"Dos {i}", "exercise": f"Ex {i}"} for i in range(10)]
        exercises["yeux"] = [{"message": f"Yeux {i}", "exercise": f"Ex {i}"} for i in range(10)]
        
        # Sauvegarder dans un nouveau fichier
        temp_file = temp_config_dir / "exercises_test.yaml"
        with open(temp_file, 'w', encoding='utf-8') as f:
            yaml.dump(exercises, f)
        
        # Configurer 100% dos
        prefs = UserPreferences()
        prefs.problem_areas = ["dos"]
        prefs.calculate_weights()
        
        selector = ExerciseSelector(temp_file, prefs)
        
        # Faire beaucoup de sélections
        categories = []
        for _ in range(30):
            result = selector.select_next_exercise()
            if result:
                categories.append(result[0])
        
        # Compter les occurrences
        dos_count = categories.count("dos")
        prevention_count = categories.count("prevention_globale")
        
        # "dos" devrait être majoritaire (70% théorique)
        assert dos_count > prevention_count
    
    def test_zero_weight_category_not_selected(self, temp_config_dir, temp_exercises_file):
        """Test qu'une catégorie avec poids proche de 0 est rarement sélectionnée."""
        prefs = UserPreferences()
        prefs.problem_areas = ["dos"]
        prefs.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, prefs)
        
        # Faire beaucoup de sélections
        categories = []
        for _ in range(50):
            result = selector.select_next_exercise()
            if result:
                categories.append(result[0])
        
        # Les catégories non-problème devraient être très rares
        jambes_count = categories.count("jambes")
        
        # Avec un poids de 0.01, on devrait avoir très peu de sélections
        assert jambes_count < 5  # Moins de 10% des sélections


class TestMultipleCheckins:
    """Tests de check-ins multiples."""
    
    def test_multiple_checkins_track_changes(self, temp_config_dir, temp_exercises_file):
        """Test que plusieurs check-ins suivent correctement les changements."""
        prefs = UserPreferences()
        
        # Premier check-in
        prefs.update_problem_areas(["dos"])
        first_weights = prefs.weights.copy()
        
        # Deuxième check-in avec ajout de zone
        prefs.update_problem_areas(["dos", "yeux"])
        second_weights = prefs.weights.copy()
        
        # Troisième check-in avec changement complet
        prefs.update_problem_areas(["jambes", "posture"])
        third_weights = prefs.weights.copy()
        
        # Vérifier que les poids ont changé à chaque fois
        assert first_weights != second_weights
        assert second_weights != third_weights
        
        # Vérifier le nombre de check-ins
        assert prefs.stats["total_checkins"] == 3


class TestExerciseHistoryIntegration:
    """Tests d'intégration pour l'historique des exercices."""
    
    def test_exercise_history_with_real_selection(self, temp_config_dir, temp_exercises_file):
        """Test que l'historique s'intègre bien avec la sélection."""
        prefs = UserPreferences()
        prefs.update_problem_areas(["dos", "yeux"])
        
        selector = ExerciseSelector(temp_exercises_file, prefs)
        
        # Simuler une journée de notifications
        for _ in range(10):
            result = selector.select_next_exercise()
            if result:
                category, message, exercise = result
                prefs.increment_notification_count()
                prefs.add_exercise_to_history(category, message)
        
        # Vérifier l'historique
        assert len(prefs.stats["exercises_done"]) == 10
        assert prefs.stats["total_notifications"] == 10
        
        # Vérifier que chaque entrée a un timestamp
        for entry in prefs.stats["exercises_done"]:
            assert "timestamp" in entry
            assert "category" in entry
            assert "message" in entry


class TestNotificationConfiguration:
    """Tests d'intégration pour la configuration des notifications."""
    
    def test_notification_config_persists(self, temp_config_dir):
        """Test que la config de notification persiste."""
        prefs1 = UserPreferences()
        
        # Modifier la config
        new_config = {
            "frequency": 45,
            "moment": 15,
            "start_hour": 8,
            "end_hour": 18
        }
        prefs1.update_notification_config(new_config)
        
        # Recharger
        prefs2 = UserPreferences()
        
        # Vérifier
        assert prefs2.notification_config["frequency"] == 45
        assert prefs2.notification_config["moment"] == 15
        assert prefs2.notification_config["start_hour"] == 8
        assert prefs2.notification_config["end_hour"] == 18
    
    def test_partial_config_update(self, temp_config_dir):
        """Test qu'une mise à jour partielle conserve les autres valeurs."""
        prefs = UserPreferences()
        
        # Valeurs initiales
        initial_start_hour = prefs.notification_config["start_hour"]
        
        # Mise à jour partielle
        prefs.update_notification_config({"frequency": 60})
        
        # Vérifier
        assert prefs.notification_config["frequency"] == 60
        assert prefs.notification_config["start_hour"] == initial_start_hour


class TestEdgeCases:
    """Tests de cas limites."""
    
    def test_empty_problem_areas_still_selects_exercises(self, temp_config_dir, temp_exercises_file):
        """Test qu'on peut sélectionner des exercices même sans zones à problème."""
        prefs = UserPreferences()
        prefs.problem_areas = []
        prefs.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, prefs)
        
        result = selector.select_next_exercise()
        assert result is not None
        
        # Devrait sélectionner un exercice (prevention_globale a le poids le plus élevé)
        category, message, exercise = result
        # Prevention_globale devrait être dans les exercices disponibles
        assert category in selector.exercises
    
    def test_all_categories_as_problems(self, temp_config_dir, temp_exercises_file):
        """Test avec toutes les catégories comme zones à problème."""
        prefs = UserPreferences()
        prefs.problem_areas = UserPreferences.CATEGORIES.copy()
        prefs.calculate_weights()
        
        selector = ExerciseSelector(temp_exercises_file, prefs)
        
        # Devrait quand même fonctionner
        result = selector.select_next_exercise()
        assert result is not None
        
        # Les poids devraient être répartis équitablement
        total_problem_weight = sum(
            prefs.weights[cat] for cat in UserPreferences.CATEGORIES
        )
        assert total_problem_weight == pytest.approx(0.7)
    
    def test_single_exercise_in_category(self, temp_config_dir, tmp_path):
        """Test avec une seule option d'exercice dans une catégorie."""
        single_exercise = {
            "dos": [{"message": "Seul exercice", "exercise": "Fais quelque chose"}],
            "prevention_globale": [{"message": "Prev", "exercise": "Autre chose"}]
        }
        
        temp_file = tmp_path / "single.yaml"
        with open(temp_file, 'w', encoding='utf-8') as f:
            yaml.dump(single_exercise, f)
        
        prefs = UserPreferences()
        prefs.problem_areas = ["dos"]
        prefs.calculate_weights()
        
        selector = ExerciseSelector(temp_file, prefs)
        
        # Faire plusieurs sélections - devrait toujours retourner le même
        results = [selector.select_next_exercise() for _ in range(5)]
        
        # Toutes devraient être valides
        for result in results:
            assert result is not None
