# Sign Language Recognition System

This repository is organized as a full-stack project.

## Project Structure

```text
Sign-Language-Recognition-System/
├── backend/
│   ├── app.py
│   ├── routes/
│   │   └── api.py
│   ├── services/
│   │   ├── recognition_service.py
│   │   └── tts_service.py
│   ├── utils/
│   │   ├── paths.py
│   │   └── responses.py
│   ├── app/
│   │   ├── create_gestures.py
│   │   ├── load_images.py
│   │   ├── cnn_model_train.py
│   │   ├── final.py
│   │   └── paths.py
│   ├── artifacts/
│   │   └── hist
│   ├── data/
│   │   ├── database/
│   │   │   └── gesture_db.db
│   │   ├── datasets/
│   │   │   ├── train_images
│   │   │   ├── train_labels
│   │   │   ├── test_images
│   │   │   ├── test_labels
│   │   │   ├── val_images
│   │   │   └── val_labels
│   │   └── gestures/
│   ├── models/
│   │   └── cnn_model_keras2.h5
│   ├── static/
│   ├── requirements.txt
│   └── README.md
└── frontend/
    ├── index.html
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── api.js
    │   └── app.js
    ├── assets/
    │   └── images/
    └── README.md
```

## Parts

- `backend/` contains the existing Python scripts plus a Flask API that reuses the TensorFlow/Keras model, OpenCV webcam capture, MediaPipe hand tracking, SQLite gesture labels, and text-to-speech support.
- `frontend/` contains the responsive web interface, recognition dashboard, Flask API integration, and fallback mock mode for demos when the backend is unavailable.

See `backend/README.md` for backend setup and run commands.

## Quick Start

```bash
backend\venv\Scripts\activate
pip install -r backend\requirements.txt
python -m backend.app
```

Open `http://127.0.0.1:5000` in your browser.

## API Overview

- `GET /api/health`
- `POST /api/start-recognition`
- `POST /api/stop-recognition`
- `POST /api/predict`
- `POST /api/text-to-speech`
- `GET /api/stats`
- `GET /api/history`
- `POST /api/clear`
