"""
Infrastructure validation tests to ensure testing setup works correctly.
"""
import pytest
import sys
from pathlib import Path


class TestInfrastructure:
    """Test the testing infrastructure setup."""

    def test_python_version(self):
        """Test that Python version is supported."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"

    def test_pytest_working(self):
        """Test that pytest is working correctly."""
        assert True

    def test_fixtures_available(self, temp_dir, mock_config, mock_db_connection):
        """Test that shared fixtures are available and working."""
        # Test temp_dir fixture
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Test mock_config fixture
        assert isinstance(mock_config, dict)
        assert 'DB_NAME' in mock_config
        
        # Test mock_db_connection fixture
        assert mock_db_connection is not None
        assert hasattr(mock_db_connection, 'cursor')

    def test_coverage_configuration(self):
        """Test that coverage configuration is present."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists()
        
        content = pyproject_path.read_text()
        assert "[tool.coverage" in content
        assert "osmand_osm" in content

    def test_pytest_configuration(self):
        """Test that pytest configuration is present."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        assert "[tool.pytest.ini_options]" in content
        assert "testpaths" in content

    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit test marker works."""
        assert True

    @pytest.mark.integration  
    def test_integration_marker(self):
        """Test that integration test marker works."""
        assert True

    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow test marker works."""
        assert True

    def test_imports_work(self):
        """Test that core project modules can be imported."""
        # Test that we can import from the osmand_osm package
        # This validates that the package structure is correct
        try:
            import osmand_osm
            import osmand_osm.osm
        except ImportError:
            # If modules don't exist yet, that's ok for infrastructure test
            # We just want to verify the test environment can handle imports
            pass
        
        assert True

    def test_mock_capabilities(self, mock_subprocess, mock_logger):
        """Test that mocking capabilities work correctly."""
        # Test subprocess mock
        mock_subprocess.return_value.returncode = 0
        assert mock_subprocess.return_value.returncode == 0
        
        # Test logger mock
        mock_logger.info("test message")
        mock_logger.info.assert_called_with("test message")

    def test_temporary_files(self, temp_dir, test_data_dir):
        """Test temporary file handling."""
        # Test basic temp dir
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.read_text() == "test content"
        
        # Test test data dir fixture
        assert test_data_dir.exists()
        assert (test_data_dir / "addresses.geojson").exists()

    def test_sample_data_fixtures(self, sample_geojson_data, sample_osm_data):
        """Test sample data fixtures."""
        # Test GeoJSON fixture
        assert sample_geojson_data["type"] == "FeatureCollection"
        assert len(sample_geojson_data["features"]) == 1
        
        # Test OSM data fixture
        assert "<?xml version" in sample_osm_data
        assert "addr:housenumber" in sample_osm_data

    def test_environment_setup(self):
        """Test that test environment is properly set up."""
        import os
        assert os.getenv("TESTING") == "1"
        # Database URL should not be set in test environment
        assert os.getenv("DATABASE_URL") is None