# 🧘 Oxy-Zen

Application de rappels d'exercices adaptatifs pour ta journée de travail. Parce que ton corps mérite mieux qu'une vie de statue! 🗿

## 🎯 Fonctionnalités

- 🔔 **Notifications récurrentes** : Configurables (30 min, 1h, 2h) pendant tes heures de travail
- ⚙️ **Configuration personnalisable** : Fréquence, horaires de travail, moment d'envoi
- 🎭 **Messages sarcastiques** : Des rappels avec humour pour te motiver à bouger
- 🎯 **Adaptation intelligente** : Check-in quotidien pour identifier tes zones à problème
- 📊 **Pondération 70/30** : 70% d'exercices ciblés sur tes problèmes, 30% de prévention globale
- 💾 **Messages personnalisables** : Fichier YAML externe pour éditer les messages
- ⏸️ **Contrôle facile** : Pause/reprise depuis l'icône système
- 📈 **Statistiques** : Suivi de tes notifications et exercices

## 📥 Installation (Utilisateur final)

### Installation rapide - Exécutable Windows

**Prérequis** : Windows 10/11 uniquement

**Pas besoin d'installer Python !** 🎉

1. **Télécharge l'exécutable**
   - Télécharge `OxyZen.exe` depuis la dernière release
   - Ou demande à un développeur de le générer (voir section développeur ci-dessous)

2. **Lance l'application**
   - Double-clique sur `OxyZen.exe`
   - Une fenêtre de check-in apparaîtra pour configurer tes besoins
   - L'icône apparaîtra dans la barre système (près de l'horloge)

3. **[Optionnel] Configure le démarrage automatique**
   - Appuie sur `Win + R`, tape `shell:startup` et appuie sur Entrée
   - Copie `OxyZen.exe` dans ce dossier (ou crée un raccourci)
   - L'application démarrera automatiquement à chaque connexion Windows

**C'est tout !** L'application ne nécessite aucune installation supplémentaire. 🚀

---

## 📥 Installation (Développeur)

### Prérequis
- Python 3.12 ou supérieur
- Windows 10/11
- `uv` (gestionnaire de paquets)

### Étapes

1. **Clone ou télécharge ce projet**
   ```powershell
   cd C:\Users\TON_USER\Code\oxy-zen
   ```

2. **Installe les dépendances avec uv**
   ```powershell
   uv sync
   ```

3. **Lance l'application**
   ```powershell
   uv run python main.py
   ```

## 🚀 Premier lancement

Au premier lancement, une fenêtre de check-in apparaîtra automatiquement :

1. Coche les zones qui te posent problème (dos, yeux, jambes, posture, respiration, fatigue)
2. Ou coche "Tout va bien (RAS)" si aucun souci particulier
3. Valide

L'application ajustera automatiquement les exercices proposés selon tes besoins!

## 💡 Utilisation

### Icône système

Une fois lancée, l'application apparaît dans la barre système (près de l'horloge). Clique droit sur l'icône pour :

- � **Déclencher notification** : Test immédiat d'une notification
- ⏰ **Snooze 5 min** : Rappel de la dernière notification dans 5 minutes
- 📝 **Check-in manuel** : Refaire le questionnaire
- 📊 **Voir statistiques** : Consulter tes stats d'utilisation
- ⚙️ **Configurer notifications** : Personnaliser fréquence et horaires
- ⏸️ **Pause 1 heure** : Suspendre temporairement
- 🌙 **Pause jusqu'à demain** : Désactiver pour aujourd'hui
- ▶️ **Reprendre** : Réactiver après une pause
- ❌ **Quitter** : Fermer l'application

### Notifications

Selon la fréquence configurée (par défaut toutes les 30 minutes, entre 7h30 et 16h, uniquement en semaine), tu recevras une notification avec :
- Un message sarcastique motivant
- Une instruction d'exercice précise

Exemple : 
```
"Ton dos appelle son avocat 🦴"
Étire-toi en arrière pendant 30 secondes, mains sur les hanches
```

### Configuration des notifications

Depuis le menu système, clique sur **"Configurer notifications"** pour personnaliser :

- **Fréquence** : Toutes les 30 min, 1h, 2h, ou jamais
- **Moment d'envoi** : À l'heure pile (10:00), +7 min (10:07), +15 min (10:15), ou +23 min (10:23)
- **Horaires de travail** : Heure de début et de fin (par défaut 7h30 - 16h00)

Les changements sont sauvegardés automatiquement et appliqués immédiatement.

### Check-in quotidien

Une fois par jour (heure aléatoire entre 10h et 14h), une fenêtre de check-in rapide apparaît pour mettre à jour tes besoins. Tu peux aussi le déclencher manuellement depuis le menu.

## ⚙️ Personnalisation

### Configuration via l'interface

Utilise le menu **"Configurer notifications"** (clic droit sur l'icône système) pour personnaliser :

- **Fréquence des notifications** : 30 min, 1h, 2h, ou désactiver
- **Moment d'envoi** : Décalage de 0, 7, 15, ou 23 minutes par rapport à l'heure de base
- **Horaires de travail** : Personnalise ton heure de début et de fin de journée

### Modifier les messages

Édite le fichier `data/exercises.yaml` pour personnaliser les messages et exercices :

```yaml
dos:
  - message: "Ton message sarcastique ici"
    exercise: "Instructions de l'exercice ici"
```

Catégories disponibles : 
- `dos` : Exercices pour le dos et lombaires
- `yeux` : Exercices pour les yeux et fatigue oculaire
- `jambes` : Exercices pour les jambes et circulation
- `posture` : Exercices de posture et nuque
- `respiration` : Exercices de respiration
- `fatigue_generale` : Exercices énergisants
- `prevention_globale` : Exercices de prévention générale

### Format et validation du YAML

Le fichier `data/exercises.yaml` est automatiquement validé au démarrage de l'application pour garantir la sécurité et la cohérence des données.

**Schéma requis** :

```yaml
categorie_nom:
  - message: "Message sarcastique ou motivant"
    exercise: "Instructions précises de l'exercice"
  - message: "Autre message"
    exercise: "Autres instructions"
```

**Règles de validation** :
- Le fichier doit être un dictionnaire valide (format YAML)
- Chaque catégorie doit être une chaîne de caractères non vide
- Chaque catégorie contient une liste d'exercices
- Chaque exercice doit avoir les champs obligatoires :
  - `message` : Chaîne de caractères non vide (message affiché dans la notification)
  - `exercise` : Chaîne de caractères non vide (instructions de l'exercice)

**Sécurité** :
- Le fichier `exercises.yaml` doit être situé dans le répertoire `data/` du projet
- Les tentatives d'accès à des fichiers en dehors de ce répertoire (path traversal) sont bloquées
- Les erreurs de validation sont loguées dans `~/.oxy-zen/app.log`

**Exemple complet** :
```yaml
dos:
  - message: "Ton dos appelle son avocat 🦴"
    exercise: "Étire-toi en arrière pendant 30 secondes, mains sur les hanches"
  - message: "Tes lombaires demandent justice"
    exercise: "Rotations du bassin, 10 fois dans chaque sens"

yeux:
  - message: "Tes yeux font grève 👀"
    exercise: "Regarde un point éloigné (6m+) pendant 20 secondes"
```

Si le fichier est invalide ou corrompu, l'application charge automatiquement un ensemble d'exercices de secours pour continuer à fonctionner.

## 🔧 Lancement automatique au démarrage

### Option 1 : Dossier de démarrage Windows

1. Utilise le script de lancement : `scripts\start.bat`

2. Appuie sur `Win + R`, tape `shell:startup` et appuie sur Entrée

3. Copie le fichier `scripts\start.bat` dans ce dossier (ou crée un raccourci)

### Option 2 : Planificateur de tâches

1. Ouvre le Planificateur de tâches Windows
2. Crée une nouvelle tâche de base
3. Définis le déclencheur : "À l'ouverture de session"
4. Action : "Démarrer un programme"
5. Programme : `C:\chemin\vers\uv.exe`
6. Arguments : `run python main.py`
7. Dossier de démarrage : `C:\Users\TON_USER\Code\oxy-zen`

## � Générer l'exécutable (Développeur)

### Build de l'exécutable Windows

Pour créer un fichier `OxyZen.exe` autonome distributable :

```powershell
# Depuis la racine du projet
.\scripts\build.bat
```

Le script va :
1. Installer PyInstaller et les dépendances de développement via `uv`
2. Utiliser PyInstaller avec la configuration `build.spec`
3. Générer `dist\OxyZen.exe` (~15-25 MB)

**Fichiers générés** :
- `dist\OxyZen.exe` : Exécutable final à distribuer
- `build\` : Fichiers temporaires de build (peut être supprimé)

**Test de l'exécutable** :
```powershell
cd dist
.\OxyZen.exe
```

**⚠️ Important** : Teste l'exe sur une machine **sans Python installé** pour valider le packaging.

### Configuration PyInstaller

Le fichier `build.spec` configure le packaging :
- **Mode onefile** : Un seul fichier .exe (portable)
- **Mode windowed** : Pas de console visible
- **Données intégrées** : `data/exercises.yaml` embarqué dans l'exe
- **Imports cachés** : Modules non détectés automatiquement (`pystray`, `PIL._tkinter_finder`)
- **Compression UPX** : Réduction de la taille de l'exe

### Build manuel (avancé)

```powershell
# Installer PyInstaller
uv sync --group dev

# Lancer le build avec PyInstaller
uv run pyinstaller build.spec --clean

# Options supplémentaires
uv run pyinstaller build.spec --clean --log-level DEBUG  # Verbose
```
## 🚀 Release automatique (Développeur)

### Process de release avec GitHub Actions

Le projet utilise GitHub Actions pour automatiser le build et la création de releases.

**Workflow automatique** :
1. Tag une version → Déclenche le build
2. Build Windows automatique avec PyInstaller
3. Création d'une release GitHub avec l'exe
4. Package disponible dans les releases

### Créer une release

**Option 1 : Avec le script helper (Recommandé)** 🌟

```powershell
# Utilise la version de pyproject.toml (actuellement 0.1.0)
.\scripts\release.ps1

# Ou spécifie une nouvelle version
.\scripts\release.ps1 -Version 1.0.0
```

Le script va :
- ✅ Vérifier que le repo est propre (pas de changements non commités)
- ✅ Optionnellement mettre à jour `pyproject.toml` avec la nouvelle version
- ✅ Créer et pusher le tag Git (ex: `v1.0.0`)
- ✅ Déclencher automatiquement le workflow GitHub Actions
- ✅ Afficher les liens pour suivre le build et la release

**Option 2 : Manuellement**

```powershell
# 1. Mettre à jour la version dans pyproject.toml
#    version = "1.0.0"

# 2. Commiter le changement
git add pyproject.toml
git commit -m "chore: bump version to 1.0.0"

# 3. Créer et pusher le tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Suivre le build

Une fois le tag pushé :

1. **Workflow en cours** : https://github.com/olivierruineau/oxy-zen/actions
   - Vérification de la version (tag = pyproject.toml)
   - Build Windows (~5 minutes)
   - Création de la release

2. **Release publiée** : https://github.com/olivierruineau/oxy-zen/releases
   - `OxyZen.exe` (~18 MB) attaché automatiquement
   - Notes de release générées depuis les commits

### En cas de problème

Si le build échoue ou tu veux annuler :

```powershell
# Supprimer le tag localement
git tag -d v1.0.0

# Supprimer le tag sur GitHub
git push origin :refs/tags/v1.0.0
```

### Versionning

Le projet utilise [Semantic Versioning](https://semver.org/lang/fr/) :
- **MAJOR** (1.0.0) : Changements incompatibles
- **MINOR** (0.1.0) : Nouvelles fonctionnalités compatibles
- **PATCH** (0.0.1) : Corrections de bugs

**⚠️ Important** : La version dans `pyproject.toml` et le tag Git doivent correspondre exactement.
## �📁 Structure du projet

```
oxy-zen/
├── .github/             # Configuration GitHub
│   └── workflows/
│       └── release.yml  # Workflow CI/CD (build & release)
├── src/                 # Code source principal
│   ├── app.py          # Application principale
│   ├── config.py       # Gestion des préférences utilisateur
│   └── ui/             # Interfaces graphiques
│       ├── checkin_window.py          # Fenêtre de check-in
│       ├── stats_window.py            # Fenêtre de statistiques
│       └── notification_config_window.py  # Fenêtre de configuration
├── data/               # Données de l'application
│   └── exercises.yaml  # Messages et exercices (embarqué dans l'exe)
├── scripts/            # Scripts utilitaires
│   ├── start.bat      # Lancement rapide (dev)
│   ├── build.bat      # Build local PyInstaller
│   ├── release.ps1    # Helper pour créer des releases
│   └── kill.bat       # Arrêt forcé
├── dist/               # Exécutable généré (après build)
│   └── OxyZen.exe     # Distributable final (~18 MB)
├── build/              # Fichiers temporaires PyInstaller (après build)
├── main.py            # Point d'entrée
├── build.spec         # Configuration PyInstaller
├── pyproject.toml     # Configuration du projet (version + dépendances)
└── README.md          # Ce fichier
```

## 🔍 Fichiers de configuration

L'application crée automatiquement un dossier de configuration :
- **Windows** : `C:\Users\TON_USER\.oxy-zen\config.json`

Ce fichier contient :
- **Zones à problème** : Tes zones identifiées lors du check-in
- **Date du dernier check-in** : Timestamp de ta dernière mise à jour
- **Pondérations calculées** : Poids de chaque catégorie d'exercices
- **Statistiques d'utilisation** : Nombre de notifications, historique des exercices
- **Configuration des notifications** :
  - `frequency` : Fréquence en minutes (30, 60, 120, ou 0 pour désactiver)
  - `moment` : Décalage en minutes (0, 7, 15, ou 23)
  - `start_hour` et `start_minute` : Heure de début de travail
  - `end_hour` et `end_minute` : Heure de fin de travail

Tu peux le supprimer pour réinitialiser l'application.

## 🐛 Dépannage

### Les notifications n'apparaissent pas
- Vérifie que les notifications Windows sont activées
- Vérifie le mode "Concentration" (Focus Assist) dans les paramètres Windows
- Lance l'app en dehors du weekend ou des heures de travail pour tester

### L'icône système n'apparaît pas
- Vérifie que Pillow est bien installé : `uv run python -c "import PIL; print('OK')"`
- Redémarre l'application

### Erreur au lancement
- Assure-toi d'avoir Python 3.12+ : `python --version`
- Réinstalle les dépendances : `uv sync --reinstall`
- Vérifie que tous les fichiers sont présents

### L'app ne respecte pas les horaires
- Vérifie l'heure système de Windows
- Vérifie que tu es bien en semaine (lun-ven)

## 📊 Algorithme de pondération

L'application utilise un algorithme intelligent pour sélectionner les exercices :

1. **Check-in** : Tu identifies tes zones à problème
2. **Calcul des poids** : 
   - 70% du poids total réparti équitablement sur tes zones à problème
   - 30% alloué à la prévention globale
   - Petit poids résiduel (1%) sur les autres catégories
3. **Sélection** : À chaque notification, une catégorie est tirée selon ces poids
4. **Anti-répétition** : Les 3 derniers messages sont évités

Exemple : Si tu coches "Dos" et "Yeux"
- Dos : 35% de chances
- Yeux : 35% de chances
- Prévention globale : 30% de chances
- Autres catégories : ~1% chacune

## � Tests

Le projet utilise `pytest` pour garantir la qualité du code avec des tests unitaires et d'intégration.

### Lancer les tests

```powershell
# Installation des dépendances de test
uv sync --all-groups

# Exécuter tous les tests
uv run pytest

# Avec rapport de couverture
uv run pytest --cov=src --cov-report=term-missing
```

### Couverture de code

- **Couverture totale : ~55-60%**
- `src/config.py` : 97% ✅
- `src/app.py` : 72% ✅
- `src/ui/*` : 15-20% (tests manuels recommandés)

### CI/CD

Les tests s'exécutent automatiquement sur chaque Pull Request vers `main` :
- Validation de la couverture (objectif : 60-80%)
- Rapport automatique dans les commentaires PR
- Configuration : [.github/workflows/tests.yml](.github/workflows/tests.yml)

Pour plus de détails, voir [tests/README.md](tests/README.md).

## �🤝 Contribution

Tu veux ajouter tes propres messages sarcastiques ? Édite `exercises.yaml` et partage tes meilleures répliques! 😄

## 📜 Licence

Ce projet est libre d'utilisation. Prends soin de toi! 💪

---

**Rappel** : Cette application ne remplace pas un avis médical. Si tu as des douleurs persistantes, consulte un professionnel de santé. 🏥