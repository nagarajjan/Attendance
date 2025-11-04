from database import get_db
import datetime

def log_attendance_record(employee_id, status, photo_path, visitor_name=None):
    """Logs an attendance event into the database."""
    db = get_db()
    timestamp = datetime.datetime.now().isoformat()
    
    db.execute(
        "INSERT INTO attendance_logs (employee_id, visitor_name, timestamp, status, photo_capture_path) VALUES (?, ?, ?, ?, ?)",
        (employee_id, visitor_name, timestamp, status, photo_path)
    )
    db.commit()
    return True

def get_attendance_history():
    """Retrieves all attendance logs."""
    db = get_db()
    cursor = db.execute("SELECT * FROM attendance_logs ORDER BY timestamp DESC")
    return cursor.fetchall()

def register_employee_with_face(name, photo_path, face_encoding):
    """Registers a new employee, saving their face encoding."""
    db = get_db()
    db.execute(
        "INSERT INTO employees (name, photo_path, face_encoding) VALUES (?, ?, ?)",
        (name, photo_path, face_encoding.tobytes()) # Store encoding as bytes
    )
    db.commit()
    return True
