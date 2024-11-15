# setup_dirs.py
from pathlib import Path

def setup_directories():
    BASE_DIR = Path(__file__).resolve().parent
    
    # Required directories
    directories = [
        BASE_DIR / 'static',
        BASE_DIR / 'staticfiles',
        BASE_DIR / 'credentials',
        BASE_DIR / 'forms' / 'static',
        BASE_DIR / 'logs',
    ]
    
    print("\nSetting up project directories...")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created/Verified directory: {directory}")
    
    print("\nAll directories created successfully!")
    print("\nNext steps:")
    print("1. Place your Google credentials JSON file in:", BASE_DIR / 'credentials' / 'form-service-credentials.json')
    print("2. Run: python manage.py collectstatic")
    print("3. Run: python manage.py runserver")

if __name__ == "__main__":
    setup_directories()