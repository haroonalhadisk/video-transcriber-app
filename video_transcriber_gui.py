import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import speech_recognition as sr

class VideoTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Transcriber")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Set application icon and style
        self.root.minsize(600, 450)
        
        # Variables
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.language_var = tk.StringVar(value="en-US")
        self.keep_audio_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Create UI elements
        self.create_ui()
        
        # Threading variables
        self.transcription_thread = None
        self.is_transcribing = False
    
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
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Language selection
        language_frame = ttk.Frame(options_frame)
        language_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(language_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        
        languages = {
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "German": "de-DE",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese (Mandarin)": "zh-CN"
        }
        
        language_combobox = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                        values=list(languages.values()), width=10)
        language_combobox.pack(side=tk.LEFT, padx=5)
        
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
                output_file = os.path.splitext(filename)[0] + "_transcription.txt"
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
    
    def transcribe_audio(self, audio_file, language):
        self.update_progress(40, "Starting transcription (this may take some time)...")
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(audio_file) as source:
                self.update_progress(50, "Reading audio file...")
                audio_data = recognizer.record(source)
            
            self.update_progress(60, "Recognizing speech (this may take some time)...")
            text = recognizer.recognize_google(audio_data, language=language)
            
            self.update_progress(90, "Transcription completed")
            return text
        except sr.UnknownValueError:
            self.update_progress(0, "Speech recognition could not understand the audio")
            messagebox.showerror("Error", "The audio could not be understood. Try a different video or check audio quality.")
            return None
        except sr.RequestError as e:
            self.update_progress(0, f"Could not request results from Google Speech Recognition service; {e}")
            messagebox.showerror("Error", f"Could not connect to Google Speech Recognition service: {e}")
            return None
        except Exception as e:
            self.update_progress(0, f"Error during transcription: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during transcription: {str(e)}")
            return None
    
    def transcribe_video_thread(self):
        video_file = self.video_path.get()
        output_file = self.output_path.get()
        language = self.language_var.get()
        keep_audio = self.keep_audio_var.get()
        
        # Create audio file name
        audio_file = os.path.splitext(video_file)[0] + ".wav"
        
        # Extract audio from video
        if self.extract_audio_with_ffmpeg(video_file, audio_file):
            # Transcribe the audio
            transcription = self.transcribe_audio(audio_file, language)
            
            if transcription:
                # Write transcription to file
                try:
                    with open(output_file, "w", encoding="utf-8") as file:
                        file.write(transcription)
                    
                    # Preview in the text area
                    self.root.after(0, lambda: self.update_output_text(
                        transcription[:1000] + "..." if len(transcription) > 1000 else transcription
                    ))
                    
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
    root = tk.Tk()
    app = VideoTranscriberGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()