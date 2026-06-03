# Backend

Python backend and machine-learning runtime for the Sign Language Recognition System.

## Contents

```text
backend/
├── app.py
├── routes/
│   └── api.py
├── services/
│   ├── recognition_service.py
│   └── tts_service.py
├── utils/
│   ├── paths.py
│   └── responses.py
├── app/
│   ├── create_gestures.py
│   ├── load_images.py
│   ├── cnn_model_train.py
│   ├── final.py
│   ├── display_gestures.py
│   ├── Rotate_images.py
│   ├── set_hand_histogram.py
│   └── paths.py
├── artifacts/
│   └── hist
├── data/
│   ├── database/
│   │   └── gesture_db.db
│   ├── datasets/
│   │   ├── train_images
│   │   ├── train_labels
│   │   ├── test_images
│   │   ├── test_labels
│   │   ├── val_images
│   │   └── val_labels
│   └── gestures/
├── models/
│   └── cnn_model_keras2.h5
├── static/
├── requirements.txt
└── venv/
```

## Setup

From the repository root:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Flask Web App

From the repository root:

```bash
backend\venv\Scripts\activate
python -m backend.app
```

Then open:

```text
http://127.0.0.1:5000
```

The Flask app serves the existing frontend and exposes JSON endpoints under `/api`.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Check model, database, camera/session status. |
| `POST` | `/api/start-recognition` | Load the model if needed and open the webcam. |
| `POST` | `/api/stop-recognition` | Release the webcam and stop the session. |
| `POST` | `/api/predict` | Read a webcam frame and return gesture, text, confidence, and detection status. |
| `POST` | `/api/text-to-speech` | Speak generated text with the backend TTS service. |
| `GET` | `/api/stats` | Return session totals, average confidence, and last prediction. |
| `GET` | `/api/history` | Return recent confident recognition events. |
| `POST` | `/api/clear` | Clear session history and statistics. |

`POST /api/predict` can also accept an optional JSON body with a base64 encoded image:

```json
{
  "frame": "data:image/jpeg;base64,..."
}
```

If no frame is provided, the backend uses the active server-side webcam session.

## Legacy Commands

Run these from the repository root:

```bash
python backend/app/create_gestures.py
python backend/app/Rotate_images.py
python backend/app/load_images.py
python backend/app/cnn_model_train.py
python backend/app/final.py
```

The scripts use `backend/app/paths.py`, so model, dataset, gesture, database, and artifact files resolve consistently from the backend directory.
