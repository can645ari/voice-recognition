import pyaudio
import wave
import speech_recognition as sr
from sklearn.preprocessing import LabelEncoder
import librosa
import joblib
import numpy as np
import time

# Ses kaydı ve gerçek zamanlı tahmin için ayarlar
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Gerçek zamanlı ses kaydı
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    print("Recording...")
    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

# Konuşma tanıma
def recognize_speech(file_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file_path)
    with audio_file as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language='tr-TR')
        #print(f"Recognized Text: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Özellik çıkarma
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

# Tek bir ses dosyasını tahmin etme
def predict_single_file(file_path, model):
    try:
        audio_data, sr = librosa.load(file_path, sr=22050)
        audio_data = librosa.util.normalize(audio_data)
        features = extract_features(audio_data, sr)
        features = features.reshape(1, -1)  # Yeniden şekillendir
        prediction = model.predict(features)
        return prediction[0]
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Kaydedilen ses dosyasını kullanarak tahmin yapma ve konuşma tanıma
def predict_and_recognize(model):
    record_audio()
    predicted_label = predict_single_file(WAVE_OUTPUT_FILENAME, model)
    recognized_text = recognize_speech(WAVE_OUTPUT_FILENAME)
    
    if recognized_text:
        print(f"Predicted Label: {predicted_label}")
        print(f"Recognized Speech: {recognized_text}")
    else:
        print("No speech recognized.")

# Modeli yükleme
model = joblib.load("C:\\Users\\Hp\\Downloads\\AhmetModeli.pkl")

# Sonsuz döngü içinde tahmin ve konuşma tanıma
while True:
    predict_and_recognize(model)
    print("Waiting for the next recording...")
    time.sleep(2)  # Yeni kayıt yapmadan önce 2 saniye bekle