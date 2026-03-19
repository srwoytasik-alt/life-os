# config.py

import os

class Config:
    # Try multiple environment variable names
    database_url = (
        os.environ.get('SUPABASE_DATABASE_URL') or 
        os.environ.get('DATABASE_URL') or 
        None
    )
    
    # Handle Render's postgres:// vs postgresql:// difference
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # THIS MUST BE SET - no fallback to SQLite for production
    SQLALCHEMY_DATABASE_URI = database_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Base engine options (will be overridden in app.py based on database type)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }