import cv2
import numpy as np
import os
import sqlite3
import random
import mediapipe as mp
from paths import DATABASE_PATH, GESTURES_DIR, ensure_directories

# Parameters
image_x, image_y = 50, 50

def init_create_folder_database():
    ensure_directories()
    if not DATABASE_PATH.exists():
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("CREATE TABLE gesture ( g_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, g_name TEXT NOT NULL )")
        conn.commit()
        conn.close()

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

def store_in_db(g_id, g_name):
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        conn.execute("INSERT INTO gesture (g_id, g_name) VALUES (?, ?)", (g_id, g_name))
    except sqlite3.IntegrityError:
        choice = input(f"Gesture ID {g_id} already exists. Update name to '{g_name}'? (y/n): ")
        if choice.lower() == "y":
            conn.execute("UPDATE gesture SET g_name = ? WHERE g_id = ?", (g_name, g_id))
    conn.commit()
    conn.close()

def get_hand_mask(img, hands_module):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands_module.process(img_rgb)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            points = []
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * img.shape[1]), int(lm.y * img.shape[0])
                points.append([cx, cy])
            
            points = np.array(points, dtype=np.int32)
            hull = cv2.convexHull(points)
            cv2.fillConvexPoly(mask, hull, 255)
            
            mp_hands = mp.solutions.hands
            for connection in mp_hands.HAND_CONNECTIONS:
                p1 = (int(hand_landmarks.landmark[connection[0]].x * img.shape[1]), int(hand_landmarks.landmark[connection[0]].y * img.shape[0]))
                p2 = (int(hand_landmarks.landmark[connection[1]].x * img.shape[1]), int(hand_landmarks.landmark[connection[1]].y * img.shape[0]))
                cv2.line(mask, p1, p2, 255, 15)
                
    return mask

def store_images(g_id):
    # Initialize MediaPipe INSIDE the function to keep the startup clean
    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    
    print("DEBUG: Searching for camera...")
    cam = None
    for index in [0, 1, 2]:
        temp_cam = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if temp_cam.isOpened():
            ret, frame = temp_cam.read()
            if ret:
                cam = temp_cam
                print(f"SUCCESS: Using Camera {index}")
                break
        temp_cam.release()

    if cam is None:
        print("CRITICAL ERROR: Could not open any camera.")
        return

    total_pics = 300
    gesture_folder = GESTURES_DIR / str(g_id)
    create_folder(gesture_folder)
    pic_no = 0
    flag_capture = False

    print("\n--- OPERATING INSTRUCTIONS ---")
    print("1. A window will open showing your webcam.")
    print("2. Position your hand so the 'Mask' window shows a solid white shape.")
    print("3. Press 'c' to START/PAUSE capture.")
    print("4. Press 'q' to QUIT early.")
    print("------------------------------\n")

    while True:
        ret, img = cam.read()
        if not ret: break
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (640, 480))
        
        mask = get_hand_mask(img, hands_detector)
        
        x, y, w, h = 200, 50, 400, 400
        thresh = mask[y:y+h, x:x+w]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]

        if flag_capture and len(contours) > 0:
            contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(contour) > 1000:
                x1, y1, w1, h1 = cv2.boundingRect(contour)
                save_img = thresh[y1:y1 + h1, x1:x1 + w1]

                if w1 > h1:
                    save_img = cv2.copyMakeBorder(save_img, int((w1 - h1) / 2), int((w1 - h1) / 2), 0, 0, cv2.BORDER_CONSTANT, value=0)
                elif h1 > w1:
                    save_img = cv2.copyMakeBorder(save_img, 0, 0, int((h1 - w1) / 2), int((h1 - w1) / 2), cv2.BORDER_CONSTANT, value=0)

                save_img = cv2.resize(save_img, (image_x, image_y))
                if random.randint(0, 10) % 2 == 0:
                    save_img = cv2.flip(save_img, 1)

                pic_no += 1
                cv2.imwrite(str(gesture_folder / f"{pic_no}.jpg"), save_img)
                if pic_no % 50 == 0:
                    print(f"PROGRESS: {pic_no}/{total_pics} images saved.")

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, f"Captured: {pic_no}/{total_pics}", (30, 450), cv2.FONT_HERSHEY_TRIPLEX, 1, (127, 127, 255), 2)
        if flag_capture:
            cv2.putText(img, "CAPTURING...", (30, 60), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 255), 2)

        cv2.imshow("Webcam Feed", img)
        cv2.imshow("Hand Mask (Must be White)", mask)

        kp = cv2.waitKey(1) & 0xFF
        if kp == ord('c'):
            flag_capture = not flag_capture
            print("Capture Status: " + ("ON" if flag_capture else "OFF"))
        if kp == ord('q') or pic_no >= total_pics:
            break

    cam.release()
    cv2.destroyAllWindows()
    if pic_no >= total_pics:
        print(f"\nSUCCESS: Gesture {g_id} captured completely!")

if __name__ == "__main__":
    init_create_folder_database()
    print("=== SIGN LANGUAGE DATA CAPTURE ===")
    try:
        g_id_in = int(input("Step 1: Enter Gesture ID (e.g. 1): "))
        g_name_in = input("Step 2: Enter Gesture Name (e.g. A): ")
        store_in_db(g_id_in, g_name_in)
        store_images(g_id_in)
    except Exception as e:
        print(f"Error: {e}")
