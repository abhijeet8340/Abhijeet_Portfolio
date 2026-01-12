import tkinter as tk
from tkinter import messagebox
from database import get_connection
from ui.login_ui import open_login

def open_register():
    reg = tk.Tk()
    reg.title("Register")
    reg.geometry("350x300")

    tk.Label(reg, text="Register", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(reg, text="Username").pack()
    username_entry = tk.Entry(reg)
    username_entry.pack(pady=5)
    tk.Label(reg, text="Password").pack()
    password_entry = tk.Entry(reg, show="*")
    password_entry.pack(pady=5)

    def register_user():
        username = username_entry.get()
        password = password_entry.get()
        db = get_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            messagebox.showinfo("Success", "Registration Successful!")
            reg.destroy()
            open_login()
        except:
            messagebox.showerror("Error", "Username already exists!")
        db.close()

    tk.Button(reg, text="Register", command=register_user, width=20).pack(pady=10)
    tk.Button(reg, text="Back to Login", command=lambda:[reg.destroy(), open_login()], width=20).pack()

    reg.mainloop()
