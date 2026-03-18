import os

class Config:
    # Use environment variable or default to SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance', 'lifeos.db'))
    
    # If DATABASE_URL starts with postgres://, convert to postgresql:// (for Render compatibility)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite specific optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280
    }