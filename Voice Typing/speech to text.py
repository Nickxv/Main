import tkinter as tk
from tkinter import ttk
import speech_recognition as sr

class VoiceTypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Typing App")
        self.root.geometry("800x400")

        self.label = ttk.Label(root, text="Press the button and start speaking:")
        self.label.pack(pady=10)

        self.text_var = tk.StringVar()
        self.entry = ttk.Entry(root, textvariable=self.text_var, state='readonly', font=('Arial', 12))
        self.entry.pack(pady=10, padx=10, fill=tk.X)

        self.start_button = ttk.Button(root, text="Start Typing", command=self.start_typing)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.recognizer = sr.Recognizer()

    def start_typing(self):
        self.text_var.set("Listening...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.root.update()

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=5)

        try:
            text = self.recognizer.recognize_google(audio)
            self.text_var.set(text)
        except sr.UnknownValueError:
            self.text_var.set("Sorry, could not understand audio.")
        except sr.RequestError as e:
            self.text_var.set(f"Could not request results from Google Speech Recognition service; {e}")

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def stop_listening(self):
        self.recognizer.stop()
        self.text_var.set("Listening stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceTypingApp(root)
    root.mainloop()
