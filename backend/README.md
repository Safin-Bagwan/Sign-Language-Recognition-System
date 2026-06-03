# Backend

Python backend and machine-learning runtime for the Sign Language Recognition System.

## Contents

```text
backend/
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

## Commands

Run these from the repository root:

```bash
python backend/app/create_gestures.py
python backend/app/Rotate_images.py
python backend/app/load_images.py
python backend/app/cnn_model_train.py
python backend/app/final.py
```

The scripts use `backend/app/paths.py`, so model, dataset, gesture, database, and artifact files resolve consistently from the backend directory.
