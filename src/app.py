"""
Oxy-Zen - Application de rappels d'exercices adaptatifs
Envoie des notifications récurrentes pour encourager les pauses santé pendant la journée de travail.
"""

import yaml
import random
import schedule
import time
import threading
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Tuple

from winotify import Notification, audio
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

from .config import UserPreferences
from .ui import show_checkin_dialog, show_stats_window


class ExerciseSelector:
    """Gère le chargement et la sélection pondérée des exercices."""
    
    def __init__(self, exercises_file: Path, preferences: UserPreferences):
        self.exercises_file = exercises_file
        self.preferences = preferences
        self.exercises: Dict[str, List[Dict]] = {}
        self.recent_messages = []  # Cache anti-répétition
        
        self.load_exercises()
    
    def load_exercises(self):
        """Charge les exercices depuis le fichier YAML."""
        try:
            with open(self.exercises_file, 'r', encoding='utf-8') as f:
                self.exercises = yaml.safe_load(f)
            print(f"✅ {sum(len(exs) for exs in self.exercises.values())} exercices chargés")
        except Exception as e:
            print(f"❌ Erreur lors du chargement des exercices: {e}")
            # Fallback avec un exercice par défaut
            self.exercises = {
                "prevention_globale": [{
                    "message": "Bouge un peu!",
                    "exercise": "Fais des étirements"
                }]
            }
    
    def select_next_exercise(self) -> Optional[Tuple[str, str, str]]:
        """
        Sélectionne le prochain exercice selon la pondération.
        
        Returns:
            Tuple (catégorie, message, exercice) ou None si erreur
        """
        if not self.exercises:
            return None
        
        # Obtenir les poids actuels
        weights = self.preferences.weights
        
        # Créer des listes pour random.choices
        categories = []
        category_weights = []
        
        for cat, weight in weights.items():
            if cat in self.exercises and self.exercises[cat] and weight > 0:
                categories.append(cat)
                category_weights.append(weight)
        
        if not categories:
            return None
        
        # Sélectionner une catégorie selon la pondération
        selected_category = random.choices(categories, weights=category_weights, k=1)[0]
        
        # Sélectionner un exercice aléatoire dans cette catégorie
        available_exercises = self.exercises[selected_category]
        
        # Éviter la répétition des 3 derniers messages
        attempts = 0
        while attempts < 10:  # Limite pour éviter boucle infinie
            exercise = random.choice(available_exercises)
            message = exercise['message']
            
            if message not in self.recent_messages or len(available_exercises) <= 3:
                # Ajouter au cache et limiter à 3 derniers
                self.recent_messages.append(message)
                if len(self.recent_messages) > 3:
                    self.recent_messages.pop(0)
                
                return (selected_category, message, exercise['exercise'])
            
            attempts += 1
        
        # Fallback: retourner quand même un exercice
        exercise = random.choice(available_exercises)
        return (selected_category, exercise['message'], exercise['exercise'])


class OxyZenApp:
    """Application principale Oxy-Zen."""
    
    def __init__(self):
        self.preferences = UserPreferences()
        self.selector = ExerciseSelector(
            Path(__file__).parent.parent / "data" / "exercises.yaml",
            self.preferences
        )
        
        self.running = True
        self.paused = False
        self.pause_until = None
        
        # Thread pour le scheduler
        self.schedule_thread = None
        
        # Icône système
        self.icon = None
        
        print("🧘 Oxy-Zen démarré!")
    
    def send_notification(self, category: str, message: str, exercise: str):
        """Envoie une notification Windows."""
        try:
            notif = Notification(
                app_id="Oxy-Zen",
                title=message,
                msg=exercise,
                duration="short",
                icon=str(Path(__file__).parent / "icon.png") if (Path(__file__).parent / "icon.png").exists() else ""
            )
            
            # Son discret
            notif.set_audio(audio.Default, loop=False)
            
            # Afficher
            notif.show()
            
            # Statistiques
            self.preferences.increment_notification_count()
            self.preferences.add_exercise_to_history(category, message)
            
            print(f"📬 Notification envoyée: {message}")
            
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    def notification_job(self):
        """Job de notification (appelé par le scheduler)."""
        if self.paused:
            print("⏸️  En pause, notification ignorée")
            return
        
        # Vérifier l'heure de pause si définie
        if self.pause_until and datetime.now() < self.pause_until:
            print("⏸️  En pause temporaire")
            return
        else:
            self.pause_until = None
            self.paused = False
        
        # Sélectionner un exercice
        result = self.selector.select_next_exercise()
        if result:
            category, message, exercise = result
            self.send_notification(category, message, exercise)
    
    def checkin_job(self):
        """Job de check-in quotidien."""
        if self.paused:
            return
        
        print("🔔 Check-in quotidien!")
        self.show_checkin()
    
    def show_checkin(self):
        """Affiche la fenêtre de check-in."""
        def callback(areas):
            if areas is not None:
                self.preferences.update_problem_areas(areas)
                print(f"✅ Zones mises à jour: {areas}")
                # Recharger les poids dans le selector
                self.selector.preferences = self.preferences
                # Mettre à jour le menu après changement
                if self.icon:
                    self.update_icon_menu()
        
        # Lancer dans un thread séparé pour ne pas bloquer
        def run_checkin():
            show_checkin_dialog(callback, self.preferences.problem_areas)
        
        thread = threading.Thread(target=run_checkin, daemon=True)
        thread.start()
    
    def show_stats(self):
        """Affiche la fenêtre de statistiques."""
        # Lancer dans un thread séparé pour ne pas bloquer
        def run_stats():
            stats = self.preferences.get_stats_summary()
            show_stats_window(stats)
        
        thread = threading.Thread(target=run_stats, daemon=True)
        thread.start()
    
    def setup_schedule(self):
        """Configure les tâches planifiées."""
        # Notifications toutes les 30 minutes entre 7h30 et 16h, lun-ven
        schedule.every(30).minutes.do(self.notification_job)
        
        # Check-in quotidien une fois par jour (heure aléatoire entre 10h et 14h)
        checkin_hour = random.randint(10, 13)
        checkin_minute = random.randint(0, 59)
        checkin_time = f"{checkin_hour:02d}:{checkin_minute:02d}"
        schedule.every().day.at(checkin_time).do(self.checkin_job)
        
        print(f"📅 Notifications: toutes les 30 min (7h30-16h, lun-ven)")
        print(f"📅 Check-in quotidien: {checkin_time}")
    
    def should_run_now(self) -> bool:
        """Vérifie si on doit exécuter les jobs maintenant (horaires et jours)."""
        now = datetime.now()
        
        # Vérifier le jour (lundi=0, dimanche=6)
        if now.weekday() >= 5:  # Weekend
            return False
        
        # Vérifier l'heure (7h30 - 16h00)
        current_time = now.time()
        start_time = dt_time(7, 30)
        end_time = dt_time(16, 0)
        
        return start_time <= current_time <= end_time
    
    def schedule_loop(self):
        """Boucle principale du scheduler."""
        while self.running:
            # Ne vérifier les jobs que pendant les heures de travail
            if self.should_run_now():
                schedule.run_pending()
            
            time.sleep(60)  # Vérifier toutes les minutes
    
    def pause_for_hour(self):
        """Met en pause pour 1 heure."""
        from datetime import timedelta
        self.paused = True
        self.pause_until = datetime.now() + timedelta(hours=1)
        print("⏸️  Pause 1 heure")
        self.update_icon_menu()
    
    def pause_until_tomorrow(self):
        """Met en pause jusqu'au lendemain."""
        from datetime import timedelta
        self.paused = True
        # Pause jusqu'à demain 7h30
        tomorrow = datetime.now() + timedelta(days=1)
        self.pause_until = tomorrow.replace(hour=7, minute=30, second=0, microsecond=0)
        print("⏸️  Pause jusqu'à demain")
        self.update_icon_menu()
    
    def resume(self):
        """Reprend les notifications."""
        self.paused = False
        self.pause_until = None
        print("▶️  Reprise")
        self.update_icon_menu()
    
    def quit_app(self, icon=None, item=None):
        """Quitte l'application."""
        print("👋 Arrêt d'Oxy-Zen")
        self.running = False
        if self.icon:
            self.icon.stop()
    
    def create_icon_image(self):
        """Crée une image d'icône simple."""
        # Créer une image 64x64 avec un cercle et "OZ"
        img = Image.new('RGB', (64, 64), color='#3498db')
        draw = ImageDraw.Draw(img)
        
        # Cercle blanc
        draw.ellipse([8, 8, 56, 56], fill='white', outline='#2980b9', width=3)
        
        # Texte "🧘" ou "OZ" (approximation)
        draw.text((20, 18), "OZ", fill='#3498db')
        
        return img
    
    def update_icon_menu(self):
        """Met à jour le menu de l'icône."""
        if self.icon:
            self.icon.menu = self.create_menu()
    
    def create_menu(self):
        """Crée le menu de l'icône système."""
        status = "⏸️ EN PAUSE" if self.paused else "✅ Actif"
        areas = ", ".join(self.preferences.problem_areas) if self.preferences.problem_areas else "Aucune"
        
        return Menu(
            MenuItem(f"Status: {status}", None, enabled=False),
            MenuItem(f"Zones: {areas}", None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Check-in manuel", lambda: self.show_checkin()),
            MenuItem("Voir statistiques", lambda: self.show_stats()),
            Menu.SEPARATOR,
            MenuItem("Pause 1 heure", lambda: self.pause_for_hour(), enabled=not self.paused),
            MenuItem("Pause jusqu'à demain", lambda: self.pause_until_tomorrow(), enabled=not self.paused),
            MenuItem("Reprendre", lambda: self.resume(), enabled=self.paused),
            Menu.SEPARATOR,
            MenuItem("Quitter", self.quit_app)
        )
    
    def setup_system_tray(self):
        """Configure l'icône dans la barre système."""
        icon_image = self.create_icon_image()
        
        self.icon = Icon(
            "Oxy-Zen",
            icon_image,
            "Oxy-Zen - Rappels d'exercices",
            menu=self.create_menu()
        )
    
    def run(self):
        """Lance l'application."""
        # Check-in initial si nécessaire
        if self.preferences.needs_initial_checkin():
            print("👋 Premier lancement! Faisons un check-in initial...")
            # Le check-in sera dans un thread séparé
            self.show_checkin()
            # Petit délai pour laisser la fenêtre s'ouvrir
            import time
            time.sleep(0.5)
        
        # Configurer le scheduler
        self.setup_schedule()
        
        # Lancer le thread du scheduler
        self.schedule_thread = threading.Thread(target=self.schedule_loop, daemon=True)
        self.schedule_thread.start()
        
        # Configurer et lancer l'icône système (bloquant)
        self.setup_system_tray()
        self.icon.run()


def main():
    """Point d'entrée principal."""
    app = OxyZenApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Arrêt via Ctrl+C")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
