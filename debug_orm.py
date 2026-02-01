from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True)
    
    # Relationships
    student_profile = relationship(
        "StudentProfile",
        uselist=False,
        backref=backref("user", uselist=False)
    )

class StudentProfile(Base):
    __tablename__ = 'student_profiles'
    user_id = Column(String(36), ForeignKey(User.id), primary_key=True)
    
    # No explicit relationship here, relying on backref

if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:')
    try:
        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
