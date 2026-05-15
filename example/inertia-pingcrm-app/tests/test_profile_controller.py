import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from bootstrap.application import app
from app.http.controllers.profile_controller import save_photo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app.fastapi, raise_server_exceptions=True)


def _make_upload(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={"content-type": content_type},
    )


# ---------------------------------------------------------------------------
# save_photo unit tests
# ---------------------------------------------------------------------------

class TestSavePhoto:
    async def test_returns_none_when_no_file(self):
        result = await save_photo(None)
        assert result is None

    async def test_returns_none_when_filename_empty(self):
        upload = _make_upload("", b"data", "image/jpeg")
        result = await save_photo(upload)
        assert result is None

    async def test_returns_none_for_non_image(self):
        upload = _make_upload("doc.pdf", b"data", "application/pdf")
        result = await save_photo(upload)
        assert result is None

    async def test_saves_image_and_returns_key(self):
        upload = _make_upload("avatar.png", b"fake-image-bytes", "image/png")

        with patch("app.http.controllers.profile_controller.Storage") as mock_storage:
            mock_disk = MagicMock()
            mock_storage.disk.return_value = mock_disk

            result = await save_photo(upload)

        assert result is not None
        assert result.startswith("photos/")
        assert result.endswith(".png")
        mock_storage.disk.assert_called_once_with("s3")
        mock_disk.put.assert_called_once()

    async def test_uses_jpg_fallback_when_no_extension(self):
        upload = _make_upload("avatar", b"fake-image-bytes", "image/jpeg")

        with patch("app.http.controllers.profile_controller.Storage") as mock_storage:
            mock_storage.disk.return_value = MagicMock()
            result = await save_photo(upload)

        assert result.endswith(".jpg")


# ---------------------------------------------------------------------------
# edit endpoint tests
# ---------------------------------------------------------------------------

class TestEditEndpoint:
    def test_redirects_unauthenticated_to_login(self, client):
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"

    def test_renders_profile_for_authenticated_user(self, client):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.email = "john@example.com"
        mock_user.photo_path = None

        with (
            patch("app.http.controllers.profile_controller.User") as mock_user_cls,
            patch("app.http.controllers.profile_controller.Inertia") as mock_inertia,
        ):
            mock_user_cls.find = AsyncMock(return_value=mock_user)
            mock_inertia.render.return_value = MagicMock(status_code=200)

            response = client.get(
                "/profile",
                cookies={"session": _fake_session(user_id=1)},
            )

        props = mock_inertia.render.call_args[0][1]["user"]
        assert props["first_name"] == "John"
        assert props["photo"] is None

    def test_photo_url_uses_images_route(self, client):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.first_name = "Jane"
        mock_user.last_name = "Doe"
        mock_user.email = "jane@example.com"
        mock_user.photo_path = "photos/abc123.png"

        with (
            patch("app.http.controllers.profile_controller.User") as mock_user_cls,
            patch("app.http.controllers.profile_controller.Inertia") as mock_inertia,
        ):
            mock_user_cls.find = AsyncMock(return_value=mock_user)
            mock_inertia.render.return_value = MagicMock(status_code=200)

            client.get(
                "/profile",
                cookies={"session": _fake_session(user_id=1)},
            )

        props = mock_inertia.render.call_args[0][1]["user"]
        assert props["photo"] == "/images/photos/abc123.png"


# ---------------------------------------------------------------------------
# update endpoint tests
# ---------------------------------------------------------------------------

class TestUpdateEndpoint:
    def test_redirects_unauthenticated_to_login(self, client):
        response = client.post("/profile", data={}, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"

    def test_updates_user_fields(self, client):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.update = AsyncMock()

        with (
            patch("app.http.controllers.profile_controller.User") as mock_user_cls,
            patch("app.http.controllers.profile_controller.save_photo", new=AsyncMock(return_value=None)),
        ):
            mock_user_cls.find = AsyncMock(return_value=mock_user)

            client.post(
                "/profile",
                data={
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "email": "alice@example.com",
                    "password": "",
                },
                cookies={"session": _fake_session(user_id=1)},
                follow_redirects=False,
            )

        update_data = mock_user.update.call_args[0][0]
        assert update_data["first_name"] == "Alice"
        assert update_data["last_name"] == "Smith"
        assert update_data["email"] == "alice@example.com"
        assert "password" not in update_data

    def test_updates_password_when_provided(self, client):
        mock_user = MagicMock()
        mock_user.update = AsyncMock()

        with (
            patch("app.http.controllers.profile_controller.User") as mock_user_cls,
            patch("app.http.controllers.profile_controller.save_photo", new=AsyncMock(return_value=None)),
        ):
            mock_user_cls.find = AsyncMock(return_value=mock_user)

            client.post(
                "/profile",
                data={
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "email": "alice@example.com",
                    "password": "newpassword",
                },
                cookies={"session": _fake_session(user_id=1)},
                follow_redirects=False,
            )

        update_data = mock_user.update.call_args[0][0]
        assert update_data["password"] == "newpassword"

    def test_updates_photo_when_uploaded(self, client):
        mock_user = MagicMock()
        mock_user.update = AsyncMock()

        with (
            patch("app.http.controllers.profile_controller.User") as mock_user_cls,
            patch(
                "app.http.controllers.profile_controller.save_photo",
                new=AsyncMock(return_value="photos/abc123.png"),
            ),
        ):
            mock_user_cls.find = AsyncMock(return_value=mock_user)

            client.post(
                "/profile",
                data={
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "email": "alice@example.com",
                    "password": "",
                },
                cookies={"session": _fake_session(user_id=1)},
                follow_redirects=False,
            )

        update_data = mock_user.update.call_args[0][0]
        assert update_data["photo_path"] == "photos/abc123.png"

    def test_redirects_to_profile_after_update(self, client):
        mock_user = MagicMock()
        mock_user.update = AsyncMock()

        with (
            patch("app.http.controllers.profile_controller.User") as mock_user_cls,
            patch("app.http.controllers.profile_controller.save_photo", new=AsyncMock(return_value=None)),
        ):
            mock_user_cls.find = AsyncMock(return_value=mock_user)

            response = client.post(
                "/profile",
                data={
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "email": "alice@example.com",
                    "password": "",
                },
                cookies={"session": _fake_session(user_id=1)},
                follow_redirects=False,
            )

        assert response.status_code == 303
        assert response.headers["location"] == "/profile"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_session(user_id: int) -> str:
    """Build a signed session cookie that AuthMiddleware will accept."""
    import itsdangerous
    signer = itsdangerous.TimestampSigner("...")
    import json, base64
    payload = base64.b64encode(json.dumps({"user": {"id": user_id}}).encode()).decode()
    return signer.sign(payload).decode()
