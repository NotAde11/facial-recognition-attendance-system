from itertools import count
import cv2
import os
import streamlit as st
import psycopg2
from datetime import datetime
import pandas as pd
import glob
from sqlalchemy import create_engine, text
import numpy as np
from PIL import Image
import shutil
import pandas as pd
import json
import bcrypt
import time
import warnings


# Define DB params as a constant in the backend
DB_PARAMS = {
    "dbname": "facial_recognition_db", 
    "user": "postgres",
    "password": "Psalm91^&", 
    "host": "localhost", 
    "port": "5433"
}
# Use the credentials you already have
DB_URL = f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"
engine = create_engine(DB_URL)

def run_recognition(cam_index=0):
    # 1. Check for classifier file
    if not os.path.exists("classifier.yml"):
        return "Error: Train AI first."
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("classifier.yml")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    cap = cv2.VideoCapture(cam_index)
    
    if not cap.isOpened():
        return "Error: Could not access the camera."

    total_verifications = 0
    successful_db_writes = 0
    latency_records = {
        "preprocessing": [],
        "detection": [],
        "recognition": [],
        "database": []
    }

    while True:
        frame_start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break 

        t_pre_start = time.time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        latency_records["preprocessing"].append(time.time() - t_pre_start)

        t_det_start = time.time()
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        latency_records["detection"].append(time.time() - t_det_start)
        
        for (x, y, w, h) in faces:
            t_rec_start = time.time()
            id_num, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            latency_records["recognition"].append(time.time() - t_rec_start)
            
            if confidence < 75.5:
                total_verifications += 1
                t_db_start = time.time()
                # We now pass the integer. 
                # Inside log_attendance, we will query: WHERE id LIKE '%22031879'
                display_name = log_attendance(id_num)
                
                latency_records["database"].append(time.time() - t_db_start)
                
                if display_name and display_name != "Error" and display_name != "Unknown":
                    successful_db_writes += 1
                # IMPORTANT: Ensure log_attendance is also in backend.py
                name = display_name 
                color = (0, 255, 0)
            else:
                name = "Unknown"
                color = (0, 0, 255)
                
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, str(name), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        frame_time = time.time() - frame_start
        current_fps = 1.0 / frame_time if frame_time > 0 else 0.0
        
        cv2.putText(frame, f"Live FPS: {current_fps:.1f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        cv2.imshow("Recognition - Press Space Bar to stop", frame)
        
        # Stops the loop if 'q' is pressed in the OpenCV window
        if cv2.waitKey(1) & 0xFF == 32: 
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*50)
    print("      CHAPTER 4: REAL-TIME PERFORMANCE METRICS       ")
    print("="*50)
    
    # Calculate Latency Averages (convert seconds to milliseconds)
    for stage, times in latency_records.items():
        avg_ms = (sum(times) / len(times) * 1000) if times else 0.0
        print(f"Average {stage.capitalize()} Latency : {avg_ms:.2f} ms")
        
    # Calculate Average FPS across all recorded frames
    all_frame_times = latency_records["preprocessing"]
    if all_frame_times:
        avg_fps = len(all_frame_times) / sum(all_frame_times)
        print(f"Average System Throughput       : {avg_fps:.2f} FPS")
        
    # Calculate Database Logging Success Rate
    db_rate = (successful_db_writes / total_verifications * 100) if total_verifications > 0 else 0.0
    print(f"Total Recognition Triggers      : {total_verifications}")
    print(f"Successful DB Writes Verified   : {successful_db_writes}")
    print(f"Database Logging Success Rate   : {db_rate:.2f}%")
    print("="*50 + "\n")
    
    return "Recognition Session Ended"


# Global dictionary to track cooldowns
last_logged = {}

def log_attendance(student_id):
    global last_logged
    now = datetime.now()
    
    # 1. Cooldown Check
    if student_id in last_logged:
        time_diff = (now - last_logged[student_id]).total_seconds()
        if time_diff < 30:
            return last_logged.get(f"{student_id}_name", "Verified")

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. Improved Mapping: 
        # We strip non-digits from the input just in case, then search.
        clean_id = "".join(filter(str.isdigit, str(student_id)))
        
        # This query looks for the Matric No that contains the numeric sequence
        search_term = f"%{clean_id}%"
        cur.execute("SELECT id, name FROM students WHERE id LIKE %s", (search_term,))
        result = cur.fetchone()
        
        # 2. BACKUP: If the LIKE fails, do a manual numeric comparison
        if not result:
            cur.execute("SELECT id, name FROM students")
            all_rows = cur.fetchall()
            for row in all_rows:
                db_id = row[0]
                # Strip letters from DB ID (e.g., '22CG031879' -> '22031879')
                db_numeric = "".join(filter(str.isdigit, db_id))
                if db_numeric == clean_id:
                    result = row
                    break

        if not result:
            cur.close()
            conn.close()
            return "Unknown Matric No."
        
        full_matric_no = result[0]
        name = result[1]
        
        # 4. Record the Attendance
        cur.execute("""
            INSERT INTO daily_attendance (student_id, date, presence, time_marked) 
            VALUES (%s, CURRENT_DATE, 'Present', CURRENT_TIME) 
            ON CONFLICT (student_id, date) 
            DO UPDATE SET presence='Present', time_marked=CURRENT_TIME
        """, (full_matric_no,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Update local tracking
        last_logged[student_id] = now
        last_logged[f"{student_id}_name"] = name
        
        return name
    except Exception as e:
        print(f"DB Error: {e}")
        return "Error"
        

def get_attendance_data():
    try:
        query = """
            SELECT s.id AS "Matric No.", s.name AS "Student Name", 
                   COALESCE(a.presence, 'Absent') AS "Status", 
                   a.time_marked AS "Time Marked"
            FROM students s
            LEFT JOIN daily_attendance a ON s.id = a.student_id 
            WHERE a.date = CURRENT_DATE OR a.date IS NULL
            ORDER BY a.presence DESC, s.id ASC
        """ # (keep your long query here)
        # Use engine.connect() instead of conn
        df = pd.read_sql_query(text(query), engine.connect())
        
        if not df.empty and "Time Marked" in df.columns:
            df["Time Marked"] = df["Time Marked"].apply(
                lambda x: x.strftime("%H:%M:%S") if x else "--:--:--"
            )
        return df
    except Exception as e:
        return f"Error: {str(e)}"
    

DATA_PATH = "data"
NEW_DATA_PATH = os.path.join(DATA_PATH, "new") # Path to data/new

def generate_dataset(s_id, s_name):
    if not s_id or not s_name:
        return "Error: Matric No. and Student Name are required."
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO students (id, name) VALUES (%s, %s) 
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """, (s_id, s_name))
            conn.commit()
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            return "Error: Matric No. must follow format 00XX000000 (e.g., 22CG031879)"
        except Exception as e:
            conn.rollback()
            return f"Error: {str(e)}"
        finally:
            conn.close()

        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        if not os.path.exists(DATA_PATH): 
            os.makedirs(DATA_PATH)
            
        if not os.path.exists(NEW_DATA_PATH): 
            os.makedirs(NEW_DATA_PATH)

        # Clean numeric format extracted safely before tracking loops begin
        numeric_id = "".join(filter(str.isdigit, str(s_id)))
        session_captured = 0

        while True:
            ret, img = cap.read()
            if not ret: break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                session_captured += 1
                
                # Generates a dynamic unique millisecond key suffix preventing overwrites
                stamp = int(time.time() * 1000) + session_captured
                
                cv2.imwrite(f"{NEW_DATA_PATH}/student.{numeric_id}.{stamp}.jpg", gray[y:y+h, x:x+w])
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(img, f"Captured: {session_captured}/100", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
            cv2.imshow("Capturing Images... Press Space Bar to stop", img)
            if cv2.waitKey(1) & 0xFF == 32 or session_captured >= 100: 
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return f"Success: Captured {session_captured} images for {s_name}"
    except Exception as e:
        return f"Error: {str(e)}"

def remove_student(s_id):
    if not s_id:
        return "Error: Provide a Student Matric No."
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. Delete attendance first due to Foreign Key constraints
        cur.execute("DELETE FROM daily_attendance WHERE student_id = %s", (s_id,))
        
        # 2. Delete the student and capture how many rows were affected
        cur.execute("DELETE FROM students WHERE id = %s", (s_id,))
        deleted_count = cur.rowcount 
        
        conn.commit()
        cur.close()
        conn.close()

        # 3. Logic check: If no rows were deleted, the student didn't exist
        if deleted_count == 0:
            return f"Error: Student with Matric No. {s_id} not found."

        # 4. Remove image files (only if the DB delete actually worked)
        files = glob.glob(os.path.join(DATA_PATH, f"student.{s_id}.*.jpg"))
        # We also need to check for the numeric version of the ID if you used that for images
        numeric_id = "".join(filter(str.isdigit, s_id))
        files += glob.glob(os.path.join(DATA_PATH, f"student.{numeric_id}.*.jpg"))
        
        for f in files:
            if os.path.exists(f):
                os.remove(f)
            
        return f"Success: Student {s_id} and associated data removed."
        
    except Exception as e:
        return f"Error: {str(e)}"
    
    
def initialize_attendance():
    try:
        # 1. Define the SQL string first
        query = """
            INSERT INTO daily_attendance (student_id, date, presence) 
            SELECT id, CURRENT_DATE, 'Absent' 
            FROM students 
            ON CONFLICT (student_id, date) DO NOTHING
        """
        
        with engine.begin() as conn:
            # 2. Execute the query
            result = conn.execute(text(query))
            # 3. Get the count of how many rows were actually added
            count = result.rowcount 
        
        if count == 0:
            return "Roster already initialized or no new students to add."
        return f"Success: {count} students added to today's roster as Absent."
        
    except Exception as e:
        return f"Error: {str(e)}"
    

def process_classifier(mode="full"):
    """
    mode='full': Trains on ALL images in 'data'.
    mode='quick': Updates model using images in 'data/new'.
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    DATA_PATH = "data"
    NEW_DATA_PATH = "data/new"
    MODEL_FILE = "classifier.yml"

    # Define which folder to pull training images from
    train_folder = DATA_PATH if mode == "full" else NEW_DATA_PATH
    
    if not os.path.exists(train_folder):
        return f"Error: Folder {train_folder} does not exist."

    image_paths = [os.path.join(train_folder, f) for f in os.listdir(train_folder) if f.endswith('.jpg')]
    
    if not image_paths:
        return f"Error: No images found in {train_folder}."

    faces = []
    ids = []

    try:
        for image_path in image_paths:
            filename = os.path.basename(image_path)
            
            # 1. Skip files that don't match the student pattern
            if not filename.startswith("student."):
                continue
                
            parts = filename.split(".")
            # Expected pattern: student.123456.1.jpg (at least 3 parts before .jpg)
            if len(parts) < 3:
                continue
            
            # 2. Extract numeric ID safely
            # This strips letters from "22CG031879" to get "22031879"
            raw_id = parts[1]
            numeric_id_str = "".join(filter(str.isdigit, raw_id))
            
            # 3. If numeric_id_str is empty (the '' error), skip this file
            if not numeric_id_str:
                print(f"Skipping invalid file: {filename}")
                continue
                
            s_id = int(numeric_id_str)

            # 4. Open and process image
            img = Image.open(image_path).convert('L') 
            image_np = np.array(img, 'uint8')
            
            faces.append(image_np)
            ids.append(s_id)

        if not faces:
            return "Error: No valid student images were found to train on."

        # TRAINING LOGIC
        if mode == "full":
            recognizer.train(faces, np.array(ids))
        else:
            if not os.path.exists(MODEL_FILE):
                return "Error: No existing model found. Run 'Full Retrain' first."
            recognizer.read(MODEL_FILE)
            recognizer.update(faces, np.array(ids))

        recognizer.save(MODEL_FILE)

        # FILE MANAGEMENT: Move files from 'new' to 'data' after training
        if mode == "quick" or (mode == "full" and os.path.exists(NEW_DATA_PATH)):
            new_images = [f for f in os.listdir(NEW_DATA_PATH) if f.endswith('.jpg')]
            for f in new_images:
                shutil.move(os.path.join(NEW_DATA_PATH, f), os.path.join(DATA_PATH, f))

        return f"Success: {mode.capitalize()} training complete."

    except Exception as e:
        return f"Error: {str(e)}"
    

def get_image_stats():
    DATA_PATH = "data"
    NEW_DATA_PATH = "data/new"
    
    stats = {
        "total_data": 0,
        "total_new": 0,
        "person_counts": {}
    }

    try:
        # 1. Basic counts
        if os.path.exists(DATA_PATH):
            stats["total_data"] = len([f for f in os.listdir(DATA_PATH) if f.endswith('.jpg')])
        if os.path.exists(NEW_DATA_PATH):
            stats["total_new"] = len([f for f in os.listdir(NEW_DATA_PATH) if f.endswith('.jpg')])

        # 2. Get all registered students from DB
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name FROM students"))
            # student_map = { "22031879": ("22CG031879", "Ade"), ... }
            student_map = {}
            for row in result:
                m_no = str(row[0])
                s_name = row[1]
                numeric_part = "".join(filter(str.isdigit, m_no))
                student_map[numeric_part] = (m_no, s_name)

        # 3. Count images per person (check both folders)
        all_files = []
        if os.path.exists(DATA_PATH): all_files += os.listdir(DATA_PATH)
        if os.path.exists(NEW_DATA_PATH): all_files += os.listdir(NEW_DATA_PATH)

        for filename in all_files:
            if filename.startswith("student."):
                parts = filename.split(".")
                if len(parts) >= 2:
                    file_id_part = parts[1]
                    # Strip letters just in case the filename has them
                    numeric_key = "".join(filter(str.isdigit, file_id_part))
                    
                    if numeric_key in student_map:
                        full_id, name = student_map[numeric_key]
                        key = f"{name} ({full_id})"
                        stats["person_counts"][key] = stats["person_counts"].get(key, 0) + 1
        
        # 4. Sort the results so they appear in a consistent order
        stats["person_counts"] = dict(sorted(stats["person_counts"].items()))
        
        return stats
    except Exception as e:
        return f"Error: {str(e)}"
    

def delete_json_user(username_to_delete, password_to_verify):
    JSON_FILE = "users.json" # Make sure this matches your actual filename
    
    try:
        # 1. Read the current users
        with open(JSON_FILE, "r") as f:
            users = json.load(f)
        
        user_key = username_to_delete.strip()
        # 2. Check if user exists and delete
        if user_key not in users:
            return "Error: User not found."
        
        hashed_password = users[user_key]
        password_bytes = password_to_verify.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')    
        
        # 3. Verify the password (assuming JSON is {"user": "pass"})
        if bcrypt.checkpw(password_bytes, hashed_bytes):
            del users[user_key]    
            
            with open(JSON_FILE, "w") as f:
                json.dump(users, f, indent=4)
            
            return f"Success: {user_key} deleted."
        else:
            return "Error: Password verification failed."
            
    except FileNotFoundError:
        return "Error: users.json file not found."
    except Exception as e:
        return f"Error: {str(e)}"