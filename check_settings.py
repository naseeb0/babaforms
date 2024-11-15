# Create a file called check_settings.py
import os
from dotenv import load_dotenv

def check_settings():
    load_dotenv()
    
    print("\nCurrent Environment Settings:")
    print("-" * 30)
    print(f"DJANGO_ENVIRONMENT: {os.getenv('DJANGO_ENVIRONMENT', 'Not set')}")
    print(f"DEBUG: {os.getenv('DEBUG', 'Not set')}")
    print(f"DB settings present: {any(key.startswith('DB_') for key in os.environ)}")
    
    if os.getenv('DJANGO_ENVIRONMENT') != 'development':
        print("\n⚠️  Warning: Not using development environment!")
        print("Make sure your .env file has: DJANGO_ENVIRONMENT=development")

if __name__ == "__main__":
    check_settings()