from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./domains.db")

# Check if SQLite Cloud is configured and available
def is_sqlitecloud_available():
    """Check if SQLite Cloud package is available"""
    try:
        import sqlalchemy_sqlitecloud
        return True
    except ImportError:
        return False

# Handle SQLite Cloud configuration
if DATABASE_URL.startswith("sqlitecloud://"):
    if not is_sqlitecloud_available():
        print("Warning: SQLite Cloud URL detected but package not available. Falling back to local SQLite.")
        DATABASE_URL = "sqlite:///./domains.db"
    else:
        print("✅ Using SQLite Cloud database")

# SQLAlchemy setup
# Only use check_same_thread for local SQLite, not SQLite Cloud
connect_args = {}
if DATABASE_URL.startswith("sqlite:///"):
    connect_args = {"check_same_thread": False}
    print("✅ Using local SQLite database")

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Databases setup for async operations
# For SQLite Cloud, we need to use a different approach since databases package doesn't support it
if DATABASE_URL.startswith("sqlitecloud://"):
    # For SQLite Cloud, we'll use synchronous operations only
    database = None
    print("ℹ️  SQLite Cloud: Using synchronous database operations")
else:
    database = Database(DATABASE_URL)
    print("ℹ️  Local SQLite: Using asynchronous database operations")

# Base class for models
Base = declarative_base()
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def connect_db():
    """Connect to database"""
    if database:
        await database.connect()
        print("✅ Connected to database")

async def disconnect_db():
    """Disconnect from database"""
    if database:
        await database.disconnect()
        print("✅ Disconnected from database")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified") 