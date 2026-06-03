import logging
import subprocess
import threading

LOGGER = logging.getLogger(__name__)


class TextToSpeechService:
    def __init__(self):
        self.enabled = True

    def speak(self, text):
        clean_text = self._validate_text(text)
        thread = threading.Thread(target=self._speak_windows, args=(clean_text,), daemon=True)
        thread.start()
        return {
            "status": "queued",
            "text": clean_text,
        }

    def _validate_text(self, text):
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")

        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Text is required.")

        if len(clean_text) > 500:
            raise ValueError("Text-to-speech input must be 500 characters or fewer.")

        return clean_text

    def _speak_windows(self, text):
        if not self.enabled:
            return

        try:
            command = (
                "Add-Type -AssemblyName System.Speech; "
                "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$speak.Speak($args[0])"
            )
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", command, text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            LOGGER.exception("Text-to-speech playback failed")


tts_service = TextToSpeechService()
