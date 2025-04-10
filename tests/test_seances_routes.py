# tests/test_seance_routes.py
import pytest
from unittest.mock import patch, MagicMock
from API.Database.Models import Seance
from API.routes import create_seance, get_seances

def test_create_seance(mock_db):
    seance_data = MagicMock()
    seance_data.temp_C = 20.0
    seance_data.wind_speed = 5.0
    seance_data.wind_gust = 10.0
    seance_data.wind_dir = "East"
    seance_data.pressure = 1010.0
    seance_data.precipitation = 0.0
    
    user = {"sub": "1"}
    
    mock_seance = MagicMock()
    mock_seance.id = 1
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    with patch('API.routes.Seance') as MockSeance:
        MockSeance.return_value = mock_seance
        
        result =  create_seance(seance_data, user, mock_db)
        
        MockSeance.assert_called_once_with(
            user_id="1",
            temp_C=20.0,
            wind_speed=5.0,
            wind_gust=10.0,
            wind_dir="East",
            pressure=1010.0,
            precipitation=0.0
        )
        mock_db.add.assert_called_once_with(mock_seance)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_seance)
        assert result == mock_seance

def test_get_seances(mock_db):
    user = {"sub": "1"}
    
    mock_seances = [MagicMock(), MagicMock()]
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_all = MagicMock(return_value=mock_seances)
    
    mock_query.filter.return_value = mock_filter
    mock_filter.all.return_value = mock_seances
    mock_db.query.return_value = mock_query
    
    result =  get_seances(user, mock_db)
    
    mock_db.query.assert_called_once_with(Seance)
    mock_query.filter.assert_called_once()
    assert result == mock_seances

