import pytest
from pathlib import Path

@pytest.fixture
def srtm_path():
    path = Path(__file__).resolve().parent.parent / "scripts/srtm"
    return path 