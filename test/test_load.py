import pandas as pd
import sys
import os
import pytest
from unittest.mock import patch, Mock, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.load import save_to_csv, load_to_gsheet, save_to_postgresql

# Test fungsi save_to_csv()
def test_save_to_csv_success(tmp_path):
    """Test apakah fungsi save_to_csv berhasil menyimpan data ke file CSV."""
    df = pd.DataFrame({'col1': [1], 'col2': ['a']})
    file_path = tmp_path / "test.csv"

    result = save_to_csv(df, file_path) 

    assert file_path.exists()  
    assert result is True  

# Test fungsi save_to_csv dengan error handling
@patch('pandas.DataFrame.to_csv')
def test_save_to_csv_error(mock_to_csv, capsys):
    """Test apakah fungsi save_to_csv menangani error dengan benar."""
    df = pd.DataFrame({'col1': [1], 'col2': ['a']})
    mock_to_csv.side_effect = Exception("Simulated error")
    
    result = save_to_csv(df, "test.csv")
    
    captured = capsys.readouterr()
    assert "❌ Gagal menyimpan ke CSV: Simulated error" in captured.out
    assert result is False  

# Test fungsi load_to_gsheet() jika berhasil
@patch('utils.load.Credentials')
@patch('utils.load.build')
def test_load_to_gsheet_success(mock_build, mock_credentials):
    """Test apakah fungsi load_to_gsheet berhasil mengirim data ke Google Sheets."""
    df = pd.DataFrame({'Name': ['Alice'], 'Age': [30]})
    spreadsheet_id = 'dummy_id'
    range_name = 'Sheet1!A1'

    # Mock objek service
    mock_service = Mock()
    mock_spreadsheets = Mock()
    mock_values = Mock()
    mock_update = Mock()
    mock_execute = Mock(return_value={'updatedCells': 2})


    mock_update.execute = mock_execute
    mock_values.update.return_value = mock_update
    mock_spreadsheets.values.return_value = mock_values
    mock_service.spreadsheets.return_value = mock_spreadsheets
    mock_build.return_value = mock_service

    # Jalankan fungsi
    result = load_to_gsheet(df, spreadsheet_id, range_name)
    mock_values.update.assert_called_once()
    assert result is True  

# Test fungsi load_to_gsheet() jika terjadi error
@patch('utils.load.Credentials')
@patch('utils.load.build')
def test_load_to_gsheet_error(mock_build, mock_credentials, capsys):
    """Test apakah fungsi load_to_gsheet menangani error dengan benar."""
    df = pd.DataFrame({'Name': ['Bob'], 'Age': [25]})
    mock_build.side_effect = Exception("Simulated error")

    result = load_to_gsheet(df, 'dummy_id', 'Sheet1!A1')

    captured = capsys.readouterr()
    assert "❌ Gagal mengirim ke Google Sheets" in captured.out
    assert result is False 