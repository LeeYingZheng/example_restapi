from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor # reveal col name
import time
from .config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SQLAlchemy connect to postgres db

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
Approach 2: connect to local database directly with psycopg2 db driver. Check commented SQL commands in each functions for 2nd approach.
while True:
    try:
        conn = psycopg2.connect(host='localhost',database='restapi_example',
        user='postgres',password='root', cursor_factory=RealDictCursor)
        cur = conn.cursor()
        logging.info("  ++++ DATABASE CONNECTION SUCCESSFUL ++++    ")
        break

    except Exception as e:
        logging.warning("  ++++ DATABASE CONNECTION FAILURE ++++    ")
        logging.warning("ERROR MSG: " + str(e))
        time.sleep(2)

"""