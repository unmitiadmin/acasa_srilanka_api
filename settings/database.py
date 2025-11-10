from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from . import env

engine = create_engine(env.get("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
