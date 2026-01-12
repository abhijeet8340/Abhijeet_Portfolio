# attendance_system.py
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import cv2
import os
import csv
from datetime import datetime, date
from PIL import Image
import numpy as np

# ------------------ Paths / Config ------------------
DATASET_DIR = "dataset"
TRAINER_DIR = "trainer"
TRAINER_FILE = os.path.join(TRAINER_DIR, "trainer.yml")
STUDENTS_FILE = "students.csv"            # stores mapping: student_id,name
ATTENDANCE_DIR = "attendance"
ATTENDANCE_FILE = os.path.join(ATTENDANCE_DIR, "attendance.csv")

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
SAMPLES_PER_PERSON = 30
CONFIDENCE_THRESHOLD = 70  # lower is more confident

# Ensure directories exist
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(TRAINER_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# ------------------ Utility functions ------------------
def read_students():
    """Return dict student_id(str) -> name"""
    mapping = {}
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    sid, name = row[0], row[1]
                    mapping[sid] = name
    return mapping

def append_student_to_file(student_id, name):
    # Avoid duplicate entries
    mapping = read_students()
    if student_id in mapping:
        return
    with open(STUDENTS_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([student_id, name])

def ensure_attendance_file():
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "name", "date", "time"])

def append_attendance(student_id, name, date_str, time_str):
    ensure_attendance_file()
    with open(ATTENDANCE_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([student_id, name, date_str, time_str])

# ------------------ Face Capture ------------------
def capture_faces_interactive(student_id, name, samples=SAMPLES_PER_PERSON):
    """Open webcam and save face images for given student_id"""
    detector = cv2.CascadeClassifier(CASCADE_PATH)
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Webcam Error", "Cannot open webcam. Check camera and try again.")
        return False

    count = 0
    messagebox.showinfo("Capture", f"Ready to capture {samples} face samples for {name}. Press ESC to stop early.")
    while True:
        ret, img = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            filename = os.path.join(DATASET_DIR, f"User.{student_id}.{count}.jpg")
            cv2.imwrite(filename, face_img)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(img, f"{count}/{samples}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        cv2.imshow(f"Capturing faces for {name} - ESC to stop", img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27 or count >= samples:
            break

    cam.release()
    cv2.destroyAllWindows()
    if count == 0:
        messagebox.showerror("Capture Failed", "No faces were captured.")
        return False
    messagebox.showinfo("Capture Complete", f"Captured {count} samples for {name}.")
    return True

# ------------------ Training ------------------
def train_recognizer():
    image_paths = [os.path.join(DATASET_DIR, f) for f in os.listdir(DATASET_DIR)
                   if f.endswith(".jpg") or f.endswith(".png")]
    if not image_paths:
        messagebox.showwarning("No Data", "No face images found in dataset/. Capture faces first.")
        return

    detector = cv2.CascadeClassifier(CASCADE_PATH)
    face_samples = []
    ids = []
    for path in image_paths:
        try:
            img = Image.open(path).convert('L')
            img_np = np.array(img, 'uint8')
            # filename format: User.<student_id>.<count>.jpg
            namepart = os.path.basename(path).split(".")
            if len(namepart) < 3:
                continue
            student_id = namepart[1]
            faces = detector.detectMultiScale(img_np)
            for (x, y, w, h) in faces:
                face_samples.append(img_np[y:y+h, x:x+w])
                ids.append(int(student_id))
        except Exception as e:
            print("Skipping", path, e)

    if not face_samples:
        messagebox.showerror("Training Failed", "No faces found in dataset images.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(face_samples, np.array(ids))
    recognizer.write(TRAINER_FILE)
    messagebox.showinfo("Training Complete", f"Trained on {len(set(ids))} people. Model saved to {TRAINER_FILE}")

# ------------------ Mark Attendance ------------------
def mark_attendance_live():
    if not os.path.exists(TRAINER_FILE):
        messagebox.showwarning("No Model", "Trainer not found. Train model first.")
        return

    students = read_students()  # mapping str->name
    # invert mapping: numeric id -> name
    id_to_name = {int(k): v for k, v in students.items()}

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_FILE)
    detector = cv2.CascadeClassifier(CASCADE_PATH)

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Webcam Error", "Cannot open webcam.")
        return

    today = date.today().isoformat()
    already_marked = set()  # store student_id strings marked during this session or across file
    # Load already-marked from file for today
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 3 and row[2] == today:
                    already_marked.add(row[0])

    font = cv2.FONT_HERSHEY_SIMPLEX
    messagebox.showinfo("Attendance", "Opening camera to mark attendance. Press ESC to stop.")
    while True:
        ret, img = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            try:
                pred_id, confidence = recognizer.predict(face_img)
            except Exception as e:
                # sometimes face region is too small; skip
                continue

            if confidence < CONFIDENCE_THRESHOLD:
                name = id_to_name.get(pred_id, f"ID:{pred_id}")
                label = f"{name} ({pred_id})"
                # Mark attendance if not already marked
                if str(pred_id) not in already_marked:
                    now = datetime.now()
                    date_str = now.date().isoformat()
                    time_str = now.time().strftime("%H:%M:%S")
                    append_attendance(str(pred_id), name, date_str, time_str)
                    already_marked.add(str(pred_id))
                    print(f"Marked attendance: {pred_id} - {name} at {time_str}")
                else:
                    # already marked today
                    pass
                status_text = "Present"
            else:
                label = "Unknown"
                status_text = ""

            # draw rectangle + text
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0) if status_text else (0,0,255), 2)
            cv2.putText(img, label, (x, y-10), font, 0.7, (255,255,255), 2)
            if status_text:
                cv2.putText(img, status_text, (x, y+h+20), font, 0.6, (255,255,255), 1)

        cv2.imshow("Mark Attendance - ESC to stop", img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Done", "Attendance session finished.")

# ------------------ UI: main panel ------------------
def open_attendance_panel():
    panel = tk.Tk()
    panel.title("Face Recognition Attendance System")
    panel.state('zoomed')  # full-screen
    panel.config(bg="#1b1b2f")

    # Title
    title = tk.Label(panel, text="FACE RECOGNITION ATTENDANCE SYSTEM",
                     font=("Arial", 26, "bold"), bg="#1b1b2f", fg="white")
    title.pack(pady=30)

    # Input frame
    frame = tk.Frame(panel, bg="#2a2a40", padx=20, pady=20)
    frame.pack(pady=10)

    tk.Label(frame, text="Student ID", font=("Arial", 12), bg="#2a2a40", fg="white").grid(row=0, column=0, pady=8)
    sid_entry = tk.Entry(frame, font=("Arial", 12), width=30)
    sid_entry.grid(row=0, column=1, pady=8, padx=10)

    tk.Label(frame, text="Name", font=("Arial", 12), bg="#2a2a40", fg="white").grid(row=1, column=0, pady=8)
    name_entry = tk.Entry(frame, font=("Arial", 12), width=30)
    name_entry.grid(row=1, column=1, pady=8, padx=10)

    # Buttons
    def on_add_student():
        sid = sid_entry.get().strip()
        name = name_entry.get().strip()
        if not sid or not name:
            # allow interactive prompt if empty
            sid = simpledialog.askstring("Student ID", "Enter Student ID:")
            if not sid:
                return
            name = simpledialog.askstring("Student Name", "Enter Student Name:")
            if not name:
                return
        append_student_to_file(sid, name)
        ok = capture_faces_interactive(sid, name, samples=SAMPLES_PER_PERSON)
        if ok:
            messagebox.showinfo("Saved", f"Student {name} ({sid}) images saved.")
        sid_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)

    def on_train():
        train_recognizer()

    def on_mark():
        mark_attendance_live()

    def on_view():
        # reuse small viewer window
        view_win = tk.Toplevel(panel)
        view_win.title("Attendance Records")
        view_win.geometry("900x500")
        view_win.config(bg="#2a2a40")

        tk.Label(view_win, text="Attendance Records", font=("Arial", 18, "bold"),
                 bg="#2a2a40", fg="white").pack(pady=10)

        cols = ("student_id", "name", "date", "time")
        tree = ttk.Treeview(view_win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.title())
            tree.column(c, width=200, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        if os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    tree.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("No Data", "No attendance data found yet.")

    btn_frame = tk.Frame(panel, bg="#1b1b2f")
    btn_frame.pack(pady=40)

    btn_style = {"font": ("Arial", 12, "bold"), "fg": "white", "width": 24, "height": 2, "relief": "flat"}

    tk.Button(btn_frame, text="Add Student & Capture Faces", bg="#0078d7", command=on_add_student, **btn_style).grid(row=0, column=0, padx=12, pady=8)
    tk.Button(btn_frame, text="Train Model", bg="#28a745", command=on_train, **btn_style).grid(row=0, column=1, padx=12, pady=8)
    tk.Button(btn_frame, text="Mark Attendance", bg="#ff9800", command=on_mark, **btn_style).grid(row=1, column=0, padx=12, pady=8)
    tk.Button(btn_frame, text="View Attendance", bg="#6f42c1", command=on_view, **btn_style).grid(row=1, column=1, padx=12, pady=8)

    # Logout/close
    def do_exit():
        panel.destroy()

    tk.Button(panel, text="Exit", bg="#dc3545", command=do_exit, **btn_style).pack(pady=20)

    panel.mainloop()

# If this file is run directly, open the panel
if __name__ == "__main__":
    open_attendance_panel()
