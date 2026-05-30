# Sign Language Interpreter using Deep Learning

An end-to-end sign language recognition system that uses Computer Vision and Deep Learning (CNN) to interpret hand gestures in real-time and convert them into text and speech.

## 🚀 Features
- **Real-time Recognition**: Instant interpretation of hand gestures via webcam.
- **Deep Learning Model**: Utilizes a Convolutional Neural Network (CNN) trained on thousands of images.
- **MediaPipe Integration**: Precise hand landmark detection and tracking.
- **Text-to-Speech (TTS)**: Audible output of recognized gestures.
- **Database Driven**: Uses SQLite to map model predictions to gesture names.
- **Custom Gesture Support**: Scripts included to create, train, and expand the gesture library.

## 🛠️ Tech Stack
- **Language**: Python 3.11
- **Deep Learning**: TensorFlow, Keras
- **Computer Vision**: OpenCV, MediaPipe
- **Database**: SQLite3
- **Audio**: pyttsx3 / Windows PowerShell SAPI

## 📂 Project Structure
```text
├── Code/
│   ├── final.py                # Main application script
│   ├── create_gestures.py      # Capture new gesture data
│   ├── cnn_model_train.py      # Train the CNN model
│   ├── set_hand_histogram.py   # Set skin color histogram for segmentation
│   ├── load_images.py          # Data preprocessing
│   └── display_gestures.py     # Utility to view captured data
├── gestures/                   # Dataset directory (per-class folders)
├── gesture_db.db               # SQLite database mapping IDs to names
├── cnn_model_keras2.h5         # Pre-trained CNN model
└── hist                        # Pickled skin color histogram
```

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/sign-language-interpreter.git
cd sign-language-interpreter
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 📖 How to Use

### Running the Interpreter
To start the real-time recognition:
```bash
python Code/final.py
```
- The application will open your webcam.
- Place your hand within the designated area.
- The system will predict the gesture and speak the output.

### Adding New Gestures
1. **Set Histogram**: Run `python Code/set_hand_histogram.py` to calibrate for your skin tone (press 'c' to capture, 's' to save).
2. **Capture Data**: Run `python Code/create_gestures.py` to record new images for a specific gesture.
3. **Train Model**: Run `python Code/cnn_model_train.py` to retrain the network with your new data.

## 👥 Authors
- **Safin Bagwan**
