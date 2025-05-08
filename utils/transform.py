import pandas as pd
import numpy as np
import re

def transform_to_DataFrame(data):
    try:
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error saat mengubah data ke DataFrame: {e}")
        return pd.DataFrame()  # Return DataFrame kosong sebagai fallback

def clean_price(price_str):
    try:
        # Hapus simbol $ dan koma, lalu konversi ke float
        cleaned = re.sub(r'[\$,]', '', str(price_str))
        return float(cleaned)
    except (ValueError, TypeError) as e:
        print(f"Error saat membersihkan harga '{price_str}': {e}")
        return np.nan

def extract_rating(rating_str):
    try:
        match = re.search(r'(\d+\.\d)', str(rating_str))
        if match:
            return float(match.group(1))
        return np.nan
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error saat mengekstrak rating '{rating_str}': {e}")
        return np.nan

def extract_colors(colors_str):
    try:
        match = re.search(r'(\d+)', str(colors_str))
        if match:
            return int(match.group(1))
        return 0
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error saat mengekstrak colors '{colors_str}': {e}")
        return 0

def transform_data(data, exchange_rate=16000):
    try:
        #menghindari SettingWithCopyWarning
        df = data.copy()
        
        # Menghapus baris duplikat
        df_clean = df.drop_duplicates()
        print(f"Menghapus {len(df) - len(df_clean)} baris duplikat")
        df = df_clean
        
        # Filter data dengan judul tidak valid
        valid_title_mask = df['Title'] != 'Unknown Product'
        df_clean = df[valid_title_mask]
        print(f"Menghapus {len(df) - len(df_clean)} baris dengan judul tidak valid")
        df = df_clean
        
        # Transformasi kolom Price
        df['Price'] = df['Price'].replace(['Price Not Found', 'Price Unavailable'], np.nan)
        
        # Konversi Price ke float dan kali dengan exchange rate
        df['Price'] = df['Price'].apply(clean_price) * exchange_rate
        
        # Hapus baris dengan Price yang tidak valid (NaN)
        before_len = len(df)
        df = df.dropna(subset=['Price'])
        print(f"Menghapus {before_len - len(df)} baris dengan harga tidak valid")
        

        df['Rating'] = df['Rating'].apply(extract_rating)
        df['Colors'] = df['Colors'].apply(extract_colors)
        df['Size'] = df['Size'].str.replace('Size:', '').str.strip()
        df['Gender'] = df['Gender'].str.replace('Gender:', '').str.strip()
        for col in ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'Timestamp']:
            if df[col].isnull().any():
                print(f"Peringatan: Masih ada nilai null di kolom {col}")
        
        # Validasi tipe data
        df['Title'] = df['Title'].astype(str)
        df['Price'] = df['Price'].astype(float)
        df['Rating'] = df['Rating'].astype(float)
        df['Colors'] = df['Colors'].astype(int)
        df['Size'] = df['Size'].astype(str)
        df['Gender'] = df['Gender'].astype(str)
        df['Timestamp'] = df['Timestamp'].astype(str)
        
        print(f"Transformasi selesai. Hasil: {len(df)} baris data bersih.")
        return df
        
    except Exception as e:
        print(f"Error saat melakukan transformasi data: {e}")
        # Return data asli sebagai fallback
        return data