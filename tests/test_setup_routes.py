# tests/test_setup_routes.py
from unittest.mock import patch, MagicMock

from API.routes import create_setup, check_ammo


def test_check_ammo(mock_db, test_ammo):
    existing_ammo = MagicMock()
    existing_ammo.name = "Test Ammo"

    # Case 1: Ammo exists
    mock_db.query.return_value.filter.return_value.first.return_value = test_ammo
    result = check_ammo(existing_ammo, mock_db)
    assert result == test_ammo.id

    # Case 2: Ammo doesn't exist, need to create it
    mock_db.query.return_value.filter.return_value.first.side_effect = [None, test_ammo]
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    with patch("API.routes.Ammo") as MockAmmo:
        MockAmmo.return_value = test_ammo
        result = check_ammo(existing_ammo, mock_db)
        assert result == test_ammo.id
        mock_db.add.assert_called_once_with(test_ammo)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(test_ammo)


def test_create_setup(mock_db, test_ammo):
    setup_data = MagicMock()
    setup_data.name = "Test Setup"
    setup_data.gear = "Test Gear"
    setup_data.ammo = "Test Ammo"
    setup_data.position = "Standing"
    setup_data.drills = "Basic"

    user = {"sub": "1"}

    mock_setup = MagicMock()
    mock_setup.id = 1
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    with (
        patch("API.routes.check_ammo", return_value=test_ammo.id) as mock_check_ammo,
        patch("API.routes.Setup") as MockSetup,
    ):
        MockSetup.return_value = mock_setup

        result = create_setup(setup_data, user, mock_db)

        MockSetup.assert_called_once_with(
            user_id="1",
            name="Test Setup",
            gear="Test Gear",
            ammo=test_ammo.id,
            position="Standing",
            drills="Basic",
        )
        mock_db.add.assert_called_once_with(mock_setup)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_setup)
        assert result == mock_setup
