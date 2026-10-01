import os
import cv2
import numpy as np
from PIL import Image

def run_comprehensive_evaluation():
    BASE_TEST_DIR = "data/test"
    MODEL_FILE = "classifier.yml"
    CASCADE_FILE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    
    if not os.path.exists(MODEL_FILE):
        print(f"Error: Trained model file '{MODEL_FILE}' not found.")
        return
    if not os.path.exists(BASE_TEST_DIR):
        print(f"Error: Base test directory '{BASE_TEST_DIR}' missing.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)
    face_cascade = cv2.CascadeClassifier(CASCADE_FILE)
    
    categories = [d for d in os.listdir(BASE_TEST_DIR) if os.path.isdir(os.path.join(BASE_TEST_DIR, d))]
    if not categories:
        categories = [""]

    print("\n" + "="*75)
    print("      EXECUTING COMPREHENSIVE BIOMETRIC & ROBUSTNESS EVALUATION       ")
    print("="*75)

    for cat in categories:
        current_dir = os.path.join(BASE_TEST_DIR, cat) if cat else BASE_TEST_DIR
        image_files = [f for f in os.listdir(current_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            continue
            
        cat_title = cat.upper() if cat else "GENERAL TEST BATCH"
        print(f"\n--- EVALUATING CATEGORY: {cat_title} ({len(image_files)} Files Found) ---")
        
        # Chapter 4 Metric Counters per category
        total_images = 0
        true_positives = 0  
        true_negatives = 0  
        false_positives = 0 
        false_negatives = 0 

        for filename in image_files:
            image_path = os.path.join(current_dir, filename)
            is_registered = False
            true_id = None
            
            if filename.startswith("student."):
                is_registered = True
                try:
                    true_id = int("".join(filter(str.isdigit, filename.split(".")[1])))
                except (ValueError, IndexError):
                    continue
            elif filename.startswith("unknown."):
                is_registered = False
            else:
                continue 

            img = Image.open(image_path).convert('L')
            image_np = np.array(img, 'uint8')
            
            # Haar Cascade detection
            faces = face_cascade.detectMultiScale(image_np, 1.3, 5)
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                roi = image_np[y:y+h, x:x+w]
            else:
                # FIXED: Fallback safety prevents skipping pre-cropped files
                roi = image_np
                
            total_images += 1
            predicted_id, confidence = recognizer.predict(roi)
            is_recognized = confidence < 75.5 # Match system threshold configuration
            
            # Confusion Matrix Logic
            if is_registered:
                if is_recognized and predicted_id == true_id:
                    true_positives += 1
                elif is_recognized and predicted_id != true_id:
                    false_positives += 1
                    print(f" [MISCLASSIFIED] Folder: {cat if cat else 'root'} | File: {filename}")
                    print(f"   -> System mistook Student {true_id} for Student {predicted_id} (Conf: {confidence:.1f})")
                else:
                    false_negatives += 1
                    print(f" [MISSED FACE] Folder: {cat if cat else 'root'} | File: {filename}")
                    print(f"   -> System flagged registered Student {true_id} as 'Unknown' (Conf: {confidence:.1f})")
            else:
                if not is_recognized:
                    true_negatives += 1
                else:
                    false_positives += 1
                    print(f" [SECURITY BREACH] Folder: {cat if cat else 'root'} | File: {filename}")
                    print(f"   -> System mistook an Unknown face for Student {predicted_id} (Conf: {confidence:.1f})")

        # Calculations
        correct_decisions = true_positives + true_negatives
        accuracy_score = (correct_decisions / total_images * 100) if total_images > 0 else 0.0

        # Print layout built exactly for Chapter 4 data entry
        print(f" > Total Images Processed          : {total_images}")
        print(f" > Category Accuracy Score         : {accuracy_score:.2f}%")
        print(f"   [Confusion Matrix Breakdown]")
        print(f"    • True Positives (Correct Match) : {true_positives}")
        print(f"    • True Negatives (Correct Reject): {true_negatives}")
        print(f"    • False Positives (Misclassified): {false_positives}")
        print(f"    • False Negatives (Missed Face)  : {false_negatives}")
        print("-" * 50)
        
    print("\n" + "="*75 + "\n")

if __name__ == "__main__":
    run_comprehensive_evaluation()