import os
import warnings
import logging
import asyncio
import wave
import keyboard
import pyaudio
import pyttsx3
import simpleaudio as sa
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
import pyfiglet
from termcolor import colored
import colorama

import PyTubeStudio.client as pts
from llm import run_yumi_agent   # your Grok‑powered agent

# Initialize colorama for cross-platform coloring
debug = True
colorama.init(autoreset=True)

load_dotenv()
warnings.filterwarnings(
    "ignore",
    message=r".*overrides an existing Pydantic .* decorator"
)
warnings.filterwarnings("ignore", category=UserWarning)

# ─── Audio Recording ──────────────────────────────────────────────
def record_audio(path="input.wav"):
    """Record while RIGHT_SHIFT is held down, save to path, and return filepath."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(colored("Hold RIGHT_SHIFT to talk...", "yellow"))
    frames = []
    # Wait for keypress
    while not keyboard.is_pressed('RIGHT_SHIFT'):
        asyncio.sleep(0.1)
    # Record while held
    while keyboard.is_pressed('RIGHT_SHIFT'):
        frames.append(stream.read(CHUNK))
    print(colored("Recording stopped.", "yellow"))

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return path

# ─── Speech Recognition ──────────────────────────────────────────
VOSK_MODEL_PATH = "model-en-us"
def transcribe_vosk(wav_path: str) -> str:
    """Return plain-text transcript of the WAV at wav_path."""
    wf = wave.open(wav_path, "rb")
    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())

    result_text = ""
    while True:
        data = wf.readframes(4000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            result_text += eval(rec.Result()).get("text", "")
    result_text += eval(rec.FinalResult()).get("text", "")
    wf.close()
    return result_text.strip()

# ─── Text‑to‑Speech ───────────────────────────────────────────────
def speak(text: str):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        if debug: print(colored(f"TTS error: {e}", "red"))


def speak_and_play(text: str, filename="yumi.wav"):
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, filename)
        engine.runAndWait()
        wave_obj = sa.WaveObject.from_wave_file(filename)
        wave_obj.play().wait_done()
    except Exception as e:
        if debug: print(colored(f"Audio playback error: {e}", "red"))

# ─── VTuber Session ──────────────────────────────────────────────
async def vtuber_session():
    vts = pts.PyTubeStudio(token_path="yumi_token.txt")
    try:
        await vts.connect()
        await vts.authenticate()
        print(colored("✅ Connected & authenticated to VTube Studio!", "green"))
    except Exception as e:
        print(colored(f"❌ Connection error: {e}", "red"))
        return

    while True:
        try:
            choice = input(colored("\n1=text  2=voice  3=exit → ", "cyan"))
            if choice == '1':
                text = input(colored("Enter message: ", "magenta"))
                reply = run_yumi_agent(text)
                print(colored("Yumi:", "blue"), reply)
                speak_and_play(reply)

            elif choice == '2':
                wav = record_audio()
                user_text = transcribe_vosk(wav)
                print(colored("You said:", "blue"), user_text or colored("[no speech]", "yellow"))
                reply = run_yumi_agent(user_text)
                print(colored("Yumi:", "blue"), reply)
                speak_and_play(reply)

            elif choice == '3':
                print(colored("Goodbye!", "yellow"))
                break

            else:
                print(colored("Invalid entry.", "red"))
        except Exception as e:
            # Catch everything and keep looping
            print(colored(f"Loop error: {e}", "red"))

    try:
        await vts.close()
        print(colored("Session closed.", "yellow"))
    except Exception:
        pass

if __name__ == "__main__":
    banner = colored(pyfiglet.figlet_format("Welcome to Yumi"), "cyan")
    print(banner)
    print(colored("made with ❤️ by Shivanshu Prajapati", "green"))
    asyncio.run(vtuber_session())







