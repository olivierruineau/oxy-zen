# 🎨 Guide d'Intégration de l'Icône - Oxy-Zen

> Guide étape par étape pour intégrer l'icône personnalisée dans le projet

## 📋 Vue d'ensemble

Ton icône (personnage blanc en position d'étirement sur fond vert) est parfaite pour Oxy-Zen! Elle doit être intégrée à deux endroits:
1. **Icône exécutable Windows** (.ico pour propriétés fichier)
2. **Icône system tray** (image pour la barre des tâches)

---

## 🔧 Étape 1: Préparer les Fichiers

### 1.1 Créer le dossier `assets/`

```powershell
# Depuis la racine du projet
mkdir assets
```

### 1.2 Convertir PNG en ICO (Multi-résolutions)

L'icône Windows doit contenir plusieurs résolutions pour être nette partout.

**Option A: En ligne (Rapide)**
1. Va sur https://icoconvert.com/ ou https://convertio.co/png-ico/
2. Upload ton image PNG
3. Sélectionne toutes les résolutions:
   - 16x16 (taskbar small)
   - 32x32 (taskbar medium)
   - 48x48 (explorer)
   - 64x64
   - 128x128 (large icons)
   - 256x256 (extra large)
4. Télécharge `icon.ico`
5. Place dans `assets/icon.ico`

**Option B: Avec Python (Recommandé pour le projet)**

Créer `scripts/create_icon.py`:

```python
"""
Script pour créer l'icône multi-résolutions depuis une image source.
Usage: python scripts/create_icon.py assets/source_icon.png
"""

from PIL import Image
import sys
from pathlib import Path

def create_ico(source_path: Path, output_path: Path):
    """
    Crée un fichier .ico multi-résolutions depuis une image source.
    
    Args:
        source_path: Chemin vers l'image source (PNG, JPG, etc.)
        output_path: Chemin de sortie pour le .ico
    """
    # Charger l'image source
    img = Image.open(source_path)
    
    # Résolutions pour Windows
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Créer les versions redimensionnées
    icons = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Sauvegarder en .ico
    icons[0].save(
        output_path,
        format='ICO',
        sizes=sizes,
        append_images=icons[1:]
    )
    
    print(f"✅ Icône créée: {output_path}")
    print(f"   Résolutions: {', '.join(f'{w}x{h}' for w, h in sizes)}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_icon.py <source_image>")
        sys.exit(1)
    
    source = Path(sys.argv[1])
    if not source.exists():
        print(f"❌ Fichier introuvable: {source}")
        sys.exit(1)
    
    output = Path('assets/icon.ico')
    output.parent.mkdir(exist_ok=True)
    
    create_ico(source, output)
```

**Utilisation:**
```powershell
# 1. Place ton image PNG dans assets/
copy ton_image.png assets\source_icon.png

# 2. Génère le .ico
python scripts\create_icon.py assets\source_icon.png

# Résultat: assets/icon.ico créé
```

### 1.3 Copier aussi en PNG

Pour l'icône system tray (pystray), garde aussi le PNG:

```powershell
# Copie ton PNG dans assets/
copy ton_image.png assets\icon.png

# Structure finale:
# assets/
#   ├── icon.ico      # Pour l'exécutable Windows
#   ├── icon.png      # Pour system tray pendant exécution
#   └── source_icon.png  # Source originale (optionnel)
```

---

## 🔨 Étape 2: Modifier le Code

### 2.1 Mettre à jour `src/app.py`

Remplacer la méthode `create_icon_image()`:

```python
def get_icon_path(self) -> Optional[Path]:
    """
    Retourne le chemin vers l'icône, compatible PyInstaller.
    
    Returns:
        Path vers icon.png ou None si introuvable
    """
    # Essayer depuis assets/ (mode développement et PyInstaller)
    base_path = get_base_path()
    icon_path = base_path / 'assets' / 'icon.png'
    
    if icon_path.exists():
        return icon_path
    
    # Fallback si fichier manquant
    logger.warning(f"Icône introuvable: {icon_path}")
    return None

def create_icon_image(self):
    """
    Charge l'icône depuis le fichier ou crée une icône par défaut.
    
    Returns:
        Image PIL pour l'icône system tray
    """
    # Essayer de charger l'icône depuis le fichier
    icon_path = self.get_icon_path()
    
    if icon_path and icon_path.exists():
        try:
            logger.info(f"Chargement icône depuis: {icon_path}")
            img = Image.open(icon_path)
            
            # Redimensionner si nécessaire (tray icons = 16x16 ou 32x32)
            if img.size != (constants.ICON_SIZE, constants.ICON_SIZE):
                img = img.resize(
                    (constants.ICON_SIZE, constants.ICON_SIZE),
                    Image.Resampling.LANCZOS
                )
            
            return img
            
        except Exception as e:
            logger.error(f"Erreur chargement icône: {e}", exc_info=True)
            # Continuer vers fallback
    
    # Fallback: Créer icône programmatiquement (ancien code)
    logger.info("Création icône par défaut (fallback)")
    img = Image.new('RGB', (constants.ICON_SIZE, constants.ICON_SIZE), color='#3498db')
    draw = ImageDraw.Draw(img)
    
    # Cercle blanc
    margin = constants.ICON_SIZE // 8
    draw.ellipse(
        [margin, margin, constants.ICON_SIZE - margin, constants.ICON_SIZE - margin], 
        fill='white', 
        outline='#2980b9', 
        width=3
    )
    
    # Texte "OZ"
    text_x = constants.ICON_SIZE // 3
    text_y = constants.ICON_SIZE // 4
    draw.text((text_x, text_y), "OZ", fill='#3498db')
    
    return img
```

### 2.2 Vérifier les constantes

Dans `src/constants.py`, assurer que `ICON_SIZE` est défini:

```python
# Taille de l'icône system tray (Windows standard)
ICON_SIZE = 64  # 64x64 pour bonne qualité, sera redimensionné automatiquement
```

---

## 📦 Étape 3: Mettre à jour PyInstaller

### 3.1 Modifier `build.spec`

```python
# Données à inclure dans l'exécutable
datas = [
    ('data/exercises.yaml', 'data'),  # Fichier YAML des exercices
    ('assets/icon.png', 'assets'),    # ← AJOUTER: Icône pour system tray
]

# ... plus bas dans le fichier ...

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OxyZen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # ← MODIFIER: Chemin vers l'icône
    version_file='version_info.txt',
)
```

---

## ✅ Étape 4: Tester

### 4.1 Test en mode développement

```powershell
# Activer l'environnement
.venv\Scripts\Activate.ps1

# Lancer l'application
python main.py

# Vérifier dans les logs:
# "Chargement icône depuis: C:\...\assets\icon.png"
# L'icône dans la barre système devrait afficher ton image
```

### 4.2 Test de build

```powershell
# Build l'exécutable
.\scripts\build.bat

# Vérifier:
# 1. dist\OxyZen.exe existe
# 2. Propriétés du fichier affichent ton icône
# 3. Clic droit → Propriétés → onglet Détails: icône visible
```

### 4.3 Test de l'exécutable

```powershell
# Lancer l'exécutable
.\dist\OxyZen.exe

# Vérifier:
# 1. Icône dans barre système = ton image
# 2. Pas d'erreur dans %USERPROFILE%\.oxy-zen\app.log
```

---

## 🐛 Dépannage

### Icône ne s'affiche pas (system tray)

**Problème:** Icône par défaut "OZ" au lieu de ton image

**Solutions:**
1. Vérifier que `assets/icon.png` existe:
   ```powershell
   Test-Path assets\icon.png
   ```

2. Vérifier les logs:
   ```powershell
   Get-Content ~\.oxy-zen\app.log | Select-String "icon"
   ```

3. Vérifier dans build:
   ```powershell
   # Extraire l'exécutable et vérifier le contenu
   # (PyInstaller crée archive auto-extractible)
   .\dist\OxyZen.exe --help  # Force extraction
   # Vérifier dans %TEMP%\_MEI* si assets/icon.png présent
   ```

### Icône floue

**Problème:** Icône pixelisée dans system tray

**Solution:** Augmenter `ICON_SIZE` dans `src/constants.py`:
```python
ICON_SIZE = 64  # Au lieu de 32
```

### Build échoue

**Problème:** `FileNotFoundError: assets/icon.ico`

**Solution:**
```powershell
# Vérifier que le fichier existe
Test-Path assets\icon.ico

# Si manquant, le créer
python scripts\create_icon.py assets\source_icon.png
```

---

## 📁 Structure Finale

```
oxy-zen/
├── assets/
│   ├── icon.ico          # Multi-résolutions pour Windows exe
│   ├── icon.png          # Pour system tray pendant exécution
│   └── source_icon.png   # Source originale (backup)
├── scripts/
│   ├── build.bat
│   └── create_icon.py    # Script génération .ico
├── src/
│   └── app.py            # Mis à jour pour charger icône
├── build.spec            # Mis à jour avec icon path
└── dist/
    └── OxyZen.exe        # Avec belle icône! 🎉
```

---

## 🎯 Checklist Finale

Avant de commit:

- [ ] `assets/icon.ico` créé (multi-résolutions)
- [ ] `assets/icon.png` présent
- [ ] `src/app.py` mis à jour avec `get_icon_path()` et `create_icon_image()`
- [ ] `build.spec` mis à jour (`icon=` et `datas`)
- [ ] `scripts/create_icon.py` créé
- [ ] `.gitignore` mis à jour (optionnel):
  ```
  # Garder les icônes sources, ignorer builds intermédiaires
  assets/source_icon.png  # Optionnel
  ```
- [ ] Testé en dev: `python main.py`
- [ ] Testé build: `.\scripts\build.bat`
- [ ] Testé exe: `.\dist\OxyZen.exe`
- [ ] Icône visible dans propriétés fichier
- [ ] Icône visible dans system tray

---

## 🚀 Prochaines Étapes

Une fois l'icône intégrée:

1. **Commit les changements:**
   ```powershell
   git add assets/ src/app.py build.spec scripts/create_icon.py
   git commit -m "feat: add custom icon for application and system tray
   
   - Add professional stretching person icon (green background)
   - Create multi-resolution .ico for Windows executable
   - Update system tray to load icon from file
   - Add fallback to programmatic icon if file missing
   - Add script to generate .ico from source image
   
   Closes Phase 5 icon task"
   ```

2. **Mettre à jour TODO.md:**
   - [x] Icône professionnel intégré ✅

3. **Optionnel - Créer release:**
   ```powershell
   .\scripts\release.ps1 -Version 0.2.1
   ```
   Release note: "Added custom icon"

---

## 💡 Conseils Design

Ton icône actuelle est excellente! Quelques suggestions optionnelles:

**Optimisations possibles:**
- **Contraste:** Le blanc sur vert fonctionne bien
- **Simplicité:** Le design épuré est parfait pour small sizes
- **Cohérence:** Garde le vert zen cohérent avec le nom "Oxy-Zen"

**Variations futures (Phase 6):**
- Icône "pausé" (gris?)
- Icône "notification" (badge?)
- Icône "nuit" pour dark mode Windows

---

*Guide créé: 9 mars 2026*
*Compatible avec: Oxy-Zen v0.2.0+*
