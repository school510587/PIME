from __future__ import unicode_literals
import ctypes
import platform
import os

# Load the NVDA client library.
dll_name = "nvdaControllerClient64.dll" if platform.architecture()[0] == "64bit" else "nvdaControllerClient32.dll"
nvdacc_lib = ctypes.windll.LoadLibrary(os.path.join(os.path.dirname(__file__), dll_name))

# Test if the user is running NVDA. If yes, 0 is returned.
def testIfRunning():
    return nvdacc_lib.nvdaController_testIfRunning()

# Ask NVDA to show a specified message on the braille display.
def brailleMessage(message):
    return nvdacc_lib.nvdaController_brailleMessage(message)
# Ask NVDA to speak a specified message.
def speakText(text):
    return nvdacc_lib.nvdaController_speakText(text)

# Interrupt the speech of NVDA.
def cancelSpeech():
    return nvdacc_lib.nvdaController_cancelSpeech()

