import sqlite3

def setup_database():
    conn = sqlite3.connect('campus_access.db')
    cursor = conn.cursor()

    # Create staff table with access hours
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Staff (
            id INTEGER PRIMARY KEY,
            employee_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            photo_encoding BLOB, -- For future face recognition encoding
            allowed_start TEXT, -- e.g., "08:00"
            allowed_end TEXT -- e.g., "18:00"
        )
 ''')

    # Create attendance/access logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AccessLogs (
            log_id INTEGER PRIMARY KEY,
            employee_id TEXT,
            timestamp TEXT NOT NULL,
            access_status TEXT NOT NULL, -- e.g., "GRANTED", "DENIED"
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("Database setup�complete.")