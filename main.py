
import tkinter as tk
import json
from datetime import datetime
from pathlib import Path
import os
import sys
import tkinter.messagebox as messagebox

class LifeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.is_topmost = True
        self.root.wm_attributes("-topmost", self.is_topmost)
        self.root.geometry("+100+100")

        # Use a frame for better border control
        self.frame = tk.Frame(root, bg="lightgrey", bd=1, relief="solid")
        self.frame.pack()

        self.label = tk.Label(
            self.frame,
            font=("Helvetica", 16),
            bg="lightgrey",
            fg="black"
        )
        self.label.pack(padx=5, pady=5)

        # Bind events to both frame and label to catch all clicks
        for widget in [self.frame, self.label]:
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)
            widget.bind("<ButtonRelease-1>", self.on_release)
            widget.bind("<Button-3>", self.toggle_topmost)  # Right-click to toggle topmost

        if getattr(sys, 'frozen', False):
            application_path = Path(sys.executable).parent
        else:
            application_path = Path(__file__).parent
        self.config_path = application_path / "config.json"
        self.life_expectancy = self.load_life_expectancy()

        self.display_mode = "ymd"
        self.is_dragging = False
        self.after_id = None

        self.update_display()

    def load_life_expectancy(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return datetime.strptime(config["life_expectancy"], "%Y-%m-%d")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def update_display(self):
        # Cancel any pending update to avoid stacking calls
        if self.after_id:
            self.root.after_cancel(self.after_id)

        if self.life_expectancy:
            now = datetime.now()
            delta = self.life_expectancy - now

            if delta.total_seconds() <= 0:
                self.label.config(text="Congratulations!")
            else:
                days = delta.days
                if self.display_mode == "ymd":
                    years = days // 365
                    weeks = (days % 365) // 7
                    remaining_days = (days % 365) % 7
                    self.label.config(text=f"Life: {years}y {weeks}w {remaining_days}d")
                else:  # self.display_mode == "days"
                    self.label.config(text=f"Life: {days} days")
        else:
            self.label.config(text="Set your life expectancy in config.json")

        # Schedule the next update
        self.after_id = self.root.after(1000, self.update_display)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        self.is_dragging = False

    def do_move(self, event):
        self.is_dragging = True
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")


    def on_release(self, event):
        if not self.is_dragging:
            self.toggle_display()
        # Reset flag after any release
        self.is_dragging = False

    def toggle_display(self):
        if self.display_mode == "ymd":
            self.display_mode = "days"
        else:
            self.display_mode = "ymd"
        # Trigger an immediate update
        self.update_display()

    def toggle_topmost(self, event):
        self.is_topmost = not self.is_topmost
        self.root.wm_attributes("-topmost", self.is_topmost)

if __name__ == "__main__":
    # Create a lock file to prevent multiple instances
    # Note: This is a simple implementation. For more robust solutions,
    # consider using a library that handles atomic file locking.
    lock_file_path = Path(os.environ["TEMP"]).absolute() / "lifetracker.lock"

    try:
        # Exclusive creation mode ('x') raises FileExistsError if the file already exists.
        lock_file = open(lock_file_path, "x")
    except FileExistsError:
        # If the lock file already exists, another instance is running.
        # You can optionally show a message to the user.
        # For example, using a simple tkinter message box.
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        tk.messagebox.showinfo("LifeTracker", "LifeTracker is already running.")
        root.destroy()
        sys.exit(0)


    try:
        root = tk.Tk()
        app = LifeTrackerApp(root)
        root.mainloop()
    finally:
        # Clean up the lock file on exit
        lock_file.close()
        os.remove(lock_file_path)
