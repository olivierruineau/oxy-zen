# 🏗️ Architecture Oxy-Zen

> Documentation technique de l'architecture de l'application
> Version: 0.2.0
> Dernière mise à jour: 6 mars 2026

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture Globale](#architecture-globale)
- [Composants Principaux](#composants-principaux)
- [Flux de Données](#flux-de-données)
- [Gestion de l'État](#gestion-de-létat)
- [Patterns et Principes](#patterns-et-principes)
- [Sécurité](#sécurité)
- [Décisions Techniques](#décisions-techniques)
- [Évolution Future](#évolution-future)

---

## 🎯 Vue d'ensemble

### Résumé

Oxy-Zen est une application desktop Windows qui envoie des rappels périodiques d'exercices adaptatifs pour prévenir les problèmes liés à la sédentarité au travail. L'application détecte l'inactivité de l'utilisateur et envoie des notifications avec des exercices personnalisés selon les besoins signalés.

### Caractéristiques Clés

- **Plateforme**: Windows Desktop (10/11)
- **Language**: Python 3.12+
- **Architecture**: Modulaire avec séparation des responsabilités
- **UI**: Tkinter pour interfaces graphiques
- **Notifications**: winotify (notifications natives Windows)
- **System Tray**: pystray pour icône système persistante
- **Packaging**: PyInstaller pour exécutable standalone

### Statistiques (v0.2.0)

```
Lignes de code:     ~3000
Modules:            12
Tests:              220
Coverage:           75%
Dépendances:        5 (production)
```

---

## 🏛️ Architecture Globale

### Diagramme de Composants

```
┌─────────────────────────────────────────────────────────────┐
│                        OxyZen Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  UI Layer    │  │   Managers   │  │    Core      │      │
│  │              │  │              │  │              │      │
│  │ - CheckIn    │  │ - Schedule   │  │ - App        │      │
│  │ - Stats      │  │ - Notifs     │  │ - Config     │      │
│  │ - Config     │  │ - Icon       │  │ - Security   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                           │                                  │
│  ┌────────────────────────┴────────────────────────┐        │
│  │           Platform Integrations                  │        │
│  │                                                   │        │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────────┐    │        │
│  │  │ Windows │  │ winotify│  │   pystray    │    │        │
│  │  │   API   │  │         │  │              │    │        │
│  │  └─────────┘  └─────────┘  └──────────────┘    │        │
│  └──────────────────────────────────────────────────┘        │
│                                                               │
│  ┌────────────────────────────────────────────────┐          │
│  │              Data & Storage                     │          │
│  │                                                  │          │
│  │  ~/.oxy-zen/                                    │          │
│  │  ├── config.json    (user preferences)         │          │
│  │  └── app.log        (application logs)         │          │
│  │                                                  │          │
│  │  data/                                           │          │
│  │  └── exercises.yaml (exercise definitions)      │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Couches Architecturales

#### 1. **UI Layer** (`src/ui/`)
- Fenêtres Tkinter pour interactions utilisateur
- Composants: CheckInWindow, StatsWindow, NotificationConfigWindow
- Base class: BaseWindow (fonctionnalités communes)

#### 2. **Managers Layer** (`src/managers/`)
- Orchestration de fonctionnalités spécifiques
- ScheduleManager, NotificationManager, IconManager
- Prêts pour injection de dépendances (Phase 6)

#### 3. **Core Layer** (`src/`)
- Logique métier principale (OxyZenApp)
- Configuration (UserPreferences)
- Sécurité (validation, path checking)
- Logging centralisé

#### 4. **Platform Integration**
- Windows API (idle detection, session lock)
- winotify (notifications natives)
- pystray (system tray icon)

#### 5. **Data & Storage**
- Configuration JSON persistante
- Logs rotatifs (5MB max)
- Exercices YAML avec validation schéma

---

## 🔧 Composants Principaux

### 1. OxyZenApp (`src/app.py`)

**Responsabilité**: Orchestrateur principal de l'application

```python
class OxyZenApp:
    """Application principale gérant le cycle de vie complet."""
    
    def __init__(self):
        self.preferences: UserPreferences
        self.selector: ExerciseSelector
        self.icon: pystray.Icon
        self._lock: threading.Lock  # Thread safety
        
    def run(self) -> None:
        """Lance l'application (blocking)."""
        
    def send_notification(self, ...) -> None:
        """Envoie notification avec exercice."""
        
    def schedule_loop(self) -> None:
        """Loop principale de scheduling (thread séparé)."""
```

**Caractéristiques**:
- Thread-safe avec `threading.Lock()`
- Détection idle sophistiquée (Windows API)
- Gestion pause/reprise
- Anti-répétition messages récents
- Exclusion automatique weekends

### 2. ExerciseSelector (`src/app.py`)

**Responsabilité**: Sélection intelligente d'exercices

```python
class ExerciseSelector:
    """Sélectionne exercices selon préférences utilisateur."""
    
    def select_exercise(self) -> Tuple[str, str, str]:
        """
        Retourne (category, message, exercise).
        
        Pondération: 70% ciblés / 30% préventifs
        Anti-répétition des 3 derniers messages
        """
```

**Algorithme**:
1. Décider catégorie (70% problème user / 30% préventif)
2. Sélectionner exercice aléatoire dans catégorie
3. Vérifier non-répétition (3 derniers messages)
4. Retry si répétition (max 10 tentatives)

### 3. UserPreferences (`src/config.py`)

**Responsabilité**: Gestion configuration utilisateur

```python
class UserPreferences:
    """Configuration utilisateur persistante."""
    
    CONFIG_DIR = Path.home() / ".oxy-zen"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    def load(self) -> None:
        """Charge config depuis JSON."""
        
    def save(self) -> None:
        """Sauvegarde atomique (temp file + rename)."""
        
    def update_problem_areas(self, areas: List[str]) -> None:
        """Met à jour zones problématiques."""
```

**Données stockées**:
- `problem_areas`: Zones problématiques signalées
- `exercise_history`: 20 derniers exercices
- `notification_count`: Compteur total
- `last_checkin`: Date dernier check-in
- `notification_config`: Fréquence, horaires, etc.

### 4. System Tray Icon (`src/app.py`)

**Responsabilité**: Interface système persistante

**Menu items**:
```
📬 Déclencher notification maintenant
⏰ Snooze 5 minutes
📝 Check-in manuel
📊 Voir statistiques
⚙️ Configurer notifications
⏸️ Pause 1 heure / Pause jusqu'à demain
▶️ Reprendre
❌ Quitter
```

**Comportement**:
- Mise à jour dynamique du menu (état pause)
- Callbacks thread-safe
- Icône persistante même si fenêtres fermées

### 5. UI Windows (`src/ui/`)

#### CheckInWindow
```python
class CheckInWindow(tk.Toplevel):
    """
    Fenêtre de check-in quotidien.
    
    Checkboxes: Dos, Yeux, Jambes, Posture, Respiration, Fatigue, RAS
    Sauvegarde automatique dans preferences.problem_areas
    """
```

#### StatsWindow
```python
class StatsWindow(tk.Toplevel):
    """
    Affiche statistiques d'utilisation.
    
    - Total notifications envoyées
    - Dernier check-in
    - 20 derniers exercices avec timestamps
    """
```

#### NotificationConfigWindow
```python
class NotificationConfigWindow(tk.Toplevel):
    """
    Configuration des notifications.
    
    - Intervalle (30min, 1h, 2h)
    - Horaires début/fin (avec validation)
    - Désactivation weekends
    """
```

### 6. Managers (`src/managers/`)

**Note**: Modules créés pour évolution future, pas encore utilisés massivement.

#### ScheduleManager
```python
class ScheduleManager:
    """Gestion du planning de notifications (futur)."""
    pass
```

#### NotificationManager
```python
class NotificationManager:
    """Gestion de l'envoi de notifications (futur)."""
    pass
```

#### IconManager
```python
class IconManager:
    """Gestion de l'icône système (futur)."""
    pass
```

**Évolution prévue (Phase 6)**: Migration de la logique depuis OxyZenApp vers managers avec injection de dépendances.

---

## 🔄 Flux de Données

### Lifecycle Complet d'une Notification

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Démarrage Application                                     │
│    main() → OxyZenApp.__init__() → load config, exercises   │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Premier Check-in (si jamais fait)                         │
│    show_checkin() → CheckInWindow → save problem_areas      │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Lancement Threads                                          │
│    - Thread principal: UI / system tray                       │
│    - Thread schedule_loop: monitoring et notifications        │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Schedule Loop (toutes les 10s)                            │
│    ┌──────────────────────────────────────────────┐         │
│    │ Vérifications:                                │         │
│    │ - Est-ce un weekend? → Skip                   │         │
│    │ - Dans horaires travail? → Skip              │         │
│    │ - Application pausée? → Skip                 │         │
│    │ - Session verrouillée? → Skip                │         │
│    │ - Idle < seuil? → Skip                       │         │
│    │ - Déjà notifié récemment? → Skip             │         │
│    └──────────────┬───────────────────────────────┘         │
│                   │ Toutes conditions OK                     │
└───────────────────┼──────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Sélection Exercice                                         │
│    ExerciseSelector.select_exercise()                         │
│    ┌──────────────────────────────────────────────┐         │
│    │ 1. Random: 70% problème user / 30% préventif │         │
│    │ 2. Choisir catégorie appropriée              │         │
│    │ 3. Random exercice dans catégorie            │         │
│    │ 4. Vérifier anti-répétition (3 derniers)     │         │
│    │ 5. Retry si répétition (max 10 fois)         │         │
│    └──────────────┬───────────────────────────────┘         │
└───────────────────┼──────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Envoi Notification                                         │
│    send_notification(category, message, exercise)            │
│    ┌──────────────────────────────────────────────┐         │
│    │ 1. Créer winotify.Notification               │         │
│    │ 2. Titre = message sarcastique               │         │
│    │ 3. Body = instruction exercice                │         │
│    │ 4. Log envoi (logger.info)                   │         │
│    │ 5. Show notification                          │         │
│    └──────────────┬───────────────────────────────┘         │
└───────────────────┼──────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. Mise à Jour État                                           │
│    - last_notification = (category, message, exercise)       │
│    - exercise_history.append(...)                            │
│    - notification_count += 1                                 │
│    - preferences.save() [atomic write]                       │
└──────────────────┬─────────────────────────────────────────── │
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ 8. Retour Schedule Loop                                       │
│    → Attendre intervalle configuré → Recommencer 4          │
└──────────────────────────────────────────────────────────────┘
```

### Détection Session Verrouillée

```python
# Windows API via ctypes
def is_session_locked() -> bool:
    user32 = ctypes.windll.User32
    return not user32.GetForegroundWindow()
```

### Détection Idle

```python
def get_idle_duration() -> int:
    """Retourne secondes depuis dernière activité."""
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ('cbSize', ctypes.c_uint),
            ('dwTime', ctypes.c_uint),
        ]
    
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    user32.GetLastInputInfo(ctypes.byref(lii))
    
    millis = kernel32.GetTickCount() - lii.dwTime
    return millis // 1000
```

---

## 🔐 Gestion de l'État

### État Partagé (Thread-Safe)

**Problème**: Plusieurs threads accèdent aux même variables.

**Solution**: `threading.Lock()` pour tous les accès.

```python
class OxyZenApp:
    def __init__(self):
        self._lock = threading.Lock()
        self._paused = False
        self._last_notification = None
        
    @property
    def paused(self) -> bool:
        with self._lock:
            return self._paused
    
    @paused.setter
    def paused(self, value: bool) -> None:
        with self._lock:
            self._paused = value
            logger.info(f"Paused state changed: {value}")
```

**Variables protégées**:
- `paused`: État pause/reprise
- `last_notification`: Dernière notification (pour snooze)
- `exercise_history`: Historique pour anti-répétition

**Threads concurrents**:
1. Main thread (UI Events, system tray callbacks)
2. schedule_loop thread (monitoring + notifications)
3. UI windows threads (CheckIn, Stats, Config)
4. Snooze thread (délai 5min)

### Persistance Configuration

**Écriture Atomique**:

```python
def save(self) -> None:
    """Atomic write pour éviter corruption."""
    # 1. Créer temp file dans même directory
    temp_fd, temp_path = tempfile.mkstemp(
        dir=self.CONFIG_DIR,
        prefix='.config_',
        suffix='.tmp'
    )
    
    try:
        # 2. Écrire dans temp
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 3. Atomic rename (POSIX + Windows)
        os.replace(temp_path, self.CONFIG_FILE)
        
    except Exception as e:
        # 4. Cleanup en cas d'erreur
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
```

**Avantages**:
- Pas de corruption si crash pendant write
- `os.replace()` atomique sur Windows et POSIX
- Rollback automatique en cas d'erreur

---

## 🎨 Patterns et Principes

### Design Patterns Utilisés

#### 1. **Singleton** (Implicite)
```python
# Une seule instance de OxyZenApp
app = OxyZenApp()
app.run()  # Bloquant
```

#### 2. **Observer** (System Tray Callbacks)
```python
menu_items = [
    pystray.MenuItem(
        "Pause 1 heure",
        lambda: self.pause_until(datetime.now() + timedelta(hours=1))
    ),
    # Callbacks notifiés lors du clic
]
```

#### 3. **Strategy** (ExerciseSelector)
```python
# Stratégie de sélection configurable (70/30)
if random.random() < 0.7 and self.preferences.problem_areas:
    # Stratégie: exercices ciblés
else:
    # Stratégie: exercices préventifs
```

#### 4. **Template Method** (BaseWindow)
```python
class BaseWindow:
    def center_window(self):
        """Template commun pour toutes les fenêtres."""
        # Calcul centrage
        # Positionnement
```

### Principes SOLID

#### Single Responsibility
- `OxyZenApp`: Orchestration
- `UserPreferences`: Configuration
- `ExerciseSelector`: Sélection exercices
- `CheckInWindow`: UI check-in
- Chaque classe a une responsabilité claire

#### Open/Closed
- `BaseWindow` extensible pour nouvelles fenêtres
- Managers prêts pour extension (Phase 6)

#### Liskov Substitution
- Toutes fenêtres héritent de `tk.Toplevel`
- Comportement cohérent

#### Interface Segregation
- Interfaces minimales (pas de dépendances inutiles)
- Couplage faible entre composants

#### Dependency Inversion
- (À améliorer Phase 6 avec injection de dépendances dans managers)

---

## 🔒 Sécurité

### Défenses Implémentées

#### 1. **Path Traversal Protection**
```python
def validate_file_path(file_path: Path, allowed_dir: Path) -> Path:
    """Valide que le chemin reste dans répertoire autorisé."""
    resolved = file_path.resolve()
    allowed = allowed_dir.resolve()
    
    if not str(resolved).startswith(str(allowed)):
        raise SecurityError(f"Path traversal attempt: {file_path}")
    
    return resolved
```

#### 2. **YAML Schema Validation**
```python
def validate_exercises_schema(data: dict) -> bool:
    """Valide structure attendue du YAML."""
    required_keys = ['problematic_areas', 'preventive']
    
    for key in required_keys:
        if key not in data:
            raise ValidationError(f"Missing key: {key}")
    
    # Validation détaillée de la structure
    # ...
    return True
```

#### 3. **Input Validation UI**
```python
# Dans NotificationConfigWindow.save()
if start_hour >= end_hour:
    messagebox.showerror("Erreur", "Heure début doit être < heure fin")
    return

if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
    messagebox.showerror("Erreur", "Heures invalides (0-23)")
    return
```

#### 4. **Safe YAML Loading**
```python
# Toujours yaml.safe_load() (jamais yaml.load())
with open(self.exercises_file, 'r', encoding='utf-8') as f:
    self.exercises = yaml.safe_load(f)
    validate_exercises_schema(self.exercises)  # +validation
```

#### 5. **Thread Safety**
- Locks sur tous états partagés
- Properties encapsulent accès
- Prévient race conditions

### Security Audit Results

**Version 0.2.0**: Note A+
- 0 vulnérabilités critiques
- 0 vulnérabilités moyennes
- 3 vulnérabilités faibles (acceptables)
- Dependabot actif
- pip-audit dans CI

Voir [SECURITY_REVIEW.md](../SECURITY_REVIEW.md) pour détails.

---

## 🤔 Décisions Techniques

### Pourquoi Python?

**✅ Avantages**:
- Développement rapide
- Écosystème riche (tkinter, winotify, pystray)
- Excellent tooling (pytest, coverage, pylint)
- PyInstaller pour distribution standalone

**⚠️ Limitations**:
- Performance suffisante pour use case (pas calculs lourds)
- Taille exécutable ~30MB (acceptable)
- Temps démarrage ~2-3s (acceptable pour app desktop)

### Pourquoi Tkinter?

**✅ Avantages**:
- Inclus dans Python (pas de dépendance externe)
- Simple pour UIs basiques
- Cross-platform (si besoin futur)
- Léger

**⚠️ Limitations**:
- Look old-school (mais suffisant pour use case)
- Pas de composants avancés (graphiques → Phase 6)

**Alternatives considérées**:
- PyQt: Trop lourd pour needs simples
- Electron: Overkill, taille énorme
- Web app: Complexité serveur inutile

### Pourquoi Windows-only?

**Raisonnement**:
- Marché cible: travailleurs de bureau Windows
- Idle detection simple (Windows API)
- winotify meilleure intégration que alternatives
- Multi-platform possible Phase 6 si demande

### PyInstaller vs Alternatives

**PyInstaller choisi car**:
- Mature et stable
- Good Windows support
- Executable standalone
- Pas de runtime externe requis

**Alternatives considérées**:
- cx_Freeze: Moins mature
- Nuitka: Compile Python, complexe
- py2exe: Windows-only, moins actif

---

## 📊 Métriques de Qualité

### Coverage par Module (v0.2.0)

```
Module                                Coverage
─────────────────────────────────────────────
src/app.py                            87%
src/config.py                         98%
src/security.py                       95%
src/constants.py                      100%
src/logging_config.py                 100%
src/ui/checkin_window.py             88%
src/ui/stats_window.py               93%
src/ui/notification_config_window.py  99%
src/ui/base_window.py                85%
src/managers/*.py                     0% (pas encore utilisés)
─────────────────────────────────────────────
TOTAL                                 75%
```

### Complexité Cyclomatique

**Cibles**:
- Fonctions simples: < 10
- Fonctions moyennes: 10-20
- Fonctions complexes: > 20 (à refactoriser)

**État actuel** (approximatif):
- Majorité des fonctions: < 10 ✅
- `OxyZenApp.schedule_loop()`: ~15 (acceptable)
- `ExerciseSelector.select_exercise()`: ~12 (acceptable)

### Dette Technique

**Identifiée**:
1. Managers créés mais pas utilisés (prévu Phase 6)
2. BaseWindow pas utilisée par fenêtres existantes (non prioritaire)
3. Pas d'interface graphique pour éditer exercises.yaml (Phase 6 Option B)
4. Pas de support multi-plateforme (Phase 6 Option D)

**Priorité**: Faible - Focus sur features utilisateur Phase 6

---

## 🚀 Évolution Future

### Phase 6 Options

#### Option A: Analytics Dashboard (Recommandé)
```
Nouveaux modules:
- src/analytics.py (calculs statistiques)
- src/ui/analytics_window.py (graphiques matplotlib)

Intégration:
- Menu system tray: "📊 Dashboard Analytics"
- Utilise exercise_history existant
- Pas de changements architecture majeurs
```

#### Option D: Multi-Platform
```
Refactoring majeur:
src/platform/
├── __init__.py (abstraction commune)
├── windows.py (code actuel)
├── macos.py (nouvelles implémentations)
└── linux.py

Changements:
- Abstraire système de notifications
- Abstraire idle detection
- Abstraire system tray
- Factory pattern pour créer bon platform manager
```

### Migration vers Managers

**Actuel** (v0.2.0):
```python
class OxyZenApp:
    # Toute la logique dans une classe
    def schedule_loop(self): ...
    def send_notification(self): ...
    def create_tray_icon(self): ...
```

**Futur** (Phase 6):
```python
class OxyZenApp:
    def __init__(
        self,
        schedule_mgr: ScheduleManager,
        notif_mgr: NotificationManager,
        icon_mgr: IconManager
    ):
        # Injection de dépendances
        self.schedule = schedule_mgr
        self.notifs = notif_mgr
        self.icon = icon_mgr
    
    def run(self):
        # Orchestration simple
        self.icon.create()
        self.schedule.start()
```

**Avantages**:
- Testabilité ++
- Séparation responsabilités
- Extensibilité
- Maintenabilité

---

## 📚 Ressources et Références

### Documentation Externe

- [Python Threading](https://docs.python.org/3/library/threading.html)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [Windows API Reference](https://docs.microsoft.com/en-us/windows/win32/api/)
- [PyInstaller Manual](https://pyinstaller.org/)

### Documentation Projet

- [README.md](../README.md) - Guide utilisateur
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Guide contributeur
- [ROADMAP.md](../ROADMAP.md) - Plan évolution
- [SECURITY_REVIEW.md](../SECURITY_REVIEW.md) - Audit sécurité
- [TODO.md](../TODO.md) - Tâches planifiées

---

## 🔄 Historique des Versions

**v0.2.0** (Mars 2026): Fondations solides
- Architecture modulaire
- 75% test coverage
- Thread safety
- Sécurité A+

**v0.1.0** (Février 2026): MVP fonctionnel
- Fonctionnalités de base
- Architecture monolithique

---

*Document vivant - mis à jour avec évolution du projet*
*Dernière révision: 6 mars 2026 par Olivier Ruineau*
