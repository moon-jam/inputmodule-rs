import os
import threading
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from inputmodule.inputmodule import (
    send_command,
    get_version,
    brightness,
    get_brightness,
    bootloader,
    CommandVals,
)
from inputmodule.gui.games import snake
from inputmodule.gui.ledmatrix import countdown, random_eq, clock
from inputmodule.gui.gui_threading import stop_thread, is_dev_disconnected
from inputmodule.inputmodule.ledmatrix import (
    percentage,
    pattern,
    animate,
    PATTERNS,
    PWM_FREQUENCIES,
    show_symbols,
    show_string,
    pwm_freq,
    image_bl,
    image_greyscale,
)

def update_brightness_slider(devices):
    average_brightness = None
    for dev in devices:
        if not average_brightness:
            average_brightness = 0

        br = get_brightness(dev)
        average_brightness += br
    if average_brightness:
        brightness_scale.set(average_brightness)

def popup(message):
    messagebox.showinfo("Framework Laptop 16 LED Matrix", message)

def run_gui(devices):
    root = tk.Tk()
    root.title("LED Matrix Control")
    root.geometry("400x900")

    # Configure dark theme
    style = ttk.Style()
    root.configure(bg="#2b2b2b")
    style.configure("TLabelframe", background="#2b2b2b", foreground="white")
    style.configure("TLabelframe.Label", background="#2b2b2b", foreground="white")
    style.configure("TCheckbutton", background="#2b2b2b", foreground="white")
    style.configure("TButton", background="white", foreground="#2b2b2b")
    style.configure("TEntry", fieldbackground="#2b2b2b", foreground="white")
    style.configure("TCombobox", fieldbackground="#2b2b2b", foreground="white")
    style.configure("TScale", background="#2b2b2b", troughcolor="gray")
    style.configure("TSpinbox", background="#2b2b2b", foreground="white")
    style.map("TButton", background=[("active", "gray"), ("!active", "#2b2b2b")])
    
    # Device Checkboxes
    detected_devices_frame = ttk.LabelFrame(root, text="Detected Devices", style="TLabelframe")
    detected_devices_frame.pack(fill="x", padx=10, pady=5)

    global device_checkboxes
    device_checkboxes = {}
    for dev in devices:
        version = get_version(dev)
        device_info = (
            f"{dev.name}\nSerial No: {dev.serial_number}\nFW Version:{version}"
        )
        checkbox_var = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(detected_devices_frame, text=device_info, variable=checkbox_var, style="TCheckbutton")
        checkbox.pack(anchor="w")
        device_checkboxes[dev.name] = checkbox_var

    # Device Control Buttons
    device_control_frame = ttk.LabelFrame(root, text="Device Control", style="TLabelframe")
    device_control_frame.pack(fill="x", padx=10, pady=5)
    control_buttons = {
        "Bootloader": "bootloader",
        "Sleep": "sleep",
        "Wake": "wake"
    }
    for text, action in control_buttons.items():
        ttk.Button(device_control_frame, text=text, command=lambda a=action: perform_action(devices, a), style="TButton").pack(side="left", padx=5, pady=5)

    # Brightness Slider
    brightness_frame = ttk.LabelFrame(root, text="Brightness", style="TLabelframe")
    brightness_frame.pack(fill="x", padx=10, pady=5)
    global brightness_scale
    brightness_scale = tk.Scale(brightness_frame, from_=0, to=255, orient='horizontal', command=lambda value: set_brightness(devices, value), bg="#2b2b2b", fg="white", troughcolor="gray", highlightbackground="#2b2b2b")
    brightness_scale.set(120)  # Default value
    brightness_scale.pack(fill="x", padx=5, pady=5)

    # Animation Control
    animation_frame = ttk.LabelFrame(root, text="Animation", style="TLabelframe")
    animation_frame.pack(fill="x", padx=10, pady=5)
    animation_buttons = {
        "Start Animation": "start_animation",
        "Stop Animation": "stop_animation"
    }
    for text, action in animation_buttons.items():
        ttk.Button(animation_frame, text=text, command=lambda a=action: perform_action(devices, a), style="TButton").pack(side="left", padx=5, pady=5)

    # Pattern Combo Box
    pattern_frame = ttk.LabelFrame(root, text="Pattern", style="TLabelframe")
    pattern_frame.pack(fill="x", padx=10, pady=5)
    pattern_combo = ttk.Combobox(pattern_frame, values=PATTERNS, style="TCombobox")
    pattern_combo.pack(fill="x", padx=5, pady=5)
    pattern_combo.bind("<<ComboboxSelected>>", lambda event: set_pattern(devices, pattern_combo.get()))

    # Percentage Slider
    percentage_frame = ttk.LabelFrame(root, text="Fill screen X% (could be volume indicator)", style="TLabelframe")
    percentage_frame.pack(fill="x", padx=10, pady=5)
    percentage_scale = tk.Scale(percentage_frame, from_=0, to=100, orient='horizontal', command=lambda value: set_percentage(devices, value), bg="#2b2b2b", fg="white", troughcolor="gray", highlightbackground="#2b2b2b")
    percentage_scale.pack(fill="x", padx=5, pady=5)

    # Countdown Timer
    countdown_frame = ttk.LabelFrame(root, text="Countdown Timer", style="TLabelframe")
    countdown_frame.pack(fill="x", padx=10, pady=5)
    countdown_spinbox = tk.Spinbox(countdown_frame, from_=1, to=60, width=5, bg="#2b2b2b", fg="white", textvariable=tk.StringVar(value=10))
    countdown_spinbox.pack(side="left", padx=5, pady=5)
    ttk.Label(countdown_frame, text="Seconds", style="TLabel").pack(side="left")
    ttk.Button(countdown_frame, text="Start", command=lambda: start_countdown(devices, countdown_spinbox.get()), style="TButton").pack(side="left", padx=5, pady=5)
    ttk.Button(countdown_frame, text="Stop", command=stop_thread, style="TButton").pack(side="left", padx=5, pady=5)

    # Black & White and Greyscale Images in same row
    image_frame = ttk.LabelFrame(root, text="Black&White Images / Greyscale Images", style="TLabelframe")
    image_frame.pack(fill="x", padx=10, pady=5)
    ttk.Button(image_frame, text="Send stripe.gif", command=lambda: send_image(devices, "stripe.gif", image_bl), style="TButton").pack(side="left", padx=5, pady=5)
    ttk.Button(image_frame, text="Send greyscale.gif", command=lambda: send_image(devices, "greyscale.gif", image_greyscale), style="TButton").pack(side="left", padx=5, pady=5)

    # Display Current Time
    time_frame = ttk.LabelFrame(root, text="Display Current Time", style="TLabelframe")
    time_frame.pack(fill="x", padx=10, pady=5)
    ttk.Button(time_frame, text="Start", command=lambda: perform_action(devices, "start_time"), style="TButton").pack(side="left", padx=5, pady=5)
    ttk.Button(time_frame, text="Stop", command=stop_thread, style="TButton").pack(side="left", padx=5, pady=5)

    # Custom Text
    custom_text_frame = ttk.LabelFrame(root, text="Custom Text", style="TLabelframe")
    custom_text_frame.pack(fill="x", padx=10, pady=5)
    custom_text_entry = ttk.Entry(custom_text_frame, width=20, style="TEntry")
    custom_text_entry.pack(side="left", padx=5, pady=5)
    ttk.Button(custom_text_frame, text="Show", command=lambda: show_custom_text(devices, custom_text_entry.get()), style="TButton").pack(side="left", padx=5, pady=5)

    # Display Text with Symbols
    symbols_frame = ttk.LabelFrame(root, text="Display Text with Symbols", style="TLabelframe")
    symbols_frame.pack(fill="x", padx=10, pady=5)
    ttk.Button(symbols_frame, text="Send '2 5 degC thunder'", command=lambda: send_symbols(devices), style="TButton").pack(side="left", padx=5, pady=5)

    # PWM Frequency Combo Box
    pwm_freq_frame = ttk.LabelFrame(root, text="PWM Frequency", style="TLabelframe")
    pwm_freq_frame.pack(fill="x", padx=10, pady=5)
    pwm_freq_combo = ttk.Combobox(pwm_freq_frame, values=PWM_FREQUENCIES, style="TCombobox")
    pwm_freq_combo.pack(fill="x", padx=5, pady=5)
    pwm_freq_combo.bind("<<ComboboxSelected>>", lambda: set_pwm_freq(devices, pwm_freq_combo.get()))

    # Equalizer
    equalizer_frame = ttk.LabelFrame(root, text="Equalizer", style="TLabelframe")
    equalizer_frame.pack(fill="x", padx=10, pady=5)
    ttk.Button(equalizer_frame, text="Start random equalizer", command=lambda: perform_action(devices, "start_eq"), style="TButton").pack(side="left", padx=5, pady=5)
    ttk.Button(equalizer_frame, text="Stop", command=stop_thread, style="TButton").pack(side="left", padx=5, pady=5)

    root.mainloop()

def perform_action(devices, action):
    action_map = {
        "bootloader": bootloader,
        "sleep": lambda dev: send_command(dev, CommandVals.Sleep, [True]),
        "wake": lambda dev: send_command(dev, CommandVals.Sleep, [False]),
        "start_animation": lambda dev: animate(dev, True),
        "stop_animation": lambda dev: animate(dev, False),
        "start_time": lambda dev: threading.Thread(target=clock, args=(dev,), daemon=True).start(),
        "start_eq": lambda dev: threading.Thread(target=random_eq, args=(dev,), daemon=True).start()
    }
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        if action in action_map:
            action_map[action](dev)

def set_brightness(devices, value):
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        brightness(dev, int(value))

def set_pattern(devices, pattern_name):
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        pattern(dev, pattern_name)

def set_percentage(devices, value):
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        percentage(dev, int(value))

def show_custom_text(devices, text):
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        show_string(dev, text.upper())

def send_image(devices, image_name, image_function):
    selected_devices = get_selected_devices(devices)
    path = os.path.join(resource_path(), "res", image_name)
    if not os.path.exists(path):
        popup(f"Image file {image_name} not found.")
        return
    for dev in selected_devices:
        image_function(dev, path)

def send_symbols(devices):
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        show_symbols(dev, ["2", "5", "degC", " ", "thunder"])

def start_countdown(devices, countdown_time):
    selected_devices = get_selected_devices(devices)
    if len(selected_devices) == 1:
        dev = selected_devices[0]
        threading.Thread(target=countdown, args=(dev, int(countdown_time)), daemon=True).start()
    else:
        popup("Select exactly 1 device for this action")

def set_pwm_freq(devices, freq):
    selected_devices = get_selected_devices(devices)
    for dev in selected_devices:
        pwm_freq(dev, freq)

def get_selected_devices(devices):
    return [dev for dev in devices if dev.name in device_checkboxes and device_checkboxes[dev.name].get()]

def resource_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("../../")

    return base_path
