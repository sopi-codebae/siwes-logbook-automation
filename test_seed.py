import sys
import traceback
from pathlib import Path
from datetime import date

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from app.infrastructure.database.connection import get_db_session, init_db
from app.domain.models.user import User, UserRole, StudentProfile, SupervisorProfile
from app.infrastructure.security.password import hash_password

print("Step 1: Calling init_db()...")
try:
    init_db()
    print("✅ init_db() completed")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Getting DB session...")
try:
    db = get_db_session()
    print("✅ DB session obtained")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Querying User count...")
try:
    count = db.query(User).count()
    print(f"✅ Query successful, found {count} users")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    db.close()
    sys.exit(1)

print("\nStep 4: Creating supervisor user...")
try:
    supervisor = User(
        email="supervisor@example.com",
        password_hash=hash_password("password"),
        role=UserRole.SUPERVISOR,
        is_active=True
    )
    db.add(supervisor)
    db.flush()
    print(f"✅ Supervisor created with ID: {supervisor.id}")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    db.rollback()
    db.close()
    sys.exit(1)

print("\nStep 5: Creating supervisor profile...")
try:
    supervisor_profile = SupervisorProfile(
        user_id=supervisor.id,
        staff_id="SUP/2024/001",
        faculty="Faculty of Physical Sciences"
    )
    db.add(supervisor_profile)
    db.flush()
    print("✅ Supervisor profile created")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    db.rollback()
    db.close()
    sys.exit(1)

print("\nStep 6: Committing...")
try:
    db.commit()
    print("✅ Committed successfully")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    db.rollback()
    db.close()
    sys.exit(1)

db.close()
print("\n✅✅✅ ALL STEPS PASSED! Database seeded successfully!")
