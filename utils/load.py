import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import psycopg2
from sqlalchemy import create_engine

def save_to_csv(df, filename="products.csv"):
    """Simpan DataFrame ke file CSV lokal."""
    try:
        df.to_csv(filename, index=False)
        print(f"✅ Data berhasil disimpan ke {filename}")
        return True
    except Exception as e:
        print(f"❌ Gagal menyimpan ke CSV: {e}")
        return False
        
def load_to_gsheet(df, spreadsheet_id, range_name):
    """Kirim DataFrame ke Google Sheets."""
    try:
        creds = Credentials.from_service_account_file(
            'google-sheets-api.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)

        # Siapkan data: header + isinya
        data = [df.columns.tolist()] + df.values.tolist()

        body = {'values': data}
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"✅ {result.get('updatedCells')} sel diperbarui di Google Sheets.")
        return True

    except Exception as e:
        print(f"❌ Gagal mengirim ke Google Sheets: {e}")
        return False
