# Assets - Icônes Oxy-Zen

## 📁 Structure

```
assets/
├── README.md           # Ce fichier
├── source_icon.png     # Ton image originale (à ajouter)
├── icon.png            # Pour system tray (généré depuis source)
└── icon.ico            # Pour l'exécutable Windows (généré)
```

## 🎨 Étapes d'intégration

### 1. Ajoute ton icône
Place ton image PNG ici: `assets/source_icon.png`

### 2. Génère les formats
```powershell
# Génère icon.ico multi-résolutions
python scripts\create_icon.py assets\source_icon.png

# Copie pour system tray
copy assets\source_icon.png assets\icon.png
```

### 3. Teste
```powershell
python main.py  # Mode dev
.\scripts\build.bat  # Build exe
```

## 📐 Spécifications

### Icon.png (System Tray)
- Format: PNG
- Taille recommandée: 64x64px minimum (sera redimensionnée auto)
- Usage: Affichée dans la barre système pendant l'exécution

### Icon.ico (Exécutable)
- Format: ICO multi-résolutions
- Résolutions incluses: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- Usage: Propriétés fichier Windows, explorateur

## 🎯 Design actuel
Icône verte avec personnage blanc en position d'étirement
- Cohérent avec le nom "Oxy-Zen" (bien-être, respiration)
- Visible sur fonds clairs et sombres
- Simplicité pour les petites tailles

---
*Voir [ICON_CHECKLIST.md](../ICON_CHECKLIST.md) pour la checklist complète*
