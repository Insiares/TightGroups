# tests/test_inference.py
from unittest.mock import patch, MagicMock

from API.routes import inference, inference_test


def test_inference(mock_db):
    seance_id = 1
    image_id = 1
    user = {"sub": "1"}

    mock_image = MagicMock()
    mock_image.file_path = "./API/images/test.jpg"

    mock_score = MagicMock()
    mock_score.id = 1

    mock_db.query.return_value.filter.return_value.first.return_value = mock_image
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Mock the predict_groupsize function
    with (
        patch("API.routes.predict_groupsize", return_value=5) as mock_predict,
        patch("API.routes.Score") as MockScore,
        patch("os.path.dirname", return_value="/test/dir"),
    ):
        MockScore.return_value = mock_score

        result = inference(seance_id, image_id, user, mock_db)

        assert result == 5
        mock_db.query.assert_called_once()
        mock_predict.assert_called_once()
        mock_db.add.assert_called_once_with(mock_score)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_score)


def test_inference_test(mock_db):
    with (
        patch("API.routes.predict_groupsize", return_value=3) as mock_predict,
        patch("os.path.dirname", return_value="/test/dir"),
    ):
        result = inference_test()

        assert result == 3
        mock_predict.assert_called_once()
