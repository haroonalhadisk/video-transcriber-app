import os
import sys
import subprocess
import tkinter as tk

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
    
    # Import local modules after package check
    from video_transcriber_gui import VideoTranscriberGUI
    
    # Import the batch processing functionality and attach it to the GUI class
    import batch_processing
    VideoTranscriberGUI.integrate_batch_processing = batch_processing.integrate_batch_processing
    
    # Import the Instagram integration functionality and attach it to the GUI class
    import instagram_integration
    VideoTranscriberGUI.integrate_instagram = instagram_integration.integrate_instagram
        
    root = tk.Tk()
    app = VideoTranscriberGUI(root)
    
    # Initialize Instagram integration if enabled
    if hasattr(app, 'integrate_instagram'):
        app.integrate_instagram()
    
    root.mainloop()

if __name__ == "__main__":
    main()