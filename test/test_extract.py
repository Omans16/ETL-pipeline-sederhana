import sys
import os
import pytest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import extract

@patch("utils.extract.requests.Session")
def test_fetching_content_success(mock_session):
    """Test fungsi fetching_content ketika request berhasil."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body>Test</body></html>"
    mock_session.return_value.get.return_value = mock_response

    url = "https://example.com"
    result = extract.fetching_content(url)

    assert result == b"<html><body>Test</body></html>"

@patch("utils.extract.requests.Session")
def test_fetching_content_error(mock_session):
    """Test fungsi fetching_content ketika terjadi error."""
    # Setup mock response untuk error
    mock_session.return_value.get.side_effect = Exception("Connection error")

    url = "https://example.com"
    result = extract.fetching_content(url)

    assert result is None

def test_extract_product_data_complete():
    """Test fungsi extract_product_data dengan data lengkap."""
    html = '''
    <div class="collection-card">
        <h3 class="product-title">Test Jacket</h3>
        <span class="price">$99</span>
        <p style="font-size: 14px;">Rating: ⭐4.5/5</p>
        <p style="font-size: 14px;">Colors: 3 Colors</p>
        <p style="font-size: 14px;">Size: M</p>
        <p style="font-size: 14px;">Gender: Unisex</p>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    card = soup.find("div", class_="collection-card")
    result = extract.extract_product_data(card)

    assert result["Title"] == "Test Jacket"
    assert result["Price"] == "$99"
    assert result["Rating"] == "⭐4.5/5"
    assert result["Colors"] == "3 Colors"
    assert result["Size"] == "M"
    assert result["Gender"] == "Unisex"
    assert "Timestamp" in result

def test_extract_product_data_missing_elements():
    """Test fungsi extract_product_data dengan beberapa data hilang."""
    html = '''
    <div class="collection-card">
        <h3 class="product-title">Test Product</h3>
        <span class="price">$129</span>
        <!-- Missing rating, colors, size, gender -->
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    card = soup.find("div", class_="collection-card")
    result = extract.extract_product_data(card)

    assert result["Title"] == "Test Product"
    assert result["Price"] == "$129"
    assert result["Rating"] == "-"
    assert result["Colors"] == "-"
    assert result["Size"] == "-"
    assert result["Gender"] == "-"
    assert "Timestamp" in result

def test_extract_product_data_error_handling():
    """Test error handling dalam fungsi extract_product_data."""
    # Passing invalid card element
    with patch("bs4.element.Tag.find", side_effect=Exception("Parsing error")):
        result = extract.extract_product_data(Mock())
        assert result["Title"] == "Error"
        assert "Timestamp" in result

@patch("utils.extract.fetching_content")
def test_scrape_fashion_studio_one_page(mock_fetching):
    """Test fungsi scrape_fashion_studio dengan satu halaman."""
    # Simulasi halaman 1: ada 1 produk + tombol next
    html_page_1 = '''
    <div class="collection-card">
        <h3 class="product-title">Item 1</h3>
        <span class="price">$100</span>
        <p style="font-size: 14px;">Rating: ⭐4/5</p>
        <p style="font-size: 14px;">Colors: 3 Colors</p>
        <p style="font-size: 14px;">Size: L</p>
        <p style="font-size: 14px;">Gender: Male</p>
    </div>
    <li class="page-item next"></li>
    '''

    # Simulasi halaman 2: tidak ada produk dan tidak ada tombol next
    html_page_2 = '''
    <p>Tidak ada produk</p>
    '''

    # Atur return value agar mock_fetching mengembalikan dua halaman berturut-turut
    mock_fetching.side_effect = [html_page_1.encode("utf-8"), html_page_2.encode("utf-8")]

    result = extract.scrape_fashion_studio("https://dummy.com", start_page=1, delay=0)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["Title"] == "Item 1"
    assert result[0]["Price"] == "$100"
    assert result[0]["Colors"] == "3 Colors"
    assert len(result) == 1  # Memastikan hanya satu produk yang diambil

@patch("utils.extract.fetching_content")
def test_scrape_fashion_studio_multiple_pages(mock_fetching):
    """Test fungsi scrape_fashion_studio dengan beberapa halaman."""

    html_page_1 = '''
    <div class="collection-card">
        <h3 class="product-title">Item 1</h3>
        <span class="price">$100</span>
        <p style="font-size: 14px;">Rating: ⭐4/5</p>
        <p style="font-size: 14px;">Colors: 3 Colors</p>
        <p style="font-size: 14px;">Size: L</p>
        <p style="font-size: 14px;">Gender: Male</p>
    </div>
    <li class="page-item next"></li>
    '''

    html_page_2 = '''
    <div class="collection-card">
        <h3 class="product-title">Item 2</h3>
        <span class="price">$200</span>
        <p style="font-size: 14px;">Rating: ⭐4.5/5</p>
        <p style="font-size: 14px;">Colors: 2 Colors</p>
        <p style="font-size: 14px;">Size: M</p>
        <p style="font-size: 14px;">Gender: Female</p>
    </div>
    <li class="page-item next"></li>
    '''

    html_page_3 = '''
    <div class="collection-card">
        <h3 class="product-title">Item 3</h3>
        <span class="price">$300</span>
        <p style="font-size: 14px;">Rating: ⭐5/5</p>
        <p style="font-size: 14px;">Colors: 1 Colors</p>
        <p style="font-size: 14px;">Size: S</p>
        <p style="font-size: 14px;">Gender: Unisex</p>
    </div>
    '''

    # Atur return value untuk tiga halaman
    mock_fetching.side_effect = [
        html_page_1.encode("utf-8"), 
        html_page_2.encode("utf-8"),
        html_page_3.encode("utf-8")
    ]

    result = extract.scrape_fashion_studio("https://dummy.com", start_page=1, delay=0, max_pages=3)

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["Title"] == "Item 1"
    assert result[1]["Title"] == "Item 2"
    assert result[2]["Title"] == "Item 3"

@patch("utils.extract.fetching_content")
def test_scrape_fashion_studio_error_handling(mock_fetching):
    """Test error handling dalam fungsi scrape_fashion_studio."""
    # Simulasi error pada fetching
    mock_fetching.side_effect = Exception("Network error")
    
    # Memastikan fungsi tidak crash dan mengembalikan list kosong
    result = extract.scrape_fashion_studio("https://dummy.com", delay=0)
    assert isinstance(result, list)
    assert len(result) == 0

if __name__ == "__main__":
    # Contoh penggunaan fungsi scrape_fashion_studio
    data = extract.scrape_fashion_studio("https://fashion-studio.dicoding.dev/", start_page=1, delay=1)
    print(f"Total produk yang berhasil di-scrape: {len(data)}")
    if data:
        print("Contoh data produk pertama:")
        for key, value in data[0].items():
            print(f"{key}: {value}")