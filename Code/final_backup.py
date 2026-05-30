import cv2
import pickle
import numpy as np
import tensorflow as tf
import os
import sqlite3
import pyttsx3
import mediapipe as mp
from tensorflow.keras.models import load_model
from threading import Thread

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Initialize Text-to-Speech engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
except Exception as e:
    print(f"Warning: TTS engine failed to initialize: {e}")
    engine = None

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load the trained model
if os.path.exists('cnn_model_keras2.h5'):
    model = load_model('cnn_model_keras2.h5')
    print("SUCCESS: Model loaded.")
else:
    print("ERROR: Model 'cnn_model_keras2.h5' not found.")
    exit()

image_x, image_y = 50, 50
x, y, w, h = 200, 50, 400, 400
is_voice_on = True

def get_hand_mask(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
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
            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection[0], connection[1]
                p1 = (int(hand_landmarks.landmark[start_idx].x * img.shape[1]), int(hand_landmarks.landmark[start_idx].y * img.shape[0]))
                p2 = (int(hand_landmarks.landmark[end_idx].x * img.shape[1]), int(hand_landmarks.landmark[end_idx].y * img.shape[0]))
                cv2.line(mask, p1, p2, 255, 15)
    return mask

def keras_process_image(img):
    img = cv2.resize(img, (image_x, image_y))
    img = np.array(img, dtype=np.float32)
    img = img / 255.0
    img = np.reshape(img, (1, image_x, image_y, 1))
    return img

def keras_predict(model, image):
    processed = keras_process_image(image)
    pred_probab = model.predict(processed, verbose=0)[0]
    pred_class = list(pred_probab).index(max(pred_probab))
    return max(pred_probab), pred_class

def get_pred_text_from_db(pred_class):
    try:
        conn = sqlite3.connect("gesture_db.db")
        cursor = conn.execute("SELECT g_name FROM gesture WHERE g_id=?", (pred_class,))
        for row in cursor:
            conn.close()
            return row[0]
        conn.close()
    except: pass
    return "Unknown"

def get_pred_from_contour(contour, thresh):
    x1, y1, w1, h1 = cv2.boundingRect(contour)
    save_img = thresh[y1:y1+h1, x1:x1+w1]
    if w1 > h1:
        save_img = cv2.copyMakeBorder(save_img, int((w1-h1)/2) , int((w1-h1)/2) , 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
    elif h1 > w1:
        save_img = cv2.copyMakeBorder(save_img, 0, 0, int((h1-w1)/2) , int((h1-w1)/2) , cv2.BORDER_CONSTANT, (0, 0, 0))
    
    pred_probab, pred_class = keras_predict(model, save_img)
    return get_pred_text_from_db(pred_class) if pred_probab*100 > 70 else ""

def say_text(text):
    if not is_voice_on or engine is None: return
    try:
        engine.say(text)
        engine.runAndWait()
    except: pass

def get_img_contour_thresh(img):
    img = cv2.flip(img, 1)
    img = cv2.resize(img, (640, 480))
    mask = get_hand_mask(img)
    thresh = mask[y:y+h, x:x+w]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
    return img, contours, thresh

def text_mode(cam):
    text, word, count_same_frame = "", "", 0

    def mouse_click(event, x_mouse, y_mouse, flags, param):
        nonlocal word
        if event == cv2.EVENT_LBUTTONDOWN:
            # The blackboard starts at x=640 (img width) in the hstack result
            # Button is at (1000, 400) to (1150, 450) on blackboard
            if 640 + 1000 < x_mouse < 640 + 1150 and 400 < y_mouse < 450:
                word = ""

    cv2.namedWindow("Sign Language Interpreter")
    cv2.setMouseCallback("Sign Language Interpreter", mouse_click)

    while True:
        ret, img = cam.read()
        if not ret: break
        img, contours, thresh = get_img_contour_thresh(img)
        old_text = text
        if len(contours) > 0:
            contour = max(contours, key = cv2.contourArea)
            if cv2.contourArea(contour) > 1000:
                text = get_pred_from_contour(contour, thresh)
                if old_text == text: count_same_frame += 1
                else: count_same_frame = 0
                if count_same_frame > 20:
                    word += text
                    Thread(target=say_text, args=(text,)).start()
                    count_same_frame = 0

        blackboard = np.zeros((480, 1200, 3), dtype=np.uint8)
        cv2.putText(blackboard, "MediaPipe Mode", (150, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (255, 0,0))
        cv2.putText(blackboard, "Predicted: " + text, (30, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 0))
        cv2.putText(blackboard, word, (30, 240), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255))
        
        # Draw Clear Button
        cv2.rectangle(blackboard, (1000, 400), (1150, 450), (255, 255, 255), -1)
        cv2.putText(blackboard, "CLEAR", (1020, 435), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 0, 0))

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        res = np.hstack((img, blackboard))
        cv2.imshow("Sign Language Interpreter", res)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): 
            break
        elif key == ord('c'):
            word = ""
    return 0

def recognize():
    # Try indices 0, 1, 2 with DirectShow backend for Windows
    cam = None
    for index in [0, 1, 2]:
        print(f"DEBUG: Trying camera index {index}...")
        temp_cam = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if temp_cam.isOpened():
            ret, frame = temp_cam.read()
            if ret:
                cam = temp_cam
                print(f"SUCCESS: Using Camera Index {index}")
                break
        temp_cam.release()
    
    if cam is None:
        print("CRITICAL ERROR: Could not open any camera.")
        return
        
    text_mode(cam)
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize()
