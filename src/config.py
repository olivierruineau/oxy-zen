"""Module de gestion de la configuration utilisateur pour Oxy-Zen."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class UserPreferences:
    """Gère les préférences utilisateur et la pondération des exercices."""
    
    CONFIG_DIR = Path.home() / ".oxy-zen"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    # Catégories disponibles
    CATEGORIES = [
        "dos",
        "yeux", 
        "jambes",
        "posture",
        "respiration",
        "fatigue_generale",
    ]
    
    def __init__(self):
        self.problem_areas: List[str] = []
        self.last_checkin: str = ""
        self.weights: Dict[str, float] = {}
        self.stats = {
            "total_notifications": 0,
            "total_checkins": 0,
            "exercises_done": [],
        }
        # Ajout config notification (fréquence en minutes, moment en minutes)
        self.notification_config = {
            "frequency": 30,  # par défaut toutes les 30 min
            "moment": 0,      # par défaut à l'heure pile
            "start_hour": 7,  # heure de début de travail
            "start_minute": 30,
            "end_hour": 16,   # heure de fin de travail
            "end_minute": 0,
        }
        # Créer le répertoire de config si nécessaire
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Charger la config existante ou créer une nouvelle
        self.load()
    
    def load(self):
        """Charge la configuration depuis le fichier JSON."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.problem_areas = data.get("problem_areas", [])
                    self.last_checkin = data.get("last_checkin", "")
                    self.weights = data.get("weights", {})
                    self.stats = data.get("stats", self.stats)
                    self.notification_config = data.get("notification_config", self.notification_config)
            except (json.JSONDecodeError, IOError):
                # Si erreur de lecture, on garde les valeurs par défaut
                pass
        # Si pas de poids définis, calculer avec configuration par défaut
        if not self.weights:
            self.calculate_weights()
    
    def save(self):
        """Sauvegarde la configuration dans le fichier JSON."""
        data = {
            "problem_areas": self.problem_areas,
            "last_checkin": self.last_checkin,
            "weights": self.weights,
            "stats": self.stats,
            "notification_config": self.notification_config,
        }
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de la config: {e}")
    
    def update_notification_config(self, config: Dict):
        """Met à jour la configuration des notifications et sauvegarde."""
        self.notification_config.update(config)
        self.save()
    
    def update_problem_areas(self, areas: List[str]):
        """Met à jour les zones à problème et recalcule les poids."""
        self.problem_areas = [area for area in areas if area in self.CATEGORIES]
        self.last_checkin = datetime.now().isoformat()
        self.stats["total_checkins"] += 1
        self.calculate_weights()
        self.save()
    
    def calculate_weights(self):
        """
        Calcule les poids pour chaque catégorie selon l'algorithme 70/30.
        70% du poids total est réparti sur les zones à problème.
        30% du poids est attribué à la prévention globale.
        """
        self.weights = {}
        
        if not self.problem_areas:
            # Si aucun problème identifié, tout va en prévention globale
            for cat in self.CATEGORIES:
                self.weights[cat] = 0.1
            self.weights["prevention_globale"] = 1.0
        else:
            # 70% réparti sur les zones à problème
            problem_weight = 0.7 / len(self.problem_areas)
            
            for cat in self.CATEGORIES:
                if cat in self.problem_areas:
                    self.weights[cat] = problem_weight
                else:
                    self.weights[cat] = 0.01  # Petit poids résiduel
            
            # 30% pour la prévention globale
            self.weights["prevention_globale"] = 0.3
    
    def increment_notification_count(self):
        """Incrémente le compteur de notifications envoyées."""
        self.stats["total_notifications"] += 1
        self.save()
    
    def add_exercise_to_history(self, category: str, message: str):
        """Ajoute un exercice à l'historique (garde les 20 derniers)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "message": message,
        }
        self.stats["exercises_done"].append(entry)
        
        # Garder seulement les 20 derniers
        if len(self.stats["exercises_done"]) > 20:
            self.stats["exercises_done"] = self.stats["exercises_done"][-20:]
        
        self.save()
    
    def get_stats_summary(self) -> Dict:
        """Retourne un résumé des statistiques pour affichage."""
        return {
            "total_notifications": self.stats["total_notifications"],
            "total_checkins": self.stats["total_checkins"],
            "problem_areas": self.problem_areas,
            "last_checkin": self.last_checkin,
            "recent_exercises": self.stats["exercises_done"][-5:] if self.stats["exercises_done"] else [],
        }
    
    def needs_initial_checkin(self) -> bool:
        """Vérifie si un check-in initial est nécessaire."""
        return not self.last_checkin
