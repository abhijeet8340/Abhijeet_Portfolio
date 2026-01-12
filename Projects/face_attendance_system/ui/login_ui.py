import tkinter as tk
from tkinter import messagebox
from database import get_connection
from ui.dashboard_ui import open_dashboard
from ui.register_ui import open_register

def open_login():
    login = tk.Tk()
    login.title("Login")
    login.geometry("350x300")

    tk.Label(login, text="Login", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(login, text="Username").pack()
    username_entry = tk.Entry(login)
    username_entry.pack(pady=5)
    tk.Label(login, text="Password").pack()
    password_entry = tk.Entry(login, show="*")
    password_entry.pack(pady=5)

    def login_user():
        username = username_entry.get()
        password = password_entry.get()
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        db.close()
        if result:
            messagebox.showinfo("Success", "Login Successful")
            login.destroy()
            open_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    tk.Button(login, text="Login", command=login_user, width=20).pack(pady=10)
    tk.Button(login, text="Register", command=lambda:[login.destroy(), open_register()], width=20).pack()

    login.mainloop()
