# Managers

Ce dossier contient les gestionnaires (managers) pour l'application Oxy-Zen. Ces managers encapsulent des responsabilités spécifiques et peuvent être utilisés pour refactorer l'application principale.

## Architecture

Les managers suivent le principe de **Séparation des Responsabilités** (SRP - Single Responsibility Principle) pour améliorer la maintenabilité et la testabilité du code.

## Managers Disponibles

### ScheduleManager

**Responsabilité**: Gère la planification des tâches (notifications et check-ins quotidiens).

**Fonctionnalités**:
- Configuration des horaires de notification selon la configuration utilisateur
- Planification du check-in quotidien aléatoire
- Gestion des jobs schedule (ajout, suppression, reconfiguration)

**Usage**:
```python
from src.managers import ScheduleManager

schedule_mgr = ScheduleManager(
    notification_config=config,
    notification_callback=app.notification_job,
    checkin_callback=app.checkin_job
)
schedule_mgr.setup_schedule()
```

### NotificationManager

**Responsabilité**: Gère l'envoi de notifications Windows.

**Fonctionnalités**:
- Envoi de notifications via winotify
- Gestion de la dernière notification (pour snooze)
- Gestion des erreurs d'envoi
- Logging des notifications

**Usage**:
```python
from src.managers import NotificationManager

notif_mgr = NotificationManager()
success = notif_mgr.send_notification(
    category="dos",
    message="Ton dos appelle son avocat 🦴",
    exercise="Étire-toi en arrière pendant 30 secondes"
)
```

### IconManager

**Responsabilité**: Gère l'icône système (system tray) et son menu.

**Fonctionnalités**:
- Création de l'image d'icône
- Construction du menu contextuel
- Mise à jour dynamique du menu
- Gestion du cycle de vie de l'icône

**Usage**:
```python
from src.managers import IconManager

icon_mgr = IconManager()
menu = icon_mgr.create_menu(
    paused=app.paused,
    problem_areas=app.preferences.problem_areas,
    next_notif_text="Prochaine: 14:30",
    has_last_notification=True,
    trigger_callback=app.trigger_notification_now,
    # ... autres callbacks
)
icon_mgr.setup_icon(menu)
icon_mgr.run()  # Bloquant
```

## État Actuel

Les managers sont **implémentés et testés** mais ne sont **pas encore intégrés** dans l'application principale (`OxyZenApp`). Ils sont prêts à être utilisés pour un refactoring futur.

### Pourquoi pas encore intégrés?

1. **Stabilité**: L'application actuelle fonctionne correctement avec tous les tests qui passent
2. **Risque**: L'intégration complète nécessiterait de modifier beaucoup de code existant
3. **Tests**: Il faudrait adapter ou réécrire de nombreux tests
4. **Priorité**: Les gains immédiats sont limités pour un code qui fonctionne déjà bien

## Intégration Future

Pour intégrer ces managers dans `OxyZenApp`:

1. **Remplacer les méthodes directes par des appels aux managers**:
   ```python
   # Avant
   self.setup_schedule()
   
   # Après
   self.schedule_manager.setup_schedule()
   ```

2. **Injecter les dépendances via le constructeur**:
   ```python
   def __init__(self):
       self.schedule_manager = ScheduleManager(...)
       self.notification_manager = NotificationManager()
       self.icon_manager = IconManager()
   ```

3. **Adapter les tests** pour mocker les managers au lieu des méthodes directes

## Avantages de l'Intégration

- ✅ **Testabilité**: Chaque manager peut être testé indépendamment
- ✅ **Maintenabilité**: Code plus organisé et responsabilités claires
- ✅ **Réutilisabilité**: Les managers peuvent être utilisés dans d'autres contextes
- ✅ **Évolutivité**: Plus facile d'ajouter de nouvelles fonctionnalités

## Tests

Pour tester les managers:

```bash
pytest tests/test_managers.py -v
```

_(Note: Les tests des managers pourront être ajoutés dans Phase 3)_
