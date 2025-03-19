import os
import time
import asyncio
import sounddevice as sd
import numpy as np
import wave
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QThread, pyqtSignal
from pypresence import Presence
from bleak import BleakScanner

# Discord Rich Presence
CLIENT_ID = "1351667093283536896"  # Remplace par ton ID Discord
rpc = Presence(CLIENT_ID)
try:
    rpc.connect()
    rpc.update(state="En ligne sur Just Chat", details="Discussion Bluetooth", large_image="logo")
except Exception as e:
    print(f"Erreur Discord RPC: {e}")

# Créer un dossier pour stocker les messages vocaux
SAVE_DIR = "messages_vocaux"
os.makedirs(SAVE_DIR, exist_ok=True)

class VoiceRecorder(QThread):
    """Thread pour enregistrer un message vocal sans bloquer l'interface."""
    recording_done = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        duration = 5  # secondes
        sample_rate = 44100  # Fréquence d'échantillonnage standard (évite le pitch trop bas)
        channels = 1  # Mono pour éviter d'avoir un canal vide

        filename = os.path.join(SAVE_DIR, f"{self.username}_voice_{int(time.time())}.wav")

        print("🔴 Enregistrement...")
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype=np.int16)
        sd.wait()

        print("✅ Enregistrement terminé !")

        # Sauvegarde du fichier correctement
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16 bits (2 octets)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())

        self.recording_done.emit(filename)

class JustChat(QWidget):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Just Chat")
        self.setGeometry(100, 100, 600, 400)
        
        self.layout = QVBoxLayout()
        self.setFont(QFont("Arial", 12))
        
        self.label = QLabel("Entrez votre pseudo:")
        self.input_username = QLineEdit()
        self.button_submit = QPushButton("Valider")
        self.button_submit.clicked.connect(self.setUsername)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_username)
        self.layout.addWidget(self.button_submit)
        
        self.setLayout(self.layout)
    
    def setUsername(self):
        self.username = self.input_username.text().strip()
        if self.username:
            self.showChat()
    
    def showChat(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()
        
        self.chat_title = QLabel(f"Just Chat - {self.username}")
        self.chat_title.setFont(QFont("Arial", 16))
        
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Envoyer")
        self.send_button.setEnabled(True)
        self.send_button.clicked.connect(self.sendMessage)

        self.voice_button = QPushButton("🎤 Enregistrer un message vocal")
        self.voice_button.setEnabled(True)
        self.voice_button.clicked.connect(self.recordVoiceMessage)

        self.play_button = QPushButton("▶ Écouter le dernier message vocal")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.playVoiceMessage)

        self.layout.addWidget(self.chat_title)
        self.layout.addWidget(self.chat_box)
        self.layout.addWidget(self.message_input)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.voice_button)
        self.layout.addWidget(self.play_button)
        
        self.setLayout(self.layout)
    
    def sendMessage(self):
        message = self.message_input.text().strip()
        if message:
            self.chat_box.append(f"Vous: {message}")
            self.message_input.clear()

    def recordVoiceMessage(self):
        self.chat_box.append("🎤 Enregistrement en cours... Parlez maintenant !")
        self.voice_thread = VoiceRecorder(self.username)
        self.voice_thread.recording_done.connect(self.onRecordingFinished)
        self.voice_thread.start()

    def onRecordingFinished(self, filename):
        self.chat_box.append(f"📤 Message vocal enregistré : {filename}")
        self.play_button.setEnabled(True)

    def playVoiceMessage(self):
        """Joue le dernier message vocal enregistré."""
        files = sorted(os.listdir(SAVE_DIR), reverse=True)
        if files:
            last_file = os.path.join(SAVE_DIR, files[0])
            self.chat_box.append(f"▶ Lecture de {last_file}...")
            self.playAudio(last_file)

    def playAudio(self, filename):
        """Lit un fichier audio."""
        with wave.open(filename, 'rb') as wf:
            sample_rate = wf.getframerate()
            audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            sd.play(audio_data, samplerate=sample_rate)
            sd.wait()
            self.chat_box.append("🔊 Lecture terminée.")

if __name__ == "__main__":
    app = QApplication([])
    window = JustChat()
    window.show()
    app.exec()
