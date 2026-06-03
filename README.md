# Sign Language Recognition System

This repository is organized as a full-stack project.

## Project Structure

```text
Sign-Language-Recognition-System/
├── backend/
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
│   ├── requirements.txt
│   └── README.md
└── frontend/
    └── README.md
```

## Parts

- `backend/` contains the existing Python, OpenCV, MediaPipe, TensorFlow/Keras, SQLite, and text-to-speech code.
- `frontend/` is reserved for the web UI that will be developed next.

See `backend/README.md` for backend setup and run commands.
