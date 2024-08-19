import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyaudio
import wave
import threading

# Kayıt düğmeleri
is_recording = False
output_filename = "output.wav"
frames = []

def set_window_center(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

def record_audio():
    global is_recording
    if is_recording:
        print("Zaten kayıt yapılıyor.")
        return
    
    is_recording = True
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Kayıt başlatıldı.")

    def record_frames():
        global frames
        while is_recording:
            data = stream.read(CHUNK)
            frames.append(data)

    t = threading.Thread(target=record_frames)
    t.start()

def stop_recording():
    global is_recording
    if is_recording:
        is_recording = False
        print("Kayıt durduruldu.")
        save_audio()

def save_audio():
    global frames
    global output_filename
    audio = pyaudio.PyAudio()
    stream = audio.open(format=audio.get_format_from_width(2), channels=2, rate=44100, output=True)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()
    frames = []

def on_button_click(action, sub_frame, name_label, record_label):
    if action == "açmak":
        sub_frame.config(borderwidth=2, relief="solid", style="Highlighted.TFrame")  # Stili ayarla
        name_label.config(foreground="blue")
        record_label.pack()  # Resmi göster
    elif action == "kapatmak":
        sub_frame.config(borderwidth=0, relief="flat", style="TFrame")  # Normal stile geri dön
        name_label.config(foreground="black")
        record_label.pack_forget()  # Resmi gizle

root = tk.Tk()
root.title("Ses Tanımlama Projesi")
set_window_center(root, 1000, 600)

# Stil tanımlamaları
style = ttk.Style()
style.configure("Normal.TFrame", background="white")
style.configure("Highlighted.TFrame", background="white")

profiles = [
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Ahmet"),
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Özlem"),
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Ali"),
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Can")
]

# Profil resimlerini ve isimlerini eklemek için çerçeve oluştur
profile_frame = ttk.Frame(root)
profile_frame.pack(pady=10)

for i, (path, name) in enumerate(profiles):
    sub_frame = ttk.Frame(profile_frame, style="Normal.TFrame")
    sub_frame.grid(row=0, column=i, padx=20, pady=10)

    img = Image.open(path).resize((150, 150))
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(sub_frame, image=photo)
    label.image = photo
    label.pack()

    name_label = tk.Label(sub_frame, text=name, foreground="black", font=("Arial", 18, "bold"))
    name_label.pack()

    # Resmi içeren çerçeve
    record_frame = tk.Frame(sub_frame)
    record_frame.pack()

    record_icon = Image.open("record_icon.png").resize((45, 45))
    record_photo = ImageTk.PhotoImage(record_icon)

    record_label = tk.Label(record_frame, image=record_photo)
    record_label.image = record_photo
    record_label.pack_forget()  # Resmi başlangıçta gizle

    button_sub_frame = ttk.Frame(sub_frame)
    button_sub_frame.pack()

    button_open = ttk.Button(button_sub_frame, text=f"{name} açmak", command=lambda sf=sub_frame, nl=name_label, rl=record_label: on_button_click("açmak", sf, nl, rl))
    button_open.pack(pady=5)

    button_close = ttk.Button(button_sub_frame, text=f"{name} kapatmak", command=lambda sf=sub_frame, nl=name_label, rl=record_label: on_button_click("kapatmak", sf, nl, rl))
    button_close.pack(pady=5)

button_frame = ttk.Frame(root, width=800, height=50)
button_frame.pack(padx=675, pady=10, fill=tk.BOTH)

record_img = Image.open("play-button.png").resize((50, 50))
stop_img = Image.open("pause-button.png").resize((50, 50))

record_icon = ImageTk.PhotoImage(record_img)
stop_icon = ImageTk.PhotoImage(stop_img)

record_button = ttk.Button(button_frame, image=record_icon, command=record_audio, cursor="hand2")
record_button.grid(row=0, column=0, padx=20)

stop_button = ttk.Button(button_frame, image=stop_icon, command=stop_recording, cursor="hand2")
stop_button.grid(row=0, column=1, padx=20)

result_frame = ttk.Frame(root, width=800, height=250)
result_frame.pack(padx=20, pady=20, fill=tk.BOTH)

table = ttk.Treeview(result_frame, columns=("Kişi", "Kelime Sayısı", "Konuşma Oranı", "Duygu Durumu"), show="headings")
table.heading("Kişi", text="Kişi")
table.heading("Kelime Sayısı", text="Kelime Sayısı")
table.heading("Konuşma Oranı", text="Konuşma Oranı")
table.heading("Duygu Durumu", text="Duygu Durumu")
table.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

veriler = [
    ("Ahmet", 1500, 0.75, "Mutlu"),
    ("Özlem", 2000, 0.85, "Sinirli"),
    ("Ali", 1200, 0.65, "Üzgün"),
    ("Can", 1800, 0.80, "Nötr")
]

for data in veriler:
    kisi, kelime_sayisi, konusma_orani, duygu_durumu = data
    table.insert("", "end", values=[kisi, kelime_sayisi, konusma_orani, duygu_durumu])

root.mainloop()
