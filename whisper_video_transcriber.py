import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import torch
import whisper
import time

class VideoTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Transcriber - Whisper AI")
        self.root.geometry("750x550")
        self.root.resizable(True, True)
        
        # Set application style
        self.root.minsize(650, 500)
        
        # Variables
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.model_var = tk.StringVar(value="base")
        self.language_var = tk.StringVar(value="en")
        self.keep_audio_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        self.word_timestamps_var = tk.BooleanVar(value=True)
        
        # Create UI elements
        self.create_ui()
        
        # Threading variables
        self.transcription_thread = None
        self.is_transcribing = False
        self.whisper_model = None
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Video file selection
        ttk.Label(file_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(file_frame, text="Browse", command=self.browse_video).grid(row=0, column=2, padx=5, pady=5)
        
        # Output file selection
        ttk.Label(file_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Transcription Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Model selection
        model_frame = ttk.Frame(options_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Whisper Model:").pack(side=tk.LEFT, padx=5)
        
        models = {
            "Tiny (Fast, Less Accurate)": "tiny",
            "Base (Balanced)": "base",
            "Small (Better Accuracy)": "small",
            "Medium (High Accuracy)": "medium",
            "Large (Best Quality, Slow)": "large"
        }
        
        model_combobox = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                     values=list(models.values()), width=15)
        model_combobox.pack(side=tk.LEFT, padx=5)
        
        # Language selection
        language_frame = ttk.Frame(options_frame)
        language_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(language_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        
        languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese": "zh",
            "Auto-detect": None
        }
        
        language_combobox = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                        values=list(languages.values()), width=10)
        language_combobox.pack(side=tk.LEFT, padx=5)
        
        # Timestamp checkbox
        ttk.Checkbutton(options_frame, text="Include word-level timestamps", 
                      variable=self.word_timestamps_var).pack(anchor=tk.W, pady=5)
        
        # Keep audio checkbox
        ttk.Checkbutton(options_frame, text="Keep extracted audio file", 
                      variable=self.keep_audio_var).pack(anchor=tk.W, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Start Transcription", command=self.start_transcription).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_transcription, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)
        self.cancel_button = button_frame.winfo_children()[1]  # Store cancel button reference
        
        # Progress bar and status
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, 
                       variable=self.progress_var, mode='determinate').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status label
        status_label = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=5)
        
        # Output text area
        ttk.Label(main_frame, text="Transcription Preview:").pack(anchor=tk.W, pady=5)
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text.config(state=tk.DISABLED)
    
    def browse_video(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.video_path.set(filename)
            # Auto-create output path
            if not self.output_path.get():
                output_file = os.path.splitext(filename)[0] + "_transcript.txt"
                self.output_path.set(output_file)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save Transcription As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def update_progress(self, value, status_text):
        self.progress_var.set(value)
        self.status_var.set(status_text)
        if value == 100:
            self.is_transcribing = False
            self.cancel_button.config(state=tk.DISABLED)
    
    def update_output_text(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
    
    def extract_audio_with_ffmpeg(self, video_file, audio_file):
        self.update_progress(10, f"Extracting audio from {os.path.basename(video_file)}...")
        
        try:
            # Use FFmpeg to extract audio
            subprocess.run([
                "ffmpeg", "-i", video_file, "-q:a", "0", "-map", "a", audio_file, "-y"
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.update_progress(30, "Audio extracted successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.update_progress(0, f"Error extracting audio: {str(e)}")
            messagebox.showerror("Error", f"Failed to extract audio: {str(e)}")
            return False
        except FileNotFoundError:
            self.update_progress(0, "Error: FFmpeg not found. Please install FFmpeg.")
            messagebox.showerror("Error", "FFmpeg not found. Please install FFmpeg and make sure it's in your PATH.")
            return False
    
    def format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS.MS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def transcribe_with_whisper(self, audio_file, model_name, language, word_timestamps):
        self.update_progress(40, f"Loading Whisper {model_name} model (this may take some time)...")
        
        try:
            # Check for GPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if device == "cuda":
                self.update_progress(45, f"Using GPU acceleration with {device}")
            else:
                self.update_progress(45, f"Using CPU for processing (slower)")
            
            # Load Whisper model
            if self.whisper_model is None or self.whisper_model.model.is_multilingual != (language is not None):
                self.whisper_model = whisper.load_model(model_name, device=device)
            
            self.update_progress(50, "Model loaded. Transcribing audio...")
            
            # Run transcription
            transcribe_options = {
                "task": "transcribe",
                "verbose": False,
                "word_timestamps": word_timestamps,
            }
            
            if language:
                transcribe_options["language"] = language
            
            start_time = time.time()
            result = self.whisper_model.transcribe(audio_file, **transcribe_options)
            elapsed = time.time() - start_time
            
            self.update_progress(90, f"Transcription completed in {elapsed:.2f} seconds")
            
            # Format output based on word timestamps option
            if word_timestamps and 'words' in result:
                # Create detailed output with word-level timestamps
                detailed_text = result['text']
                
                # Create a timestamped transcript
                timestamped_text = []
                segment_start = None
                current_text = []
                
                for segment in result['segments']:
                    segment_time = self.format_timestamp(segment['start'])
                    segment_text = segment['text'].strip()
                    timestamped_text.append(f"[{segment_time}] {segment_text}")
                
                return {
                    'text': result['text'],
                    'detailed': '\n'.join(timestamped_text)
                }
            else:
                # Simple output without timestamps
                return {
                    'text': result['text'],
                    'detailed': result['text']
                }
                
        except Exception as e:
            self.update_progress(0, f"Error during transcription: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during transcription: {str(e)}")
            return None
    
    def transcribe_video_thread(self):
        video_file = self.video_path.get()
        output_file = self.output_path.get()
        model_name = self.model_var.get()
        language = self.language_var.get() if self.language_var.get() != "None" else None
        keep_audio = self.keep_audio_var.get()
        word_timestamps = self.word_timestamps_var.get()
        
        # Create audio file name
        audio_file = os.path.splitext(video_file)[0] + ".wav"
        
        # Extract audio from video
        if self.extract_audio_with_ffmpeg(video_file, audio_file):
            # Transcribe the audio
            transcription = self.transcribe_with_whisper(audio_file, model_name, language, word_timestamps)
            
            if transcription:
                # Write transcription to file
                try:
                    with open(output_file, "w", encoding="utf-8") as file:
                        file.write(transcription['detailed'])
                    
                    # Preview in the text area
                    preview_text = transcription['detailed']
                    if len(preview_text) > 2000:
                        preview_text = preview_text[:2000] + "...\n\n[Transcript truncated in preview. Full text saved to file.]"
                    
                    self.root.after(0, lambda: self.update_output_text(preview_text))
                    
                    self.update_progress(100, f"Transcription saved to {os.path.basename(output_file)}")
                except Exception as e:
                    self.update_progress(0, f"Error saving transcription: {str(e)}")
                    messagebox.showerror("Error", f"Failed to save transcription: {str(e)}")
            
            # Clean up
            if not keep_audio and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                    self.update_progress(100, "Transcription completed and temporary files removed")
                except Exception as e:
                    print(f"Error removing temporary file: {str(e)}")
        
        # Reset transcription state
        self.is_transcribing = False
        self.root.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
    
    def start_transcription(self):
        video_file = self.video_path.get()
        output_file = self.output_path.get()
        
        # Validate inputs
        if not video_file:
            messagebox.showerror("Error", "Please select a video file.")
            return
        
        if not os.path.exists(video_file):
            messagebox.showerror("Error", f"Video file not found: {video_file}")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        # Check if required packages are installed
        try:
            import whisper
            import torch
        except ImportError:
            messagebox.showerror("Error", "Missing required packages. Please install with:\n\npip install torch openai-whisper")
            return
            
        # Check if already transcribing
        if self.is_transcribing:
            messagebox.showinfo("Info", "Transcription is already in progress.")
            return
        
        # Reset UI
        self.progress_var.set(0)
        self.status_var.set("Starting transcription...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # Enable cancel button
        self.cancel_button.config(state=tk.NORMAL)
        
        # Start transcription in a separate thread
        self.is_transcribing = True
        self.transcription_thread = threading.Thread(target=self.transcribe_video_thread)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def cancel_transcription(self):
        if self.is_transcribing:
            # We can't actually stop the thread, but we can mark it as canceled
            # and clean up when it's done
            self.is_transcribing = False
            self.status_var.set("Transcription canceled")
            self.progress_var.set(0)
            messagebox.showinfo("Info", "Transcription has been canceled. Please wait for current operations to complete.")
            self.cancel_button.config(state=tk.DISABLED)


def main():
    # Check for required packages
    try:
        import whisper
        import torch
    except ImportError:
        print("Required packages not found. Installing...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "torch", "openai-whisper"
        ])
        print("Installation complete. Please restart the application.")
        input("Press Enter to exit...")
        sys.exit(1)
        
    root = tk.Tk()
    app = VideoTranscriberGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import sys
    main()