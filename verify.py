# test_sheets.py
import os
import django
from pathlib import Path

def test_sheets_setup():
    print("\nTesting Google Sheets Setup:")
    print("-" * 40)
    
    # Initialize Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formcore.settings')
    django.setup()
    
    from forms.google_sheets import GoogleSheetsManager
    
    # Create manager instance
    manager = GoogleSheetsManager()
    
    # Test connection
    if manager.test_connection():
        print("✅ Successfully connected to Google Sheets")
    else:
        print("❌ Failed to connect to Google Sheets")
        
    # Print settings info
    from django.conf import settings
    print(f"\nCredentials file path: {settings.GOOGLE_SHEETS_CREDENTIALS_FILE}")
    print(f"File exists: {settings.GOOGLE_SHEETS_CREDENTIALS_FILE.exists()}")

if __name__ == "__main__":
    test_sheets_setup()