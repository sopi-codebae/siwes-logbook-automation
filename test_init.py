import sys
import traceback
from pathlib import Path

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

print("Step 1: Importing User models...")
try:
    from app.domain.models.user import User, StudentProfile, SupervisorProfile
    print("✅ User models imported")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Importing init_db...")
try:
    from app.infrastructure.database.connection import init_db
    print("✅ init_db imported")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Calling init_db()...")
try:
    init_db()
    print("✅ init_db() completed successfully!")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅✅✅ ALL STEPS PASSED!")
