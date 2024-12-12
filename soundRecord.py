import pyaudio
import numpy as np
import wave
import time
from tkinter import Tk, Label
from threading import Thread, Event

# Ses ayarları
CHUNK = 1024  # Örnek başına okunan veri
FORMAT = pyaudio.paInt16  # 16-bit ses formatı
CHANNELS = 1  # Mono
RATE = 44100  # Örnekleme hızı (Hz)
DURATION = 20  # Kayıt süresi (saniye)
WAIT_TIME = 600  # Tekrarlama süresi (saniye)

def record_audio_to_wav(duration, filename, update_label_func):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    update_label_func(text='Recording...')
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    update_label_func(text='Recorded. Waiting...')

    # Save audio data as WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def start_recording_thread(label, stop_event):
    while not stop_event.is_set():
        current_time = time.strftime("%Y%m%d-%H%M%S")  # Zaman damgası
        wav_filename = f'output_{current_time}.wav'

        record_audio_to_wav(DURATION, wav_filename, label.config)

        for remaining in range(WAIT_TIME - DURATION, 0, -1):
            if stop_event.is_set():
                break
            label.config(text=f'Next recording in {remaining} seconds...')
            time.sleep(1)
    label.config(text='Recording stopped.')

def on_close(stop_event, root):
    stop_event.set()
    root.destroy()

# GUI setup
root = Tk()
root.title("Audio Recorder")
root.geometry("300x100")

label = Label(root, text="Waiting to start...")
label.pack(pady=20)

stop_event = Event()
thread = Thread(target=start_recording_thread, args=(label, stop_event))
thread.start()

root.protocol("WM_DELETE_WINDOW", lambda: on_close(stop_event, root))
root.mainloop()

# Wait for thread to finish before exiting
thread.join()