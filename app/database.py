import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cp_user:secret123@localhost:5432/codigos_postales"
)

engine = create_engine(DATABASE_URL, connect_args={} if "postgresql" in DATABASE_URL else {"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
