import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./worldcup.db")
SQLALCHEMY_DATABASE_URL = DATABASE_URL

connect_args = {"check_same_thread": False}
poolclass = None
if "memory" in DATABASE_URL:
    poolclass = StaticPool

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args, poolclass=poolclass
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()