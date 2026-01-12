import cv2
import os
from database import connect_db

def capture_faces(student_id, name):
    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    count = 0
    path = 'dataset'
    os.makedirs(path, exist_ok=True)

    while True:
        ret, frame = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            cv2.imwrite(f"{path}/User.{student_id}.{count}.jpg", gray[y:y+h, x:x+w])
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imshow('Capturing Faces (Press ESC to stop)', frame)

        if cv2.waitKey(1) & 0xFF == 27 or count >= 30:
            break

    cam.release()
    cv2.destroyAllWindows()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (student_id, name, image_count) VALUES (%s, %s, %s)", (student_id, name, count))
    conn.commit()
    conn.close()
    print(f"[INFO] Faces captured for {name}")
