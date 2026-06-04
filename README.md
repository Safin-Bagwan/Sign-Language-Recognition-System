# Sign Language Recognition System

A full-stack Sign Language Recognition System that captures webcam input in the browser, streams frames to a Flask API, processes hand gestures with OpenCV and MediaPipe, classifies gestures with a TensorFlow/Keras CNN model, and returns recognized text, confidence scores, speech output, session history, and analytics.

This project is designed as a practical assistive-technology prototype for converting sign language gestures into readable text and speech through a browser-based interface.

## Project Overview

Sign language communication can be difficult to interpret for people who do not know the gesture vocabulary. This project addresses that gap by providing a real-time web application that detects hand gestures from a webcam and translates them into text and speech.

The application uses a static responsive frontend for webcam capture and user interaction, a Flask backend for API orchestration, MediaPipe for hand landmark detection, OpenCV for image preprocessing, TensorFlow/Keras for CNN inference, SQLite for gesture label mapping, and browser/backend speech synthesis for audio output. It also includes a recognition history table and statistics dashboard for session-level analytics.

## Features

- Real-time webcam recognition from the browser
- Browser-to-Flask frame streaming with base64 JPEG frames
- TensorFlow/Keras CNN gesture predictions
- MediaPipe hand landmark detection
- OpenCV frame decoding, masking, ROI extraction, and preprocessing
- Gesture confidence scoring
- Text-to-speech conversion
- Recognition history
- Statistics dashboard
- Responsive frontend
- REST API backend
- Backend API tests and frontend integration contract tests

## Architecture

```text
Browser Webcam
↓
Frontend (HTML/CSS/JS)
↓
Flask API
↓
OpenCV + MediaPipe
↓
TensorFlow Model
↓
SQLite Database
↓
Prediction Response
```

The recommended runtime path is a single Flask server. `backend/app.py` serves the static frontend from `frontend/` and exposes all JSON endpoints under `/api`.

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- Flask
- Flask-Cors

### Machine Learning

- TensorFlow/Keras
- OpenCV
- MediaPipe
- NumPy

### Database

- SQLite

### Testing

- Python `unittest`
- Node.js built-in test runner

## Project Structure

```text
Sign-Language-Recognition-System/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── wsgi.py
│   ├── requirements.txt
│   ├── routes/
│   │   └── api.py
│   ├── services/
│   │   ├── recognition_service.py
│   │   └── tts_service.py
│   ├── utils/
│   │   ├── paths.py
│   │   └── responses.py
│   ├── models/
│   │   └── cnn_model_keras2.h5
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
│   ├── artifacts/
│   │   └── hist
│   └── app/
│       ├── create_gestures.py
│       ├── load_images.py
│       ├── cnn_model_train.py
│       ├── final.py
│       ├── final_backup.py
│       ├── display_gestures.py
│       ├── Rotate_images.py
│       ├── set_hand_histogram.py
│       └── paths.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   └── app.js
│   ├── assets/
│   │   ├── images/
│   │   │   └── hero-ai-sign-language.png
│   │   └── icons/
│   └── pages/
├── tests/
│   ├── __init__.py
│   ├── test_backend_api.py
│   └── frontend_static.test.mjs
├── package.json
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Windows 10 or newer
- Python 3.11 recommended
  - The current workspace virtual environment uses Python 3.11.9.
  - `backend/requirements.txt` pins TensorFlow/Keras 2.15.0, so Python 3.11 is the safest version.
- Git
- A modern browser with webcam support, such as Chrome or Edge
- A working webcam
- Node.js only if you want to run frontend tests

### Backend Setup

From the repository root:

```powershell
py -3.11 -m venv backend\venv
backend\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

If PowerShell blocks script activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
backend\venv\Scripts\Activate.ps1
```

### Required Runtime Files

The web application expects these files to exist:

```text
backend/models/cnn_model_keras2.h5
backend/data/database/gesture_db.db
```

Verify them with:

```powershell
Test-Path backend\models\cnn_model_keras2.h5
Test-Path backend\data\database\gesture_db.db
```

Both commands should return `True`.

The dataset files in `backend/data/datasets/` and gesture images in `backend/data/gestures/` are used by the legacy data preparation and training scripts. They are not required for normal web-app inference if the trained model and SQLite database already exist.

### Environment Variables

Local development works with the defaults in `backend/config.py`. Optional variables:

```powershell
$env:APP_ENV="development"
$env:FLASK_ENV="development"
$env:CORS_ORIGINS="http://127.0.0.1:5000,http://localhost:5000,http://127.0.0.1:5173,http://localhost:5173"
$env:MAX_CONTENT_LENGTH="4194304"
$env:RECOGNITION_FRAME_REQUIRED="true"
$env:LOG_LEVEL="INFO"
```

## Running the Application

Recommended method from the repository root:

```powershell
backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m backend.app
```

Open:

```text
http://127.0.0.1:5000
```

The Flask server starts at `127.0.0.1:5000`, serves `frontend/index.html`, and exposes the REST API under `/api`.

## Usage Guide

1. Open `http://127.0.0.1:5000`.
2. Click `Start Recognition`.
3. Allow webcam permission when the browser prompts you.
4. Keep your hand visible in the webcam preview.
5. Watch the current gesture, confidence score, and recognized text update in the recognition panel.
6. Use `Text-to-Speech` to speak the generated sentence.
7. Review recent predictions in the recognition history table.
8. Monitor session totals and average confidence in the statistics dashboard.
9. Click `Stop Recognition` to stop the session and release the browser camera stream.
10. Click `Clear Text` to reset local text, backend history, and session statistics.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Returns model, database, camera, and session status. |
| `POST` | `/api/start-recognition` | Loads the model if needed and starts recognition. Browser mode is the default. |
| `POST` | `/api/stop-recognition` | Stops recognition and releases any server-side camera session. |
| `POST` | `/api/predict` | Accepts a base64 image frame and returns gesture prediction data. |
| `POST` | `/api/text-to-speech` | Queues text for backend speech synthesis. |
| `GET` | `/api/stats` | Returns session totals, average confidence, and last prediction. |
| `GET` | `/api/history` | Returns recent confident predictions. |
| `POST` | `/api/clear` | Clears recognition history and statistics. |

Example browser prediction request:

```json
{
  "frame": "data:image/jpeg;base64,..."
}
```

Example start request:

```json
{
  "source": "browser"
}
```

The backend also supports explicit server-camera mode with `"source": "server"`, but browser mode is the recommended web-app path.

## Machine Learning Pipeline

1. The browser captures webcam video with `navigator.mediaDevices.getUserMedia`.
2. `frontend/js/app.js` draws the video frame to an off-DOM canvas.
3. The canvas is encoded as a JPEG data URL and sent to `POST /api/predict`.
4. `backend/routes/api.py` decodes the base64 payload and converts it into an OpenCV image.
5. `backend/services/recognition_service.py` flips and resizes the frame.
6. MediaPipe Hands detects hand landmarks.
7. A hand mask is generated from the landmark hull and hand connections.
8. The region of interest is cropped from the mask.
9. OpenCV finds the largest contour and prepares a normalized `50x50` grayscale input.
10. The TensorFlow/Keras model in `backend/models/cnn_model_keras2.h5` predicts gesture class probabilities.
11. The highest-probability class is mapped to a gesture label from `backend/data/database/gesture_db.db`.
12. The API returns the gesture label, text, confidence score, detection status, and timestamp.

## Testing

Run backend API tests:

```powershell
backend\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Run frontend contract tests:

```powershell
npm test
```

Run Python compile checks:

```powershell
backend\venv\Scripts\python.exe -m compileall -q backend tests
```

Current test coverage includes all Flask API endpoints and static frontend integration contracts. Full browser webcam verification still requires an interactive browser with camera permission.

## Screenshots

### Landing Page

Add screenshot here:

```text
screenshots/landing-page.png
```

### Recognition Page

Add screenshot here:

```text
screenshots/recognition-page.png
```

### Dashboard

Add screenshot here:

```text
screenshots/dashboard.png
```

### Statistics

Add screenshot here:

```text
screenshots/statistics.png
```

## Current Status

The application is integrated as a Flask-served web app with browser webcam capture, backend frame decoding, TensorFlow/MediaPipe/OpenCV recognition logic, SQLite label lookup, text-to-speech, session history, and dashboard statistics.

Known remaining work:

- Verify browser webcam prediction end-to-end in an interactive browser.
- Add full browser/DOM frontend tests.
- Add CI for backend tests, frontend tests, and compile checks.
- Write a full production deployment runbook.
- Refactor or archive duplicate legacy scripts under `backend/app/`.
- Decide a long-term artifact strategy for large model and dataset files.

## Future Improvements

- User authentication
- Cloud deployment
- Persistent analytics storage
- Multi-user support
- Improved model accuracy
- Production CI/CD workflow
- Full browser automation tests
- Model artifact storage with Git LFS or external artifact hosting

## Resume Highlights

- Built a full-stack sign language recognition web application with Flask, TensorFlow/Keras, OpenCV, MediaPipe, and SQLite.
- Implemented browser-based webcam capture and base64 frame streaming from JavaScript to a Flask REST API.
- Integrated a CNN inference pipeline for real-time gesture classification and confidence scoring.
- Used MediaPipe hand landmark detection and OpenCV preprocessing for hand-mask extraction and ROI preparation.
- Designed a responsive frontend with live recognition controls, prediction cards, text output, history, and analytics dashboard.
- Added text-to-speech support for converting generated gesture text into audio output.
- Implemented REST endpoints for recognition lifecycle, prediction, text-to-speech, statistics, history, and clearing session data.
- Added automated backend API tests and frontend integration contract tests.

## Troubleshooting

### Backend Does Not Start

Check that the virtual environment is active and dependencies are installed:

```powershell
backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m backend.app
```

### TensorFlow Or MediaPipe Install Fails

Use Python 3.11 on Windows. The dependency versions in `backend/requirements.txt` are pinned around TensorFlow/Keras 2.15.0.

### Model File Not Found

Verify:

```powershell
Test-Path backend\models\cnn_model_keras2.h5
```

### Database Not Found

Verify:

```powershell
Test-Path backend\data\database\gesture_db.db
```

### API Unavailable In Browser

Confirm Flask is running and open:

```text
http://127.0.0.1:5000/api/health
```

### Webcam Does Not Start

- Use `http://127.0.0.1:5000`.
- Allow browser camera permission.
- Close other applications using the webcam.
- Try Chrome or Edge.

## License

This project is provided under the MIT License. You may use, modify, and distribute the code with attribution. If this repository is published publicly, add a dedicated `LICENSE` file containing the full MIT License text.
