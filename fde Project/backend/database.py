from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database local file banayega 'fde_ops.db' ke naam se
SQLALCHEMY_DATABASE_URL = "sqlite:///./fde_ops.db"

# SQLite ke liye check_same_thread=False zaroori hota hai FastAPI mein
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()