import time
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    )
}

def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    session = requests.Session()
    try:
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None

def extract_product_data(card):
    """Mengambil informasi produk: title, price, colors, size, gender dari card (elemen html)."""
    try:
        title_element = card.find('h3', class_='product-title')
        title = title_element.text.strip() if title_element else "Title Not Found"
        
        price_element = card.find('span', class_='price') or card.find('p', class_='price')
        price = price_element.text.strip() if price_element else "Price Not Found"
        
        details = card.find_all('p', style=lambda value: value and "font-size" in value)
        
        colors = size = gender = rating = "-"
        
        for detail in details:
            text = detail.text.strip()
            if "Rating:" in text:
                rating = text.replace("Rating:", "").strip()
            elif "Colors" in text:
                colors = text.replace("Colors:", "").strip()
            elif "Size" in text:
                size = text.replace("Size:", "").strip()
            elif "Gender" in text:
                gender = text.replace("Gender:", "").strip()

        # Tambahkan kolom timestamp (saat data diekstrak)
        timestamp = datetime.now().isoformat()

        products = {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "Timestamp": timestamp
        }
        return products
    except Exception as e:
        print(f"Terjadi kesalahan saat mengekstrak data produk: {e}")
        # Return empty product data with timestamp as a failsafe
        return {
            "Title": "Error",
            "Price": "Error",
            "Rating": "Error",
            "Colors": "Error",
            "Size": "Error",
            "Gender": "Error",
            "Timestamp": datetime.now().isoformat()
        }

def scrape_fashion_studio(base_url, start_page=1, delay=2, max_pages=50):
    """Fungsi utama untuk mengambil keseluruhan data produk, mulai dari requests hingga menyimpannya dalam variabel data. """
    data = []
    page_number = start_page
    pages_scraped = 0

    try:
        while pages_scraped < max_pages:
            if page_number == 1:
                url = base_url
            else:
                url = f"{base_url}page{page_number}"
            
            print(f"Scraping halaman: {url}")

            content = fetching_content(url)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                cards_element = soup.find_all('div', class_='collection-card')
                
                if not cards_element:
                    print(f"Tidak ada produk yang ditemukan pada halaman {page_number}")
                    break
                    
                for card in cards_element:
                    product = extract_product_data(card)
                    if product["Title"] != "Error":
                        data.append(product)

                next_button = soup.find('li', class_='page-item next')
                if next_button:
                    page_number += 1 
                    pages_scraped += 1
                    time.sleep(delay)  # Delay sebelum lanjut halaman berikutnya
                else:
                    print("Tidak ada halaman berikutnya. Proses scraping selesai.")
                    break  # Berhenti kalau tidak ada tombol Next
            else:
                print(f"Gagal mengambil konten dari halaman {page_number}")
                break  # Berhenti kalau fetching error
                
        print(f"Proses scraping selesai. Total {len(data)} produk berhasil di-scrape dari {pages_scraped + 1} halaman.")
        return data
        
    except Exception as e:
        print(f"Terjadi kesalahan saat melakukan scraping: {e}")
        return data  # Return data yang sudah dikumpulkan sejauh ini