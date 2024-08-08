import cv2
import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

# Initialize the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_number TEXT NOT NULL,
    roll_number TEXT NOT NULL,
    image_path TEXT NOT NULL
)
''')

conn.commit()

def capture_image():
    # Get the roll number to name the image
    r_number = roll_number.get()
    if not r_number:
        messagebox.showerror("Error", "Roll number is required to capture image.")
        return

    # Directory to save images
    save_dir = "D:\\bproject"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # File path to save the image
    file_path = os.path.join(save_dir, f"{r_number}.png")

    # Open the default camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open video stream.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        messagebox.showerror("Error", "Failed to capture image.")
        return

    cv2.imwrite(file_path, frame)
    image_path.set(file_path)

    img = Image.open(file_path)
    img = img.resize((200, 200), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel.configure(image=img)
    panel.image = img

def save_to_db():
    w_number = whatsapp_number.get()
    r_number = roll_number.get()
    img_path = image_path.get()

    if not (w_number and r_number and img_path):
        messagebox.showerror("Error", "All fields are required.")
        return

    cursor.execute("INSERT INTO students (whatsapp_number, roll_number, image_path) VALUES (?, ?, ?)", (w_number, r_number, img_path))
    conn.commit()

    messagebox.showinfo("Success", "Data saved successfully.")

    # Clear fields
    whatsapp_number.set('')
    roll_number.set('')
    image_path.set('')
    panel.configure(image='')

# Set up the GUI
root = tk.Tk()
root.title("Student Information")

tk.Label(root, text="WhatsApp Number:").grid(row=0, column=0, padx=10, pady=5)
tk.Label(root, text="Roll Number:").grid(row=1, column=0, padx=10, pady=5)
tk.Label(root, text="Image:").grid(row=2, column=0, padx=10, pady=5)

whatsapp_number = tk.StringVar()
roll_number = tk.StringVar()
image_path = tk.StringVar()

tk.Entry(root, textvariable=whatsapp_number).grid(row=0, column=1, padx=10, pady=5)
tk.Entry(root, textvariable=roll_number).grid(row=1, column=1, padx=10, pady=5)
tk.Entry(root, textvariable=image_path, state='readonly').grid(row=2, column=1, padx=10, pady=5)

tk.Button(root, text="Capture Image", command=capture_image).grid(row=3, column=0, columnspan=2, padx=10, pady=5)
tk.Button(root, text="Save", command=save_to_db).grid(row=4, column=0, columnspan=2, padx=10, pady=5)

panel = tk.Label(root)
panel.grid(row=5, column=0, columnspan=2)

root.mainloop()

# Close the database connection
conn.close()
