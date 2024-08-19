import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import os
import librosa
from sklearn.ensemble import RandomForestClassifier
import joblib
import pyaudio
import threading
import time

# Model yükleme
model = joblib.load("C:\\Users\\Hp\\Downloads\\AhmetModeli2.pkl")

# Tahmin fonksiyonu için özellik çıkarımı
def extract_features(audio_data, sr):
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
    zcr = librosa.feature.zero_crossing_rate(y=audio_data)
    chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(audio_data), sr=sr)
    
    features = np.concatenate((np.mean(mfccs.T, axis=0), 
                               np.mean(zcr.T, axis=0), 
                               np.mean(chroma.T, axis=0),
                               np.mean(spectral_contrast.T, axis=0),
                               np.mean(tonnetz.T, axis=0)))
    return features

# Kayıt parametreleri
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 22050
CHUNK = 1024
DURATION = 3  # Saniye cinsinden tahmin aralığı

is_recording = False

def set_window_center(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")
    root.state('zoomed')  # Tam ekran moduna geçiş

def record_and_predict():
    global is_recording
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while is_recording:
        frames = []
        start_time = time.time()
        while time.time() - start_time < DURATION:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
        audio_data = librosa.util.normalize(audio_data)
        features = extract_features(audio_data, RATE).reshape(1, -1)
        prediction = model.predict(features)[0]

        update_ui(prediction)

    stream.stop_stream()
    stream.close()
    p.terminate()
    reset_ui()  # Kayıt durduktan sonra UI'yi sıfırla

def start_recording():
    global is_recording
    if is_recording:
        return
    is_recording = True
    threading.Thread(target=record_and_predict).start()

def stop_recording():
    global is_recording
    is_recording = False

def update_ui(prediction):
    for name, widgets in profile_widgets.items():
        frame, name_label, record_label = widgets
        if name == prediction:
            frame.config(borderwidth=2, relief="solid", style="Highlighted.TFrame")
            name_label.config(foreground="blue", background="#83FFFD")
            record_label.config(image=record_photo, background="#83FFFD")
        else:
            frame.config(borderwidth=0, relief="flat", style="Profile.TFrame")
            name_label.config(foreground="black", background="red")
            record_label.config(image=empty_photo, background="red")

def reset_ui():
    for name, widgets in profile_widgets.items():
        frame, name_label, record_label = widgets
        frame.config(borderwidth=0, relief="flat", style="Profile.TFrame")
        name_label.config(foreground="black", background="red")
        record_label.config(image=empty_photo, background="red")

root = tk.Tk()
root.title("Ses Tanımlama Projesi")
set_window_center(root)
root.configure(background="red")

# Stil tanımlamaları
style = ttk.Style()
style.configure("Normal.TFrame")
style.configure("Highlighted.TFrame", background="#83FFFD")
style.configure("Red.TFrame", background="red")
style.configure("Profile.TFrame", background="red")

profiles = [
    ("profil.png", "melih"),
    ("profil.png", "ozlem"),
    ("profil.png", "ali"),
    ("profil.png", "can")
]

profile_frame = ttk.Frame(root, style="Red.TFrame")
profile_frame.pack(pady=150)  # Yukarıdan daha fazla boşluk bırakmak için pady değerini artırdık
profile_frame.config(borderwidth=2)

profile_widgets = {}

for path, name in profiles:
    sub_frame = ttk.Frame(profile_frame, style="Profile.TFrame")
    sub_frame.pack(side=tk.LEFT, padx=50, pady=40)

    img = Image.open(path).resize((150, 150))
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(sub_frame, image=photo, background="white")
    label.image = photo
    label.pack()

    name_label = tk.Label(sub_frame, text=name, foreground="black", font=("Arial", 18, "bold"), background="red")
    name_label.pack()

    empty_image = Image.new('RGBA', (45, 45), (255, 255, 255, 0))
    empty_photo = ImageTk.PhotoImage(empty_image)

    record_icon = Image.open("record_icon3.png").resize((100, 100))  # Boyutları 2 kat büyütüldü
    record_photo = ImageTk.PhotoImage(record_icon)

    record_label = tk.Label(sub_frame, image=empty_photo, background="red")
    record_label.image = empty_photo
    record_label.pack()

    profile_widgets[name] = (sub_frame, name_label, record_label)

# Ekran boyutunu al
screen_width = root.winfo_screenwidth()

button_frame = ttk.Frame(root, width=800, height=50, style="Red.TFrame")
button_frame.pack(pady=10, expand=True)  # Ortalamak için expand eklenmiştir

record_img = Image.open("play-button.png").resize((100, 90))  # Boyutları 2 kat büyütüldü
stop_img = Image.open("pause-button.png").resize((100, 90))  # Boyutları 2 kat büyütüldü

record_icon = ImageTk.PhotoImage(record_img)
stop_icon = ImageTk.PhotoImage(stop_img)

record_button = ttk.Button(button_frame, image=record_icon, command=start_recording, cursor="hand2")
record_button.grid(row=0, column=0, padx=20)

stop_button = ttk.Button(button_frame, image=stop_icon, command=stop_recording, cursor="hand2")
stop_button.grid(row=0, column=1, padx=20)

button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

result_frame = ttk.Frame(root, width=800, height=350, style="Red.TFrame")
result_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

# Metin alanı ekleme
text_frame = ttk.Frame(root, style="Red.TFrame")
text_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

result_text = tk.Text(text_frame, height=5, font=("Arial", 12))
result_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
