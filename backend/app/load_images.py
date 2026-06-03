import cv2
from glob import glob
import numpy as np
import random
from sklearn.utils import shuffle
import pickle
import os
from pathlib import Path
from paths import DATASETS_DIR, GESTURES_DIR, ensure_directories

def pickle_images_labels():
    ensure_directories()
    images_labels = []
    # Find all .jpg files inside the gestures directory
    images = glob(str(GESTURES_DIR / "*" / "*.jpg"))
    
    if not images:
        print("CRITICAL ERROR: No images found in the 'gestures' folder. Did you capture any?")
        return None
        
    images.sort()
    print(f"DEBUG: Found {len(images)} total images. Processing...")
    
    for image in images:
        # Extract label from the parent folder name (e.g., 'gestures/1/100.jpg' -> '1')
        label = Path(image).parent.name
        img = cv2.imread(image, 0)
        
        if img is None:
            print(f"  Warning: Skipping unreadable image {image}")
            continue
            
        images_labels.append((np.array(img, dtype=np.uint8), int(label)))
    
    return images_labels

images_labels = pickle_images_labels()

if images_labels:
    print("DEBUG: Shuffling and splitting data...")
    images_labels = shuffle(shuffle(shuffle(shuffle(images_labels))))
    images, labels = zip(*images_labels)
    total_count = len(images_labels)
    print(f"SUCCESS: Processed {total_count} images.")

    # Data split: 5/6 Train, 1/12 Test, 1/12 Val
    train_end = int(5/6 * total_count)
    test_end = int(11/12 * total_count)

    print(f"DEBUG: Splitting: {train_end} Train, {test_end - train_end} Test, {total_count - test_end} Val")

    # Save training set
    with open(DATASETS_DIR / "train_images", "wb") as f:
        pickle.dump(images[:train_end], f)
    with open(DATASETS_DIR / "train_labels", "wb") as f:
        pickle.dump(labels[:train_end], f)
    print("SUCCESS: Saved training data.")

    # Save testing set
    with open(DATASETS_DIR / "test_images", "wb") as f:
        pickle.dump(images[train_end:test_end], f)
    with open(DATASETS_DIR / "test_labels", "wb") as f:
        pickle.dump(labels[train_end:test_end], f)
    print("SUCCESS: Saved testing data.")

    # Save validation set
    with open(DATASETS_DIR / "val_images", "wb") as f:
        pickle.dump(images[test_end:], f)
    with open(DATASETS_DIR / "val_labels", "wb") as f:
        pickle.dump(labels[test_end:], f)
    print("SUCCESS: Saved validation data.")
else:
    print("ERROR: Data processing aborted due to missing images.")
