import numpy as np
import pickle
import cv2, os
from glob import glob
import tensorflow as tf
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import backend as K

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def get_image_size():
    img_files = glob('gestures/*/*.jpg')
    if not img_files:
        return (50, 50)
    img = cv2.imread(img_files[0], 0)
    return img.shape

image_x, image_y = get_image_size()

def cnn_model(num_of_classes):
    print(f"DEBUG: Creating model for {num_of_classes} classes.")
    model = Sequential()
    model.add(Conv2D(16, (2,2), input_shape=(image_x, image_y, 1), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same'))
    model.add(Conv2D(32, (3,3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(3, 3), padding='same'))
    model.add(Conv2D(64, (5,5), activation='relu'))
    model.add(MaxPooling2D(pool_size=(5, 5), strides=(5, 5), padding='same'))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(num_of_classes, activation='softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    filepath="cnn_model_keras2.h5"
    checkpoint1 = ModelCheckpoint(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint1]
    return model, callbacks_list

def train():
    print("DEBUG: Loading data...")
    try:
        with open("train_images", "rb") as f:
            train_images = np.array(pickle.load(f))
        with open("train_labels", "rb") as f:
            train_labels = np.array(pickle.load(f), dtype=np.int32)

        with open("val_images", "rb") as f:
            val_images = np.array(pickle.load(f))
        with open("val_labels", "rb") as f:
            val_labels = np.array(pickle.load(f), dtype=np.int32)
    except FileNotFoundError:
        print("ERROR: Training data files not found. Run load_images.py first.")
        return

    # Determine number of classes from labels
    num_of_classes = int(max(np.max(train_labels), np.max(val_labels)) + 1)
    print(f"DEBUG: Detected {num_of_classes} classes from data.")

    # Normalize images
    train_images = train_images / 255.0
    val_images = val_images / 255.0

    train_images = np.reshape(train_images, (train_images.shape[0], image_x, image_y, 1))
    val_images = np.reshape(val_images, (val_images.shape[0], image_x, image_y, 1))
    train_labels = to_categorical(train_labels, num_classes=num_of_classes)
    val_labels = to_categorical(val_labels, num_classes=num_of_classes)

    model, callbacks_list = cnn_model(num_of_classes)
    model.summary()
    
    model.fit(train_images, train_labels, validation_data=(val_images, val_labels), epochs=10, batch_size=64, callbacks=callbacks_list)
    
    scores = model.evaluate(val_images, val_labels, verbose=0)
    print("CNN Accuracy: %.2f%%" % (scores[1]*100))
    model.save('cnn_model_keras2.h5')
    print("SUCCESS: Model saved as 'cnn_model_keras2.h5'")

if __name__ == "__main__":
    train()
    K.clear_session()
