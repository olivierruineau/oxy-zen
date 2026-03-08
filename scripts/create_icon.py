"""
Script pour créer l'icône multi-résolutions depuis une image source.

Usage:
    python scripts/create_icon.py assets/source_icon.png

Crée:
- assets/icon.ico (multi-résolutions pour l'exécutable Windows)
- assets/icon.png (64x64 pour le system tray)
"""

from PIL import Image, ImageChops
import sys
from pathlib import Path

# Taille pour l'icône system tray (doit correspondre à ICON_SIZE dans src/constants.py)
ICON_SIZE = 64

# Seuil de tolérance pour détecter le blanc (0-255, plus bas = plus strict)
WHITE_THRESHOLD = 240


def create_ico(source_path: Path, output_path: Path):
    """
    Crée un fichier .ico multi-résolutions depuis une image source.
    
    Args:
        source_path: Chemin vers l'image source (PNG, JPG, etc.)
        output_path: Chemin de sortie pour le .ico
    """
    try:
        # Charger l'image source
        print(f"📂 Chargement: {source_path}")
        img = Image.open(source_path)
        
        # Résolutions pour Windows (taskbar, explorer, large icons, etc.)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Créer les versions redimensionnées
        print(f"🔄 Génération de {len(sizes)} résolutions...")
        icons = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
            print(f"   ✓ {size[0]}x{size[1]}")
        
        # Sauvegarder en .ico
        print(f"💾 Sauvegarde: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        icons[0].save(
            output_path,
            format='ICO',
            sizes=sizes,
            append_images=icons[1:]
        )
        
        # Afficher résultat
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"\n✅ Icône .ico créée avec succès!")
        print(f"   Fichier: {output_path}")
        print(f"   Taille: {file_size:.1f} KB")
        print(f"   Résolutions: {', '.join(f'{w}x{h}' for w, h in sizes)}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


def remove_white_background(img: Image.Image, threshold: int = WHITE_THRESHOLD) -> Image.Image:
    """
    Rend le fond blanc transparent.
    
    Args:
        img: Image PIL à traiter
        threshold: Seuil pour détecter le blanc (0-255, défaut: 240)
                  Pixels avec R, G, B > threshold deviennent transparents
    
    Returns:
        Image avec fond transparent
    """
    # Convertir en RGBA si nécessaire
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Obtenir les données de pixels
    pixels = img.load()
    width, height = img.size
    
    # Parcourir tous les pixels
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # Si le pixel est proche du blanc (au-dessus du seuil), le rendre transparent
            if r > threshold and g > threshold and b > threshold:
                pixels[x, y] = (r, g, b, 0)  # Alpha = 0 (transparent)
    
    return img


def create_png(source_path: Path, output_path: Path, size: int = ICON_SIZE):
    """
    Crée un PNG redimensionné pour le system tray.
    
    Args:
        source_path: Chemin vers l'image source (PNG, JPG, etc.)
        output_path: Chemin de sortie pour le PNG
        size: Taille en pixels (carré, défaut: 64)
    """
    try:
        # Charger l'image source
        img = Image.open(source_path)
        
        # Redimensionner
        print(f"\n🔄 Génération PNG pour system tray...")
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Rendre le fond blanc transparent
        print(f"✨ Suppression du fond blanc (seuil: {WHITE_THRESHOLD})...")
        transparent = remove_white_background(resized, WHITE_THRESHOLD)
        
        # Sauvegarder en PNG avec transparence
        print(f"💾 Sauvegarde: {output_path}")
        transparent.save(output_path, format='PNG', optimize=True)
        
        # Afficher résultat
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"\n✅ Icône .png créée avec succès!")
        print(f"   Fichier: {output_path}")
        print(f"   Taille: {file_size:.1f} KB")
        print(f"   Résolution: {size}x{size}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


def main():
    """Point d'entrée du script."""
    if len(sys.argv) != 2:
        print("❌ Usage incorrect")
        print("   python scripts/create_icon.py <source_image>")
        print("\nExemple:")
        print("   python scripts/create_icon.py assets/source_icon.png")
        sys.exit(1)
    
    source = Path(sys.argv[1])
    
    if not source.exists():
        print(f"❌ Fichier introuvable: {source}")
        sys.exit(1)
    
    if source.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        print(f"⚠️  Avertissement: {source.suffix} n'est pas un format standard")
        print("   Formats recommandés: .png, .jpg, .bmp")
    
    ico_output = Path('assets/icon.ico')
    png_output = Path('assets/icon.png')
    
    print(f"\n🎨 Création d'icônes Oxy-Zen")
    print(f"   Source: {source}")
    print(f"   Sortie .ico: {ico_output}")
    print(f"   Sortie .png: {png_output}\n")
    
    # Créer l'icône .ico multi-résolutions
    create_ico(source, ico_output)
    
    # Créer le PNG redimensionné pour system tray
    create_png(source, png_output, ICON_SIZE)
    
    print(f"\n🎉 Terminé! Les deux fichiers sont prêts:")
    print(f"   • {ico_output} → Pour l'exécutable Windows (build)")
    print(f"   • {png_output} → Pour le system tray (runtime)")


if __name__ == '__main__':
    main()
