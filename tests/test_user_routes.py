# tests/test_user_routes.py
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
import io

from API.routes import create_user, upload_image


def test_create_user(mock_db):
    user_data = MagicMock()
    user_data.email = "new@example.com"
    user_data.username = "newuser"
    user_data.password = "newpassword"

    mock_user = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    with (
        patch("API.routes.User") as MockUser,
        patch("API.routes.get_password_hash", return_value="hashed_password"),
    ):
        MockUser.return_value = mock_user

        result = create_user(user_data, mock_db)

        MockUser.assert_called_once_with(
            email="new@example.com", username="newuser", password_hash="hashed_password"
        )
        mock_db.add.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)
        assert result == mock_user


def test_upload_image(mock_db):
    # Create a mock file for testing
    content = b"test image content"
    file = MagicMock(spec=UploadFile)
    file.filename = "test.jpg"
    file.file = io.BytesIO(content)

    setup_id = 1
    seance_id = 1
    user = {"sub": "1"}

    mock_image = MagicMock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    with (
        patch("API.routes.Image") as MockImage,
        patch("builtins.open", MagicMock()),
        patch("shutil.copyfileobj") as mock_copy,
    ):
        MockImage.return_value = mock_image

        result = upload_image(setup_id, seance_id, file, user, mock_db)

        MockImage.assert_called_once()
        mock_copy.assert_called_once()
        mock_db.add.assert_called_once_with(mock_image)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_image)
        assert result == mock_image
