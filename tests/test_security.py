"""Tests pour le module de sécurité - Validation des chemins et des schémas."""

import pytest
import yaml
from pathlib import Path
from src.security import (
    validate_path,
    validate_exercises_schema,
    load_and_validate_exercises,
    PathTraversalError,
    InvalidSchemaError,
    get_allowed_data_dir
)


class TestPathValidation:
    """Tests pour la validation des chemins de fichiers."""

    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Crée un répertoire de données temporaire."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return data_dir

    @pytest.fixture
    def valid_file(self, temp_data_dir):
        """Crée un fichier valide dans le répertoire autorisé."""
        file_path = temp_data_dir / "test.yaml"
        file_path.write_text("test: data")
        return file_path

    def test_validate_path_accepts_valid_file(self, valid_file, temp_data_dir):
        """Test qu'un fichier valide dans le répertoire autorisé est accepté."""
        # Act
        result = validate_path(valid_file, temp_data_dir)
        
        # Assert
        assert result == valid_file.resolve()

    def test_validate_path_rejects_parent_directory_traversal(self, temp_data_dir, tmp_path):
        """Test que la traversée vers le répertoire parent est rejetée."""
        # Arrange - Créer un fichier en dehors du répertoire autorisé
        outside_file = tmp_path / "outside.yaml"
        outside_file.write_text("malicious: data")
        
        # Act & Assert
        with pytest.raises(PathTraversalError, match="doit être dans le répertoire autorisé"):
            validate_path(outside_file, temp_data_dir)

    def test_validate_path_rejects_traversal_with_dots(self, temp_data_dir, tmp_path):
        """Test que la traversée avec .. est rejetée."""
        # Arrange - Créer un fichier en dehors
        outside_file = tmp_path / "malicious.yaml"
        outside_file.write_text("malicious: data")
        
        # Tenter de traverser avec ../
        traversal_path = temp_data_dir / ".." / "malicious.yaml"
        
        # Act & Assert
        with pytest.raises(PathTraversalError, match="doit être dans le répertoire autorisé"):
            validate_path(traversal_path, temp_data_dir)

    def test_validate_path_rejects_nonexistent_file(self, temp_data_dir):
        """Test qu'un fichier inexistant est rejeté."""
        # Arrange
        nonexistent = temp_data_dir / "does_not_exist.yaml"
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            validate_path(nonexistent, temp_data_dir)

    def test_validate_path_rejects_directory(self, temp_data_dir):
        """Test qu'un répertoire (pas un fichier) est rejeté."""
        # Arrange - Créer un sous-répertoire
        subdir = temp_data_dir / "subdir"
        subdir.mkdir()
        
        # Act & Assert
        with pytest.raises(PathTraversalError, match="doit pointer vers un fichier"):
            validate_path(subdir, temp_data_dir)

    def test_validate_path_handles_symlinks_safely(self, temp_data_dir, tmp_path):
        """Test que les liens symboliques sont résolus et validés."""
        # Arrange - Créer un fichier en dehors du répertoire autorisé
        outside_file = tmp_path / "outside.yaml"
        outside_file.write_text("data: test")
        
        # Créer un lien symbolique pointant vers ce fichier
        symlink = temp_data_dir / "link.yaml"
        try:
            symlink.symlink_to(outside_file)
        except OSError:
            pytest.skip("Les liens symboliques ne sont pas supportés sur ce système")
        
        # Act & Assert - Le lien devrait être rejeté car il pointe hors du répertoire
        with pytest.raises(PathTraversalError):
            validate_path(symlink, temp_data_dir)


class TestSchemaValidation:
    """Tests pour la validation du schéma YAML."""

    def test_validate_schema_accepts_valid_data(self):
        """Test qu'un schéma valide est accepté."""
        # Arrange
        data = {
            "dos": [
                {"message": "Test message", "exercise": "Test exercise"}
            ],
            "yeux": [
                {"message": "Eye test", "exercise": "Eye exercise"}
            ]
        }
        
        # Act
        result = validate_exercises_schema(data)
        
        # Assert
        assert result == data

    def test_validate_schema_rejects_none(self):
        """Test que None est rejeté."""
        with pytest.raises(InvalidSchemaError, match="données YAML sont vides"):
            validate_exercises_schema(None)

    def test_validate_schema_rejects_non_dict(self):
        """Test qu'un type non-dictionnaire est rejeté."""
        with pytest.raises(InvalidSchemaError, match="doit être un dictionnaire"):
            validate_exercises_schema([1, 2, 3])

    def test_validate_schema_rejects_empty_dict(self):
        """Test qu'un dictionnaire vide est rejeté."""
        with pytest.raises(InvalidSchemaError, match="dictionnaire d'exercices est vide"):
            validate_exercises_schema({})

    def test_validate_schema_rejects_non_string_category(self):
        """Test qu'un nom de catégorie non-string est rejeté."""
        data = {
            123: [{"message": "test", "exercise": "test"}]
        }
        with pytest.raises(InvalidSchemaError, match="nom de catégorie doit être une chaîne"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_empty_category_name(self):
        """Test qu'un nom de catégorie vide est rejeté."""
        data = {
            "  ": [{"message": "test", "exercise": "test"}]
        }
        with pytest.raises(InvalidSchemaError, match="nom de catégorie ne peut pas être vide"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_non_list_exercises(self):
        """Test que des exercices non-liste sont rejetés."""
        data = {
            "dos": "not a list"
        }
        with pytest.raises(InvalidSchemaError, match="doivent être une liste"):
            validate_exercises_schema(data)

    def test_validate_schema_accepts_empty_category(self):
        """Test qu'une catégorie vide génère un warning mais est acceptée."""
        data = {
            "dos": [],
            "yeux": [{"message": "test", "exercise": "test"}]
        }
        # Ne devrait pas lever d'exception
        result = validate_exercises_schema(data)
        assert result == data

    def test_validate_schema_rejects_non_dict_exercise(self):
        """Test qu'un exercice non-dictionnaire est rejeté."""
        data = {
            "dos": ["string instead of dict"]
        }
        with pytest.raises(InvalidSchemaError, match="doit être un dictionnaire"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_missing_message_field(self):
        """Test qu'un exercice sans champ 'message' est rejeté."""
        data = {
            "dos": [{"exercise": "test"}]
        }
        with pytest.raises(InvalidSchemaError, match="manque les champs.*message"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_missing_exercise_field(self):
        """Test qu'un exercice sans champ 'exercise' est rejeté."""
        data = {
            "dos": [{"message": "test"}]
        }
        with pytest.raises(InvalidSchemaError, match="manque les champs.*exercise"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_non_string_message(self):
        """Test qu'un message non-string est rejeté."""
        data = {
            "dos": [{"message": 123, "exercise": "test"}]
        }
        with pytest.raises(InvalidSchemaError, match="champ 'message'.*doit être une chaîne"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_empty_message(self):
        """Test qu'un message vide est rejeté."""
        data = {
            "dos": [{"message": "  ", "exercise": "test"}]
        }
        with pytest.raises(InvalidSchemaError, match="champ 'message'.*ne peut pas être vide"):
            validate_exercises_schema(data)

    def test_validate_schema_rejects_empty_exercise(self):
        """Test qu'un exercice vide est rejeté."""
        data = {
            "dos": [{"message": "test", "exercise": ""}]
        }
        with pytest.raises(InvalidSchemaError, match="champ 'exercise'.*ne peut pas être vide"):
            validate_exercises_schema(data)

    def test_validate_schema_accepts_multiple_categories_and_exercises(self):
        """Test qu'un schéma complexe valide est accepté."""
        data = {
            "dos": [
                {"message": "Msg 1", "exercise": "Ex 1"},
                {"message": "Msg 2", "exercise": "Ex 2"},
            ],
            "yeux": [
                {"message": "Eye msg", "exercise": "Eye ex"}
            ],
            "jambes": [
                {"message": "Leg msg 1", "exercise": "Leg ex 1"},
                {"message": "Leg msg 2", "exercise": "Leg ex 2"},
                {"message": "Leg msg 3", "exercise": "Leg ex 3"},
            ]
        }
        
        result = validate_exercises_schema(data)
        assert result == data


class TestLoadAndValidate:
    """Tests pour la fonction complète de chargement et validation."""

    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Crée un répertoire de données temporaire."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return data_dir

    @pytest.fixture
    def valid_exercises_file(self, temp_data_dir):
        """Crée un fichier d'exercices valide."""
        file_path = temp_data_dir / "exercises.yaml"
        data = {
            "dos": [
                {"message": "Test dos", "exercise": "Exercice dos"}
            ],
            "yeux": [
                {"message": "Test yeux", "exercise": "Exercice yeux"}
            ]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        return file_path

    def test_load_and_validate_successful(self, valid_exercises_file, temp_data_dir):
        """Test qu'un fichier valide est chargé avec succès."""
        # Act
        result = load_and_validate_exercises(valid_exercises_file, temp_data_dir)
        
        # Assert
        assert "dos" in result
        assert "yeux" in result
        assert len(result["dos"]) == 1
        assert result["dos"][0]["message"] == "Test dos"

    def test_load_and_validate_rejects_path_traversal(self, temp_data_dir, tmp_path):
        """Test que la traversée de chemin est rejetée."""
        # Arrange
        outside_file = tmp_path / "malicious.yaml"
        with open(outside_file, 'w') as f:
            yaml.dump({"dos": [{"message": "test", "exercise": "test"}]}, f)
        
        # Act & Assert
        with pytest.raises(PathTraversalError):
            load_and_validate_exercises(outside_file)

    def test_load_and_validate_rejects_invalid_schema(self, temp_data_dir):
        """Test qu'un schéma invalide est rejeté."""
        # Arrange - Créer un fichier avec un schéma invalide
        file_path = temp_data_dir / "invalid.yaml"
        data = {
            "dos": [{"message": "missing exercise field"}]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        # Act & Assert
        with pytest.raises(InvalidSchemaError, match="manque les champs"):
            load_and_validate_exercises(file_path, temp_data_dir)

    def test_load_and_validate_rejects_malformed_yaml(self, temp_data_dir):
        """Test qu'un fichier YAML mal formé est rejeté."""
        # Arrange
        file_path = temp_data_dir / "malformed.yaml"
        file_path.write_text("{ invalid yaml [ syntax")
        
        # Act & Assert
        with pytest.raises(InvalidSchemaError, match="YAML mal formé"):
            load_and_validate_exercises(file_path, temp_data_dir)

    def test_load_and_validate_works_with_real_exercises_file(self):
        """Test avec le vrai fichier d'exercices du projet."""
        # Arrange
        exercises_path = get_allowed_data_dir() / "exercises.yaml"
        
        if not exercises_path.exists():
            pytest.skip("Le fichier exercises.yaml n'existe pas")
        
        # Act
        result = load_and_validate_exercises(exercises_path)
        
        # Assert
        assert isinstance(result, dict)
        assert len(result) > 0
        # Vérifier quelques catégories attendues
        expected_categories = ["dos", "yeux", "jambes", "posture", "respiration"]
        for cat in expected_categories:
            assert cat in result, f"La catégorie '{cat}' devrait être présente"


class TestSecurityLogging:
    """Tests pour vérifier que les tentatives suspectes sont loggées."""

    def test_path_traversal_is_logged(self, tmp_path, caplog):
        """Test que les tentatives de path traversal sont loggées."""
        # Arrange
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        outside_file = tmp_path / "outside.yaml"
        outside_file.write_text("test")
        
        # Act
        with pytest.raises(PathTraversalError):
            validate_path(outside_file, data_dir)
        
        # Assert - Vérifier qu'un warning a été logué
        assert any("Tentative de path traversal" in record.message for record in caplog.records)
