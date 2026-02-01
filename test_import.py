import sys
import traceback
from pathlib import Path

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

print("Attempting to import User...")
try:
    from app.domain.models.user import User, StudentProfile, SupervisorProfile
    print("✅ Import successful!")
    print(f"User module: {User.__module__}")
    print(f"User has student_profile: {hasattr(User, 'student_profile')}")
    if hasattr(User, 'student_profile'):
        print(f"  Type: {type(getattr(User, 'student_profile'))}")
except Exception as e:
    print("❌ Import FAILED!")
    print(f"Error: {e}")
    traceback.print_exc()
