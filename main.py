import os
import sys
import subprocess
import tkinter as tk
from video_transcriber_gui import VideoTranscriberGUI

def main():
    # Check for required packages
    try:
        import whisper
        import torch
        import requests  # For Notion API
    except ImportError:
        print("Required packages not found. Installing...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "torch", "openai-whisper", "requests"
        ])
        print("Installation complete. Please restart the application.")
        input("Press Enter to exit...")
        sys.exit(1)
        
    root = tk.Tk()
    app = VideoTranscriberGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()