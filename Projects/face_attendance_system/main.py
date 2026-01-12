# # main.py
# import tkinter as tk
# from tkinter import messagebox
# from face_recognition import capture_faces
# from train_model import train_classifier
# from attendance import mark_attendance
# from attendance_viewer import open_attendance_viewer

# # # main.py
# # from ui.login_ui import open_login

# # if __name__ == "__main__":
# #     open_login()


# def add_student():
#     sid = student_id_entry.get()
#     name = student_name_entry.get()
#     if sid == "" or name == "":
#         messagebox.showwarning("Input Error", "Please enter both Student ID and Name")
#         return
#     capture_faces(sid, name)
#     messagebox.showinfo("Success", f"Faces captured for {name}")

# def train_data():
#     train_classifier()
#     messagebox.showinfo("Training", "Training Complete")

# def take_attendance():
#     mark_attendance()
#     messagebox.showinfo("Attendance", "Attendance Marked Successfully")

# root = tk.Tk()
# root.title("Face Recognition Attendance System")
# root.geometry("400x400")

# tk.Label(root, text="Face Recognition Attendance System", font=("Arial", 14, "bold")).pack(pady=10)
# tk.Label(root, text="Student ID").pack()
# student_id_entry = tk.Entry(root)
# student_id_entry.pack()
# tk.Label(root, text="Name").pack()
# student_name_entry = tk.Entry(root)
# student_name_entry.pack()

# tk.Button(root, text="Add Student & Capture Faces", command=add_student).pack(pady=10)
# tk.Button(root, text="Train Model", command=train_data).pack(pady=10)
# tk.Button(root, text="Mark Attendance", command=take_attendance).pack(pady=10)


# root.mainloop()


import tkinter as tk
from tkinter import messagebox
from attendance_system import open_attendance_panel
from database import register_user, login_user

# === Root Window ===
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.state('zoomed')  # Full screen
root.config(bg="#1e1e2e")

# === Title ===
title = tk.Label(root, text="FACE RECOGNITION ATTENDANCE SYSTEM",
                 font=("Poppins", 26, "bold"), bg="#1e1e2e", fg="white")
title.pack(pady=50)

# === Login/Register Frame ===
frame = tk.Frame(root, bg="#2a2a40", padx=40, pady=40)
frame.pack(pady=50)

tk.Label(frame, text="Username", font=("Poppins", 14), bg="#2a2a40", fg="white").grid(row=0, column=0, sticky="w", pady=5)
username = tk.Entry(frame, font=("Poppins", 14), width=25)
username.grid(row=0, column=1, pady=5)

tk.Label(frame, text="Password", font=("Poppins", 14), bg="#2a2a40", fg="white").grid(row=1, column=0, sticky="w", pady=5)
password = tk.Entry(frame, font=("Poppins", 14), show="*", width=25)
password.grid(row=1, column=1, pady=5)

# === Button Styles ===
def style_button(text, command, color):
    return tk.Button(frame, text=text, font=("Poppins", 13, "bold"), bg=color, fg="white",
                     width=18, pady=8, relief="flat", cursor="hand2", command=command)

def do_login():
    if login_user(username.get(), password.get()):
        messagebox.showinfo("Login", "Login Successful!")
        root.destroy()
        open_attendance_panel()
    else:
        messagebox.showerror("Error", "Invalid credentials")

def do_register():
    if register_user(username.get(), password.get()):
        messagebox.showinfo("Success", "Registration successful!")
    else:
        messagebox.showerror("Error", "User already exists or invalid input")

login_btn = style_button("Login", do_login, "#0078d7")
register_btn = style_button("Register", do_register, "#28a745")

login_btn.grid(row=2, column=0, pady=20)
register_btn.grid(row=2, column=1, pady=20)

root.mainloop()
