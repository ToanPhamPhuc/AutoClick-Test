import customtkinter as ctk
import pyautogui
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
    def load_hotkey(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    hotkey = data.get("hotkey", "f6")
                    if not hotkey:
                        return "f6"
                    return hotkey
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hotkey settings: {e}")
            return "f6"

    def save_hotkey(self):
        try:
            with open("settings.json", "w") as f:
                json.dump({"hotkey": self.hotkey}, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save hotkey settings: {e}")

    def __init__(self):
        super().__init__()
        self.title("Stopped - Auto Clicker (Python)")
        self.attributes('-topmost', True)
        self.geometry("600x550")
        self.resizable(False, False)

        self.running = False
        self.hotkey = self.load_hotkey() or "f6"
        self.listener_should_restart = False
        self.listener_thread = None
        self.start_time = 0

        self._build_ui() #TODO
        self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.listener_thread.start()

    def only_int(self, P):
        if P == "" or (P.isdigit() and int(P) >= 0):
            return True
        return False

    def _build_ui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        vcmd = (self.register(self.only_int), '%P')

        # === Click Interval ===
        interval_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        interval_frame.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(interval_frame, text="Click interval", font=("Segoe UI", 11, "bold")).pack(anchor='w', padx=10, pady=(5, 0))
        row1 = ctk.CTkFrame(interval_frame)
        row1.pack(padx=10, pady=5)
        self.hours = ctk.CTkEntry(row1, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.mins = ctk.CTkEntry(row1, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.secs = ctk.CTkEntry(row1, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.ms = ctk.CTkEntry(row1, width=80, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.hours.insert(0, "0")
        self.mins.insert(0, "0")
        self.secs.insert(0, "0")
        self.ms.insert(0, "9")
        self.hours.pack(side='left', padx=(5, 2))
        ctk.CTkLabel(row1, text="hours", font=("Segoe UI", 11)).pack(side='left')
        self.mins.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(row1, text="mins", font=("Segoe UI", 11)).pack(side='left')
        self.secs.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(row1, text="secs", font=("Segoe UI", 11)).pack(side='left')
        self.ms.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(row1, text="milliseconds", font=("Segoe UI", 11)).pack(side='left')

        # === Click Options ===
        options_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        options_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(options_frame, text="Click options", font=("Segoe UI", 11, "bold")).pack(anchor='w', padx=10, pady=(5, 0))
        options_inner = ctk.CTkFrame(options_frame)
        options_inner.pack(padx=10, pady=5, fill='x')
        ctk.CTkLabel(options_inner, text="Mouse button:", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        self.mouse_button = ctk.CTkOptionMenu(options_inner, values=["Left", "Right", "Middle"], width=80, font=("Segoe UI", 11))
        self.mouse_button.set("Left")
        self.mouse_button.pack(side='left', padx=(0, 20))
        ctk.CTkLabel(options_inner, text="Click type:", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        self.click_type = ctk.CTkOptionMenu(options_inner, values=["Single", "Double"], width=80, font=("Segoe UI", 11))
        self.click_type.set("Single")
        self.click_type.pack(side='left')

        # === Click Repeat ===
        repeat_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        repeat_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(repeat_frame, text="Click repeat", font=("Segoe UI", 11, "bold")).pack(anchor='w', padx=10, pady=(5, 0))
        repeat_inner = ctk.CTkFrame(repeat_frame)
        repeat_inner.pack(padx=10, pady=5, fill='x')
        self.repeat_var = ctk.StringVar(value="Repeat until stopped")
        self.repeat_radio = ctk.CTkRadioButton(repeat_inner, text="Repeat", variable=self.repeat_var, value="Repeat", font=("Segoe UI", 11), command=self._update_repeat_entry)
        self.repeat_radio.pack(side='left', padx=(0, 5))
        self.repeat_times = ctk.CTkEntry(repeat_inner, width=60, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.repeat_times.insert(0, "1")
        self.repeat_times.pack(side='left', padx=(0, 10))
        self.repeat_until_radio = ctk.CTkRadioButton(repeat_inner, text="Repeat until stopped", variable=self.repeat_var, value="Repeat until stopped", font=("Segoe UI", 11), command=self._update_repeat_entry)
        self.repeat_until_radio.pack(side='left', padx=(0, 5))
        self._update_repeat_entry()

        # === Cursor Position ===
        position_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        position_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(position_frame, text="Cursor position", font=("Segoe UI", 11, "bold")).pack(anchor='w', padx=10, pady=(5, 0))
        pos_inner = ctk.CTkFrame(position_frame)
        pos_inner.pack(padx=10, pady=5, fill='x')
        self.position_var = ctk.StringVar(value="Current location")
        self.pos_radio1 = ctk.CTkRadioButton(pos_inner, text="Current location", variable=self.position_var, value="Current location", font=("Segoe UI", 11), command=self._update_position_entry)
        self.pos_radio1.pack(side='left', padx=(0, 10))
        self.pos_radio2 = ctk.CTkRadioButton(pos_inner, text="Pick location", variable=self.position_var, value="Pick location", font=("Segoe UI", 11), command=self._update_position_entry)
        self.pos_radio2.pack(side='left', padx=(0, 10))
        self.x_entry = ctk.CTkEntry(pos_inner, width=60, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.y_entry = ctk.CTkEntry(pos_inner, width=60, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        self.x_entry.insert(0, "0")
        self.y_entry.insert(0, "0")
        self.x_entry.pack(side='left', padx=(0, 5))
        self.y_entry.pack(side='left', padx=(0, 5))
        self.pick_btn = ctk.CTkButton(pos_inner, text="Pick location", command=self.pick_location, font=("Segoe UI", 11))
        self.pick_btn.pack(side='left', padx=(0, 5))
        self._update_position_entry()

        # === Buttons ===
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        self.start_btn = ctk.CTkButton(button_frame, text=f"Start ({(self.hotkey or 'f6').upper()})", command=self.start_clicking, font=("Segoe UI", 11))
        self.stop_btn = ctk.CTkButton(button_frame, text=f"Stop ({self.hotkey.upper()})", command=self.stop_clicking, state='disabled', font=("Segoe UI", 11))
        self.hotkey_btn = ctk.CTkButton(button_frame, text="Hotkey setting", command=self.set_hotkey, font=("Segoe UI", 11))
        self.record_btn = ctk.CTkButton(button_frame, text="Record & Playback", command=self.fake_record, font=("Segoe UI", 11))
        self.start_btn.pack(side='left', padx=10)
        self.stop_btn.pack(side='left', padx=10)
        self.hotkey_btn.pack(side='left', padx=10)
        self.record_btn.pack(side='left', padx=10)

        # === Status Label ===
        self.status_label = ctk.CTkLabel(main_frame, text="Status: Idle", font=("Segoe UI", 11))
        self.status_label.pack(pady=(10, 5))

        self.info_label = ctk.CTkLabel(main_frame, text="Note: Maximum CPS is limited by your system and Python. Setting interval <10ms may not increase speed.", font=("Segoe UI", 9), text_color="red")
        self.info_label.pack(pady=(0, 5))
        self.cps_label = ctk.CTkLabel(main_frame, text="CPS: 0.0", font=("Segoe UI", 11, "bold"))
        self.cps_label.pack(pady=(0, 5))

        self.hotkey_label = ctk.CTkLabel(main_frame, text=f"Hotkey: {self.hotkey.upper()}", font=("Segoe UI", 11))
        self.hotkey_label.pack(pady=(0, 5))

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

    def pick_location(self):
        self.iconify()
        print("Click anywhere to pick location, or press ESC to cancel...")

        def restore_window():
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.focus_force()
            self.after(200, lambda: self.attributes('-topmost', False))
            self._update_position_entry()

        def on_click(event):
            if hasattr(event, 'event_type') and event.event_type == 'down':
                x, y = mouse.get_position()
                self.x_entry.configure(state='normal')
                self.y_entry.configure(state='normal')
                self.x_entry.delete(0, 'end')
                self.y_entry.delete(0, 'end')
                self.x_entry.insert(0, str(x))
                self.y_entry.insert(0, str(y))
                mouse.unhook_all()
                restore_window()

        def on_esc(e):
            if e.name == 'esc':
                mouse.unhook_all()
                restore_window()

        mouse.hook(on_click)
        # Don't suppress ESC key - let it pass through to other applications
        keyboard_hook = keyboard.on_press(on_esc, suppress=False)

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

    def start_clicking(self):
        if self.running: return
        self.running = True
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.title("Clicking - Auto Clicker (Python)")
        self.status_label.configure(text="Status: Starting...")
        threading.Thread(target=self.perform_clicks, daemon=True).start()

    def stop_clicking(self):
        self.running = False
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.title("Stopped - Auto Clicker (Python)")
        self.status_label.configure(text="Status: Idle")
        self.cps_label.configure(text="CPS: 0.0")

    def set_hotkey(self):
        # Remove topmost from main window
        self.attributes('-topmost', False)

        dialog = ctk.CTkToplevel(self)
        dialog.title("Hotkey Setting")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="Hotkey Setting", font=("Segoe UI", 13, "bold")).pack(pady=(15, 5))

        frame = ctk.CTkFrame(dialog)
        frame.pack(pady=10)

        ctk.CTkLabel(frame, text="Start / Stop", font=("Segoe UI", 11)).pack(side="left", padx=10)

        hotkey_var = ctk.StringVar(value=self.hotkey.upper())
        hotkey_entry = ctk.CTkEntry(frame, width=60, textvariable=hotkey_var, font=("Segoe UI", 13), justify="center", state="readonly")
        hotkey_entry.pack(side="left", padx=10)

        def on_key(event):
            key = event.name.upper()
            hotkey_var.set(key)

        keyboard_hook = keyboard.on_press(on_key, suppress=False)

        def on_ok():
            keyboard.unhook(keyboard_hook)
            self.hotkey = hotkey_var.get().lower()
            self.hotkey_label.configure(text=f"Hotkey: {self.hotkey.upper()}")
            self.start_btn.configure(text=f"Start ({self.hotkey.upper()})")
            self.stop_btn.configure(text=f"Stop ({self.hotkey.upper()})")
            self.save_hotkey()
            # Restart the hotkey listener with new hotkey
            self.listener_should_restart = True
            if self.listener_thread and self.listener_thread.is_alive():
                self.listener_thread.join(timeout=1)
            self.listener_should_restart = False
            self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.listener_thread.start()
            dialog.destroy()
            self.attributes('-topmost', True)  # Restore topmost to main window

        def on_cancel():
            keyboard.unhook(keyboard_hook)
            dialog.destroy()
            self.attributes('-topmost', True)  # Restore topmost to main window

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Ok", command=on_ok, width=80).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=on_cancel, width=80).pack(side="left", padx=10)

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    def hotkey_listener(self):
        last_press_time = 0
        
        def on_hotkey(event):
            nonlocal last_press_time
            if event.name == self.hotkey and event.event_type == 'down':
                current_time = time.time()
                # Prevent double-triggering within 0.2 seconds
                if current_time - last_press_time > 0.2:
                    last_press_time = current_time
                    if self.running:
                        self.stop_clicking()
                    else:
                        self.start_clicking()
        
        # Use non-blocking keyboard listener that doesn't suppress keys
        keyboard_hook = keyboard.on_press(on_hotkey, suppress=False)
        
        while True:
            if self.listener_should_restart:
                keyboard.unhook(keyboard_hook)
                self.listener_should_restart = False
                break
            time.sleep(0.1)  # Small sleep to prevent high CPU usage

    def fake_record(self):
        ctk.CTkMessagebox(title="Not implemented", message="Record & Playback is not implemented yet.")

    def _update_repeat_entry(self):
        if self.repeat_var.get() == "Repeat":
            self.repeat_times.configure(state='normal')
        else:
            self.repeat_times.configure(state='disabled')

    def _update_position_entry(self):
        if self.position_var.get() == "Pick location":
            self.x_entry.configure(state='normal')
            self.y_entry.configure(state='normal')
            self.pick_btn.configure(state='normal')
        else:
            self.x_entry.configure(state='disabled')
            self.y_entry.configure(state='disabled')
            self.pick_btn.configure(state='disabled')

if __name__ == '__main__':
    app = AutoClickerApp() #TODO
    app.mainloop()