import cv2
import numpy as np
from PIL import Image
import os

def train_classifier():
    data_dir = 'dataset'
    faces = []
    ids = []

    for file in os.listdir(data_dir):
        if file.endswith(".jpg"):
            path = os.path.join(data_dir, file)
            img = Image.open(path).convert('L')
            image_np = np.array(img, 'uint8')
            id = int(file.split('.')[1])
            faces.append(image_np)
            ids.append(id)

    ids = np.array(ids)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, ids)
    os.makedirs('trainer', exist_ok=True)
    recognizer.save('trainer/trainer.yml')
    print("[INFO] Training complete. Model saved as trainer.yml")
