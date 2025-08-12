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
from pynput import keyboard as pynput_keyboard

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MultiAutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Multi Auto Clicker (Python)")
        self.attributes('-topmost', True)
        self.geometry("800x700")
        self.resizable(True, True)

        self.clickers = []
        self.next_id = 1
        self.hotkey = "f6"
        self.listener_should_restart = False
        self.listener_thread = None

        self._build_ui()
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

        # Title
        title_label = ctk.CTkLabel(main_frame, text="Multi Auto Clicker", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Add new clicker button
        add_btn = ctk.CTkButton(main_frame, text="+ Add New Clicker", command=self.add_clicker, 
                               font=("Segoe UI", 12), height=35)
        add_btn.pack(pady=(0, 10))

        # Scrollable frame for clickers
        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame, height=500)
        self.scrollable_frame.pack(fill='both', expand=True, padx=(0, 5))

        # Global controls
        global_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        global_frame.pack(fill='x', pady=(10, 0))
        
        global_label = ctk.CTkLabel(global_frame, text="Global Controls", font=("Segoe UI", 12, "bold"))
        global_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        global_controls = ctk.CTkFrame(global_frame)
        global_controls.pack(padx=10, pady=5, fill='x')
        
        # Global hotkey setting
        ctk.CTkLabel(global_controls, text="Global Hotkey:", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        self.hotkey_btn = ctk.CTkButton(global_controls, text="Set Hotkey", command=self.set_hotkey, 
                                       font=("Segoe UI", 11), width=100)
        self.hotkey_btn.pack(side='left', padx=(0, 20))
        
        # Global start/stop all
        self.start_all_btn = ctk.CTkButton(global_controls, text="Start All", command=self.start_all_clickers, 
                                          font=("Segoe UI", 11), width=80)
        self.start_all_btn.pack(side='left', padx=(0, 10))
        
        self.stop_all_btn = ctk.CTkButton(global_controls, text="Stop All", command=self.stop_all_clickers, 
                                         font=("Segoe UI", 11), width=80)
        self.stop_all_btn.pack(side='left', padx=(0, 10))
        
        # Status
        self.global_status = ctk.CTkLabel(global_frame, text="Status: No clickers running", font=("Segoe UI", 11))
        self.global_status.pack(pady=(5, 10))

        # Add initial clicker
        self.add_clicker()

    def add_clicker(self):
        clicker_id = self.next_id
        self.next_id += 1
        
        clicker_frame = ctk.CTkFrame(self.scrollable_frame, border_width=2, border_color="#cccccc")
        clicker_frame.pack(fill='x', pady=5, padx=5)
        
        # Clicker header
        header_frame = ctk.CTkFrame(clicker_frame)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        ctk.CTkLabel(header_frame, text=f"Clicker #{clicker_id}", font=("Segoe UI", 12, "bold")).pack(side='left')
        
        remove_btn = ctk.CTkButton(header_frame, text="Remove", command=lambda: self.remove_clicker(clicker_frame, clicker_id), 
                                  font=("Segoe UI", 10), width=70, height=25)
        remove_btn.pack(side='right')
        
        # Clicker content
        content_frame = ctk.CTkFrame(clicker_frame)
        content_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        vcmd = (self.register(self.only_int), '%P')
        
        # Click interval
        interval_frame = ctk.CTkFrame(content_frame)
        interval_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(interval_frame, text="Click interval:", font=("Segoe UI", 11)).pack(anchor='w', padx=10, pady=(5, 0))
        
        interval_inputs = ctk.CTkFrame(interval_frame)
        interval_inputs.pack(padx=10, pady=5)
        
        hours = ctk.CTkEntry(interval_inputs, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        mins = ctk.CTkEntry(interval_inputs, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        secs = ctk.CTkEntry(interval_inputs, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        ms = ctk.CTkEntry(interval_inputs, width=80, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        
        hours.insert(0, "0")
        mins.insert(0, "0")
        secs.insert(0, "0")
        ms.insert(0, "1")
        
        hours.pack(side='left', padx=(5, 2))
        ctk.CTkLabel(interval_inputs, text="h", font=("Segoe UI", 11)).pack(side='left')
        mins.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(interval_inputs, text="m", font=("Segoe UI", 11)).pack(side='left')
        secs.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(interval_inputs, text="s", font=("Segoe UI", 11)).pack(side='left')
        ms.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(interval_inputs, text="ms", font=("Segoe UI", 11)).pack(side='left')
        
        # Click options
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(options_frame, text="Click options:", font=("Segoe UI", 11)).pack(anchor='w', padx=10, pady=(5, 0))
        
        options_inputs = ctk.CTkFrame(options_frame)
        options_inputs.pack(padx=10, pady=5, fill='x')
        
        ctk.CTkLabel(options_inputs, text="Button:", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        mouse_button = ctk.CTkOptionMenu(options_inputs, values=["Left", "Right", "Middle"], width=80, font=("Segoe UI", 11))
        mouse_button.set("Left")
        mouse_button.pack(side='left', padx=(0, 20))
        
        ctk.CTkLabel(options_inputs, text="Type:", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        click_type = ctk.CTkOptionMenu(options_inputs, values=["Single", "Double"], width=80, font=("Segoe UI", 11))
        click_type.set("Single")
        click_type.pack(side='left')
        
        # Stop after time
        time_frame = ctk.CTkFrame(content_frame)
        time_frame.pack(fill='x', pady=5)
        
        # Dynamic label that changes based on selection
        time_label = ctk.CTkLabel(time_frame, text="Stop clicking after:", font=("Segoe UI", 11))
        time_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        # Radio buttons for stop condition
        stop_radio_frame = ctk.CTkFrame(time_frame)
        stop_radio_frame.pack(padx=10, pady=5, fill='x')
        
        stop_condition_var = ctk.StringVar(value="Stop after time")
        
        def update_time_label():
            if stop_condition_var.get() == "Click forever":
                time_label.configure(text="Clicking forever (no time limit)")
            else:
                time_label.configure(text="Stop clicking after:")
        
        stop_time_radio = ctk.CTkRadioButton(stop_radio_frame, text="Stop after time", variable=stop_condition_var, 
                                            value="Stop after time", font=("Segoe UI", 11), 
                                            command=lambda: self._update_stop_time_entry(stop_hours, stop_mins, stop_secs, stop_condition_var, update_time_label))
        stop_time_radio.pack(side='left', padx=(0, 10))
        
        stop_forever_radio = ctk.CTkRadioButton(stop_radio_frame, text="Click forever", variable=stop_condition_var, 
                                               value="Click forever", font=("Segoe UI", 11), 
                                               command=lambda: self._update_stop_time_entry(stop_hours, stop_mins, stop_secs, stop_condition_var, update_time_label))
        stop_forever_radio.pack(side='left', padx=(0, 10))
        
        time_inputs = ctk.CTkFrame(time_frame)
        time_inputs.pack(padx=10, pady=5)
        
        stop_hours = ctk.CTkEntry(time_inputs, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        stop_mins = ctk.CTkEntry(time_inputs, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        stop_secs = ctk.CTkEntry(time_inputs, width=50, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        
        stop_hours.insert(0, "0")
        stop_mins.insert(0, "0")
        stop_secs.insert(0, "3600")  # Default 1 hour
        
        stop_hours.pack(side='left', padx=(5, 2))
        ctk.CTkLabel(time_inputs, text="hours", font=("Segoe UI", 11)).pack(side='left')
        stop_mins.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(time_inputs, text="mins", font=("Segoe UI", 11)).pack(side='left')
        stop_secs.pack(side='left', padx=(10, 2))
        ctk.CTkLabel(time_inputs, text="secs", font=("Segoe UI", 11)).pack(side='left')
        
        # Initialize the stop time entry state
        self._update_stop_time_entry(stop_hours, stop_mins, stop_secs, stop_condition_var, update_time_label)
        
        # Cursor position
        position_frame = ctk.CTkFrame(content_frame)
        position_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(position_frame, text="Cursor position:", font=("Segoe UI", 11)).pack(anchor='w', padx=10, pady=(5, 0))
        
        pos_inputs = ctk.CTkFrame(position_frame)
        pos_inputs.pack(padx=10, pady=5, fill='x')
        
        position_var = ctk.StringVar(value="Current location")
        pos_radio1 = ctk.CTkRadioButton(pos_inputs, text="Current location", variable=position_var, value="Current location", 
                                       font=("Segoe UI", 11), command=lambda: self._update_position_entry(x_entry, y_entry, pick_btn))
        pos_radio1.pack(side='left', padx=(0, 10))
        
        pos_radio2 = ctk.CTkRadioButton(pos_inputs, text="Pick location", variable=position_var, value="Pick location", 
                                       font=("Segoe UI", 11), command=lambda: self._update_position_entry(x_entry, y_entry, pick_btn))
        pos_radio2.pack(side='left', padx=(0, 10))
        
        x_entry = ctk.CTkEntry(pos_inputs, width=60, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        y_entry = ctk.CTkEntry(pos_inputs, width=60, font=("Segoe UI", 11), validate='key', validatecommand=vcmd)
        x_entry.insert(0, "0")
        y_entry.insert(0, "0")
        x_entry.pack(side='left', padx=(0, 5))
        y_entry.pack(side='left', padx=(0, 5))
        
        pick_btn = ctk.CTkButton(pos_inputs, text="Pick location", 
                                command=lambda: self.pick_location(x_entry, y_entry), font=("Segoe UI", 11))
        pick_btn.pack(side='left', padx=(0, 5))
        
        self._update_position_entry(x_entry, y_entry, pick_btn)
        
        # Control buttons
        control_frame = ctk.CTkFrame(content_frame)
        control_frame.pack(fill='x', pady=5)
        
        start_btn = ctk.CTkButton(control_frame, text="Start", 
                                 command=lambda: self.start_clicker(clicker_id, hours, mins, secs, ms, mouse_button, 
                                                                  click_type, stop_hours, stop_mins, stop_secs, 
                                                                  position_var, x_entry, y_entry, start_btn, stop_btn, status_label, stop_condition_var), 
                                 font=("Segoe UI", 11), width=80)
        start_btn.pack(side='left', padx=(0, 10))
        
        stop_btn = ctk.CTkButton(control_frame, text="Stop", 
                                command=lambda: self.stop_clicker(clicker_id, start_btn, stop_btn, status_label), 
                                font=("Segoe UI", 11), width=80, state='disabled')
        stop_btn.pack(side='left', padx=(0, 10))
        
        # Status
        status_label = ctk.CTkLabel(control_frame, text="Status: Idle", font=("Segoe UI", 11))
        status_label.pack(side='left', padx=(20, 0))
        
        # Store clicker data
        clicker_data = {
            'id': clicker_id,
            'frame': clicker_frame,
            'running': False,
            'thread': None,
            'start_time': 0,
            'stop_time': 0,
            'clicks': 0,
            'start_btn': start_btn,
            'stop_btn': stop_btn,
            'status_label': status_label,
            'position_var': position_var,
            'x_entry': x_entry,
            'y_entry': y_entry,
            'stop_condition_var': stop_condition_var,
            'hours': hours,
            'mins': mins,
            'secs': secs,
            'ms': ms,
            'mouse_button': mouse_button,
            'click_type': click_type,
            'stop_hours': stop_hours,
            'stop_mins': stop_mins,
            'stop_secs': stop_secs
        }
        
        self.clickers.append(clicker_data)

    def remove_clicker(self, frame, clicker_id):
        # Stop the clicker if running
        for clicker in self.clickers:
            if clicker['id'] == clicker_id and clicker['running']:
                self.stop_clicker(clicker_id, clicker['start_btn'], clicker['stop_btn'], clicker['status_label'])
        
        # Remove from list and destroy frame
        self.clickers = [c for c in self.clickers if c['id'] != clicker_id]
        frame.destroy()
        
        self.update_global_status()

    def _update_position_entry(self, x_entry, y_entry, pick_btn):
        # This will be handled by the individual clicker instances
        pass

    def _update_stop_time_entry(self, stop_hours, stop_mins, stop_secs, stop_condition_var, update_label_func):
        # This method is called by the radio buttons to enable/disable the stop time entry
        if stop_condition_var.get() == "Click forever":
            stop_hours.configure(state='disabled')
            stop_mins.configure(state='disabled')
            stop_secs.configure(state='disabled')
            update_label_func() # Update the label text
        else:
            stop_hours.configure(state='normal')
            stop_mins.configure(state='normal')
            stop_secs.configure(state='normal')
            update_label_func() # Update the label text

    def pick_location(self, x_entry, y_entry):
        self.iconify()
        print("Click anywhere to pick location, or press any key to cancel...")

        def restore_window():
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.focus_force()
            self.after(200, lambda: self.attributes('-topmost', False))

        def on_click(event):
            if hasattr(event, 'event_type') and event.event_type == 'down':
                x, y = mouse.get_position()
                x_entry.configure(state='normal')
                y_entry.configure(state='normal')
                x_entry.delete(0, 'end')
                y_entry.delete(0, 'end')
                x_entry.insert(0, str(x))
                y_entry.insert(0, str(y))
                mouse.unhook_all()
                restore_window()

        def timeout_restore():
            mouse.unhook_all()
            restore_window()

        mouse.hook(on_click)
        self.after(10000, timeout_restore)

    def get_interval(self, hours, mins, secs, ms):
        try:
            h = int(hours.get() or 0)
            m = int(mins.get() or 0)
            s = int(secs.get() or 0)
            milliseconds = int(ms.get() or 0)
            if h < 0 or m < 0 or s < 0 or milliseconds < 0:
                return 0.1
            total_ms = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + milliseconds
            return max(total_ms / 1000, 0.002)
        except ValueError:
            return 0.1

    def get_stop_time(self, hours, mins, secs):
        try:
            h = int(hours.get() or 0)
            m = int(mins.get() or 0)
            s = int(secs.get() or 0)
            if h < 0 or m < 0 or s < 0:
                return 3600  # Default 1 hour
            return h * 3600 + m * 60 + s
        except ValueError:
            return 3600

    def get_position(self, position_var, x_entry, y_entry):
        if position_var.get() == "Pick location":
            try:
                x = int(x_entry.get() or 0)
                y = int(y_entry.get() or 0)
                return (x, y)
            except ValueError:
                return None
        return None

    def perform_clicks(self, clicker_id, hours, mins, secs, ms, mouse_button, click_type, 
                      stop_hours, stop_mins, stop_secs, position_var, x_entry, y_entry, 
                      start_btn, stop_btn, status_label, stop_condition_var):
        
        interval = self.get_interval(hours, mins, secs, ms)
        button = mouse_button.get()
        click_type_count = 2 if click_type.get() == "Double" else 1
        position = self.get_position(position_var, x_entry, y_entry)
        mouse_controller = Controller()

        # Find clicker data
        clicker_data = None
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                clicker_data = clicker
                break
        
        if not clicker_data:
            return

        clicker_data['start_time'] = time.time()
        clicker_data['clicks'] = 0
        next_time = time.time()

        # Check if we should stop after time or click forever
        stop_after_time = clicker_data['stop_condition_var'].get() == "Stop after time"
        if stop_after_time:
            stop_after = self.get_stop_time(stop_hours, stop_mins, stop_secs)
            clicker_data['stop_time'] = clicker_data['start_time'] + stop_after

        button_map = {'Left': Button.left, 'Right': Button.right, 'Middle': Button.middle}

        # Main clicking loop
        while clicker_data['running']:
            # Check if we should stop due to time limit
            if stop_after_time and time.time() >= clicker_data['stop_time']:
                break
                
            current_time = time.time()
            if position:
                mouse_controller.position = position
            
            for _ in range(click_type_count):
                mouse_controller.click(button_map[button])
            
            clicker_data['clicks'] += click_type_count
            
            target_time = next_time + interval
            while time.time() < target_time and clicker_data['running']:
                time.sleep(0.001)  # Small sleep to prevent high CPU usage
            next_time = target_time

        # Auto-stop when time is up (only for time-based stopping)
        if stop_after_time and time.time() >= clicker_data['stop_time']:
            self.after(0, lambda: self.stop_clicker(clicker_id, start_btn, stop_btn, status_label))
            stop_after = self.get_stop_time(stop_hours, stop_mins, stop_secs)
            messagebox.showinfo("Info", f"Clicker #{clicker_id} stopped after {stop_after} seconds")

    def start_clicker(self, clicker_id, hours, mins, secs, ms, mouse_button, click_type, 
                     stop_hours, stop_mins, stop_secs, position_var, x_entry, y_entry, 
                     start_btn, stop_btn, status_label, stop_condition_var):
        
        # Find clicker data
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                if clicker['running']:
                    return
                
                clicker['running'] = True
                clicker['thread'] = threading.Thread(
                    target=self.perform_clicks, 
                    args=(clicker_id, hours, mins, secs, ms, mouse_button, click_type, 
                          stop_hours, stop_mins, stop_secs, position_var, x_entry, y_entry, 
                          start_btn, stop_btn, status_label, stop_condition_var),
                    daemon=True
                )
                clicker['thread'].start()
                
                start_btn.configure(state='disabled')
                stop_btn.configure(state='normal')
                status_label.configure(text="Status: Running...")
                break
        
        self.update_global_status()

    def stop_clicker(self, clicker_id, start_btn, stop_btn, status_label):
        # Find clicker data
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                clicker['running'] = False
                if clicker['thread'] and clicker['thread'].is_alive():
                    clicker['thread'].join(timeout=1)
                
                start_btn.configure(state='normal')
                stop_btn.configure(state='disabled')
                status_label.configure(text="Status: Idle")
                break
        
        self.update_global_status()

    def start_all_clickers(self):
        for clicker in self.clickers:
            if not clicker['running']:
                # Use the stored references from clicker data
                self.start_clicker(
                    clicker['id'],
                    clicker['hours'], clicker['mins'], clicker['secs'], clicker['ms'],
                    clicker['mouse_button'], clicker['click_type'],
                    clicker['stop_hours'], clicker['stop_mins'], clicker['stop_secs'],
                    clicker['position_var'], clicker['x_entry'], clicker['y_entry'],
                    clicker['start_btn'], clicker['stop_btn'], clicker['status_label'], 
                    clicker['stop_condition_var']
                )

    def stop_all_clickers(self):
        for clicker in self.clickers:
            if clicker['running']:
                self.stop_clicker(
                    clicker['id'],
                    clicker['start_btn'], clicker['stop_btn'], clicker['status_label']
                )

    def update_global_status(self):
        running_count = sum(1 for clicker in self.clickers if clicker['running'])
        total_count = len(self.clickers)
        
        if running_count == 0:
            self.global_status.configure(text="Status: No clickers running")
        elif running_count == total_count:
            self.global_status.configure(text=f"Status: All {total_count} clickers running")
        else:
            self.global_status.configure(text=f"Status: {running_count}/{total_count} clickers running")

    def set_hotkey(self):
        # Remove topmost from main window
        self.attributes('-topmost', False)

        dialog = ctk.CTkToplevel(self)
        dialog.title("Global Hotkey Setting")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="Global Hotkey Setting", font=("Segoe UI", 13, "bold")).pack(pady=(15, 5))

        frame = ctk.CTkFrame(dialog)
        frame.pack(pady=10)

        ctk.CTkLabel(frame, text="Start / Stop All", font=("Segoe UI", 11)).pack(side="left", padx=10)

        hotkey_var = ctk.StringVar(value=self.hotkey.upper())
        hotkey_entry = ctk.CTkEntry(frame, width=60, textvariable=hotkey_var, font=("Segoe UI", 13), justify="center", state="readonly")
        hotkey_entry.pack(side="left", padx=10)

        def on_key(key):
            try:
                if hasattr(key, 'char'):
                    key_name = key.char.upper()
                elif hasattr(key, 'name'):
                    key_name = key.name.upper()
                else:
                    return
                hotkey_var.set(key_name)
            except AttributeError:
                pass

        keyboard_hook = pynput_keyboard.Listener(on_press=on_key)
        keyboard_hook.start()

        def on_ok():
            keyboard_hook.stop()
            self.hotkey = hotkey_var.get().lower()
            # Restart the hotkey listener with new hotkey
            self.listener_should_restart = True
            if self.listener_thread and self.listener_thread.is_alive():
                self.listener_thread.join(timeout=1)
            self.listener_should_restart = False
            self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
            self.listener_thread.start()
            dialog.destroy()
            self.attributes('-topmost', True)

        def on_cancel():
            keyboard_hook.stop()
            dialog.destroy()
            self.attributes('-topmost', True)

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Ok", command=on_ok, width=80).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=on_cancel, width=80).pack(side="left", padx=10)

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    def hotkey_listener(self):
        last_press_time = 0
        
        def on_hotkey(key):
            nonlocal last_press_time
            try:
                if hasattr(key, 'char') and key.char == self.hotkey:
                    current_time = time.time()
                    if current_time - last_press_time > 0.2:
                        last_press_time = current_time
                        self.toggle_all_clickers()
                elif hasattr(key, 'name') and key.name == self.hotkey:
                    current_time = time.time()
                    if current_time - last_press_time > 0.2:
                        last_press_time = current_time
                        self.toggle_all_clickers()
            except AttributeError:
                pass
        
        keyboard_hook = pynput_keyboard.Listener(on_press=on_hotkey)
        keyboard_hook.start()
        
        while True:
            if self.listener_should_restart:
                keyboard_hook.stop()
                self.listener_should_restart = False
                break
            time.sleep(0.1)

    def toggle_all_clickers(self):
        running_count = sum(1 for clicker in self.clickers if clicker['running'])
        total_count = len(self.clickers)
        
        if running_count == 0:
            self.start_all_clickers()
        else:
            self.stop_all_clickers()

if __name__ == '__main__':
    app = MultiAutoClickerApp()
    app.mainloop()
