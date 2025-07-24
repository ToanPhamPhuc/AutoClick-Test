import customtkinter as ctk
import pyautogui
import threading
import time
import keyboard

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OP Auto Clicker 3.1 (Python)")
        self.geometry("640x360")
        self.resizable(False, False)

        self.running = False
        self.hotkey = 'f6'

        self._build_ui()
        self._start_hotkey_listener()

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # === Click Interval ===
        interval_frame = ctk.CTkFrame(main_frame)
        interval_frame.pack(fill='x', pady=(0, 5))
        ctk.CTkLabel(interval_frame, text="Click interval", anchor='w').pack(anchor='w')
        row1 = ctk.CTkFrame(interval_frame)
        row1.pack()
        self.hours = ctk.CTkEntry(row1, width=50)
        self.mins = ctk.CTkEntry(row1, width=50)
        self.secs = ctk.CTkEntry(row1, width=50)
        self.ms = ctk.CTkEntry(row1, width=80)
        for widget, default in zip([self.hours, self.mins, self.secs, self.ms], ["0"]*4):
            widget.insert(0, default)
            widget.pack(side='left', padx=5)

        # === Click Options ===
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(options_frame, text="Click options", anchor='w').pack(anchor='w')
        self.mouse_button = ctk.CTkOptionMenu(options_frame, values=["Left", "Right", "Middle"])
        self.mouse_button.set("Left")
        self.mouse_button.pack(side='left', padx=5)
        self.click_type = ctk.CTkOptionMenu(options_frame, values=["Single", "Double"])
        self.click_type.set("Single")
        self.click_type.pack(side='left', padx=5)

        # === Click Repeat ===
        repeat_frame = ctk.CTkFrame(main_frame)
        repeat_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(repeat_frame, text="Click repeat", anchor='w').pack(anchor='w')
        self.repeat_type = ctk.CTkOptionMenu(repeat_frame, values=["Repeat", "Repeat until stopped"])
        self.repeat_type.set("Repeat until stopped")
        self.repeat_type.pack(side='left', padx=5)
        self.repeat_times = ctk.CTkEntry(repeat_frame, width=60)
        self.repeat_times.insert(0, "1")
        self.repeat_times.pack(side='left', padx=5)

        # === Cursor Position ===
        position_frame = ctk.CTkFrame(main_frame)
        position_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(position_frame, text="Cursor position", anchor='w').pack(anchor='w')
        self.position_mode = ctk.CTkOptionMenu(position_frame, values=["Current location", "Pick location"])
        self.position_mode.set("Current location")
        self.position_mode.pack(side='left', padx=5)
        self.x_entry = ctk.CTkEntry(position_frame, width=60)
        self.y_entry = ctk.CTkEntry(position_frame, width=60)
        self.x_entry.insert(0, "0")
        self.y_entry.insert(0, "0")
        self.x_entry.pack(side='left', padx=5)
        self.y_entry.pack(side='left', padx=5)

        # === Buttons ===
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        self.start_btn = ctk.CTkButton(button_frame, text="Start (F6)", command=self.start_clicking)
        self.stop_btn = ctk.CTkButton(button_frame, text="Stop (F6)", command=self.stop_clicking, state='disabled')
        self.start_btn.pack(side='left', padx=10)
        self.stop_btn.pack(side='left', padx=10)

        self.hotkey_btn = ctk.CTkButton(button_frame, text="Hotkey setting", command=self.set_hotkey)
        self.hotkey_btn.pack(side='left', padx=10)
        self.hotkey_label = ctk.CTkLabel(main_frame, text=f"Hotkey: {self.hotkey.upper()}")
        self.hotkey_label.pack()

        self.record_btn = ctk.CTkButton(main_frame, text="Record & Playback", command=self.fake_record)
        self.record_btn.pack(pady=(0, 5))

    def _start_hotkey_listener(self):
        threading.Thread(target=self.hotkey_listener, daemon=True).start()

    def get_interval(self):
        try:
            return int(self.hours.get()) * 3600 + int(self.mins.get()) * 60 + int(self.secs.get()) + int(self.ms.get()) / 1000
        except:
            return 0.1

    def get_position(self):
        if self.position_mode.get() == "Pick location":
            return (int(self.x_entry.get()), int(self.y_entry.get()))
        return None

    def perform_clicks(self):
        interval = self.get_interval()
        count = float('inf') if self.repeat_type.get() == "Repeat until stopped" else int(self.repeat_times.get())
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
        threading.Thread(target=self.perform_clicks, daemon=True).start()

    def stop_clicking(self):
        self.running = False
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')

    def set_hotkey(self):
        self.hotkey_label.configure(text="Press any key...")
        self.hotkey = keyboard.read_key()
        self.hotkey_label.configure(text=f"Hotkey: {self.hotkey.upper()}")

    def hotkey_listener(self):
        while True:
            keyboard.wait(self.hotkey)
            if self.running:
                self.stop_clicking()
            else:
                self.start_clicking()

    def fake_record(self):
        ctk.CTkMessagebox(title="Not implemented", message="Record & Playback is not implemented yet.")

if __name__ == '__main__':
    app = AutoClickerApp()
    app.mainloop()
