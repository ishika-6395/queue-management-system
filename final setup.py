import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
from datetime import datetime
from PIL import Image, ImageTk

class QueueSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Queue Management System")
        self.root.geometry("400x550")
        self.root.configure(bg="#ADD8E6")  # Light Blue Background

        # Database connection
        self.conn = sqlite3.connect("queue_system.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Load and resize logo image using PIL
        self.logo_image = Image.open(r"C:\Users\jaini\OneDrive\Desktop\queue management\logo.png")
        self.logo_image = self.logo_image.resize((80, 80), Image.LANCZOS)  # Resize to 80x80 pixels
        self.logo = ImageTk.PhotoImage(self.logo_image)

        # Heading with logo
        header_frame = tk.Frame(root, bg="#ADD8E6")
        header_frame.pack(pady=10)
        tk.Label(header_frame, image=self.logo, bg="#ADD8E6").pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Welcome to Queue System", font=("Arial", 14, "bold"), background="#ADD8E6").pack(side=tk.LEFT)

        # Username
        username_frame = tk.Frame(root, bg="#FFE4B5")  # Moccasin Background
        username_frame.pack(pady=5)
        ttk.Label(username_frame, text="Username:", font=("Arial", 12), background="#FFE4B5").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.RIGHT)

        # Password
        password_frame = tk.Frame(root, bg="#FFE4B5")  # Moccasin Background
        password_frame.pack(pady=5)
        ttk.Label(password_frame, text="Password:", font=("Arial", 12), background="#FFE4B5").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.RIGHT)

        # Buttons
        ttk.Button(root, text="Login", command=self.login).pack(pady=5)
        ttk.Button(root, text="Register", command=self.register).pack(pady=5)

    def create_tables(self):
        """Creates necessary tables if they don't exist"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                service_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                token_number INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Login Failed", "Please enter both username and password.")
            return

        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()

        if user:
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.open_dashboard(username)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Registration Failed", "Please enter a username and password.")
            return

        try:
            self.cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, 0))
            self.conn.commit()
            messagebox.showinfo("Registration Successful", "You can now log in.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Username already exists.")

    def open_dashboard(self, username):
        self.root.withdraw()
        dashboard = tk.Toplevel()
        dashboard.title("User Dashboard")
        dashboard.geometry("400x500")
        dashboard.configure(bg="#E6E6FA")  # Lavender Background

        # Heading with logo
        header_frame = tk.Frame(dashboard, bg="#E6E6FA")
        header_frame.pack(pady=10)
        tk.Label(header_frame, image=self.logo, bg="#E6E6FA").pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"Welcome, {username}!", font=("Arial", 14, "bold"), background="#E6E6FA").pack(side=tk.LEFT)

        # Service Type
        service_frame = tk.Frame(dashboard, bg="#FFFACD")  # Lemon Chiffon Background
        service_frame.pack(pady=5)
        ttk.Label(service_frame, text="Select Service:", font=("Arial", 12), background="#FFFACD").pack(side=tk.LEFT)
        self.service_var = tk.StringVar()
        service_dropdown = ttk.Combobox(service_frame, textvariable=self.service_var, values=["Bank", "Hospital"])
        service_dropdown.pack(side=tk.RIGHT)

        # Date Selection (Prevent Past Dates)
        date_frame = tk.Frame(dashboard, bg="#FFFACD")  # Lemon Chiffon Background
        date_frame.pack(pady=5)
        ttk.Label(date_frame, text="Select Date:", font=("Arial", 12), background="#FFFACD").pack(side=tk.LEFT)
        self.date_entry = DateEntry(date_frame, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd", mindate=datetime.today())
        self.date_entry.pack(side=tk.RIGHT)

        # Time Entry (24-hour format)
        time_frame = tk.Frame(dashboard, bg="#FFFACD")  # Lemon Chiffon Background
        time_frame.pack(pady=5)
        ttk.Label(time_frame, text="Enter Time (HH:MM, 24-hour format):", font=("Arial", 12), background="#FFFACD").pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(time_frame)
        self.time_entry.pack(side=tk.RIGHT)

        ttk.Button(dashboard, text="Confirm Booking", command=lambda: self.confirm_booking(username)).pack(pady=10)
        ttk.Button(dashboard, text="View My Stats", command=lambda: self.view_user_stats(username)).pack(pady=5)
        ttk.Button(dashboard, text="Logout", command=lambda: self.logout(dashboard)).pack(pady=10)

    def confirm_booking(self, username):
        service_type = self.service_var.get()
        date = self.date_entry.get()
        time = self.time_entry.get().strip()

        # Validate 24-hour time format
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showwarning("Invalid Time", "Please enter time in HH:MM 24-hour format.")
            return

        if not service_type or not date or not time:
            messagebox.showwarning("Booking Failed", "Please select a service type, date, and enter time.")
            return

        self.cursor.execute("SELECT COUNT(*) FROM bookings")
        token_number = self.cursor.fetchone()[0] + 1

        self.cursor.execute("INSERT INTO bookings (username, service_type, date, time, token_number) VALUES (?, ?, ?, ?, ?)",
                            (username, service_type, date, time, token_number))
        self.conn.commit()

        messagebox.showinfo("Booking Confirmed", f"Your token number is {token_number}")

    def view_user_stats(self, username):
        self.cursor.execute("SELECT date, COUNT(*) FROM bookings WHERE username = ? GROUP BY date", (username,))
        bookings = self.cursor.fetchall()

        if not bookings:
            messagebox.showinfo("My Stats", "No bookings yet.")
            return

        dates = [b[0] for b in bookings]
        counts = [b[1] for b in bookings]

        plt.figure(figsize=(6, 6))
        plt.bar(dates, counts, color=['#ff9999','#66b3ff','#99ff99'])
        plt.xlabel("Date")
        plt.ylabel("Number of Bookings")
        plt.title(f"{username}'s Booking History")
        plt.xticks(rotation=45)
        plt.show()

    def logout(self, dashboard):
        dashboard.destroy()
        self.root.deiconify()
        self.clear_entries()
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")

    def clear_entries(self):
        """Clears the entry fields"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

# Run Application
if __name__ == "__main__":
    root = tk.Tk()
    app = QueueSystem(root)
    root.mainloop()
