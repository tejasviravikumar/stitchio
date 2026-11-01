"""Configure an isolated SQLite database before importing the application."""
import io
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.update(
    DATABASE_URL=os.environ.get("TEST_DATABASE_URL", f"sqlite:///{_tmp}/test.db"),
    LOCAL_UPLOAD_DIR=f"{_tmp}/uploads",
    ENVIRONMENT="dev",
    DEV_AUTH_BYPASS="true",
    SUPABASE_URL="",
    SUPABASE_SERVICE_KEY="",
    SUPABASE_JWT_SECRET="",
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (120, 160), (240, 200, 210)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def measurements():
    return {"height_cm": 165, "bust_cm": 92, "waist_cm": 72, "hip_cm": 98}
