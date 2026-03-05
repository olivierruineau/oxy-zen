#!/usr/bin/env python
"""Script pour vérifier que la couverture de tests est dans la plage acceptable."""

import sys
import xml.etree.ElementTree as ET

def check_coverage(coverage_file='coverage.xml', min_coverage=54, max_coverage=80):
    """
    Vérifie que la couverture est entre min et max.
    
    Args:
        coverage_file: Chemin vers le fichier coverage.xml
        min_coverage: Couverture minimale acceptable (%)
        max_coverage: Couverture maximale acceptable (%)
    
    Returns:
        0 si dans la plage, 1 sinon
    """
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Extraire le taux de couverture
        line_rate = float(root.attrib['line-rate'])
        coverage = line_rate * 100
        
        print(f"Couverture actuelle : {coverage:.2f}%")
        print(f"Plage acceptable : {min_coverage}%-{max_coverage}%")
        
        if min_coverage <= coverage <= max_coverage:
            print("✅ Couverture dans la plage acceptable")
            return 0
        elif coverage < min_coverage:
            print(f"❌ Couverture trop basse (minimum : {min_coverage}%)")
            return 1
        else:
            print(f"⚠️ Couverture trop élevée (maximum : {max_coverage}%) - Envisager de réduire les tests redondants")
            return 0  # Warning mais pas d'échec
            
    except FileNotFoundError:
        print(f"❌ Fichier {coverage_file} introuvable")
        return 1
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la couverture : {e}")
        return 1

if __name__ == '__main__':
    sys.exit(check_coverage())
