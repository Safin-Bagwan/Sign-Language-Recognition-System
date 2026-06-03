import logging
import sqlite3
import threading
from collections import deque
from datetime import datetime, timezone

import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

from backend.utils.paths import DATABASE_PATH, MODEL_PATH, ensure_directories

LOGGER = logging.getLogger(__name__)


class RecognitionError(RuntimeError):
    pass


class RecognitionService:
    def __init__(self):
        self.image_x = 50
        self.image_y = 50
        self.roi_x = 200
        self.roi_y = 50
        self.roi_w = 400
        self.roi_h = 400
        self.confidence_threshold = 70.0
        self._lock = threading.RLock()
        self._model = None
        self._camera = None
        self._camera_index = None
        self._running = False
        self._source = None
        self._history = deque(maxlen=50)
        self._total_detected = 0
        self._total_confidence = 0.0
        self._session_started_at = None
        self._last_prediction = None
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
        )

    def health(self):
        model_exists = MODEL_PATH.exists()
        database_exists = DATABASE_PATH.exists()
        return {
            "status": "ready" if model_exists and database_exists else "degraded",
            "model_loaded": self._model is not None,
            "model_path": str(MODEL_PATH),
            "model_exists": model_exists,
            "database_exists": database_exists,
            "running": self._running,
            "source": self._source,
            "camera_index": self._camera_index,
        }

    def start(self, source="browser"):
        with self._lock:
            self._load_model()
            if self._running:
                return self._session_payload("already_running")

            source = self._normalize_source(source)
            if source == "server":
                self._camera = self._open_camera()
            else:
                self._release_camera()

            self._running = True
            self._source = source
            self._session_started_at = datetime.now(timezone.utc)
            LOGGER.info("Recognition started in %s mode", source)
            return self._session_payload("started")

    def stop(self):
        with self._lock:
            self._release_camera()
            self._running = False
            self._source = None
            LOGGER.info("Recognition stopped")
            return self._session_payload("stopped")

    def predict(self, frame=None):
        with self._lock:
            self._load_model()
            if frame is None:
                if not self._running or self._camera is None or self._source != "server":
                    raise RecognitionError("A browser image frame is required for prediction.")
                ok, frame = self._camera.read()
                if not ok or frame is None:
                    raise RecognitionError("Could not read a frame from the camera.")

            prediction = self._predict_frame(frame)
            self._last_prediction = prediction

            if prediction["detected"]:
                self._history.appendleft(prediction)
                self._total_detected += 1
                self._total_confidence += prediction["confidence"]

            return prediction

    def stats(self):
        with self._lock:
            average = round(self._total_confidence / self._total_detected, 2) if self._total_detected else 0
            return {
                "running": self._running,
                "source": self._source,
                "total_gestures": self._total_detected,
                "average_confidence": average,
                "session_started_at": self._session_started_at.isoformat() if self._session_started_at else None,
                "history_count": len(self._history),
                "last_prediction": self._last_prediction,
            }

    def history(self):
        with self._lock:
            return list(self._history)

    def clear(self):
        with self._lock:
            self._history.clear()
            self._total_detected = 0
            self._total_confidence = 0.0
            self._last_prediction = None
            self._session_started_at = datetime.now(timezone.utc) if self._running else None
            return self.stats()

    def _load_model(self):
        if self._model is not None:
            return

        ensure_directories()
        if not MODEL_PATH.exists():
            raise RecognitionError(f"Model file not found: {MODEL_PATH}")

        LOGGER.info("Loading Keras model from %s", MODEL_PATH)
        self._model = load_model(str(MODEL_PATH))

    def _open_camera(self):
        for index in (0, 1, 2):
            LOGGER.info("Trying camera index %s", index)
            camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if camera.isOpened():
                ok, _ = camera.read()
                if ok:
                    self._camera_index = index
                    return camera
            camera.release()

        self._camera_index = None
        raise RecognitionError("Could not open a webcam on camera indices 0, 1, or 2.")

    def _release_camera(self):
        if self._camera is not None:
            self._camera.release()
        self._camera = None
        self._camera_index = None

    def _predict_frame(self, frame):
        display_frame, contours, threshold = self._get_img_contour_thresh(frame)
        if not contours:
            return self._empty_prediction("No hand detected")

        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) <= 1000:
            return self._empty_prediction("Hand contour too small")

        confidence, class_id = self._predict_from_contour(contour, threshold)
        label = self._label_for_class(class_id)
        detected = confidence >= self.confidence_threshold and label != "Unknown"
        text = label if detected else ""

        return {
            "detected": detected,
            "gesture": label if detected else "Waiting",
            "text": text,
            "confidence": round(confidence, 2),
            "class_id": int(class_id),
            "message": "Prediction ready" if detected else "Low confidence prediction",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "frame_width": int(display_frame.shape[1]),
            "frame_height": int(display_frame.shape[0]),
        }

    def _empty_prediction(self, message):
        return {
            "detected": False,
            "gesture": "Waiting",
            "text": "",
            "confidence": 0,
            "class_id": None,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _get_img_contour_thresh(self, frame):
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 480))
        mask = self._get_hand_mask(frame)
        threshold = mask[self.roi_y : self.roi_y + self.roi_h, self.roi_x : self.roi_x + self.roi_w]
        contours = cv2.findContours(threshold.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        return frame, contours, threshold

    def _get_hand_mask(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        if not results.multi_hand_landmarks:
            return mask

        for landmarks in results.multi_hand_landmarks:
            points = []
            for landmark in landmarks.landmark:
                cx = int(landmark.x * frame.shape[1])
                cy = int(landmark.y * frame.shape[0])
                points.append([cx, cy])

            points = np.array(points, dtype=np.int32)
            hull = cv2.convexHull(points)
            cv2.fillConvexPoly(mask, hull, 255)

            for connection in self._mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection[0], connection[1]
                p1 = (
                    int(landmarks.landmark[start_idx].x * frame.shape[1]),
                    int(landmarks.landmark[start_idx].y * frame.shape[0]),
                )
                p2 = (
                    int(landmarks.landmark[end_idx].x * frame.shape[1]),
                    int(landmarks.landmark[end_idx].y * frame.shape[0]),
                )
                cv2.line(mask, p1, p2, 255, 15)

        return mask

    def _predict_from_contour(self, contour, threshold):
        x, y, width, height = cv2.boundingRect(contour)
        image = threshold[y : y + height, x : x + width]

        if width > height:
            pad = int((width - height) / 2)
            image = cv2.copyMakeBorder(image, pad, pad, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
        elif height > width:
            pad = int((height - width) / 2)
            image = cv2.copyMakeBorder(image, 0, 0, pad, pad, cv2.BORDER_CONSTANT, (0, 0, 0))

        processed = self._process_image(image)
        probabilities = self._model.predict(processed, verbose=0)[0]
        class_id = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities) * 100)
        return confidence, class_id

    def _process_image(self, image):
        image = cv2.resize(image, (self.image_x, self.image_y))
        image = np.array(image, dtype=np.float32) / 255.0
        return np.reshape(image, (1, self.image_x, self.image_y, 1))

    def _label_for_class(self, class_id):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                row = conn.execute("SELECT g_name FROM gesture WHERE g_id=?", (int(class_id),)).fetchone()
        except sqlite3.Error:
            LOGGER.exception("Failed to read gesture label from database")
            return "Unknown"

        return row[0] if row else "Unknown"

    def _session_payload(self, status):
        return {
            "status": status,
            "running": self._running,
            "camera_index": self._camera_index,
            "source": self._source,
            "session_started_at": self._session_started_at.isoformat() if self._session_started_at else None,
        }

    def _normalize_source(self, source):
        normalized = str(source or "browser").strip().lower()
        if normalized not in {"browser", "server"}:
            raise RecognitionError("Recognition source must be 'browser' or 'server'.")
        return normalized


recognition_service = RecognitionService()
