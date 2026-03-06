"""Module de sécurité pour Oxy-Zen - Validation des chemins et des schémas."""

import logging
from pathlib import Path
from typing import Dict, List, Any

# Configuration du logger
logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Exception levée pour les problèmes de sécurité."""
    pass


class PathTraversalError(SecurityError):
    """Exception levée lors d'une tentative de path traversal."""
    pass


class InvalidSchemaError(SecurityError):
    """Exception levée lorsque le schéma YAML est invalide."""
    pass


# Constante : Répertoire autorisé pour les fichiers de données
def get_allowed_data_dir() -> Path:
    """
    Retourne le répertoire autorisé pour les fichiers de données.
    
    Returns:
        Path: Le répertoire data/ dans le répertoire de l'application
    """
    from .app import get_base_path
    return get_base_path() / "data"


ALLOWED_DATA_DIR = None  # Sera initialisé au runtime


def validate_path(file_path: Path, allowed_dir: Path = None) -> Path:
    """
    Valide qu'un chemin de fichier est sécurisé et dans le répertoire autorisé.
    
    Args:
        file_path: Le chemin à valider
        allowed_dir: Le répertoire autorisé (par défaut: ALLOWED_DATA_DIR)
    
    Returns:
        Path: Le chemin résolu et validé
    
    Raises:
        PathTraversalError: Si le chemin tente une traversée de répertoire
        FileNotFoundError: Si le fichier n'existe pas
    """
    if allowed_dir is None:
        allowed_dir = get_allowed_data_dir()
    
    try:
        # Résoudre le chemin absolu
        resolved_path = file_path.resolve()
        resolved_allowed_dir = allowed_dir.resolve()
        
        # Vérifier que le chemin résolu est bien dans le répertoire autorisé
        if not str(resolved_path).startswith(str(resolved_allowed_dir)):
            logger.warning(
                f"⚠️ Tentative de path traversal détectée: {file_path} "
                f"(résolu: {resolved_path}) n'est pas dans {resolved_allowed_dir}"
            )
            raise PathTraversalError(
                f"Le fichier doit être dans le répertoire autorisé: {resolved_allowed_dir}"
            )
        
        # Vérifier que le fichier existe
        if not resolved_path.exists():
            raise FileNotFoundError(f"Le fichier n'existe pas: {resolved_path}")
        
        # Vérifier que c'est bien un fichier (pas un répertoire)
        if not resolved_path.is_file():
            raise PathTraversalError(
                f"Le chemin doit pointer vers un fichier: {resolved_path}"
            )
        
        logger.debug(f"✅ Chemin validé: {resolved_path}")
        return resolved_path
    
    except FileNotFoundError:
        # Re-lever FileNotFoundError sans l'encapsuler
        raise
    except (OSError, ValueError) as e:
        logger.error(f"❌ Erreur lors de la validation du chemin: {e}")
        raise PathTraversalError(f"Chemin invalide: {file_path}") from e


def validate_exercises_schema(data: Any) -> Dict[str, List[Dict[str, str]]]:
    """
    Valide que les données chargées depuis le YAML respectent le schéma attendu.
    
    Schéma attendu:
    {
        "category_name": [
            {
                "message": "string",
                "exercise": "string"
            },
            ...
        ],
        ...
    }
    
    Args:
        data: Les données à valider
    
    Returns:
        Dict[str, List[Dict[str, str]]]: Les données validées
    
    Raises:
        InvalidSchemaError: Si le schéma est invalide
    """
    if data is None:
        raise InvalidSchemaError("Les données YAML sont vides (None)")
    
    if not isinstance(data, dict):
        raise InvalidSchemaError(
            f"Le schéma doit être un dictionnaire, reçu: {type(data).__name__}"
        )
    
    if not data:
        raise InvalidSchemaError("Le dictionnaire d'exercices est vide")
    
    # Valider chaque catégorie
    for category, exercises in data.items():
        # Valider le nom de la catégorie
        if not isinstance(category, str):
            raise InvalidSchemaError(
                f"Le nom de catégorie doit être une chaîne, reçu: {type(category).__name__}"
            )
        
        if not category.strip():
            raise InvalidSchemaError("Le nom de catégorie ne peut pas être vide")
        
        # Valider la liste d'exercices
        if not isinstance(exercises, list):
            raise InvalidSchemaError(
                f"Les exercices de '{category}' doivent être une liste, "
                f"reçu: {type(exercises).__name__}"
            )
        
        if not exercises:
            logger.warning(f"⚠️ La catégorie '{category}' est vide")
            continue
        
        # Valider chaque exercice
        for i, exercise in enumerate(exercises):
            if not isinstance(exercise, dict):
                raise InvalidSchemaError(
                    f"L'exercice {i} de '{category}' doit être un dictionnaire, "
                    f"reçu: {type(exercise).__name__}"
                )
            
            # Vérifier les champs requis
            required_fields = {"message", "exercise"}
            exercise_fields = set(exercise.keys())
            
            missing_fields = required_fields - exercise_fields
            if missing_fields:
                raise InvalidSchemaError(
                    f"L'exercice {i} de '{category}' manque les champs: "
                    f"{', '.join(sorted(missing_fields))}"
                )
            
            # Valider les types des champs
            for field in required_fields:
                value = exercise[field]
                if not isinstance(value, str):
                    raise InvalidSchemaError(
                        f"Le champ '{field}' de l'exercice {i} de '{category}' "
                        f"doit être une chaîne, reçu: {type(value).__name__}"
                    )
                
                if not value.strip():
                    raise InvalidSchemaError(
                        f"Le champ '{field}' de l'exercice {i} de '{category}' "
                        f"ne peut pas être vide"
                    )
    
    total_exercises = sum(len(exercises) for exercises in data.values())
    logger.info(
        f"✅ Schéma validé: {len(data)} catégories, "
        f"{total_exercises} exercices au total"
    )
    
    return data


def load_and_validate_exercises(file_path: Path, allowed_dir: Path = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Charge et valide un fichier d'exercices de manière sécurisée.
    
    Cette fonction combine la validation du chemin et la validation du schéma
    pour charger de manière sûre un fichier d'exercices.
    
    Args:
        file_path: Le chemin du fichier d'exercices
        allowed_dir: Le répertoire autorisé (par défaut: ALLOWED_DATA_DIR)
    
    Returns:
        Dict[str, List[Dict[str, str]]]: Les exercices validés
    
    Raises:
        PathTraversalError: Si le chemin est invalide
        InvalidSchemaError: Si le schéma YAML est invalide
        FileNotFoundError: Si le fichier n'existe pas
        yaml.YAMLError: Si le fichier YAML est mal formé
    """
    import yaml
    
    # Étape 1: Valider le chemin
    validated_path = validate_path(file_path, allowed_dir)
    
    # Étape 2: Charger le fichier YAML
    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"❌ Erreur de parsing YAML: {e}")
        raise InvalidSchemaError(f"Fichier YAML mal formé: {e}") from e
    
    # Étape 3: Valider le schéma
    validated_data = validate_exercises_schema(data)
    
    return validated_data
