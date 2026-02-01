import sys
from pathlib import Path

# Setup path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from app.infrastructure.database.connection import engine
from app.domain.models.base import Base
# Import all models to ensure metadata is populated
from app.domain.models import * 
from seed_db import seed_data

def reset():
    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped.")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return

    print("Re-seeding database...")
    try:
        seed_data()
        print("✅ Reset complete!")
    except Exception as e:
        print(f"❌ Error during reset: {e}")

if __name__ == "__main__":
    reset()
