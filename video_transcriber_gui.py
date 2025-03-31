import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import torch
import whisper
import time
from notion_integration import NotionIntegration  # Import our Notion integration class

class VideoTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Transcriber - Whisper AI")
        self.root.geometry("800x650")  # Increased height for Notion settings
        self.root.resizable(True, True)
        
        # Set application style
        self.root.minsize(650, 550)
        
        # Variables
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.model_var = tk.StringVar(value="base")
        self.language_var = tk.StringVar(value="en")
        self.keep_audio_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Ready")
        self.word_timestamps_var = tk.BooleanVar(value=True)
        
        # Notion integration variables
        self.notion_enabled = tk.BooleanVar(value=False)
        self.notion_token = tk.StringVar()
        self.notion_database_id = tk.StringVar()
        
        # Initialize Notion integration
        self.notion_api = NotionIntegration()
        
        # Create UI elements
        self.create_ui()
        
        # Threading variables
        self.transcription_thread = None
        self.is_transcribing = False
        self.whisper_model = None
        
        # Load saved Notion settings if available
        self.load_notion_settings()
        
        # Initialize batch processing
        if hasattr(self, 'integrate_batch_processing'):
            self.integrate_batch_processing()
    
    def create_ui(self):
        # Main frame with notebook for tabs
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Transcription")
        
        # Notion settings tab
        notion_tab = ttk.Frame(self.notebook)
        self.notebook.add(notion_tab, text="Notion Integration")
        
        # ===== MAIN TAB =====
        # File selection frame
        file_frame = ttk.LabelFrame(main_tab, text="File Selection", padding="10")
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
        options_frame = ttk.LabelFrame(main_tab, text="Transcription Options", padding="10")
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
        
        # Notion integration checkbox
        notion_frame = ttk.Frame(options_frame)
        notion_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(notion_frame, text="Send to Notion after transcription", 
                      variable=self.notion_enabled).pack(side=tk.LEFT, padx=5)
        
        # Status indicator for Notion
        self.notion_status = ttk.Label(notion_frame, text="Not configured", foreground="red")
        self.notion_status.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Start Transcription", command=self.start_transcription).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_transcription, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)
        self.cancel_button = button_frame.winfo_children()[1]  # Store cancel button reference
        
        # Progress bar and status
        progress_frame = ttk.Frame(main_tab)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, 
                       variable=self.progress_var, mode='determinate').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status label
        status_label = ttk.Label(main_tab, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=5)
        
        # Output text area
        ttk.Label(main_tab, text="Transcription Preview:").pack(anchor=tk.W, pady=5)
        self.output_text = scrolledtext.ScrolledText(main_tab, wrap=tk.WORD, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text.config(state=tk.DISABLED)
        
        # ===== NOTION INTEGRATION TAB =====
        notion_settings_frame = ttk.LabelFrame(notion_tab, text="Notion API Settings", padding="10")
        notion_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Notion API Token
        ttk.Label(notion_settings_frame, text="Notion API Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.token_entry = ttk.Entry(notion_settings_frame, textvariable=self.notion_token, width=50, show="*")
        self.token_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Show/Hide token button
        self.show_token_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(notion_settings_frame, text="Show", variable=self.show_token_var, 
                       command=self.toggle_token_visibility).grid(row=0, column=2, padx=5, pady=5)
        
        # Notion Database ID
        ttk.Label(notion_settings_frame, text="Notion Database ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(notion_settings_frame, textvariable=self.notion_database_id, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        notion_settings_frame.columnconfigure(1, weight=1)
        
        # Notion API buttons
        notion_buttons_frame = ttk.Frame(notion_tab)
        notion_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(notion_buttons_frame, text="Test Connection", command=self.test_notion_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(notion_buttons_frame, text="Save Settings", command=self.save_notion_settings).pack(side=tk.LEFT, padx=5)
        
        # Notion help text
        help_frame = ttk.LabelFrame(notion_tab, text="Help", padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        help_text = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD, height=10)
        help_text.pack(fill=tk.BOTH, expand=True)
        help_text.insert(tk.END, """
How to set up Notion integration:

1. Create a Notion integration at https://www.notion.so/my-integrations
   - Give it a name like "Video Transcriber"
   - Select the appropriate workspace
   - Copy the "Internal Integration Token"

2. Get your Database ID:
   - Create a database in Notion where you want to store transcriptions
   - Share the database with your integration (click "Share" and add your integration)
   - Copy the Database ID from the URL:
     - The URL format is: https://www.notion.so/{workspace}/{database_id}?v={view_id}
     - The Database ID is the part between the workspace name and the question mark

3. Enter both values in the fields above and click "Test Connection"

4. Click "Save Settings" to store your configuration
        """)
        help_text.config(state=tk.DISABLED)
    
    def toggle_token_visibility(self):
        """Toggle the visibility of the Notion API token"""
        if self.show_token_var.get():
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def test_notion_connection(self):
        """Test the connection to Notion API"""
        token = self.notion_token.get()
        database_id = self.notion_database_id.get()
        
        if not token or not database_id:
            messagebox.showerror("Error", "Please enter both Notion API Token and Database ID.")
            return
        
        # Update the Notion API with the new credentials
        self.notion_api.set_token(token)
        self.notion_api.set_database_id(database_id)
        
        # Test the connection
        success, message = self.notion_api.test_connection()
        
        if success:
            messagebox.showinfo("Success", message)
            self.notion_status.config(text="Configured", foreground="green")
        else:
            messagebox.showerror("Error", message)
            self.notion_status.config(text="Error", foreground="red")
    
    def save_notion_settings(self):
        """Save Notion settings to a config file"""
        token = self.notion_token.get()
        database_id = self.notion_database_id.get()
        
        if not token or not database_id:
            messagebox.showerror("Error", "Please enter both Notion API Token and Database ID.")
            return
        
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.join(os.path.expanduser("~"), ".videotranscriber")
            os.makedirs(config_dir, exist_ok=True)
            
            # Save settings to config file
            config_file = os.path.join(config_dir, "notion_config.txt")
            with open(config_file, "w") as f:
                f.write(f"{token}\n{database_id}")
            
            messagebox.showinfo("Success", "Notion settings saved successfully.")
            
            # Update the Notion API with the new credentials
            self.notion_api.set_token(token)
            self.notion_api.set_database_id(database_id)
            self.notion_status.config(text="Configured", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_notion_settings(self):
        """Load Notion settings from config file"""
        try:
            config_file = os.path.join(os.path.expanduser("~"), ".videotranscriber", "notion_config.txt")
            
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        token = lines[0].strip()
                        database_id = lines[1].strip()
                        
                        self.notion_token.set(token)
                        self.notion_database_id.set(database_id)
                        
                        # Update the Notion API with the loaded credentials
                        self.notion_api.set_token(token)
                        self.notion_api.set_database_id(database_id)
                        
                        # Test connection
                        success, _ = self.notion_api.test_connection()
                        if success:
                            self.notion_status.config(text="Configured", foreground="green")
        except Exception as e:
            print(f"Error loading Notion settings: {str(e)}")
    
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
                    'detailed': '\n'.join(timestamped_text),
                    'duration': result.get('duration', None)
                }
            else:
                # Simple output without timestamps
                return {
                    'text': result['text'],
                    'detailed': result['text'],
                    'duration': result.get('duration', None)
                }
                
        except Exception as e:
            self.update_progress(0, f"Error during transcription: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during transcription: {str(e)}")
            return None
    
    def add_to_notion(self, video_path, transcription_text, duration=None):
        """Add the transcription to Notion"""
        if not self.notion_enabled.get():
            return True, "Notion integration disabled."
        
        self.update_progress(95, "Adding transcription to Notion...")
        
        success, message = self.notion_api.add_transcription_to_notion(
            video_path, transcription_text, duration
        )
        
        if success:
            self.update_progress(100, "Transcription added to Notion successfully.")
        else:
            self.update_progress(90, f"Error adding to Notion: {message}")
            messagebox.showerror("Notion Error", message)
        
        return success, message
    
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
                    
                    self.update_progress(95, f"Transcription saved to {os.path.basename(output_file)}")
                    
                    # Add to Notion if enabled
                    if self.notion_enabled.get():
                        self.add_to_notion(video_file, transcription['detailed'], transcription.get('duration', None))
                    else:
                        self.update_progress(100, f"Transcription saved to {os.path.basename(output_file)}")
                        
                except Exception as e:
                    self.update_progress(0, f"Error saving transcription: {str(e)}")
                    messagebox.showerror("Error", f"Failed to save transcription: {str(e)}")
            
            # Clean up
            if not keep_audio and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                    if self.status_var.get() != "Transcription canceled":
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
        
        # Check if Notion is enabled but not configured
        if self.notion_enabled.get():
            if not self.notion_token.get() or not self.notion_database_id.get():
                messagebox.showerror("Error", "Notion integration is enabled but not configured. "
                                     "Please configure it in the Notion Integration tab or disable it.")
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