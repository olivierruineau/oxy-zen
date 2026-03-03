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

## 📥 Installation

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

## 📁 Structure du projet

```
oxy-zen/
├── src/                  # Code source principal
│   ├── app.py           # Application principale
│   ├── config.py        # Gestion des préférences utilisateur
│   └── ui/              # Interfaces graphiques
│       ├── checkin_window.py          # Fenêtre de check-in
│       ├── stats_window.py            # Fenêtre de statistiques
│       └── notification_config_window.py  # Fenêtre de configuration
├── data/                # Données de l'application
│   └── exercises.yaml   # Messages et exercices
├── scripts/             # Scripts utilitaires
│   ├── start.bat       # Lancement rapide
│   └── kill.bat        # Arrêt forcé
├── main.py             # Point d'entrée
├── pyproject.toml      # Configuration du projet
└── README.md           # Ce fichier
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

## 🤝 Contribution

Tu veux ajouter tes propres messages sarcastiques ? Édite `exercises.yaml` et partage tes meilleures répliques! 😄

## 📜 Licence

Ce projet est libre d'utilisation. Prends soin de toi! 💪

---

**Rappel** : Cette application ne remplace pas un avis médical. Si tu as des douleurs persistantes, consulte un professionnel de santé. 🏥