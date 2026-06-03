import cv2
import os
from paths import GESTURES_DIR, ensure_directories

def flip_images():
    ensure_directories()
    gest_folder = GESTURES_DIR
    if not os.path.exists(gest_folder):
        print(f"ERROR: {gest_folder} directory not found.")
        return

    gesture_ids = [d for d in os.listdir(gest_folder) if os.path.isdir(os.path.join(gest_folder, d))]
    
    for g_id in gesture_ids:
        print(f"Processing gesture ID: {g_id}")
        folder_path = os.path.join(gest_folder, g_id)
        
        existing_files = os.listdir(folder_path)
        images = [f for f in existing_files if f.endswith(".jpg") and "_flipped" not in f]
        count = 0
        for filename in images:
            name_part = os.path.splitext(filename)[0]
            new_filename = f"{name_part}_flipped.jpg"
            
            if new_filename in existing_files:
                continue
                
            path = os.path.join(folder_path, filename)
            img = cv2.imread(path, 0)
            
            if img is None:
                print(f"  Warning: Could not read {path}")
                continue
                
            new_path = os.path.join(folder_path, new_filename)
            
            # Flip and save
            flipped_img = cv2.flip(img, 1)
            if cv2.imwrite(new_path, flipped_img):
                count += 1
        
        print(f"  Successfully flipped {count} new images in gesture {g_id}.")

if __name__ == "__main__":
    flip_images()
