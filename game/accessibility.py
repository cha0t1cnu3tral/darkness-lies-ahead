"""Native wx controls expose MSAA; game events also reach NVDA speech/braille."""

import ctypes
import logging
import os
from .paths import ROOT


class Narrator:
    def __init__(self, settings):
        self.settings = settings
        self.client = None
        if os.name == "nt":
            try:
                client = ctypes.WinDLL(str(ROOT / "vendor" / "nvda" / "nvdaControllerClient.dll"))
                client.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
                client.nvdaController_brailleMessage.argtypes = [ctypes.c_wchar_p]
                self.client = client
            except OSError:
                logging.exception("NVDA controller unavailable")

    def available(self):
        return bool(self.client and self.client.nvdaController_testIfRunning() == 0)

    def say(self, text):
        if not self.settings["speech"] or not self.available():
            return False
        self.client.nvdaController_cancelSpeech()
        self.client.nvdaController_speakText(text)
        self.client.nvdaController_brailleMessage(text)
        return True

    def close(self):
        if self.available():
            self.client.nvdaController_cancelSpeech()
