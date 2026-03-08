# 🎯 Checklist Intégration Icône

## Étape 1: Préparer le dossier assets/
- [ ] Créer: `mkdir assets`
- [ ] Placer ton image PNG dans: `assets\source_icon.png`

## Étape 2: Générer l'icône .ico
```powershell
python scripts\create_icon.py assets\source_icon.png
```

Résultat attendu:
- ✅ `assets/icon.ico` créé (multi-résolutions 16x16 → 256x256)
- ✅ Message de confirmation avec taille du fichier

## Étape 3: Copier l'icône pour le system tray
```powershell
copy assets\source_icon.png assets\icon.png
```

## Étape 4: Tester en mode développement
```powershell
# Activer l'environnement
.venv\Scripts\Activate.ps1

# Lancer l'app
python main.py
```

Vérifications:
- [ ] Logs montrent: "Chargement icône depuis: ...\assets\icon.png"
- [ ] Icône dans system tray affiche ton image (pas "OZ")

## Étape 5: Build et test
```powershell
# Build
.\scripts\build.bat

# Test exécutable
.\dist\OxyZen.exe
```

Vérifications:
- [ ] `dist\OxyZen.exe` existe
- [ ] Clic droit sur .exe → Propriétés → Icône visible
- [ ] System tray affiche ton icône pendant exécution

## 🚀 Commit final
```powershell
git add assets/ src/app.py build.spec scripts/create_icon.py .gitignore
git commit -m "feat: add professional icon for app and system tray"
```

## 📝 Notes
- Si icône floue: augmenter `ICON_SIZE` dans `src/constants.py`
- Si icône manquante: vérifier logs dans `%USERPROFILE%\.oxy-zen\app.log`
- Fallback automatique vers icône "OZ" si fichier manquant

---
*Voir docs/ICON_INTEGRATION.md pour détails complets*
