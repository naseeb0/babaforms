# clean_db.py
import os
import shutil
from pathlib import Path

def clean_development():
    BASE_DIR = Path(__file__).resolve().parent
    
    print("\nCleaning development environment...")
    print("-" * 40)
    
    # Remove database
    db_file = BASE_DIR / 'db.sqlite3'
    if db_file.exists():
        os.remove(db_file)
        print("✅ Removed SQLite database")
    
    # Remove all migrations except __init__.py
    for app in ['forms']:
        migrations_dir = BASE_DIR / app / 'migrations'
        if migrations_dir.exists():
            for file in migrations_dir.glob('*.py'):
                if file.name != '__init__.py':
                    os.remove(file)
            print(f"✅ Cleaned migrations for {app}")
    
    # Remove __pycache__
    for root, dirs, files in os.walk(BASE_DIR):
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
    print("✅ Removed __pycache__ directories")
    
    print("\nNow run:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py createsuperuser")

if __name__ == "__main__":
    clean_development()