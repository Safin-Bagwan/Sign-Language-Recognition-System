# Sign Language Recognition System

An AI-powered Sign Language Recognition System that translates hand gestures into real-time text and speech. Built using **TensorFlow**, **Keras**, **MediaPipe**, and **OpenCV**, this project enables accurate gesture recognition and improves communication accessibility for hearing-impaired individuals.

---

## 👨‍💻 Author

**Safin Bagwan**

🔗 GitHub Repository:
https://github.com/Safin-Bagwan/Sign-Language-Recognition-System

---

## 📖 Project Overview

The Sign Language Recognition System is a deep learning-based assistive technology project designed to bridge communication gaps between sign language users and the general public. The system uses Computer Vision and a Convolutional Neural Network (CNN) to recognize hand gestures in real time and convert them into text and speech.

By combining MediaPipe hand tracking, OpenCV image processing, and TensorFlow/Keras deep learning models, the system provides an accurate and user-friendly solution for sign language interpretation.

---

## 🚀 Features

* Real-time hand gesture recognition
* Text-to-speech conversion
* MediaPipe-based hand tracking
* CNN-powered gesture classification
* Custom gesture creation and training
* SQLite database integration
* User-friendly interface with live predictions
* Supports sentence formation and speech output

---

## 🛠️ Technologies Used

* Python
* TensorFlow
* Keras
* OpenCV
* MediaPipe
* SQLite
* NumPy
* Scikit-learn
* Pyttsx3

---

## ⚙️ System Workflow

### 1. Data Collection

Users capture hand gesture images using a webcam.

### 2. Image Processing

OpenCV and MediaPipe isolate and preprocess hand regions.

### 3. Model Training

A CNN model is trained on gesture datasets.

### 4. Real-Time Prediction

The trained model predicts gestures from live webcam input.

### 5. Text & Speech Output

Recognized gestures are converted into text and spoken aloud using Text-to-Speech technology.

---

## 📂 Project Structure

```text
Sign-Language-Recognition-System/
│
├── Code/
│   ├── create_gestures.py
│   ├── load_images.py
│   ├── cnn_model_train.py
│   ├── final.py
│   └── Rotate_images.py
│
├── gestures/
├── cnn_model_keras2.h5
├── gesture_db.db
├── requirements.txt
├── README.md
├── train_images
├── train_labels
├── test_images
├── test_labels
├── val_images
└── val_labels
```

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/Safin-Bagwan/Sign-Language-Recognition-System.git
cd Sign-Language-Recognition-System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Step 1: Capture Gesture Data

```bash
python Code/create_gestures.py
```

* Enter a unique gesture ID.
* Enter a gesture name.
* Press **C** to start image capture.

### Step 2: Augment Images (Optional)

```bash
python Code/Rotate_images.py
```

### Step 3: Prepare Dataset

```bash
python Code/load_images.py
```

### Step 4: Train CNN Model

```bash
python Code/cnn_model_train.py
```

The trained model will be saved as:

```text
cnn_model_keras2.h5
```

### Step 5: Run Real-Time Recognition

```bash
python Code/final.py
```

---

## 🎮 Controls

| Key   | Function                |
| ----- | ----------------------- |
| q     | Quit Application        |
| c     | Clear Current Sentence  |
| s     | Speak Current Sentence  |
| Space | Add Space Between Words |

---

## 🧠 Model Details

* Model Type: Convolutional Neural Network (CNN)
* Input Size: 50 × 50 grayscale images
* Framework: TensorFlow/Keras
* Hand Detection: MediaPipe
* Classification Output: Gesture ID mapped through SQLite database

---

## 📈 Future Improvements

* Support for complete sign language sentences
* Transformer-based gesture recognition models
* Mobile application deployment
* Cloud-based model serving
* Multi-language text-to-speech support

---

## 🎯 Applications

* Assistive technology for hearing-impaired individuals
* Educational sign language learning tools
* Human-computer interaction systems
* Accessibility solutions in public services

---

## 📄 License

This project is developed for educational and research purposes.

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub:

https://github.com/Safin-Bagwan/Sign-Language-Recognition-System
