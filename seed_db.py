import sys
import os
import traceback
from pathlib import Path
from urllib.parse import urlparse
from datetime import date

# Setup path to import app modules
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Try importing psycopg2
try:
    import psycopg2
except ImportError:
    psycopg2 = None

from app.infrastructure.database.connection import get_db_session, init_db
from app.domain.models.user import User, UserRole, StudentProfile, SupervisorProfile
from app.infrastructure.security.password import hash_password
from app.config import get_settings

def check_postgres_connection():
    settings = get_settings()
    url = settings.db_url
    print(f"Target DB URL: {url.split('@')[-1]}") # Hide password
    
    if 'sqlite' in url:
        print("Using SQLite.")
        return

    if not psycopg2:
        print("WARNING: psycopg2 not installed.")
        return
        
    print("Testing raw Postgres connection...")
    try:
        # Parse URL
        result = urlparse(url)
        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        conn.close()
        print("✅ Postgres connection successful!")
    except Exception as e:
        print("❌ Postgres connection FAILED:")
        print(e)
        raise

def seed_data():
    try:
        check_postgres_connection()
    except:
        return

    print("Checking for duplicate User modules...")
    user_modules = [m for m in sys.modules.keys() if 'domain.models.user' in m]
    print(f"User modules loaded: {user_modules}")
    
    print("Inspecting User class internals...")
    print(f"User module: {User.__module__}")
    print(f"User class keys: {[k for k in User.__dict__.keys() if not k.startswith('_')]}")

    print("Initializing ORM/Tables (init_db)...")
    try:
        init_db()
        print("✅ init_db() success.")
    except Exception:
        print("❌ init_db() FAILED:")
        traceback.print_exc()
        return

    print("Starting seed transaction...")
    db = get_db_session()
    try:
        # Check if users exist
        try:
            user_count = db.query(User).count()
            if user_count > 0:
                print(f"Users already exist ({user_count}). Skipping seed.")
                return
        except Exception as e:
             print(f"Error querying users: {e}")
             # might be operational error if tables don't exist?
             pass

        print("Creating users...")
        
        # Create Supervisor
        supervisor_email = "supervisor@example.com"
        supervisor = User(
            email=supervisor_email,
            full_name="Dr. Supervisor",
            password_hash=hash_password("password"),
            role=UserRole.SUPERVISOR,
            is_active=True
        )
        db.add(supervisor)
        db.flush()
        
        supervisor_profile = SupervisorProfile(
            user_id=supervisor.id,
            staff_id="SUP/2024/001",
            faculty="Faculty of Physical Sciences"
        )
        db.add(supervisor_profile)
        
        # Create Student
        student_email = "student@example.com"
        student = User(
            email=student_email,
            full_name="John Student",
            password_hash=hash_password("password"),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(student)
        db.flush()
        
        student_profile = StudentProfile(
            user_id=student.id,
            matriculation_number="CSC/2021/1001",
            department="Computer Science",
            institution="University of Technology",
            siwes_start_date=date(2024, 1, 15),
            siwes_end_date=date(2024, 7, 15)
        )
        db.add(student_profile)
        db.flush()

        # Create Geofence first (required for placement)
        from app.domain.models.placement import IndustrialPlacement, Geofence
        import uuid
        
        geofence = Geofence(
            id=str(uuid.uuid4()),
            latitude=6.5244,  # Lagos coordinates
            longitude=3.3792,
            radius_meters=500
        )
        db.add(geofence)
        db.flush()
        print("created geofence")
        
        # Create Placement (only fields that exist in the model)
        placement = IndustrialPlacement(
            id=str(uuid.uuid4()),
            company_name="Tech Solutions Ltd",
            address="123 Innovation Drive, Tech City",
            supervisor_contact="supervisor@techsolutions.com",
            geofence_id=geofence.id
        )
        db.add(placement)
        db.flush()
        print("created placement")
        
        # Link student to placement
        student_profile.placement_id = placement.id
        db.flush()
        print("linked student to placement")
        
        db.commit()
        print("\n✅ Seeding COMPLETE!")
        
    except Exception as e:
        print(f"❌ Seeding FAILED:")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
