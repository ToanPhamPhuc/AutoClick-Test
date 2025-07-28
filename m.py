import customtkinter as ctk
import threading
import time
import keyboard
import mouse
import json
import os
from tkinter import messagebox
from pynput.mouse import Button, Controller

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AutoClickerApp(ctk.CTk):
    # ... (keeping existing methods like load_hotkey, save_hotkey, __init__, only_int, _build_ui, etc. unchanged)

    def get_interval(self):
        try:
            hours = int(self.hours.get() or 0)
            mins = int(self.mins.get() or 0)
            secs = int(self.secs.get() or 0)
            ms = int(self.ms.get() or 0)
            if hours < 0 or mins < 0 or secs < 0 or ms < 0:
                return 0.1
            total_ms = hours * 3600 * 1000 + mins * 60 * 1000 + secs * 1000 + ms
            # Cap minimum interval at 2ms to aim for >40 CPS (1000/2 = 500 CPS max)
            return max(total_ms / 1000, 0.002)  # Convert to seconds, min 2ms
        except ValueError:
            return 0.1

    def get_position(self):
        if self.position_var.get() == "Pick location":
            try:
                x = int(self.x_entry.get() or 0)
                y = int(self.y_entry.get() or 0)
                return (x, y)
            except ValueError:
                return None
        return None

    def perform_clicks(self):
        interval = self.get_interval()
        count = float('inf') if self.repeat_var.get() == "Repeat until stopped" else int(self.repeat_times.get() or 1)
        button = self.mouse_button.get()
        click_type = 2 if self.click_type.get() == "Double" else 1
        position = self.get_position()
        mouse_controller = Controller()

        self.start_time = time.perf_counter_ns()
        clicks = 0
        next_time = time.perf_counter_ns()

        while self.running and clicks < count:
            current_time = time.perf_counter_ns()
            if position:
                mouse_controller.position = position
            button_map = {'Left': Button.left, 'Right': Button.right, 'Middle': Button.middle}
            for _ in range(click_type):
                mouse_controller.click(button_map[button])
            clicks += click_type
            target_time = next_time + int(interval * 1e9)
            while time.perf_counter_ns() < target_time:
                pass
            next_time = target_time
            if (time.perf_counter_ns() - self.start_time) / 1e9 >= 0.5:
                self.update_cps(clicks)
            if (time.perf_counter_ns() - self.start_time) / 1e9 > 3600:
                self.stop_clicking()
                messagebox.showwarning("Warning", "Clicking stopped after 1 hour for safety.")
                break

        self.update_cps(clicks)
        self.stop_clicking()

    def update_cps(self, clicks):
        elapsed = (time.perf_counter_ns() - self.start_time) / 1e9
        cps = clicks / elapsed if elapsed > 0 else 0.0
        self.cps_label.configure(text=f"CPS: {cps:.1f}")
        self.status_label.configure(text=f"Status: Clicking at {clicks} clicks")

    # ... (keeping existing methods like start_clicking, stop_clicking, set_hotkey, hotkey_listener, etc. unchanged)

if __name__ == '__main__':
    app = AutoClickerApp()
    app.mainloop()