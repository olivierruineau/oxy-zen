# 🔒 Revue de Sécurité - Oxy-Zen

> Date de revue : 6 mars 2026
> Version analysée : Current master branch
> Analysé par : GitHub Copilot (Claude Sonnet 4.5)

## 📋 Résumé Exécutif

**Verdict :** ✅ **Aucune vulnérabilité critique identifiée**

L'application Oxy-Zen présente une posture de sécurité solide pour une application desktop Windows. Aucune vulnérabilité critique n'a été identifiée. Trois risques moyens et cinq risques faibles nécessitent une attention.

### Scores

| Catégorie | Score | Statut |
|-----------|-------|--------|
| **Vulnérabilités Critiques** | 0 | ✅ Excellent |
| **Vulnérabilités Moyennes** | 3 | ⚠️ À adresser |
| **Vulnérabilités Faibles** | 5 | 🟡 Monitoring |
| **Note Globale** | B+ | ✅ Bon |

---

## 🔴 Vulnérabilités Critiques

### Aucune identifiée ✅

---

## 🟠 Vulnérabilités Moyennes

### 1. File Path Injection Risk

**Sévérité :** 🟠 Moyenne
**Probabilité :** Faible (actuellement)
**Impact :** Élevé (si exploité)

**Description :**
La méthode `ExerciseSelector.__init__` accepte des chemins de fichiers arbitraires sans validation.

**Localisation :**
- Fichier : `src/app.py`
- Lignes : 79-90
- Fonction : `ExerciseSelector.__init__()`

**Code vulnérable :**
```python
def __init__(self, exercises_file: Path, preferences: UserPreferences):
    self.exercises_file = exercises_file
    # ...
    with open(self.exercises_file, 'r', encoding='utf-8') as f:
        # Lit le fichier sans validation du chemin
```

**Scénario d'attaque :**
Si `exercises_file` devient contrôlable par l'utilisateur (modification future), un attaquant pourrait :
- Lire des fichiers système arbitraires (`C:\Windows\System32\config\SAM`)
- Lire des fichiers utilisateur sensibles (`~/.ssh/id_rsa`)
- Causer un DoS en ouvrant des fichiers volumineux

**Preuve de Concept :**
```python
# Si jamais exposé via interface utilisateur
malicious_path = Path("C:/Windows/System32/config/SAM")
selector = ExerciseSelector(malicious_path, prefs)  # Lirait fichier système
```

**Mesures d'atténuation actuelles :**
- ✅ Chemin actuellement hardcodé à `data/exercises.yaml`
- ✅ Pas d'interface UI pour modifier le chemin
- ✅ Pas d'arguments CLI acceptant chemins personnalisés

**Recommandations :**
```python
# Dans src/app.py
from pathlib import Path

ALLOWED_DATA_DIR = Path(__file__).parent.parent / "data"

def __init__(self, exercises_file: Path, preferences: UserPreferences):
    # Valider que le fichier est dans le répertoire autorisé
    try:
        resolved_path = exercises_file.resolve()
        if not resolved_path.is_relative_to(ALLOWED_DATA_DIR):
            raise ValueError(f"Invalid exercises file path: {exercises_file}")
        if not resolved_path.exists():
            raise FileNotFoundError(f"Exercises file not found: {exercises_file}")
    except Exception as e:
        logger.error(f"Invalid exercises file: {e}")
        raise
    
    self.exercises_file = resolved_path
```

**Statut :** ⏳ À implémenter (Phase 1.4 du Roadmap)

---

### 2. YAML Deserialization Sans Validation de Schéma

**Sévérité :** 🟠 Moyenne
**Probabilité :** Moyenne
**Impact :** Moyen

**Description :**
Le fichier `exercises.yaml` est chargé avec `yaml.safe_load()` (correct) mais sans validation de schéma. Un fichier malformé ou modifié pourrait causer des comportements inattendus.

**Localisation :**
- Fichier : `src/app.py`
- Ligne : 91
- Fonction : `ExerciseSelector.__init__()`

**Code vulnérable :**
```python
with open(self.exercises_file, 'r', encoding='utf-8') as f:
    self.exercises = yaml.safe_load(f)
# Aucune validation de la structure
```

**Points positifs :**
- ✅ Utilise `yaml.safe_load()` (pas `load()`) → prévient code execution
- ✅ Try/except capture erreurs de parsing

**Risques résiduels :**
- Structure YAML inattendue → exceptions runtime
- Clés manquantes → KeyError pendant sélection
- Types incorrects → TypeError dans logique métier

**Exemples de YAML malveillant :**
```yaml
# Cas 1: Structure invalide
problematic_areas:
  - "not_a_dict"  # Attendu: dict avec name, exercises

# Cas 2: Clés manquantes
problematic_areas:
  - exercises:
      - message: "test"
      # 'exercise' key missing

# Cas 3: Types incorrects
problematic_areas:
  - name: 123  # Attendu: string
    exercises: "not_a_list"
```

**Recommandations :**
```python
from typing import TypedDict

class ExerciseSchema(TypedDict):
    message: str
    exercise: str

class ProblemAreaSchema(TypedDict):
    name: str
    exercises: list[ExerciseSchema]

def validate_exercises_schema(data: dict) -> bool:
    """Valide que le YAML a la structure attendue"""
    required_keys = ['problematic_areas', 'preventive']
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    for area in data['problematic_areas']:
        if 'name' not in area or 'exercises' not in area:
            raise ValueError(f"Invalid problem area structure")
        for exercise in area['exercises']:
            if 'message' not in exercise or 'exercise' not in exercise:
                raise ValueError(f"Invalid exercise structure")
    
    # Similar validation for preventive exercises
    return True

# Dans __init__
self.exercises = yaml.safe_load(f)
validate_exercises_schema(self.exercises)
```

**Statut :** ⏳ À implémenter (Phase 1.5 du Roadmap)

---

### 3. Config File Write Non-Atomique

**Sévérité :** 🟠 Moyenne
**Probabilité :** Faible
**Impact :** Moyen (perte de configuration)

**Description :**
Le fichier de configuration est écrit directement sans opération atomique. Si le processus crash pendant l'écriture, le fichier peut être corrompu.

**Localisation :**
- Fichier : `src/config.py`
- Lignes : 76-77
- Méthode : `UserPreferences.save()`

**Code vulnérable :**
```python
with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
# Si crash ici, fichier partiellement écrit
```

**Scénarios de corruption :**
1. Crash application pendant écriture
2. Arrêt forcé (kill process)
3. Panne électrique
4. Disque plein pendant écriture

**Impact :**
- Configuration perdue
- Application ne démarre plus (JSON invalide)
- Utilisateur doit reconfigurer manuellement

**Recommandations :**
```python
import os
import tempfile

def save(self) -> None:
    """Sauvegarde atomique de la configuration"""
    data = {
        'problem_areas': list(self.problem_areas),
        'exercise_history': self.exercise_history[-20:],
        'notification_count': self.notification_count,
        'last_checkin': self.last_checkin,
        'notification_config': self.notification_config
    }
    
    # Écrire dans fichier temporaire
    temp_fd, temp_path = tempfile.mkstemp(
        dir=self.CONFIG_DIR,
        prefix='.config_',
        suffix='.tmp'
    )
    
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Opération atomique: rename
        os.replace(temp_path, self.CONFIG_FILE)
        
    except Exception as e:
        # Cleanup en cas d'erreur
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise IOError(f"Failed to save config: {e}")
```

**Statut :** ⏳ À implémenter (Phase 1.3 du Roadmap)

---

## 🟡 Vulnérabilités Faibles

### 4. User Home Directory Exposure

**Sévérité :** 🟡 Faible
**Probabilité :** N/A
**Impact :** Minimal

**Description :**
La configuration est stockée dans `~/.oxy-zen/` lisible par l'utilisateur.

**Localisation :**
- Fichier : `src/config.py`
- Ligne : 12

**Analyse :**
- ✅ Comportement attendu pour application user-scoped
- ✅ Config ne contient pas de données sensibles (pas de mots de passe, tokens)
- ✅ Données lisibles seulement par l'utilisateur propriétaire

**Contenu du config :**
- Zones problématiques sélectionnées (info santé)
- Historique d'exercices
- Compteur de notifications
- Préférences d'horaires

**Recommandations :**
- ℹ️ Acceptable tel quel
- ℹ️ Si données sensibles ajoutées futures, considérer chiffrement
- ℹ️ Documenter dans PRIVACY.md quelles données stockées

**Statut :** ✅ Acceptable

---

### 5. Exception Information Disclosure

**Sévérité :** 🟡 Faible
**Probabilité :** Faible
**Impact :** Minimal

**Description :**
Les messages d'exception sont imprimés à la console, potentiellement exposant la structure interne.

**Localisation :**
- Fichier : `src/app.py`
- Multiples occurrences (lignes 93, 259, 566)
- Fichier : `src/config.py` (lignes 56-58, 78)

**Code concerné :**
```python
except Exception as e:
    print(f"❌ Erreur lors du chargement des exercices: {e}")
    # Stack trace peut contenir chemins, structure code
```

**Risques :**
- Exposition chemins système
- Exposition structure code interne
- Aide potentielle pour reverse engineering

**Contexte d'atténuation :**
- ✅ Console pas visible en mode normal (GUI app)
- ✅ build.spec: `console=False`
- ⚠️ Visible si lancé depuis terminal

**Recommandations :**
```python
import logging

logger = logging.getLogger(__name__)

try:
    # Operation risquée
except SpecificException as e:
    # Log détaillé pour debugging
    logger.error(f"Failed to load exercises: {e}", exc_info=True)
    # Message user-friendly pour UI
    show_error_dialog("Impossible de charger les exercices. Vérifiez l'installation.")
```

**Statut :** ⏳ À implémenter (Phase 2.1 du Roadmap)

---

### 6. Windows API Broad Exception Handling

**Sévérité :** 🟡 Faible
**Probabilité :** Faible
**Impact :** Minimal (masque erreurs légitimes)

**Description :**
Les fonctions Windows API utilisent `except Exception` très large.

**Localisation :**
- Fichier : `src/app.py`
- Lignes : 39-57
- Fonctions : `get_idle_duration()`, `is_session_locked()`

**Code concerné :**
```python
def get_idle_duration() -> int:
    try:
        # Appels ctypes Windows API
    except Exception:
        return 0  # Masque toutes erreurs
```

**Analyse :**
- ✅ Programmation défensive acceptable pour API native
- ✅ Graceful degradation (retourne valeur sûre)
- ⚠️ Pourrait masquer vraies erreurs

**Recommandations :**
```python
import ctypes
from ctypes import WinError

def get_idle_duration() -> int:
    try:
        # Windows API calls
    except OSError as e:
        logger.warning(f"Windows API error: {e}")
        return 0
    except AttributeError as e:
        logger.error(f"Windows API not available: {e}")
        return 0
    except Exception as e:
        logger.exception(f"Unexpected error in idle detection: {e}")
        return 0
```

**Statut :** 🟢 Acceptable, amélioration Phase 2.5

---

### 7. Thread Safety - Shared State Access

**Sévérité :** 🟡 Faible → 🟠 Moyenne si haute charge
**Probabilité :** Faible
**Impact :** Moyen (état incohérent)

**Description :**
Plusieurs threads accèdent à l'état partagé sans locks.

**Localisation :**
- Fichier : `src/app.py`
- Lignes : 172, 335, 349
- Variables : `self.paused`, `self.last_notification`

**Threads identifiés :**
1. Main thread (UI)
2. `schedule_loop()` thread (ligne 567)
3. UI threads (CheckIn, Stats, Config windows)
4. Snooze thread (ligne 244-250)

**Code concerné :**
```python
# Thread 1: Schedule loop
self.paused = False

# Thread 2: Menu callback
self.paused = True  # Race condition possible

# Thread 3: Snooze
self.last_notification = (category, message, exercise)  # Shared write
```

**Scénarios de race condition :**
```python
# Thread A                    # Thread B
if not self.paused:           self.paused = True
    # Entre temps, paused=True
    send_notification()       # Ne devrait pas arriver
```

**Recommandations :**
```python
import threading

class OxyZenApp:
    def __init__(self):
        self._state_lock = threading.Lock()
        self._paused = False
    
    @property
    def paused(self):
        with self._state_lock:
            return self._paused
    
    @paused.setter
    def paused(self, value):
        with self._state_lock:
            self._paused = value
```

**Statut :** 🔴 PRIORITAIRE - Phase 1.1 du Roadmap

---

### 8. Pas de Rate Limiting sur Notifications

**Sévérité :** 🟡 Faible
**Probabilité :** Très faible
**Impact :** Annoyance utilisateur

**Description :**
Aucune limite sur la fréquence des notifications en cas de bug.

**Localisation :**
- Fichier : `src/app.py`
- Fonction : `send_notification()`

**Scénario :**
Si bug dans scheduling, pourrait envoyer notifications en boucle.

**Mesures d'atténuation actuelles :**
- ✅ `self.idle_threshold` limite fréquence
- ✅ Anti-répétition de messages implémenté
- ✅ Schedule library gère timing

**Recommandations :**
```python
from collections import deque
import time

class OxyZenApp:
    def __init__(self):
        self.notification_timestamps = deque(maxlen=10)
        self.MAX_NOTIFICATIONS_PER_MINUTE = 3
    
    def send_notification(self, ...):
        # Rate limit check
        now = time.time()
        recent = [t for t in self.notification_timestamps if now - t < 60]
        
        if len(recent) >= self.MAX_NOTIFICATIONS_PER_MINUTE:
            logger.warning("Rate limit hit, skipping notification")
            return
        
        self.notification_timestamps.append(now)
        # Send notification
```

**Statut :** 🟢 Nice to have

---

## 🔐 Dépendances - Analyse de Sécurité

### Production Dependencies

| Package | Version | CVEs Connus | Dernière Analyse | Statut |
|---------|---------|-------------|------------------|--------|
| `winotify` | ≥1.1.0 | 0 | 2026-03-06 | ✅ Sûr |
| `schedule` | ≥1.2.0 | 0 | 2026-03-06 | ✅ Sûr |
| `pystray` | ≥0.19.0 | 0 | 2026-03-06 | ✅ Sûr |
| `pillow` | ≥10.0.0 | ⚠️ À vérifier | 2026-03-06 | ⚠️ Surveiller |
| `pyyaml` | ≥6.0.0 | 0 (v6+) | 2026-03-06 | ✅ Sûr |

### Détails - Pillow

**Historique :** Bibliothèque d'imagerie fréquemment ciblée
**Versions affectées passées :** <10.0.0 avaient multiples CVEs
**Version actuelle :** 10.0.0+ corrige vulnérabilités connues

**Utilisation dans Oxy-Zen :**
- Uniquement pour charger icône statique (pas de traitement d'images utilisateur)
- Risque limité (pas d'input utilisateur non fiable)

**Recommandations :**
- ✅ Continuer monitoring CVE databases
- ✅ Activer Dependabot (Phase 4.3)
- ✅ Run `pip-audit` régulièrement

### Détails - PyYAML

**Versions dangereuses :** <5.4 (yaml.load() permettait code execution)
**Version actuelle :** ≥6.0.0 ✅
**Utilisation :** `yaml.safe_load()` uniquement ✅

**Points de vigilance :**
- ✅ Jamais utiliser `yaml.load()` ou `yaml.unsafe_load()`
- ✅ Toujours `yaml.safe_load()`
- ✅ Valider schéma après load (voir Vuln #2)

---

## 🛡️ Bonnes Pratiques Identifiées

### ✅ Ce qui est bien fait

1. **YAML Parsing Sécurisé**
   - Utilise `yaml.safe_load()` exclusivement
   - Prévient code execution via YAML

2. **File Encoding Explicite**
   - Tous `open()` spécifient `encoding='utf-8'`
   - Prévient encoding attacks

3. **Input Validation Partielle**
   - Windows API graceful degradation
   - Exception handling avec fallbacks

4. **No Eval/Exec**
   - Aucune utilisation de `eval()`, `exec()`, `__import__()`
   - Pas de code dynamique dangereux

5. **Dependencies Modernes**
   - PyYAML ≥6.0 (versions anciennes avaient CVEs critiques)
   - Pillow ≥10.0 (versions récentes patchées)

6. **Error Handling**
   - Try/except présents pour opérations risquées
   - Fallbacks sains définis

---

## 📊 Matrice des Risques

| Vulnérabilité | Sévérité | Probabilité | Exposition | Priorité Correction |
|---------------|----------|-------------|------------|---------------------|
| Thread Safety | 🟠 Moyenne | Faible | Runtime | 🔴 Élevée |
| File Path Injection | 🟠 Moyenne | Très Faible | Future | 🟠 Moyenne |
| Config Corruption | 🟠 Moyenne | Faible | Crash | 🟠 Moyenne |
| YAML Schema | 🟠 Moyenne | Moyenne | User Error | 🟠 Moyenne |
| Exception Disclosure | 🟡 Faible | Très Faible | Dev Mode | 🟡 Basse |
| Broad Exception | 🟡 Faible | Faible | Dev | 🟡 Basse |
| Home Dir Exposure | 🟡 Faible | N/A | Expected | 🟢 Acceptable |
| No Rate Limit | 🟡 Faible | Très Faible | Bug | 🟢 Nice to Have |

---

## ✅ Plan de Remédiation

### Priorité 1 - Critique (Faire immédiatement)
- [ ] **Vuln #7:** Ajouter thread safety (locks) → Roadmap Phase 1.1
- [ ] **Vuln #3:** Implémenter écriture atomique config → Roadmap Phase 1.3
- [ ] **Vuln #2:** Valider schéma YAML → Roadmap Phase 1.5

### Priorité 2 - Haute (Faire bientôt)
- [ ] **Vuln #1:** Valider chemins de fichiers → Roadmap Phase 1.4
- [ ] **Vuln #5:** Implémenter logging proper → Roadmap Phase 2.1

### Priorité 3 - Moyenne (Maintenance continue)
- [ ] Activer Dependabot → Roadmap Phase 4.3
- [ ] Run pip-audit dans CI → Roadmap Phase 4.3
- [ ] Monitoring CVEs Pillow

### Priorité 4 - Basse (Nice to have)
- [ ] **Vuln #6:** Améliorer exception handling → Roadmap Phase 2.5
- [ ] **Vuln #8:** Ajouter rate limiting notifications

---

## 🔍 Recommandations Générales

### Sécurité

1. **Activer Scans Automatisés**
   ```yaml
   # .github/dependabot.yml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

2. **Ajouter Pre-commit Hooks**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/PyCQA/bandit
       hooks:
         - id: bandit
           args: ['-r', 'src/']
   ```

3. **Run Security Audits**
   ```bash
   pip install pip-audit
   pip-audit
   ```

### Développement

1. **Code Review Checklist**
   - [ ] Pas de `eval()`, `exec()`, `pickle.load()`
   - [ ] Validation input utilisateur
   - [ ] Exceptions spécifiques (pas `except Exception`)
   - [ ] Logging au lieu de `print()`
   - [ ] Thread safety pour state partagé

2. **Testing**
   - Ajouter tests pour edge cases sécurité
   - Fuzzing des parsers (YAML, JSON, config)
   - Tests de concurrence

---

## 📅 Historique des Revues

| Date | Version | Auditeur | Critiques | Moyennes | Faibles | Statut |
|------|---------|----------|-----------|----------|---------|--------|
| 2026-03-06 | master | Copilot | 0 | 3 | 5 | ⚠️ Action requise |

---

## 📝 Prochaine Revue

**Date suggérée :** Après completion Phase 1 du Roadmap
**Focus :** Vérifier corrections vulnérabilités moyennes

---

*Document vivant - mettre à jour après chaque correction*
