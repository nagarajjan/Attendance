# database.py

import sqlite3
from flask import g

DATABASE = 'campus_access.db'

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DATES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema using a direct connection (avoids 'g')."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Staff (
            id INTEGER PRIMARY KEY,
            employee_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            contact_info TEXT,
            date_of_birth TEXT, 
            photo_path TEXT,    
            photo_encoding BLOB, 
            allowed_start TEXT, 
            allowed_end TEXT 
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AccessLogs (
            log_id INTEGER PRIMARY KEY,
            employee_id TEXT,
            timestamp TEXT NOT NULL,
            access_status TEXT NOT NULL, 
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()
