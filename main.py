import customtkinter as ctk
import pyautogui
import threading
import time
import keyboard
import mouse
import json
import os
from tkinter import messagebox, ttk
from pynput.mouse import Button, Controller
from pynput import keyboard as pynput_keyboard

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MultiAutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Multi Auto Clicker (Python)")
        self.attributes('-topmost', True)
        self.geometry("1000x700")
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

        # Create table frame
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Table header
        header_frame = ctk.CTkFrame(table_frame)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        # Header labels
        headers = ["ID", "X", "Y", "L/R", "Interval (ms)", "Stop After", "Status", "Actions"]
        header_widths = [50, 60, 60, 60, 100, 120, 100, 200]
        
        for i, (header, width) in enumerate(zip(headers, header_widths)):
            label = ctk.CTkLabel(header_frame, text=header, font=("Segoe UI", 11, "bold"), width=width)
            label.pack(side='left', padx=2)

        # Scrollable frame for clicker rows
        self.scrollable_frame = ctk.CTkScrollableFrame(table_frame, height=400)
        self.scrollable_frame.pack(fill='both', expand=True, padx=5, pady=(0, 5))

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
        self.start_all_btn = ctk.CTkButton(global_controls, text=f"Start All ({self.hotkey.upper()})", command=self.start_all_clickers, 
                                          font=("Segoe UI", 11), width=120)
        self.start_all_btn.pack(side='left', padx=(0, 10))
        
        self.stop_all_btn = ctk.CTkButton(global_controls, text=f"Stop All ({self.hotkey.upper()})", command=self.stop_all_clickers, 
                                         font=("Segoe UI", 11), width=120)
        self.stop_all_btn.pack(side='left', padx=(0, 10))
        
        # Status
        self.global_status = ctk.CTkLabel(global_frame, text="Status: No clickers running", font=("Segoe UI", 11))
        self.global_status.pack(pady=(5, 10))

        # Add initial clicker
        self.add_clicker()

    def add_clicker(self):
        clicker_id = self.next_id
        self.next_id += 1
        
        # Create clicker row frame
        row_frame = ctk.CTkFrame(self.scrollable_frame, height=40)
        row_frame.pack(fill='x', pady=2, padx=5)
        
        # ID column
        id_label = ctk.CTkLabel(row_frame, text=str(clicker_id), font=("Segoe UI", 11), width=50)
        id_label.pack(side='left', padx=2)
        
        # X coordinate
        x_entry = ctk.CTkEntry(row_frame, width=60, font=("Segoe UI", 11), placeholder_text="X")
        x_entry.insert(0, "0")
        x_entry.pack(side='left', padx=2)
        
        # Y coordinate
        y_entry = ctk.CTkEntry(row_frame, width=60, font=("Segoe UI", 11), placeholder_text="Y")
        y_entry.insert(0, "0")
        y_entry.pack(side='left', padx=2)
        
        # L/R click type
        click_type = ctk.CTkOptionMenu(row_frame, values=["Left", "Right"], width=60, font=("Segoe UI", 11))
        click_type.set("Left")
        click_type.pack(side='left', padx=2)
        
        # Interval in milliseconds
        interval_entry = ctk.CTkEntry(row_frame, width=100, font=("Segoe UI", 11), placeholder_text="1000")
        interval_entry.insert(0, "1000")
        interval_entry.pack(side='left', padx=2)
        
        # Stop after (time or forever)
        stop_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        stop_frame.pack(side='left', padx=2)
        
        stop_condition_var = ctk.StringVar(value="Time")
        stop_time_radio = ctk.CTkRadioButton(stop_frame, text="Time", variable=stop_condition_var, 
                                            value="Time", font=("Segoe UI", 9))
        stop_time_radio.pack(side='left')
        
        stop_forever_radio = ctk.CTkRadioButton(stop_frame, text="Forever", variable=stop_condition_var, 
                                               value="Forever", font=("Segoe UI", 9))
        stop_forever_radio.pack(side='left')
        
        # Stop time entry (only visible when "Time" is selected)
        stop_time_entry = ctk.CTkEntry(stop_frame, width=60, font=("Segoe UI", 9), placeholder_text="3600")
        stop_time_entry.insert(0, "3600")
        stop_time_entry.pack(side='left', padx=(5, 0))
        
        # Status
        status_label = ctk.CTkLabel(row_frame, text="Idle", font=("Segoe UI", 11), width=100)
        status_label.pack(side='left', padx=2)
        
        # Actions
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
        
        # Pick location button
        pick_btn = ctk.CTkButton(actions_frame, text="Pick", command=lambda: self.pick_location(x_entry, y_entry), 
                                font=("Segoe UI", 10), width=50, height=25)
        pick_btn.pack(side='left', padx=2)
        
        # Store clicker data
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
        
        # Update radio button commands to handle stop time entry visibility
        def update_stop_time_visibility():
            if stop_condition_var.get() == "Forever":
                stop_time_entry.configure(state='disabled')
            else:
                stop_time_entry.configure(state='normal')
        
        stop_time_radio.configure(command=update_stop_time_visibility)
        stop_forever_radio.configure(command=update_stop_time_visibility)
        update_stop_time_visibility()

    def remove_clicker(self, clicker_id):
        # Find and remove the clicker
        for i, clicker in enumerate(self.clickers):
            if clicker['id'] == clicker_id:
                if clicker['running']:
                    self.stop_clicker(clicker_id)
                clicker['row_frame'].destroy()
                self.clickers.pop(i)
                break
        
        self.update_global_status()

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

    def start_clicker(self, clicker_id):
        # Find clicker data
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                if clicker['running']:
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

    def stop_clicker(self, clicker_id):
        # Find clicker data
        for clicker in self.clickers:
            if clicker['id'] == clicker_id:
                clicker['running'] = False
                if clicker['thread'] and clicker['thread'].is_alive():
                    clicker['thread'].join(timeout=1)
                
                clicker['start_btn'].configure(state='normal')
                clicker['stop_btn'].configure(state='disabled')
                clicker['status_label'].configure(text="Idle")
                break
        
        self.update_global_status()

    def perform_clicks(self, clicker):
        try:
            x = int(clicker['x_entry'].get() or 0)
            y = int(clicker['y_entry'].get() or 0)
            interval_ms = int(clicker['interval_entry'].get() or 1000)
            click_type = clicker['click_type'].get()
            stop_condition = clicker['stop_condition_var'].get()
            stop_time_seconds = int(clicker['stop_time_entry'].get() or 3600)
            
            mouse_controller = Controller()
            button_map = {'Left': Button.left, 'Right': Button.right}
            
            clicker['start_time'] = time.time()
            clicker['clicks'] = 0
            
            while clicker['running']:
                # Check if we should stop due to time limit
                if stop_condition == "Time" and time.time() >= clicker['start_time'] + stop_time_seconds:
                    break
                
                # Move to position and click
                mouse_controller.position = (x, y)
                mouse_controller.click(button_map[click_type])
                
                clicker['clicks'] += 1
                
                # Wait for next click
                time.sleep(interval_ms / 1000.0)
            
            # Auto-stop when time is up
            if stop_condition == "Time" and time.time() >= clicker['start_time'] + stop_time_seconds:
                self.after(0, lambda: self.stop_clicker(clicker['id']))
                messagebox.showinfo("Info", f"Clicker #{clicker['id']} stopped after {stop_time_seconds} seconds")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error in clicker #{clicker['id']}: {e}")
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
            # Update the global control button texts
            self.start_all_btn.configure(text=f"Start All ({self.hotkey.upper()})")
            self.stop_all_btn.configure(text=f"Stop All ({self.hotkey.upper()})")
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
