import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyaudio
import wave
import threading
import speech_recognition as sr

# Kayıt durumu
is_recording = False
output_filename = "output.wav"
frames = []
recognizer = sr.Recognizer()

def set_window_center(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

def record_audio():
    global is_recording, frames
    if is_recording:
        print("Zaten kayıt yapılıyor.")
        return
    
    is_recording = True
    frames = []
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
            recognize_speech(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()

    t = threading.Thread(target=record_frames)
    t.start()

def stop_recording():
    global is_recording
    if is_recording:
        is_recording = False
        print("Kayıt durduruldu.")
        save_audio()

def save_audio():
    global frames, output_filename
    audio = pyaudio.PyAudio()
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

def recognize_speech(audio_data):
    audio = sr.AudioData(audio_data, 44100, 2)
    try:
        text = recognizer.recognize_google(audio, language='tr-TR')  # Türkçe tanıma
        update_text_area(text)
    except sr.UnknownValueError:
        print("Google Ses Tanıma sesi anlayamadı")
    except sr.RequestError as e:
        print(f"Google Ses Tanıma servisine erişim hatası; {e}")

def update_text_area(text):
    text_area.insert(tk.END, text + " ")
    text_area.see(tk.END)

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
root.configure(background="red")

# Stil tanımlamaları
style = ttk.Style()
style.configure("Normal.TFrame")
style.configure("Highlighted.TFrame", background="#83FFFD")

profiles = [
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Ahmet"),
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Özlem"),
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Ali"),
    ("C:\\Users\\Hp\\OneDrive\\Masaüstü\\Python\\profil.png", "Can")
]

profile_frame = ttk.Frame(root, style="Red.TFrame")
profile_frame.pack(pady=10)

style = ttk.Style()
style.configure("Red.TFrame", background="red")

# Ana stil oluştur
style = ttk.Style()
style.configure("Profile.TFrame", background="red")

for i, (path, name) in enumerate(profiles):
    sub_frame = ttk.Frame(profile_frame, style="Profile.TFrame")  # Ana stili kullan
    sub_frame.grid(row=0, column=i, padx=20, pady=10)

    img = Image.open(path).resize((150, 150))
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(sub_frame, image=photo, background="red")
    label.image = photo
    label.pack()

    name_label = tk.Label(sub_frame, text=name, foreground="black", font=("Arial", 18, "bold"), background="red")
    name_label.pack()

    # Boş resim oluşturarak yer tutucu ekle
    empty_image = Image.new('RGBA', (45, 45), (255, 255, 255, 0))
    empty_photo = ImageTk.PhotoImage(empty_image)

    record_icon = Image.open("record_icon3.png").resize((50, 50))
    record_photo = ImageTk.PhotoImage(record_icon)

    # Başlangıçta boş resim ile yer tutucu olarak oluştur
    record_label = tk.Label(sub_frame, image=empty_photo, background="red")
    record_label.image = empty_photo
    record_label.pack()  # Boş resimle yerleştir

    button_open = ttk.Button(sub_frame, text=f"{name} açmak", command=lambda sf=sub_frame, nl=name_label, rl=record_label: on_button_click("açmak", sf, nl, rl))
    button_open.pack(pady=5)

    button_close = ttk.Button(sub_frame, text=f"{name} kapatmak", command=lambda sf=sub_frame, nl=name_label, rl=record_label: on_button_click("kapatmak", sf, nl, rl))
    button_close.pack(pady=5)

    def on_button_click(action, sub_frame, name_label, record_label):
        if action == "açmak":
            sub_frame.config(borderwidth=2, relief="solid", style="Highlighted.TFrame")  # Stili ayarla
            name_label.config(foreground="blue", background="#83FFFD")
            record_label.config(image=record_photo, background="#83FFFD")  # Gerçek resmi göster
            record_label.image = record_photo  # Referansı güncelle
        elif action == "kapatmak":
            sub_frame.config(borderwidth=0, relief="flat", style="Profile.TFrame")  # Normal stile geri dön
            name_label.config(foreground="black", background="red")
            record_label.config(image=empty_photo, background="red")  # Boş resmi göster
            record_label.image = empty_photo  # Referansı güncelle 

button_frame = ttk.Frame(root, width=800, height=50, style="Red.TFrame")
button_frame.pack(padx=675, pady=10, fill=tk.BOTH)

style = ttk.Style()
style.configure("Red.TFrame", background="red")

record_img = Image.open("play-button.png").resize((50, 50))
stop_img = Image.open("pause-button.png").resize((50, 50))

record_icon = ImageTk.PhotoImage(record_img)
stop_icon = ImageTk.PhotoImage(stop_img)

record_button = ttk.Button(button_frame, image=record_icon, command=record_audio, cursor="hand2")
record_button.grid(row=0, column=0, padx=20)

stop_button = ttk.Button(button_frame, image=stop_icon, command=stop_recording, cursor="hand2")
stop_button.grid(row=0, column=1, padx=20)

result_frame = ttk.Frame(root, width=800, height=350, style="Red.TFrame")
result_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

style = ttk.Style()
style.configure("Red.TFrame", background="red")

# Metin alanı oluştur ve yerleştir
text_frame = ttk.Frame(result_frame)
text_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=20, pady=10)

text_area = tk.Text(text_frame, height=8, wrap=tk.WORD, font=("Arial", 12), background="#f7e9b6", padx=10, pady=10)
text_area.pack(fill=tk.BOTH, expand=True)

table = ttk.Treeview(result_frame, columns=("Kişi", "Kelime Sayısı", "Konuşma Oranı"), show="headings")
table.heading("Kişi", text="Kişi")
table.heading("Kelime Sayısı", text="Kelime Sayısı")
table.heading("Konuşma Oranı", text="Konuşma Oranı")
table.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

veriler = [
    ("Ahmet", 5, "20%"),
    ("Özlem", 8, "40%"),
    ("Ali", 7, "35%"),
    ("Can", 3, "5%")
]

for veri in veriler:
    table.insert('', tk.END, values=veri)

root.mainloop()
