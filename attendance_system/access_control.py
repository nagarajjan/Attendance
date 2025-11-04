# access_control.py

import face_recognition
import numpy as np
import datetime
import sqlite3
import os

DATABASE = 'campus_access.db'

def identify_face_from_capture(image_path):
    """
    Attempts to identify the person in the captured image against DB records.
    Returns (employee_id, status_message)
    """
    captured_image = face_recognition.load_image_file(image_path)
    captured_encodings = face_recognition.face_encodings(captured_image)

    if not captured_encodings:
        log_access(None, "DENIED", "No face detected in capture.")
        return None, "No face detected."
    
    captured_encoding = captured_encodings[0]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, name, photo_encoding FROM Staff")
    employees = cursor.fetchall()
    conn.close()

    for employee in employees:
        known_encoding = np.frombuffer(employee['photo_encoding'], dtype=float) 
        matches = face_recognition.compare_faces([known_encoding], captured_encoding)
        if matches[0]: # Check if the first result is True
            access_granted, name_from_check = is_access_allowed(employee['employee_id'])
            if access_granted:
                 return employee['employee_id'], f"Access GRANTED for {name_from_check}."
            else:
                 return None, f"Access DENIED for {name_from_check} (Time restriction)."
            
    log_access(None, "DENIED", "Face not recognized.")
    return None, "Face not recognized. Visitors must sign in manually."


def is_access_allowed(employee_id):
    """Checks if a specific employee has access right now based on allowed hours."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT allowed_start, allowed_end, name FROM Staff WHERE employee_id = ?", (employee_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        log_access(employee_id, "DENIED", "Unknown employee ID during access check")
        return False, "Unknown Employee"
    
    start_time_str, end_time_str, name = result
    now = datetime.datetime.now().time()
    
    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
    
    if start_time <= now <= end_time:
        return True, name
    else:
        return False, name

def log_access(employee_id, status, reason):
    """Logs the access attempt to the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO AccessLogs (employee_id, timestamp, access_status, reason) VALUES (?, ?, ?, ?)",
                   (employee_id, timestamp, status, reason))
    conn.commit()
    conn.close()
