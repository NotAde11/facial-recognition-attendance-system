import cv2
import os
import numpy as np
import psycopg2
import shutil
import glob
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image
from datetime import datetime

class AttendanceSystemMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("Facial Recognition System")
        self.root.geometry("600x700")
        self.root.configure(bg="#f4f7f6")
        
        # Configuration
        self.db_params = {
            "dbname": "facial_recognition_db", "user": "postgres",
            "password": "Psalm91^&", "host": "localhost", "port": "5433"
        }
        self.base_path = "C:/Dev/Facial/data"
        self.new_data_path = "C:/Dev/Facial/data/new"
        self.last_logged = {}

        # Container Frame (Where all views will be placed)
        self.container = tk.Frame(self.root, bg="#f4f7f6")
        self.container.pack(side="top", fill="both", expand=True)

        self.show_main_menu()

    def clear_window(self):
        """Removes everything currently visible in the container."""
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- VIEW: MAIN MENU ---
    def show_main_menu(self):
        self.clear_window()
        
        header = tk.Frame(self.container, bg="#2c3e50", height=70)
        header.pack(fill="x")
        tk.Label(header, text="FACIAL RECOGNITION DASHBOARD", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=20)

        menu_frame = tk.Frame(self.container, bg="#f4f7f6")
        menu_frame.pack(pady=20, padx=50, fill="both")

        # Buttons
        self.add_menu_btn(menu_frame, "START RECOGNITION", "#1abc9c", self.run_recognition)
        self.add_menu_btn(menu_frame, "VIEW ATTENDANCE TABLE", "#34495e", self.show_attendance_table)
        self.add_menu_btn(menu_frame, "REGISTER NEW STUDENT", "#3498db", self.show_registration_view)
        self.add_menu_btn(menu_frame, "QUICK MODEL UPDATE", "#f1c40f", lambda: self.process_classifier('1'))
        self.add_menu_btn(menu_frame, "FULL SYSTEM RETRAIN", "#e67e22", lambda: self.process_classifier('2'))
        self.add_menu_btn(menu_frame, "INITIALIZE TODAY", "#9b59b6", self.reset_attendance)
        self.add_menu_btn(menu_frame, "EXIT", "#e74c3c", self.root.quit)
        
    def add_menu_btn(self, master, text, color, cmd):
        btn = tk.Button(master, text=text, command=cmd, bg=color, fg="white", 
                        font=("Arial", 10, "bold"), pady=12, bd=0, cursor="hand2")
        btn.pack(fill="x", pady=5)

    # --- VIEW: ATTENDANCE TABLE ---
    def show_attendance_table(self):
        self.clear_window()
        
        tk.Label(self.container, text="Today's Attendance Records", font=("Arial", 14, "bold"), bg="#f4f7f6", pady=10).pack()

        # Table Styles
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Create Table
        columns = ("id", "name", "status", "time")
        tree = ttk.Treeview(self.container, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="ID")
        tree.heading("name", text="Student Name")
        tree.heading("status", text="Status")
        tree.heading("time", text="Time Marked")

        tree.column("id", width=50, anchor="center")
        tree.column("status", width=100, anchor="center")

        # Fetch Data
        try:
            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute("""
                SELECT s.id, s.name, a.presence, a.time_marked 
                FROM students s
                LEFT JOIN daily_attendance a ON s.id = a.student_id 
                WHERE a.date = CURRENT_DATE OR a.date IS NULL
                ORDER BY a.presence DESC, s.id ASC
            """)
            for row in cur.fetchall():
                # Format time to look nice
                time_str = row[3].strftime("%H:%M:%S") if row[3] else "--:--:--"
                tree.insert("", tk.END, values=(row[0], row[1], row[2], time_str))
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

        tree.pack(padx=20, pady=10, fill="both", expand=True)

        # Back Button
        tk.Button(self.container, text="← BACK TO MENU", command=self.show_main_menu, 
                  bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), pady=10, bd=0).pack(fill="x", side="bottom")

    # --- VIEW: REGISTRATION & REMOVAL ---
    def show_registration_view(self):
        self.clear_window()
        
        tk.Label(self.container, text="Student Management", font=("Arial", 14, "bold"), bg="#f4f7f6", pady=20).pack()

        form = tk.Frame(self.container, bg="#f4f7f6")
        form.pack(pady=10)

        tk.Label(form, text="Student ID:", bg="#f4f7f6").grid(row=0, column=0, pady=10, sticky="e")
        self.ent_id = tk.Entry(form, width=30)
        self.ent_id.grid(row=0, column=1, padx=10)

        tk.Label(form, text="Full Name:", bg="#f4f7f6").grid(row=1, column=0, pady=10, sticky="e")
        self.ent_name = tk.Entry(form, width=30)
        self.ent_name.grid(row=1, column=1, padx=10)

        # FIXED BUTTONS BELOW: width is now inside the Button() parentheses
        tk.Button(self.container, text="CAPTURE PHOTOS", command=self.generate_dataset, 
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"), pady=10, width=40).pack(pady=5)
        
        tk.Button(self.container, text="DELETE STUDENT", command=self.remove_student, 
                  bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), pady=10, width=40).pack(pady=5)
        
        tk.Button(self.container, text="← BACK TO MENU", command=self.show_main_menu, 
                  bg="#95a5a6", fg="white", pady=10, bd=0).pack(fill="x", side="bottom")
    # --- LOGIC METHODS (Facerec, Classifier, etc.) ---
    # Note: These are identical to the logic in the previous "Master" script, 
    # but they now use the UI methods above.

    def generate_dataset(self):
        s_id = self.ent_id.get()
        s_name = self.ent_name.get()
        if not s_id.isdigit() or not s_name:
            messagebox.showerror("Error", "Valid ID and Name required.")
            return
        
        # [Database Insert Logic...]
        try:
            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute("INSERT INTO students (id, name) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name", (s_id, s_name))
            conn.commit()
            conn.close()

            cap = cv2.VideoCapture(0)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            count = 0
            if not os.path.exists(self.new_data_path): os.makedirs(self.new_data_path)

            while True:
                ret, img = cap.read()
                faces = face_cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.3, 5)
                for (x,y,w,h) in faces:
                    count += 1
                    cv2.imwrite(f"{self.new_data_path}/student.{s_id}.{count}.jpg", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[y:y+h, x:x+w])
                    cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
                cv2.imshow("Capturing...", img)
                if cv2.waitKey(1) & 0xFF == ord('q') or count >= 100: break
            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Success", "Images Captured.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def run_recognition(self):
        if not os.path.exists("classifier.yml"):
            return messagebox.showerror("Error", "Train AI first.")
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("classifier.yml")
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        cap = cv2.VideoCapture(0)
        
        # Give the camera a second to warm up
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not access the camera.")
            return

        while True:
            ret, frame = cap.read()
            
            # THE FIX: If the camera fails to grab a frame, skip this loop iteration
            if not ret or frame is None:
                continue 

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                id_num, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                
                # Logic: Check confidence and log attendance
                if confidence < 100:
                    name = self.log_attendance(id_num)
                    color = (0, 255, 0)
                else:
                    name = "Unknown"
                    color = (0, 0, 255)
                    
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, str(name), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            cv2.imshow("Recognition - Press Q to stop", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        cap.release()
        cv2.destroyAllWindows()

    def log_attendance(self, student_id):
        # (The logic you already have for DB logging with the 30s cooldown)
        now = datetime.now()
        if student_id in self.last_logged and (now - self.last_logged[student_id]).total_seconds() < 30:
            return self.last_logged[str(student_id) + "_name"]

        try:
            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute("SELECT name FROM students WHERE id = %s", (student_id,))
            name = cur.fetchone()[0]
            cur.execute("INSERT INTO daily_attendance (student_id, date, presence, time_marked) VALUES (%s, CURRENT_DATE, 'Present', CURRENT_TIME) ON CONFLICT (student_id, date) DO UPDATE SET presence='Present', time_marked=CURRENT_TIME", (student_id,))
            conn.commit()
            conn.close()
            self.last_logged[student_id] = now
            self.last_logged[str(student_id) + "_name"] = name
            return name
        except: return "Error"

    def process_classifier(self, mode):
        clf = cv2.face.LBPHFaceRecognizer_create()
        model_file = "classifier.yml"
        
        try:
            if mode == '1': # --- QUICK UPDATE ---
                # Only look in 'data/new'
                image_paths = [os.path.join(self.new_data_path, f) for f in os.listdir(self.new_data_path) 
                               if os.path.isfile(os.path.join(self.new_data_path, f)) and f.endswith('.jpg')]
                
                if not image_paths:
                    return messagebox.showinfo("Info", "No new images in 'data/new' to process.")

                faces, ids = [], []
                for p in image_paths:
                    faces.append(np.array(Image.open(p).convert('L'), 'uint8'))
                    ids.append(int(os.path.basename(p).split(".")[1]))

                if os.path.exists(model_file):
                    clf.read(model_file)
                    clf.update(faces, np.array(ids))
                else:
                    clf.train(faces, np.array(ids))
                
                clf.write(model_file)

                # Move files from 'new' to main 'data' archive
                for p in image_paths:
                    shutil.move(p, os.path.join(self.base_path, os.path.basename(p)))
                
                messagebox.showinfo("Success", f"Quick update complete! Added {len(ids)} images to the model.")

            else: # --- FULL SYSTEM RETRAIN ---
                # Look in BOTH 'data' and 'data/new' to be 100% sure nothing is missed
                all_images = []
                for folder in [self.base_path, self.new_data_path]:
                    if os.path.exists(folder):
                        all_images.extend([os.path.join(folder, f) for f in os.listdir(folder) 
                                           if os.path.isfile(os.path.join(folder, f)) and f.endswith('.jpg')])

                if not all_images:
                    return messagebox.showerror("Error", "No images found in data folders to train on.")

                faces, ids = [], []
                for p in all_images:
                    faces.append(np.array(Image.open(p).convert('L'), 'uint8'))
                    ids.append(int(os.path.basename(p).split(".")[1]))

                print("🔄 Rebuilding model from scratch... this may take a moment.")
                clf.train(faces, np.array(ids))
                clf.write(model_file)
                
                # After a full retrain, if there was anything in 'new', move it to the archive
                new_images = [os.path.join(self.new_data_path, f) for f in os.listdir(self.new_data_path) 
                              if os.path.isfile(os.path.join(self.new_data_path, f)) and f.endswith('.jpg')]
                for p in new_images:
                    shutil.move(p, os.path.join(self.base_path, os.path.basename(p)))

                messagebox.showinfo("Success", f"Full System Retrain complete!\nTotal Images: {len(ids)}\nUnique Students: {len(set(ids))}")

        except Exception as e:
            messagebox.showerror("Classifier Error", f"An error occurred: {str(e)}")

    def reset_attendance(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute("INSERT INTO daily_attendance (student_id, date, presence) SELECT id, CURRENT_DATE, 'Absent' FROM students ON CONFLICT DO NOTHING")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Roster initialized for today.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def remove_student(self):
        s_id = self.ent_id.get()
        if not s_id: return
        try:
            conn = psycopg2.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute("DELETE FROM daily_attendance WHERE student_id = %s", (s_id,))
            cur.execute("DELETE FROM students WHERE id = %s", (s_id,))
            conn.commit()
            conn.close()
            for f in glob.glob(os.path.join(self.base_path, f"student.{s_id}.*.jpg")): os.remove(f)
            messagebox.showinfo("Success", "Student removed.")
            self.show_main_menu()
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystemMaster(root)
    root.mainloop()