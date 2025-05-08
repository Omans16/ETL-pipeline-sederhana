import os
import logging
from datetime import datetime
from utils.extract import scrape_fashion_studio
from utils.transform import transform_to_DataFrame, transform_data
from utils.load import load_to_gsheet, save_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Fungsi utama untuk scraping, transformasi data, dan penyimpanan hasil ke file CSV dan Google Sheets."""
    try:
        BASE_URL = 'https://fashion-studio.dicoding.dev/'
        SPREADSHEET_ID = '1YQ6ghlMhOt1vE_A5mBLi8fdEk9YcVjj0Sh1mLDmDHUo'  
        RANGE_NAME = 'Sheet1!A1'
        OUTPUT_DIR = 'output'

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        # Nama file output dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(OUTPUT_DIR, f"fashion_products_{timestamp}.csv")
        
        logger.info("Memulai proses scraping dari %s", BASE_URL)
        
        # Menjalankan proses scraping data produk fashion
        all_products_data = scrape_fashion_studio(BASE_URL)
        
        if not all_products_data:
            logger.warning("Tidak ada data yang ditemukan saat scraping.")
            return
            
        logger.info("Berhasil scraping %d produk", len(all_products_data))
        
        # Mengubah hasil scraping menjadi DataFrame
        df = transform_to_DataFrame(all_products_data)
        
        # Menampilkan preview dan tipe data awal
        logger.info("Preview DataFrame Awal:")
        print(df.head())
        print("\nTipe Data Awal:")
        print(df.dtypes)
        
        # Transformasi data
        exchange_rate = 16000 
        logger.info("Melakukan transformasi data dengan nilai tukar $1 = Rp%d", exchange_rate)
        df_clean = transform_data(df, exchange_rate)
        
        # Menampilkan preview dan tipe data setelah transformasi
        logger.info("Preview DataFrame Setelah Transformasi:")
        print(df_clean.head())
        print("\nTipe Data Setelah Transformasi:")
        print(df_clean.dtypes)
        
        # Simpan ke CSV
        logger.info("Menyimpan data ke %s", csv_filename)
        save_to_csv(df_clean, csv_filename)
        logger.info("Data berhasil disimpan ke CSV")
        
        # Kirim ke Google Sheets jika SPREADSHEET_ID valid
        if SPREADSHEET_ID and SPREADSHEET_ID.strip() != ' ':
            logger.info("Mengirim data ke Google Sheets")
            load_to_gsheet(df_clean, SPREADSHEET_ID, RANGE_NAME)
        else:
            logger.warning("SPREADSHEET_ID tidak valid. Data tidak dikirim ke Google Sheets.")
            
        logger.info("Proses selesai dengan sukses!")
        
    except Exception as e:
        logger.error("Terjadi kesalahan dalam proses: %s", str(e), exc_info=True)

if __name__ == "__main__":
    main()