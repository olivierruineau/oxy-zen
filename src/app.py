"""
Oxy-Zen - Application de rappels d'exercices adaptatifs
Envoie des notifications récurrentes pour encourager les pauses santé pendant la journée de travail.
"""

import yaml
import random
import schedule
import time
import threading
import ctypes
from ctypes import wintypes
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Tuple

from winotify import Notification, audio
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

from .config import UserPreferences
from .ui import show_checkin_dialog, show_stats_window


def get_idle_duration() -> int:
    """Retourne le temps d'inactivité en secondes (Windows API)."""
    try:
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', wintypes.UINT),
                ('dwTime', wintypes.DWORD),
            ]

        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
        
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
            millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0  # Convertir en secondes
        else:
            return 0
    except Exception as e:
        print(f"❌ Erreur détection inactivité: {e}")
        return 0


def is_session_locked() -> bool:
    """Détecte si la session Windows est verrouillée."""
    try:
        # OpenInputDesktop retourne NULL si le desktop est verrouillé
        hDesktop = ctypes.windll.user32.OpenInputDesktop(0, False, 0)
        if hDesktop == 0:
            return True  # Session verrouillée
        else:
            ctypes.windll.user32.CloseDesktop(hDesktop)
            return False  # Session active
    except Exception as e:
        print(f"❌ Erreur détection verrouillage: {e}")
        return False


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
        
        # Dernière notification pour snooze
        self.last_notification = None
        
        # Liste des jobs de notification pour tracking
        self.notification_jobs = []
        
        # Seuil d'inactivité (en secondes) avant de considérer l'utilisateur absent
        self.idle_threshold = 300  # 5 minutes par défaut
        
        print("🧘 Oxy-Zen démarré!")
    
    def send_notification(self, category: str, message: str, exercise: str):
        """Envoie une notification Windows."""
        try:
            # Sauvegarder pour le snooze
            self.last_notification = (category, message, exercise)
            
            notif = Notification(
                app_id="Oxy-Zen",
                title=message,
                msg=exercise,
                duration="long",  # "long" au lieu de "short" pour plus de visibilité
                icon=str(Path(__file__).parent / "icon.png") if (Path(__file__).parent / "icon.png").exists() else ""
            )
            
            # Son plus audible pour attirer l'attention
            notif.set_audio(audio.Reminder, loop=False)
            
            # Afficher (sans boutons d'action pour éviter les erreurs de protocole Windows)
            # Utiliser le menu système pour Snooze au lieu des actions de notification
            notif.show()
            
            # Statistiques
            self.preferences.increment_notification_count()
            self.preferences.add_exercise_to_history(category, message)
            
            # Mettre à jour le menu pour activer le bouton snooze
            self.update_icon_menu()
            
            print(f"📬 Notification envoyée: {message}")
            
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
    
    def snooze_notification(self):
        """Rappelle la dernière notification après 5 minutes."""
        if self.last_notification:
            category, message, exercise = self.last_notification
            print("⏰ Snooze - notification dans 5 minutes")
            
            def send_snooze():
                time.sleep(300)  # 5 minutes
                if not self.paused:
                    self.send_notification(category, message, exercise)
            
            snooze_thread = threading.Thread(target=send_snooze, daemon=True)
            snooze_thread.start()
    
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
        
        # Vérifier si la session est verrouillée
        if is_session_locked():
            print("🔒 Session verrouillée, notification ignorée")
            return
        
        # Vérifier le temps d'inactivité
        idle_time = get_idle_duration()
        if idle_time >= self.idle_threshold:
            idle_minutes = int(idle_time / 60)
            print(f"💤 Utilisateur inactif ({idle_minutes} min), notification ignorée")
            return
        
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
        # Programmer à des heures fixes au lieu d'un intervalle
        notification_times = []
        hour = 7
        minute = 30
        while hour < 16 or (hour == 16 and minute == 0):
            time_str = f"{hour:02d}:{minute:02d}"
            notification_times.append(time_str)
            job = schedule.every().day.at(time_str).do(self.notification_job)
            self.notification_jobs.append(job)
            
            # Incrémenter de 30 minutes
            minute += 30
            if minute >= 60:
                minute = 0
                hour += 1
        
        # Check-in quotidien une fois par jour (heure aléatoire entre 10h et 14h)
        checkin_hour = random.randint(10, 13)
        checkin_minute = random.randint(0, 59)
        checkin_time = f"{checkin_hour:02d}:{checkin_minute:02d}"
        schedule.every().day.at(checkin_time).do(self.checkin_job)
        
        print(f"📅 Notifications programmées: {', '.join(notification_times)}")
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
            # Ne vérifier les jobs que les jours de semaine
            now = datetime.now()
            if now.weekday() < 5:  # Lundi à vendredi seulement
                schedule.run_pending()
            
            # Actualiser le menu pour que l'info "Prochaine notification" soit à jour
            self.update_icon_menu()
            
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
    
    def trigger_notification_now(self):
        """Déclenche une notification immédiatement sur demande."""
        result = self.selector.select_next_exercise()
        if result:
            category, message, exercise = result
            self.send_notification(category, message, exercise)
            print("🔔 Notification déclenchée manuellement")
        else:
            print("❌ Impossible de sélectionner un exercice")
    
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
    
    def get_next_notification_time(self) -> Optional[str]:
        """Retourne l'heure de la prochaine notification formatée."""
        try:
            from datetime import timedelta
            now = datetime.now()
            
            # Si en pause, afficher jusqu'à quand
            if self.paused or (self.pause_until and now < self.pause_until):
                if self.pause_until:
                    return f"En pause jusqu'à {self.pause_until.strftime('%H:%M')}"
                return "En pause"
            
            # Vérifier si on est dans un jour de travail
            if now.weekday() >= 5:  # Weekend
                days_until_monday = 7 - now.weekday()
                next_work_day = now + timedelta(days=days_until_monday)
                next_work_day = next_work_day.replace(hour=7, minute=30, second=0, microsecond=0)
                return f"Lun {next_work_day.strftime('%H:%M')}"
            
            # Trouver la prochaine notification parmi les jobs sauvegardés
            next_times = []
            for job in self.notification_jobs:
                if job.next_run:
                    next_times.append(job.next_run)
            
            if next_times:
                next_run = min(next_times)
                # Si c'est aujourd'hui, afficher juste l'heure
                if next_run.date() == now.date():
                    return next_run.strftime('%H:%M')
                else:
                    return f"Demain {next_run.strftime('%H:%M')}"
            
            # Fallback: calculer manuellement la prochaine heure fixe
            current_time = now.time()
            # Liste des heures de notification
            notification_hours = [(7, 30), (8, 0), (8, 30), (9, 0), (9, 30), (10, 0), (10, 30),
                                   (11, 0), (11, 30), (12, 0), (12, 30), (13, 0), (13, 30),
                                   (14, 0), (14, 30), (15, 0), (15, 30), (16, 0)]
            
            for h, m in notification_hours:
                notif_time = dt_time(h, m)
                if current_time < notif_time:
                    return f"{h:02d}:{m:02d}"
            
            # Si après 16h, retourner demain 7h30
            return "Demain 07:30"
            
        except Exception as e:
            print(f"❌ Erreur calcul prochaine notification: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_icon_menu(self):
        """Met à jour le menu de l'icône."""
        if self.icon:
            self.icon.menu = self.create_menu()
    
    def create_menu(self):
        """Crée le menu de l'icône système."""
        status = "⏸️ EN PAUSE" if self.paused else "✅ Actif"
        areas = ", ".join(self.preferences.problem_areas) if self.preferences.problem_areas else "Aucune"
        next_notif = self.get_next_notification_time()
        next_notif_text = f"Prochaine: {next_notif}" if next_notif else "Prochaine: --"
        
        return Menu(
            MenuItem(f"Status: {status}", None, enabled=False),
            MenuItem(f"Zones: {areas}", None, enabled=False),
            MenuItem(next_notif_text, None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Déclencher notification", lambda: self.trigger_notification_now()),
            MenuItem("Snooze 5 min", lambda: self.snooze_notification(), enabled=self.last_notification is not None),
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
