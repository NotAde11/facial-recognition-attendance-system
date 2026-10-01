# Facial Recognition Attendance System (FRAS)

A computer vision-based attendance management system built with Python, OpenCV, and Streamlit. The system features a multi-page web interface, secure user authentication, automated face capture, local model training, and database logging.

---

## Key Features

- Authentication Gate: Secure sign-in verifying credentials before granting access to dashboard operations.
- Real-Time Detection: Haar Cascade-based facial tracking using camera feeds.
- Model Training Pipeline: Local classifier generation using OpenCV's LBPH algorithm without committing large model files to GitHub.
- Database Management: Automated record handling and local attendance tracking.
- Performance Evaluation: Built-in benchmarking scripts to evaluate detection robustness and model metrics.

---

## Project Structure

FRAS/ 
|-- data/                               # Image dataset directory for trained facial samples
|   `-- new/                            # Image dataset directory for new facial samples 
|       `-- .gitkeep 
|-- pages/                              # Additional Streamlit pages and sub-views 
|-- auth.py                             # Handles login verification and authentication logic 
|-- backend.py                          # Core CV pipeline: face capture, dataset loading, and model training 
|-- evaluate_robustness.py              # Script to benchmark model stability and accuracy 
|-- haarcascade_frontalface_default.xml # Pre-trained OpenCV frontal face detector 
|-- login.py                            # Main entry point: initializes Streamlit app, login UI, and routing 
|-- main_uiv3.py                        # Main application dashboard layout and camera view 
|-- metrics_chart.py                    # Generates graphical metrics and performance evaluation plots 
|-- setup_db.py                         # Database setup and schema initialization script 
|-- users.json                          # User credentials and authorized profile store 
|-- .gitignore                          # Excludes large binaries, cache, and virtual environments 
`-- README.md                           # Project documentation 

---

## Prerequisites & Installation

1. Clone the repository:
   git clone https://github.com/NotAde11/facial-recognition-attendance-system.git 
   cd facial-recognition-attendance-system

2. Set up a virtual environment (optional):
   # Windows:
   python -m venv venv
   .\venv\Scripts\activate
   # macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate

3. Install required packages:
   pip install streamlit opencv-python opencv-contrib-python numpy pillow matplotlib

---

## Setup & Running the System

1. Initialize the local attendance database:
   python setup_db.py

2. Train the facial classifier:
   - Place face image samples into data/new/ (or use the sample collection feature in the UI).
   - Run backend.py to build the classifier:
     python backend.py
   - This generates classifier.yml locally.

3. Start the application:
   streamlit run login.py
   - Sign in via the login screen (handled by auth.py).
   - Use the dashboard views (main_uiv3.py) to run detection, register users, and log attendance.

---

## Benchmarking & Evaluation

Run these scripts to check detection metrics and accuracy graphs:
python evaluate_robustness.py
python metrics_chart.py