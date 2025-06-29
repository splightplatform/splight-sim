from pathlib import Path

import pytest

from scripts import utils


@pytest.fixture
def srtm_path():
    path = Path(__file__).resolve().parent.parent / "scripts/srtm"
    return path


@pytest.fixture
def altitude_client():
    client = utils.OpenElevationClient()
    return client
