import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

def open_attendance_viewer():
    viewer = tk.Toplevel()
    viewer.title("Attendance Viewer")
    viewer.geometry("700x400")

    folder = "attendance"
    if not os.path.exists(folder):
        messagebox.showerror("Error", "No attendance folder found.")
        viewer.destroy()
        return

    files = [f for f in os.listdir(folder) if f.endswith('.csv') or f.endswith('.xlsx')]
    if not files:
        messagebox.showerror("Error", "No attendance files found.")
        viewer.destroy()
        return

    selected_file = tk.StringVar(value=files[0])

    def load_file():
        file_path = os.path.join(folder, selected_file.get())
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            for row in tree.get_children():
                tree.delete(row)

            for _, row in df.iterrows():
                tree.insert('', tk.END, values=list(row))

        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")

    tk.Label(viewer, text="Select Attendance File:", font=("Arial", 11, "bold")).pack(pady=5)
    tk.OptionMenu(viewer, selected_file, *files).pack(pady=5)
    tk.Button(viewer, text="Load Attendance", command=load_file).pack(pady=5)

    columns = ("Student_ID", "Name", "Date", "Time", "Status")
    tree = ttk.Treeview(viewer, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor=tk.CENTER)

    tree.pack(expand=True, fill='both', pady=10)

    viewer.mainloop()
