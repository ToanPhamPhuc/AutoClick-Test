import customtkinter as ctk
import pyautogui
import threading
import time
import keyboard
import mouse
import json
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AutoClickerApp(ctk.CTk):
    def load_hotkey(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    return data.get("hotkey", "f6")
        except Exception:
            pass
        return "f6"

    def save_hotkey(self):
        try:
            with open("settings.json", "w") as f:
                json.dump({"hotkey": self.hotkey}, f)
        except Exception:
            pass

    def __init__(self):
        super().__init__()
        self.title("Stopped - Auto Clicker (Python)")
        self.attributes('-topmost', True)
        self.geometry("600x500")
        self.resizable(False, False)

        self.running = False
        self.hotkey = self.load_hotkey()
        self.listener_should_restart = False
        self.listener_thread = None

        self._build_ui()
        self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.listener_thread.start()

    def _build_ui(self):
        # Set light theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # === Click Interval ===
        interval_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        interval_frame.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(interval_frame, text="Click interval", font=("Segoe UI", 11, "bold")).pack(anchor='w', padx=10, pady=(5, 0))
        row1 = ctk.CTkFrame(interval_frame)
        row1.pack(padx=10, pady=5)
        self.hours = ctk.CTkEntry(row1, width=50, font=("Segoe UI", 11))
        self.mins = ctk.CTkEntry(row1, width=50, font=("Segoe UI", 11))
        self.secs = ctk.CTkEntry(row1, width=50, font=("Segoe UI", 11))
        self.ms = ctk.CTkEntry(row1, width=80, font=("Segoe UI", 11))
        self.hours.insert(0, "0")
        self.mins.insert(0, "0")
        self.secs.insert(0, "0")
        self.ms.insert(0, "100")
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
        self.repeat_times = ctk.CTkEntry(repeat_inner, width=60, font=("Segoe UI", 11))
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
        self.x_entry = ctk.CTkEntry(pos_inner, width=60, font=("Segoe UI", 11))
        self.y_entry = ctk.CTkEntry(pos_inner, width=60, font=("Segoe UI", 11))
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
        self.start_btn = ctk.CTkButton(button_frame, text=f"Start ({self.hotkey.upper()})", command=self.start_clicking, font=("Segoe UI", 11))
        self.stop_btn = ctk.CTkButton(button_frame, text=f"Stop ({self.hotkey.upper()})", command=self.stop_clicking, state='disabled', font=("Segoe UI", 11))
        self.hotkey_btn = ctk.CTkButton(button_frame, text="Hotkey setting", command=self.set_hotkey, font=("Segoe UI", 11))
        self.record_btn = ctk.CTkButton(button_frame, text="Record & Playback", command=self.fake_record, font=("Segoe UI", 11))
        self.start_btn.pack(side='left', padx=10)
        self.stop_btn.pack(side='left', padx=10)
        self.hotkey_btn.pack(side='left', padx=10)
        self.record_btn.pack(side='left', padx=10)

        self.hotkey_label = ctk.CTkLabel(main_frame, text=f"Hotkey: {self.hotkey.upper()}", font=("Segoe UI", 11))
        self.hotkey_label.pack(pady=(0, 5))

    def _start_hotkey_listener(self):
        threading.Thread(target=self.hotkey_listener, daemon=True).start()

    def get_interval(self):
        try:
            return int(self.hours.get()) * 3600 + int(self.mins.get()) * 60 + int(self.secs.get()) + int(self.ms.get()) / 1000
        except:
            return 0.1

    def get_position(self):
        if self.position_var.get() == "Pick location":
            return (int(self.x_entry.get()), int(self.y_entry.get()))
        return None

    def pick_location(self):
        self.iconify()
        print("Click anywhere to pick location, or press ESC to cancel...")

        def restore_window():
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.focus_force()
            self.after(200, lambda: self.attributes('-topmost', False))  # Remove always-on-top after 200ms
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
        keyboard.on_press(on_esc)

    def perform_clicks(self):
        interval = self.get_interval()
        count = float('inf') if self.repeat_var.get() == "Repeat until stopped" else int(self.repeat_times.get())
        button = self.mouse_button.get().lower()
        click_type = 2 if self.click_type.get() == "Double" else 1
        position = self.get_position()

        clicks = 0
        while self.running and clicks < count:
            if position:
                pyautogui.click(x=position[0], y=position[1], button=button, clicks=click_type)
            else:
                pyautogui.click(button=button, clicks=click_type)
            time.sleep(interval)
            clicks += 1

        self.stop_clicking()

    def start_clicking(self):
        if self.running: return
        self.running = True
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.title("Clicking - Auto Clicker (Python)")
        threading.Thread(target=self.perform_clicks, daemon=True).start()

    def stop_clicking(self):
        self.running = False
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.title("Stopped - Auto Clicker (Python)")

    def set_hotkey(self):
        # Modal dialog for hotkey setting
        dialog = ctk.CTkToplevel(self)
        dialog.title("Hotkey Setting")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()  # Make modal

        ctk.CTkLabel(dialog, text="Hotkey Setting", font=("Segoe UI", 13, "bold")).pack(pady=(15, 5))

        frame = ctk.CTkFrame(dialog)
        frame.pack(pady=10)

        ctk.CTkLabel(frame, text="Start / Stop", font=("Segoe UI", 11)).pack(side="left", padx=10)

        hotkey_var = ctk.StringVar(value=self.hotkey.upper())
        hotkey_entry = ctk.CTkEntry(frame, width=60, textvariable=hotkey_var, font=("Segoe UI", 13), justify="center", state="readonly")
        hotkey_entry.pack(side="left", padx=10)

        # Listen for key press
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
            # Restart hotkey listener
            self.listener_should_restart = True
            if self.listener_thread and self.listener_thread.is_alive():
                self.listener_thread.join(timeout=1)
            self.listener_should_restart = False
            self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.listener_thread.start()
            dialog.destroy()

        def on_cancel():
            keyboard.unhook(keyboard_hook)
            dialog.destroy()

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Ok", command=on_ok, width=80).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=on_cancel, width=80).pack(side="left", padx=10)

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    def hotkey_listener(self):
        while True:
            keyboard.wait(self.hotkey)
            if self.listener_should_restart:
                self.listener_should_restart = False
                break
            if self.running:
                self.stop_clicking()
            else:
                self.start_clicking()

    def fake_record(self):
        ctk.CTkMessagebox(title="Not implemented", message="Record & Playback is not implemented yet.")

    def _update_repeat_entry(self):
        if hasattr(self, 'repeat_var') and hasattr(self, 'repeat_times'):
            if self.repeat_var.get() == "Repeat":
                self.repeat_times.configure(state='normal')
            else:
                self.repeat_times.configure(state='disabled')

    def _update_position_entry(self):
        if hasattr(self, 'position_var') and hasattr(self, 'x_entry') and hasattr(self, 'y_entry'):
            if self.position_var.get() == "Pick location":
                self.x_entry.configure(state='normal')
                self.y_entry.configure(state='normal')
                self.pick_btn.configure(state='normal')
            else:
                self.x_entry.configure(state='disabled')
                self.y_entry.configure(state='disabled')
                self.pick_btn.configure(state='disabled')

if __name__ == '__main__':
    app = AutoClickerApp()
    app.mainloop()