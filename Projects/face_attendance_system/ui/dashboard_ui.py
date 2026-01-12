import tkinter as tk
from tkinter import messagebox
from face_recognition import capture_faces
from train_model import train_classifier
from attendance import mark_attendance
from attendance_viewer import open_attendance_viewer

def open_dashboard(username):
    dash = tk.Tk()
    dash.title(f"Dashboard - {username}")
    dash.geometry("420x480")

    tk.Label(dash, text=f"Welcome, {username}", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(dash, text="Student ID").pack()
    sid_entry = tk.Entry(dash)
    sid_entry.pack()
    tk.Label(dash, text="Name").pack()
    name_entry = tk.Entry(dash)
    name_entry.pack()

    def add_student():
        sid = sid_entry.get()
        name = name_entry.get()
        if sid == "" or name == "":
            messagebox.showwarning("Input Error", "Please enter both Student ID and Name")
        else:
            capture_faces(sid, name)
            messagebox.showinfo("Success", f"Faces captured for {name}")

    def train_model():
        train_classifier()
        messagebox.showinfo("Training", "Model Trained Successfully!")

    def take_attendance():
        mark_attendance()
        messagebox.showinfo("Done", "Attendance Marked Successfully!")

    tk.Button(dash, text="Add Student & Capture Faces", command=add_student, width=25).pack(pady=10)
    tk.Button(dash, text="Train Model", command=train_model, width=25).pack(pady=10)
    tk.Button(dash, text="Mark Attendance", command=take_attendance, width=25).pack(pady=10)
    tk.Button(dash, text="View Attendance Records", command=open_attendance_viewer, width=25).pack(pady=10)
    tk.Button(dash, text="Logout", command=lambda: [dash.destroy(), __import__('ui.login_ui').login_ui.open_login()]).pack(pady=20)

    dash.mainloop()
