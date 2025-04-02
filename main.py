import os
import sys
import subprocess
import argparse
import tkinter as tk

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Video Transcriber with Whisper AI')
    parser.add_argument('-web', '--web', action='store_true', help='Run in web UI mode with Gradio')
    args = parser.parse_args()
    
    # Check for required packages
    if args.web:
        # Check if Gradio is installed for web mode
        try:
            import gradio
        except ImportError:
            print("Gradio not found. Installing required packages for web mode...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "torch", "openai-whisper", "requests", "gradio"
                ])
                print("Installation complete. Please restart the application.")
                input("Press Enter to exit...")
                sys.exit(1)
            except Exception as e:
                print(f"Error installing packages: {e}")
                sys.exit(1)
        
        # Start the web UI
        from web_ui import create_web_ui
        app = create_web_ui()
        app.launch()
    else:
        # Traditional GUI mode
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
        VideoTranscriberGUI.integrate_instagram = instagram_integration.integrate_instaloader
        
        # Import batch Instagram processing module if it exists
        try:
            import batch_instagram_integration
            # We'll use this in instagram_integration.py with extend_instagram_integration
        except ImportError:
            print("Batch Instagram processing module not found. Continuing without it.")
            
        # Import saved posts integration if it exists
        try:
            from saved_posts_integration import integrate_instagram_saved
            VideoTranscriberGUI.integrate_instagram_saved = integrate_instagram_saved
        except ImportError:
            print("Instagram saved posts module not found. Continuing without it.")
            
        root = tk.Tk()
        app = VideoTranscriberGUI(root)
        
        # Initialize Instagram integration if enabled
        if hasattr(app, 'integrate_instagram'):
            app.integrate_instagram()
        
        # Initialize Instagram saved posts integration if enabled
        if hasattr(app, 'integrate_instagram_saved'):
            app.integrate_instagram_saved()
        
        root.mainloop()

if __name__ == "__main__":
    main()