"""
Shared pytest fixtures for the osmand-osm project.
"""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest

# Handle optional psycopg import
try:
    import psycopg
    PSYCOPG_AVAILABLE = True
except ImportError:
    psycopg = None
    PSYCOPG_AVAILABLE = False


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config():
    """Mock configuration values for testing."""
    return {
        'DB_NAME': 'test_db',
        'ID_START': 17179869184,
        'test_working_dir': '/tmp/test'
    }


@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing."""
    if PSYCOPG_AVAILABLE:
        mock_conn = Mock(spec=psycopg.Connection)
    else:
        mock_conn = Mock()
    
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit = Mock()
    mock_conn.rollback = Mock()
    mock_conn.close = Mock()
    mock_cursor.execute = Mock()
    mock_cursor.fetchall = Mock(return_value=[])
    mock_cursor.fetchone = Mock(return_value=None)
    mock_cursor.close = Mock()
    return mock_conn


@pytest.fixture
def sample_geojson_data():
    """Sample GeoJSON data for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "number": "123",
                    "street": "Main St",
                    "city": "Test City",
                    "postcode": "12345",
                    "hash": "abc123def456"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-71.4188401, 41.8572897]
                }
            }
        ]
    }


@pytest.fixture
def sample_osm_data():
    """Sample OSM XML data for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="-1" lat="41.8572897" lon="-71.4188401">
    <tag k="addr:housenumber" v="123"/>
    <tag k="addr:street" v="Main St"/>
    <tag k="addr:city" v="Test City"/>
    <tag k="addr:postcode" v="12345"/>
  </node>
</osm>"""


@pytest.fixture
def mock_working_area():
    """Mock WorkingArea object for testing."""
    from unittest.mock import MagicMock
    
    mock_area = MagicMock()
    mock_area.name = "test"
    mock_area.name_underscore = "test"
    mock_area.country = "test"
    mock_area.short_name = "test"
    mock_area.directory = Path("test")
    mock_area.is_3166_2 = False
    mock_area.master_list = []
    mock_area.obf_name = "Test.obf"
    mock_area.pbf = "test/test.osm.pbf"
    mock_area.pbf_osm = "test/test-latest.osm.pbf"
    
    return mock_area


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run calls."""
    from unittest.mock import patch
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        yield mock_run


@pytest.fixture
def test_data_dir(temp_dir):
    """Create a test data directory with sample files."""
    data_dir = temp_dir / "test_data"
    data_dir.mkdir()
    
    # Create sample address file
    address_file = data_dir / "addresses.geojson"
    address_file.write_text('{"type": "FeatureCollection", "features": []}')
    
    # Create sample zip file structure
    zip_dir = data_dir / "zip_content"
    zip_dir.mkdir()
    (zip_dir / "addresses-city.geojson").write_text('{"type": "FeatureCollection", "features": []}')
    
    return data_dir


@pytest.fixture
def mock_ogr2osm():
    """Mock ogr2osm module for testing."""
    from unittest.mock import MagicMock, patch
    
    mock_ogr2osm = MagicMock()
    mock_ogr2osm.ogr2osm = MagicMock()
    
    with patch('ogr2osm.ogr2osm', mock_ogr2osm.ogr2osm):
        yield mock_ogr2osm


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables and cleanup."""
    # Set test environment variables
    monkeypatch.setenv("TESTING", "1")
    
    # Ensure we don't accidentally use real database
    monkeypatch.delenv("DATABASE_URL", raising=False)
    
    yield
    
    # Cleanup after test


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    from unittest.mock import Mock
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger