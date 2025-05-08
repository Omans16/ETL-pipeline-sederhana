import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import transform

def test_transform_to_DataFrame():
    """Test konversi dari list of dict ke DataFrame."""
    input_data = [
        {"Title": "Shirt", "Price": "$20", "Rating": "4.3", "Colors": "3", "Size": "L", "Gender": "Men", "Timestamp": "2024-05-01T12:00:00"}
    ]
    df = transform.transform_to_DataFrame(input_data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape == (1, 7)
    assert list(df.columns) == ["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"]

def test_transform_to_DataFrame_error():
    """Test penanganan error pada transform_to_DataFrame."""
    with patch('pandas.DataFrame', side_effect=Exception("Conversion error")):
        df = transform.transform_to_DataFrame([{"test": "data"}])
        assert isinstance(df, pd.DataFrame)
        assert df.empty

def test_clean_price():
    """Test fungsi clean_price dengan berbagai format harga."""
    assert transform.clean_price("$99.99") == 99.99
    assert transform.clean_price("$1,234.56") == 1234.56
    assert transform.clean_price("$0") == 0.0
    assert np.isnan(transform.clean_price("Not a price"))
    assert np.isnan(transform.clean_price(None))

def test_extract_rating():
    """Test fungsi extract_rating dengan berbagai format rating."""
    assert transform.extract_rating("⭐4.5/5") == 4.5
    assert transform.extract_rating("Rating: ⭐3.7/5") == 3.7
    assert transform.extract_rating("4.0 / 5") == 4.0
    assert np.isnan(transform.extract_rating("No rating"))
    assert np.isnan(transform.extract_rating(None))

def test_extract_colors():
    """Test fungsi extract_colors dengan berbagai format jumlah warna."""
    assert transform.extract_colors("3 Colors") == 3
    assert transform.extract_colors("Colors: 5") == 5
    assert transform.extract_colors("1") == 1
    assert transform.extract_colors("No colors") == 0
    assert transform.extract_colors(None) == 0

def test_transform_data_cleaning_and_conversion():
    """Test fungsi transform_data untuk pembersihan dan konversi data."""
    raw_data = pd.DataFrame([
        {
            "Title": "Hoodie 1",
            "Price": "$50",
            "Rating": "⭐4.5/5",
            "Colors": "3 Colors",
            "Size": "M",
            "Gender": "Unisex",
            "Timestamp": "2025-05-02T17:12:32.329018"
        },
        {
            "Title": "Hoodie 1",  # Duplikat
            "Price": "$50",
            "Rating": "⭐4.5/5",
            "Colors": "3 Colors",
            "Size": "M",
            "Gender": "Unisex",
            "Timestamp": "2025-05-02T17:12:32.329018"
        },
        {
            "Title": "Unknown Product",  # Harus dihapus
            "Price": "$99",
            "Rating": "⭐4.2/5",
            "Colors": "2 Colors",
            "Size": "L",
            "Gender": "Men",
            "Timestamp": "2025-05-02T17:12:32.329018"
        },
        {
            "Title": "Pants",
            "Price": "Price Unavailable",  # Harus dihapus
            "Rating": "⭐3.8/5",
            "Colors": "1 Colors",
            "Size": "S",
            "Gender": "Women",
            "Timestamp": "2025-05-02T17:12:32.329018"
        }
    ])
    
    exchange_rate = 16000
    
    cleaned = transform.transform_data(raw_data, exchange_rate)
    
    # Hanya 1 baris valid yang tersisa
    assert len(cleaned) == 1
    row = cleaned.iloc[0]
    assert row['Title'] == "Hoodie 1"
    assert isinstance(row['Price'], float)
    assert row['Price'] == 50 * 16000
    assert row['Rating'] == 4.5
    assert row['Colors'] == 3
    assert row['Gender'] == "Unisex"

def test_transform_data_types():
    """Test tipe data output dari transform_data."""
    data = pd.DataFrame([
        {
            "Title": "T-shirt",
            "Price": "$25",
            "Rating": "⭐4.0/5",
            "Colors": "2 Colors",
            "Size": "L",
            "Gender": "Men",
            "Timestamp": "2025-05-02T17:12:32.329018"
        }
    ])
    
    transformed = transform.transform_data(data)
    
    # Verifikasi tipe data
    assert transformed['Title'].dtype == 'object'  # string/object
    assert transformed['Price'].dtype == 'float64'
    assert transformed['Rating'].dtype == 'float64'
    assert transformed['Colors'].dtype == 'int64'
    assert transformed['Size'].dtype == 'object'  # string/object
    assert transformed['Gender'].dtype == 'object'  # string/object
    assert transformed['Timestamp'].dtype == 'object'  # string/object

def test_transform_data_error_handling():
    """Test penanganan error pada transform_data."""
    data = pd.DataFrame([{"Title": "Test", "Price": "$10"}])
    
    # Simulasi error saat transformasi
    with patch('pandas.DataFrame.copy', side_effect=Exception("Transformation error")):
        result = transform.transform_data(data)
        # Harus mengembalikan data asli jika terjadi error
        assert result.equals(data)

def test_transform_data_comprehensive():
    """Test komprehensif untuk transform_data dengan semua kasus."""
    raw_data = pd.DataFrame([
        # Data valid
        {
            "Title": "Product 1", 
            "Price": "$100", 
            "Rating": "⭐4.8/5", 
            "Colors": "5 Colors", 
            "Size": "XL", 
            "Gender": "Men", 
            "Timestamp": "2025-05-01"
        },
        # Data valid 2
        {
            "Title": "Product 2", 
            "Price": "$75.50", 
            "Rating": "⭐3.9/5", 
            "Colors": "2 Colors", 
            "Size": "S", 
            "Gender": "Women", 
            "Timestamp": "2025-05-01"
        },
        # Harga invalid
        {
            "Title": "Product 3", 
            "Price": "Price Not Found", 
            "Rating": "⭐4.5/5", 
            "Colors": "3 Colors", 
            "Size": "M", 
            "Gender": "Unisex", 
            "Timestamp": "2025-05-01"
        },
        # Rating invalid
        {
            "Title": "Product 4", 
            "Price": "$120", 
            "Rating": "Invalid Rating", 
            "Colors": "1 Colors", 
            "Size": "L", 
            "Gender": "Men", 
            "Timestamp": "2025-05-01"
        }
    ])
    
    exchange_rate = 16000
    transformed = transform.transform_data(raw_data, exchange_rate)
    
    # Harusnya hanya 2 data valid yang tersisa
    assert len(transformed) == 2
    
    # Verifikasi data pertama
    assert transformed.iloc[0]['Title'] == "Product 1"
    assert transformed.iloc[0]['Price'] == 100 * exchange_rate
    assert transformed.iloc[0]['Rating'] == 4