import customtkinter as ctk
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
        self.geometry("1100x700")
        self.resizable(True, True)

        self.clickers = []
        self.next_id = 1
        self.hotkey = "f6"
        self.listener_should_restart = False
        self.listener_thread = None
        self.settings_file = "clicker_settings.json"  # Define settings file
        
        # Advanced feature: work duration and pause duration
        self.work_duration = 7  # seconds
        self.pause_duration = 3  # seconds
        self.is_paused = False
        self.work_timer = None
        self.pause_timer = None

        self._build_ui()
        self.load_settings()

        self.unsaved_changes = False
        self.auto_save_loop()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.listener_thread.start()

    def only_int(self, P):
        if P == "" or (P.isdigit() and int(P) >= 0):
            return True
        return False
    
    def auto_save_loop(self):
        if self.unsaved_changes:
            try:
                self.save_settings()
            except Exception as e:
                print(f"Auto-save failed: {e}")
        self.after(5000, self.auto_save_loop)

    def on_close(self):
        if self.unsaved_changes:
            try:
                self.save_settings()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings before exit: {e}")
        
        # Cancel any active timers
        self.cancel_advanced_timers()
        
        self.destroy()

    def _build_ui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        title_label = ctk.CTkLabel(main_frame, text="Multi Auto Clicker", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 10))

        add_btn = ctk.CTkButton(main_frame, text="+ Add New Clicker", command=self.add_clicker, 
                               font=("Segoe UI", 12), height=35)
        add_btn.pack(pady=(0, 10))

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))

        header_frame = ctk.CTkFrame(table_frame)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        headers = ["ID", "X", "Y", "L/R", "Interval (ms)", "Stop After", "Status", "Actions"]
        header_widths = [50, 60, 60, 60, 100, 120, 100, 200]
        
        for i, (header, width) in enumerate(zip(headers, header_widths)):
            label = ctk.CTkLabel(header_frame, text=header, font=("Segoe UI", 11, "bold"), width=width)
            label.pack(side='left', padx=2)

        self.scrollable_frame = ctk.CTkScrollableFrame(table_frame, height=400)
        self.scrollable_frame.pack(fill='both', expand=True, padx=5, pady=(0, 5))

        global_frame = ctk.CTkFrame(main_frame, border_width=1, border_color="#cccccc")
        global_frame.pack(fill='x', pady=(10, 0))
        
        global_label = ctk.CTkLabel(global_frame, text="Global Controls", font=("Segoe UI", 12, "bold"))
        global_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        global_controls = ctk.CTkFrame(global_frame)
        global_controls.pack(padx=10, pady=5, fill='x')
        
        ctk.CTkLabel(global_controls, text="Global Hotkey:", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        self.hotkey_btn = ctk.CTkButton(global_controls, text="Set Hotkey", command=self.set_hotkey, 
                                       font=("Segoe UI", 11), width=100)
        self.hotkey_btn.pack(side='left', padx=(0, 20))
        
        # Advanced feature controls
        ctk.CTkLabel(global_controls, text="Work Duration (s):", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        self.work_duration_entry = ctk.CTkEntry(global_controls, width=50, font=("Segoe UI", 11), 
                                               placeholder_text="7", validate="key", 
                                               validatecommand=(self.register(self.only_int), '%P'))
        self.work_duration_entry.insert(0, str(self.work_duration))
        self.work_duration_entry.pack(side='left', padx=(0, 10))
        
        ctk.CTkLabel(global_controls, text="Pause Duration (s):", font=("Segoe UI", 11)).pack(side='left', padx=(0, 5))
        self.pause_duration_entry = ctk.CTkEntry(global_controls, width=50, font=("Segoe UI", 11), 
                                                placeholder_text="3", validate="key", 
                                                validatecommand=(self.register(self.only_int), '%P'))
        self.pause_duration_entry.insert(0, str(self.pause_duration))
        self.pause_duration_entry.pack(side='left', padx=(0, 20))
        
        self.start_all_btn = ctk.CTkButton(global_controls, text=f"Start All ({self.hotkey.upper()})", 
                                          command=self.start_all_clickers, font=("Segoe UI", 11), width=120)
        self.start_all_btn.pack(side='left', padx=(0, 10))
        
        self.stop_all_btn = ctk.CTkButton(global_controls, text=f"Stop All ({self.hotkey.upper()})", 
                                         command=self.stop_all_clickers, font=("Segoe UI", 11), width=120)
        self.stop_all_btn.pack(side='left', padx=(0, 10))
        
        self.global_status = ctk.CTkLabel(global_frame, text="Status: No clickers running", font=("Segoe UI", 11))
        self.global_status.pack(pady=(5, 10))
        
        # Advanced feature status
        self.advanced_status = ctk.CTkLabel(global_frame, text="Advanced Mode: Ready", font=("Segoe UI", 11), text_color="green")
        self.advanced_status.pack(pady=(0, 10))

        save_btn = ctk.CTkButton(global_controls, text="Save Settings", command=self.save_settings, 
                                font=("Segoe UI", 11), width=100)
        save_btn.pack(side='left', padx=(0, 10))

        self.add_clicker()
        
        # Bind change events for advanced feature settings
        self.work_duration_entry.bind('<KeyRelease>', self.on_advanced_setting_change)
        self.pause_duration_entry.bind('<KeyRelease>', self.on_advanced_setting_change)

    def add_clicker(self):
        clicker_id = self.next_id
        self.next_id += 1
        
        row_frame = ctk.CTkFrame(self.scrollable_frame, height=40)
        row_frame.pack(fill='x', pady=2, padx=5)
        
        id_label = ctk.CTkLabel(row_frame, text=str(clicker_id), font=("Segoe UI", 11), width=50)
        id_label.pack(side='left', padx=2)
        
        vcmd = (self.register(self.only_int), '%P')
        x_entry = ctk.CTkEntry(row_frame, width=60, font=("Segoe UI", 11), placeholder_text="X", validate="key", validatecommand=vcmd)
        x_entry.insert(0, "0")
        x_entry.pack(side='left', padx=2)
        
        y_entry = ctk.CTkEntry(row_frame, width=60, font=("Segoe UI", 11), placeholder_text="Y", validate="key", validatecommand=vcmd)
        y_entry.insert(0, "0")
        y_entry.pack(side='left', padx=2)
        
        click_type = ctk.CTkOptionMenu(row_frame, values=["Left", "Right"], width=60, font=("Segoe UI", 11))
        click_type.set("Left")
        click_type.pack(side='left', padx=2)
        
        interval_entry = ctk.CTkEntry(row_frame, width=100, font=("Segoe UI", 11), placeholder_text="1000", validate="key", validatecommand=vcmd)
        interval_entry.insert(0, "1000")
        interval_entry.pack(side='left', padx=2)
        
        stop_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        stop_frame.pack(side='left', padx=2)
        
        stop_condition_var = ctk.StringVar(value="Time")
        stop_time_radio = ctk.CTkRadioButton(stop_frame, text="Time", variable=stop_condition_var, 
                                            value="Time", font=("Segoe UI", 9))
        stop_time_radio.pack(side='left')
        
        stop_forever_radio = ctk.CTkRadioButton(stop_frame, text="Forever", variable=stop_condition_var, 
                                               value="Forever", font=("Segoe UI", 9))
        stop_forever_radio.pack(side='left')
        
        stop_time_entry = ctk.CTkEntry(stop_frame, width=60, font=("Segoe UI", 9), placeholder_text="3600", validate="key", validatecommand=vcmd)
        stop_time_entry.insert(0, "3600")
        stop_time_entry.pack(side='left', padx=(5, 0))
        
        status_label = ctk.CTkLabel(row_frame, text="Idle", font=("Segoe UI", 11), width=100)
        status_label.pack(side='left', padx=2)
        
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.pack(side='left', padx=2)
        
        start_btn = ctk.CTkButton(actions_frame, text="Start", command=lambda: self.start_clicker(clicker_id), 
                                 font=("Segoe UI", 10), width=60, height=25)
        start_btn.pack(side='left', padx=2)
        
        stop_btn = ctk.CTkButton(actions_frame, text="Stop", command=lambda: self.stop_clicker(clicker_id), 
                                font=("Segoe UI", 10), width=60, height=25, state='disabled')
        stop_btn.pack(side='left', padx=2)
        
        remove_btn = ctk.CTkButton(actions_frame, text="Remove", command=lambda: self.remove_clicker(clicker_id), 
                                  font=("Segoe UI", 10), width=60, height=25)
        remove_btn.pack(side='left', padx=2)
        
        pick_btn = ctk.CTkButton(actions_frame, text="Pick", command=lambda: self.pick_location(x_entry, y_entry), 
                                font=("Segoe UI", 10), width=50, height=25)
        pick_btn.pack(side='left', padx=2)
        
        clicker_data = {
            'id': clicker_id,
            'row_frame': row_frame,
            'running': False,
            'thread': None,
            'start_time': 0,
            'stop_time': 0,
            'clicks': 0,
            'start_btn': start_btn,
            'stop_btn': stop_btn,
            'status_label': status_label,
            'x_entry': x_entry,
            'y_entry': y_entry,
            'click_type': click_type,
            'interval_entry': interval_entry,
            'stop_condition_var': stop_condition_var,
            'stop_time_entry': stop_time_entry
        }
        
        self.clickers.append(clicker_data)
        
        def update_stop_time_visibility():
            if stop_condition_var.get() == "Forever":
                stop_time_entry.configure(state='disabled')
            else:
                stop_time_entry.configure(state='normal')
        
        stop_time_radio.configure(command=update_stop_time_visibility)
        stop_forever_radio.configure(command=update_stop_time_visibility)
        update_stop_time_visibility()
        
        def on_setting_change(event=None):
            self.unsaved_changes = True
        
        x_entry.bind('<KeyRelease>', on_setting_change)
        y_entry.bind('<KeyRelease>', on_setting_change)
        interval_entry.bind('<KeyRelease>', on_setting_change)
        stop_time_entry.bind('<KeyRelease>', on_setting_change)
        click_type.configure(command=on_setting_change)
        
        self.unsaved_changes = True

    def remove_clicker(self, clicker_id):
        for i, clicker in enumerate(self.clickers):
            if clicker['id'] == clicker_id:
                if clicker['running']:
                    self.stop_clicker(clicker_id)
                clicker['row_frame'].destroy()
                self.clickers.pop(i)
                break
        
        self.update_global_status()
        self.unsaved_changes = True

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
                x_entry.delete(0, 'end')
                x_entry.insert(0, str(x))  # Update X coordinate
                y_entry.delete(0, 'end')
                y_entry.insert(0, str(y))  # Update Y coordinate
                mouse.unhook_all()
                keyboard.unhook_all()
                restore_window()

        def on_key(event):
            mouse.unhook_all()
            keyboard.unhook_all()
            restore_window()

        mouse.hook(on_click)
        keyboard.hook(on_key)
        self.after(10000, lambda: [mouse.unhook_all(), keyboard.unhook_all(), restore_window()])
    def start_clicker(self, clicker_id):
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                if clicker['running']:
                    return
                
                # Don't start individual clickers if advanced cycle is active
                if self.work_timer or self.pause_timer:
                    messagebox.showinfo("Info", "Cannot start individual clickers while advanced cycle is active. Use the global hotkey to control all clickers.")
                    return
                
                clicker['running'] = True
                clicker['thread'] = threading.Thread(
                    target=self.perform_clicks, 
                    args=(clicker,),
                    daemon=True
                )
                clicker['thread'].start()
                
                clicker['start_btn'].configure(state='disabled')
                clicker['stop_btn'].configure(state='normal')
                clicker['status_label'].configure(text="Running...")
                break
        
        self.update_global_status()
        self.unsaved_changes = True

    def stop_clicker(self, clicker_id):
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                clicker['running'] = False
                if clicker['thread'] and clicker['thread'].is_alive():
                    clicker['thread'].join(timeout=1)
                clicker['thread'] = None
                
                clicker['start_btn'].configure(state='normal')
                clicker['stop_btn'].configure(state='disabled')
                clicker['status_label'].configure(text="Idle")
                break
        
        self.update_global_status()
        self.unsaved_changes = True

    def perform_clicks(self, clicker):
        try:
            x = int(clicker['x_entry'].get() or 0)
            y = int(clicker['y_entry'].get() or 0)
            interval_ms = int(clicker['interval_entry'].get() or 1000)
            click_type = clicker['click_type'].get()
            stop_condition = clicker['stop_condition_var'].get()
            stop_time_seconds = int(clicker['stop_time_entry'].get() or 3600) if stop_condition == "Time" else float('inf')
            
            if interval_ms <= 0:
                raise ValueError("Interval must be greater than 0")
            
            mouse_controller = Controller()
            button_map = {'Left': Button.left, 'Right': Button.right}
            
            clicker['start_time'] = time.time()
            clicker['clicks'] = 0
            
            while clicker['running']:
                if stop_condition == "Time" and time.time() >= clicker['start_time'] + stop_time_seconds:
                    break
                
                mouse_controller.position = (x, y)
                mouse_controller.click(button_map[click_type])
                
                clicker['clicks'] += 1
                time.sleep(interval_ms / 1000.0)
            
            self.after(0, lambda: self.stop_clicker(clicker['id']))
            if stop_condition == "Time":
                pass
                #self.after(0, lambda: messagebox.showinfo("Info", f"Clicker #{clicker['id']} stopped after {stop_time_seconds} seconds"))
                
        except ValueError as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Invalid input in clicker #{clicker['id']}: {e}"))
            self.after(0, lambda: self.stop_clicker(clicker['id']))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Error in clicker #{clicker['id']}: {e}"))
            self.after(0, lambda: self.stop_clicker(clicker['id']))

    def start_all_clickers(self):
        for clicker in self.clickers:
            if not clicker['running']:
                self.start_clicker(clicker['id'])

    def stop_all_clickers(self):
        for clicker in self.clickers:
            if clicker['running']:
                self.stop_clicker(clicker['id'])

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
                key_name = key.name if hasattr(key, 'name') else key.char
                if key_name:
                    hotkey_var.set(key_name.upper())
            except AttributeError:
                pass

        keyboard_hook = pynput_keyboard.Listener(on_press=on_key)
        keyboard_hook.start()

        def on_ok():
            keyboard_hook.stop()
            new_hotkey = hotkey_var.get().lower()
            if new_hotkey:
                self.hotkey = new_hotkey
                self.start_all_btn.configure(text=f"Start All ({self.hotkey.upper()})")
                self.stop_all_btn.configure(text=f"Stop All ({self.hotkey.upper()})")
                self.listener_should_restart = True
                if self.listener_thread and self.listener_thread.is_alive():
                    self.listener_thread.join(timeout=1)
                self.listener_should_restart = False
                self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
                self.listener_thread.start()
                self.unsaved_changes = True
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
        def on_hotkey(key):
            try:
                key_name = key.name if hasattr(key, 'name') else key.char
                if key_name and key_name.lower() == self.hotkey:
                    self.toggle_all_clickers()
            except AttributeError:
                pass
        
        with pynput_keyboard.Listener(on_press=on_hotkey) as keyboard_hook:
            keyboard_hook.join()

    def toggle_all_clickers(self):
        running_count = sum(1 for clicker in self.clickers if clicker['running'])
        total_count = len(self.clickers)
        
        if running_count == 0:
            # Start all clickers with advanced feature
            self.start_advanced_cycle()
        else:
            # Stop all clickers
            self.stop_all_clickers()
            self.cancel_advanced_timers()

    def start_advanced_cycle(self):
        """Start the advanced work/pause cycle"""
        # Cancel any existing timers
        self.cancel_advanced_timers()
        
        # Start all clickers
        self.start_all_clickers()
        
        # Update status
        self.advanced_status.configure(text=f"Advanced Mode: Working for {self.work_duration}s", text_color="orange")
        
        # Set timer to pause after work duration
        self.work_timer = self.after(self.work_duration * 1000, self.pause_clickers)

    def pause_clickers(self):
        """Pause all clickers for the pause duration"""
        if not self.is_paused:
            self.is_paused = True
            
            # Stop all clickers temporarily
            self.stop_all_clickers()
            
            # Update status
            self.advanced_status.configure(text=f"Advanced Mode: Paused for {self.pause_duration}s", text_color="red")
            
            # Set timer to resume after pause duration
            self.pause_timer = self.after(self.pause_duration * 1000, self.resume_clickers)

    def resume_clickers(self):
        """Resume all clickers and continue the cycle"""
        self.is_paused = False
        
        # Start all clickers again
        self.start_all_clickers()
        
        # Update status
        self.advanced_status.configure(text=f"Advanced Mode: Working for {self.work_duration}s", text_color="orange")
        
        # Set timer to pause again after work duration
        self.work_timer = self.after(self.work_duration * 1000, self.pause_clickers)

    def cancel_advanced_timers(self):
        """Cancel all advanced feature timers"""
        if self.work_timer:
            self.after_cancel(self.work_timer)
            self.work_timer = None
        
        if self.pause_timer:
            self.after_cancel(self.pause_timer)
            self.pause_timer = None
        
        self.is_paused = False
        self.advanced_status.configure(text="Advanced Mode: Ready", text_color="green")

    def save_settings(self):
        data = {
            "hotkey": self.hotkey,
            "work_duration": self.work_duration,
            "pause_duration": self.pause_duration,
            "clickers": []
        }
        for clicker in self.clickers:
            data["clickers"].append({
                "id": clicker["id"],
                "x": clicker["x_entry"].get(),
                "y": clicker["y_entry"].get(),
                "click_type": clicker["click_type"].get(),
                "interval": clicker["interval_entry"].get(),
                "stop_condition": clicker["stop_condition_var"].get(),
                "stop_time": clicker["stop_time_entry"].get(),
                "running": clicker["running"],
                "start_time": clicker["start_time"],
                "clicks": clicker["clicks"]
            })
        try:
            with open(self.settings_file, "w") as f:
                json.dump(data, f, indent=4)
            self.unsaved_changes = False
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self):
        self.settings_file = "clicker_settings.json"  # Ensure settings file is defined
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.hotkey = settings.get('hotkey', 'f6').lower()
                    
                    # Load advanced feature settings
                    self.work_duration = settings.get('work_duration', 7)
                    self.pause_duration = settings.get('pause_duration', 3)
                    
                    # Update UI with loaded settings
                    if hasattr(self, 'work_duration_entry'):
                        self.work_duration_entry.delete(0, 'end')
                        self.work_duration_entry.insert(0, str(self.work_duration))
                    
                    if hasattr(self, 'pause_duration_entry'):
                        self.pause_duration_entry.delete(0, 'end')
                        self.pause_duration_entry.insert(0, str(self.pause_duration))
                    
                    for clicker in self.clickers:
                        clicker['row_frame'].destroy()
                    self.clickers.clear()
                    self.next_id = 1
                    
                    for clicker_data in settings.get('clickers', []):
                        clicker_data['id'] = self.next_id
                        self._create_clicker_from_saved_data(clicker_data)
                        self.next_id += 1
                    
                    self.start_all_btn.configure(text=f"Start All ({self.hotkey.upper()})")
                    self.stop_all_btn.configure(text=f"Stop All ({self.hotkey.upper()})")
                    self.update_global_status()
                    
                    # Update advanced status
                    if hasattr(self, 'advanced_status'):
                        self.advanced_status.configure(text=f"Advanced Mode: Work {self.work_duration}s, Pause {self.pause_duration}s")
                    
                    print("Settings loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load settings: {e}")
        else:
            print("No settings file found. Starting with default settings.")

    def _create_clicker_from_saved_data(self, clicker_data):
        clicker_id = clicker_data['id']
        
        row_frame = ctk.CTkFrame(self.scrollable_frame, height=40)
        row_frame.pack(fill='x', pady=2, padx=5)
        
        id_label = ctk.CTkLabel(row_frame, text=str(clicker_id), font=("Segoe UI", 11), width=50)
        id_label.pack(side='left', padx=2)
        
        vcmd = (self.register(self.only_int), '%P')
        x_entry = ctk.CTkEntry(row_frame, width=60, font=("Segoe UI", 11), placeholder_text="X", validate="key", validatecommand=vcmd)
        x_entry.insert(0, str(clicker_data.get('x', 0)))
        x_entry.pack(side='left', padx=2)
        
        y_entry = ctk.CTkEntry(row_frame, width=60, font=("Segoe UI", 11), placeholder_text="Y", validate="key", validatecommand=vcmd)
        y_entry.insert(0, str(clicker_data.get('y', 0)))
        y_entry.pack(side='left', padx=2)
        
        click_type = ctk.CTkOptionMenu(row_frame, values=["Left", "Right"], width=60, font=("Segoe UI", 11))
        click_type.set(clicker_data.get('click_type', 'Left'))
        click_type.pack(side='left', padx=2)
        
        interval_entry = ctk.CTkEntry(row_frame, width=100, font=("Segoe UI", 11), placeholder_text="1000", validate="key", validatecommand=vcmd)
        interval_entry.insert(0, str(clicker_data.get('interval', 1000)))
        interval_entry.pack(side='left', padx=2)
        
        stop_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        stop_frame.pack(side='left', padx=2)
        
        stop_condition_var = ctk.StringVar(value=clicker_data.get('stop_condition', 'Time'))
        stop_time_radio = ctk.CTkRadioButton(stop_frame, text="Time", variable=stop_condition_var, 
                                            value="Time", font=("Segoe UI", 9))
        stop_time_radio.pack(side='left')
        
        stop_forever_radio = ctk.CTkRadioButton(stop_frame, text="Forever", variable=stop_condition_var, 
                                               value="Forever", font=("Segoe UI", 9))
        stop_forever_radio.pack(side='left')
        
        stop_time_entry = ctk.CTkEntry(stop_frame, width=60, font=("Segoe UI", 9), placeholder_text="3600", validate="key", validatecommand=vcmd)
        stop_time_entry.insert(0, str(clicker_data.get('stop_time', 3600)))
        stop_time_entry.pack(side='left', padx=(5, 0))
        
        status_label = ctk.CTkLabel(row_frame, text="Idle", font=("Segoe UI", 11), width=100)
        status_label.pack(side='left', padx=2)
        
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.pack(side='left', padx=2)
        
        start_btn = ctk.CTkButton(actions_frame, text="Start", command=lambda: self.start_clicker(clicker_id), 
                                 font=("Segoe UI", 10), width=60, height=25)
        start_btn.pack(side='left', padx=2)
        
        stop_btn = ctk.CTkButton(actions_frame, text="Stop", command=lambda: self.stop_clicker(clicker_id), 
                                font=("Segoe UI", 10), width=60, height=25, state='disabled')
        stop_btn.pack(side='left', padx=2)
        
        remove_btn = ctk.CTkButton(actions_frame, text="Remove", command=lambda: self.remove_clicker(clicker_id), 
                                  font=("Segoe UI", 10), width=60, height=25)
        remove_btn.pack(side='left', padx=2)
        
        pick_btn = ctk.CTkButton(actions_frame, text="Pick", command=lambda: self.pick_location(x_entry, y_entry), 
                                font=("Segoe UI", 10), width=50, height=25)
        pick_btn.pack(side='left', padx=2)
        
        clicker_data_stored = {
            'id': clicker_id,
            'row_frame': row_frame,
            'running': False,  # Don't restore running state to avoid threading issues
            'thread': None,
            'start_time': clicker_data.get('start_time', 0),
            'stop_time': 0,
            'clicks': clicker_data.get('clicks', 0),
            'start_btn': start_btn,
            'stop_btn': stop_btn,
            'status_label': status_label,
            'x_entry': x_entry,
            'y_entry': y_entry,
            'click_type': click_type,
            'interval_entry': interval_entry,
            'stop_condition_var': stop_condition_var,
            'stop_time_entry': stop_time_entry
        }
        
        self.clickers.append(clicker_data_stored)
        
        def update_stop_time_visibility():
            if stop_condition_var.get() == "Forever":
                stop_time_entry.configure(state='disabled')
            else:
                stop_time_entry.configure(state='normal')
        
        stop_time_radio.configure(command=update_stop_time_visibility)
        stop_forever_radio.configure(command=update_stop_time_visibility)
        update_stop_time_visibility()
        
        def on_setting_change(event=None):
            self.unsaved_changes = True
        
        x_entry.bind('<KeyRelease>', on_setting_change)
        y_entry.bind('<KeyRelease>', on_setting_change)
        interval_entry.bind('<KeyRelease>', on_setting_change)
        stop_time_entry.bind('<KeyRelease>', on_setting_change)
        click_type.configure(command=on_setting_change)

    def on_advanced_setting_change(self, event=None):
        self.unsaved_changes = True
        self.work_duration = int(self.work_duration_entry.get() or 7)
        self.pause_duration = int(self.pause_duration_entry.get() or 3)
        self.advanced_status.configure(text=f"Advanced Mode: Work {self.work_duration}s, Pause {self.pause_duration}s")

if __name__ == '__main__':
    app = MultiAutoClickerApp()
    app.mainloop()