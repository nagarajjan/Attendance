# app.py

import sys
import os
import base64
import time
import sqlite3 
import face_recognition
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, g, redirect, url_for, flash

# --- System Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# --- Local Module Imports ---
from database import close_db, init_db 
from access_control import identify_face_from_capture 

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key' 

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
DATABASE = 'campus_access.db'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

# --- Flask Lifecycle Management ---
app.teardown_appcontext(close_db)

# --- Routes ---

# 1. Main Attendance Page (Attendance Capture)
@app.route('/')
def index():
    """Serves the main attendance capture page."""
    return render_template('attendance.html')

# 2. Handle Attendance Submission (POST request from attendance.html JS fetch)
@app.route('/log_attendance', methods=['POST'])
def log_attendance():
    """Receives the image data via POST request and processes attendance."""
    data = request.json
    if not data or 'imageData' not in data:
        return {"status": "error", "message": "No image data provided"}, 400

    base64_image = data['imageData']
    header, encoded_data = base64_image.split(',')
    image_bytes = base64.b64decode(encoded_data)

    filename = f"capture_{int(time.time())}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        employee_id, status_msg = identify_face_from_capture(filepath)

        return {"status": "success", "message": status_msg}

    except IOError as e:
        app.logger.error(f"Error saving image: {e}")
        return {"status": "error", "message": "Server error saving image"}, 500

# 3. Staff Registration Form Page (GET request)
@app.route('/register', methods=['GET'])
def register_form():
    """Displays the registration form for new staff."""
    return render_template('register_staff.html')

# 4. Handle Staff Registration Submission (POST request from register_staff.html)
@app.route('/register', methods=['POST'])
def register_staff():
    """Processes the registration form submission, including photo and details."""
    name = request.form['employeeName']
    employee_id = request.form['employeeId']
    email = request.form['email']
    contact_info = request.form['contactInfo']
    dob = request.form['dob']
    allowed_start = request.form['allowedStart']
    allowed_end = request.form['allowedEnd']
    
    # Handle file upload
    if 'employeePhoto' not in request.files:
        flash("No photo part in form.", "error")
        return redirect(url_for('register_form'))
    
    file = request.files['employeePhoto']
    
    if file.filename == '':
        flash("No selected photo.", "error")
        return redirect(url_for('register_form'))

    if file:
        filename = secure_filename(f"{employee_id}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)

            if not encodings:
                os.remove(filepath) 
                flash("No face detected in the uploaded photo. Please use a clearer photo.", "error")
                return redirect(url_for('register_form'))
            
            face_encoding = encodings[0].tobytes() # Use the first encoding found

            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Staff (employee_id, name, email, contact_info, date_of_birth, photo_path, photo_encoding, allowed_start, allowed_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, name, email, contact_info, dob, filename, face_encoding, allowed_start, allowed_end))
            conn.commit()
            conn.close()

            flash(f"Staff member {name} (ID: {employee_id}) registered successfully with photo!", "success")
            return redirect(url_for('staff_list')) 

        except Exception as e:
            app.logger.error(f"Error during face encoding or DB insert: {e}")
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('register_form'))

    return redirect(url_for('register_form'))

# 5. View Staff List Page
@app.route('/list')
def staff_list():
    """Displays a list of all staff members."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Also fetch photo_path to display the image in the list
    cursor.execute("SELECT employee_id, name, photo_path FROM Staff") 
    staff_members = cursor.fetchall()
    conn.close()
    
    return render_template('staff_list.html', staff=staff_members)

# 6. View Access Logs Page
@app.route('/logs')
def access_logs():
    """Displays all access logs."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AccessLogs ORDER BY timestamp DESC LIMIT 100") 
    logs = cursor.fetchall()
    conn.close()
    
    return render_template('access_logs.html', logs=logs)

# --- Main Execution ---
if __name__ == '__main__':
    init_db() 
    app.run(debug=True)
