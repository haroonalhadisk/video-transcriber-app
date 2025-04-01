import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

def browse_input_directory(self):
    """Browse for input directory with video files"""
    directory = filedialog.askdirectory(title="Select Directory with Video Files")
    if directory:
        self.batch_directory.set(directory)
        # Auto-set output directory if not already set
        if not self.batch_output_directory.get():
            self.batch_output_directory.set(os.path.join(directory, "transcripts"))

def browse_output_directory(self):
    """Browse for output directory for transcripts"""
    directory = filedialog.askdirectory(title="Select Output Directory for Transcripts")
    if directory:
        self.batch_output_directory.set(directory)

def start_batch_transcription(self):
    """Start batch transcription process"""
    input_dir = self.batch_directory.get()
    output_dir = self.batch_output_directory.get()
    
    # Validate inputs
    if not input_dir:
        messagebox.showerror("Error", "Please select an input directory.")
        return
    
    if not os.path.isdir(input_dir):
        messagebox.showerror("Error", f"Input directory not found: {input_dir}")
        return
    
    if not output_dir:
        messagebox.showerror("Error", "Please specify an output directory.")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
            return
    
    # Check if Notion is enabled but not configured
    if self.notion_enabled.get():
        if not self.notion_token.get() or not self.notion_database_id.get():
            messagebox.showerror("Error", "Notion integration is enabled but not configured. "
                               "Please configure it in the Notion Integration tab or disable it.")
            return
    
    # Check if Groq is enabled but not configured
    if self.groq_enabled.get():
        if not self.groq_api_key.get():
            messagebox.showerror("Error", "Groq AI processing is enabled but not configured. "
                              "Please configure it in the AI Processing tab or disable it.")
            return
    
    # Find video files in the directory
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    video_files = []
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))
    
    if not video_files:
        messagebox.showerror("Error", "No video files found in the selected directory.")
        return
    
    # Confirm with user
    if not messagebox.askyesno("Confirm", 
                             f"Found {len(video_files)} video files to process. Continue?"):
        return
    
    # Reset UI for batch processing
    self.batch_progress.set(0)
    self.batch_status.set("Starting batch transcription...")
    self.batch_log.delete(1.0, tk.END)
    self.batch_cancel_button.config(state=tk.NORMAL)
    
    # Start batch transcription in a separate thread
    self.is_batch_processing = True
    self.processed_count = 0
    self.total_videos = len(video_files)
    self.batch_thread = threading.Thread(
        target=self.batch_transcribe_videos_thread,
        args=(video_files, output_dir)
    )
    self.batch_thread.daemon = True
    self.batch_thread.start()

def batch_transcribe_videos_thread(self, video_files, output_dir):
    """Process multiple video files in a thread"""
    # Import required modules inside the thread to ensure they're available
    import torch
    import whisper
    import time
    import os
    
    model_name = self.model_var.get()
    language = self.language_var.get() if self.language_var.get() != "None" else None
    keep_audio = self.keep_audio_var.get()
    word_timestamps = self.word_timestamps_var.get()
    
    # Get system prompt for Groq processing if enabled
    system_prompt = None
    if self.groq_enabled.get() and hasattr(self, "system_prompt_text"):
        system_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
    
    # Load the Whisper model at the beginning of batch processing
    try:
        # Check for GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            self.update_batch_log(f"Using GPU acceleration with {device}")
        else:
            self.update_batch_log(f"Using CPU for processing (slower)")
        
        self.update_batch_log(f"Loading Whisper {model_name} model (this may take some time)...")
        
        # Clear any existing model to prevent memory issues
        if hasattr(self, 'whisper_model'):
            self.whisper_model = None
            
        # Load a fresh model for batch processing to avoid potential state issues
        self.whisper_model = whisper.load_model(model_name, device=device)
        self.update_batch_log("Model loaded successfully.")
    except Exception as e:
        self.update_batch_log(f"Error loading Whisper model: {str(e)}")
        self.update_batch_status("Batch processing failed - model could not be loaded.")
        self.is_batch_processing = False
        self.root.after(0, lambda: self.batch_cancel_button.config(state=tk.DISABLED))
        return
    
    # Process each video file
    for i, video_file in enumerate(video_files):
        if not self.is_batch_processing:
            self.update_batch_status(f"Batch processing canceled after {i} of {len(video_files)} files")
            break
        
        video_basename = os.path.basename(video_file)
        output_basename = os.path.splitext(video_basename)[0] + "_transcript.txt"
        output_file = os.path.join(output_dir, output_basename)
        
        # Update batch log and status
        self.update_batch_log(f"Processing ({i+1}/{len(video_files)}): {video_basename}")
        self.update_batch_status(f"Processing: {video_basename}")
        
        # Extract audio from video
        audio_file = os.path.splitext(video_file)[0] + ".wav"
        if self.extract_audio_with_ffmpeg(video_file, audio_file):
            # Transcribe the audio
            try:
                # Create a fresh instance of transcribe options for each run
                transcribe_options = {
                    "task": "transcribe",
                    "verbose": False,
                    "word_timestamps": word_timestamps,
                }
                
                if language:
                    transcribe_options["language"] = language
                
                start_time = time.time()
                
                # Ensure whisper_model exists and is valid
                if not hasattr(self, 'whisper_model') or self.whisper_model is None:
                    self.update_batch_log("Reloading Whisper model...")
                    self.whisper_model = whisper.load_model(model_name, device=device)
                
                result = self.whisper_model.transcribe(audio_file, **transcribe_options)
                elapsed = time.time() - start_time
                
                self.update_batch_log(f"Transcription completed in {elapsed:.2f} seconds")
                
                # Format output based on word timestamps option
                if word_timestamps and 'words' in result:
                    # Create detailed output with word-level timestamps
                    detailed_text = result['text']
                    
                    # Create a timestamped transcript
                    timestamped_text = []
                    
                    for segment in result['segments']:
                        segment_time = self.format_timestamp(segment['start'])
                        segment_text = segment['text'].strip()
                        timestamped_text.append(f"[{segment_time}] {segment_text}")
                    
                    transcription = {
                        'text': result['text'],
                        'detailed': '\n'.join(timestamped_text),
                        'duration': result.get('duration', None)
                    }
                else:
                    # Simple output without timestamps
                    transcription = {
                        'text': result['text'],
                        'detailed': result['text'],
                        'duration': result.get('duration', None)
                    }
                
                # Process with Groq if enabled
                groq_result = None
                if self.groq_enabled.get():
                    self.update_batch_log(f"Processing with Groq AI: {video_basename}")
                    
                    # Process with Groq
                    success, result = self.groq_api.summarize_transcript(transcription['text'], system_prompt)
                    
                    if success:
                        groq_result = result
                        self.update_batch_log(f"✓ Groq processing successful: {video_basename}")
                        
                        # Write enhanced transcription to file
                        try:
                            with open(output_file, "w", encoding="utf-8") as file:
                                file.write(f"Title: {groq_result['title']}\n\n")
                                file.write(f"Summary: {groq_result['summary']}\n\n")
                                file.write("--- Original Transcript ---\n\n")
                                file.write(transcription['detailed'])
                            
                            self.update_batch_log(f"✓ Saved enhanced transcription: {output_basename}")
                        except Exception as e:
                            self.update_batch_log(f"✗ Error saving enhanced transcription: {str(e)}")
                            continue
                    else:
                        self.update_batch_log(f"✗ Groq processing failed: {result}")
                        
                        # Write original transcription instead
                        try:
                            with open(output_file, "w", encoding="utf-8") as file:
                                file.write(transcription['detailed'])
                            
                            self.update_batch_log(f"✓ Saved original transcription: {output_basename}")
                        except Exception as e:
                            self.update_batch_log(f"✗ Error saving transcription: {str(e)}")
                            continue
                else:
                    # Write transcription to file without Groq processing
                    try:
                        with open(output_file, "w", encoding="utf-8") as file:
                            file.write(transcription['detailed'])
                        
                        self.update_batch_log(f"✓ Saved: {output_basename}")
                    except Exception as e:
                        self.update_batch_log(f"✗ Error saving transcription: {str(e)}")
                        continue
                    
                # Add to Notion if enabled
                if self.notion_enabled.get():
                    if groq_result:
                        success, message = self.notion_api.add_transcription_to_notion(
                            video_file, transcription['detailed'], transcription.get('duration', None), groq_result
                        )
                    else:
                        success, message = self.notion_api.add_transcription_to_notion(
                            video_file, transcription['detailed'], transcription.get('duration', None)
                        )
                        
                    if success:
                        self.update_batch_log(f"✓ Added to Notion: {video_basename}")
                    else:
                        self.update_batch_log(f"✗ Notion error: {message}")
                            
            except Exception as e:
                self.update_batch_log(f"✗ Error transcribing {video_basename}: {str(e)}")
                continue
            
            # Clean up audio file if needed
            if not keep_audio and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception as e:
                    self.update_batch_log(f"Warning: Could not remove temporary audio file: {str(e)}")
        
        # Update progress
        self.processed_count += 1
        progress_percent = (self.processed_count / self.total_videos) * 100
        self.batch_progress.set(progress_percent)
    
    # Complete batch processing
    if self.is_batch_processing:
        self.update_batch_status(f"Batch processing completed. Processed {self.processed_count} of {self.total_videos} files.")
    else:
        self.update_batch_status(f"Batch processing canceled. Processed {self.processed_count} of {self.total_videos} files.")
    
    # Reset state and clear model reference to free memory
    self.whisper_model = None
    self.is_batch_processing = False
    self.root.after(0, lambda: self.batch_cancel_button.config(state=tk.DISABLED))

def cancel_batch_transcription(self):
    """Cancel the batch transcription process"""
    if self.is_batch_processing:
        # Mark as canceled - thread will clean up
        self.is_batch_processing = False
        self.batch_status.set("Canceling batch processing...")
        messagebox.showinfo("Info", "Batch processing will be canceled after the current file completes.")
        self.batch_cancel_button.config(state=tk.DISABLED)

def update_batch_log(self, message):
    """Update the batch processing log with a message"""
    self.root.after(0, lambda: self._update_batch_log_impl(message))

def _update_batch_log_impl(self, message):
    """Implementation of batch log update (called from main thread)"""
    self.batch_log.insert(tk.END, message + "\n")
    self.batch_log.see(tk.END)  # Scroll to the end

def update_batch_status(self, message):
    """Update the batch processing status"""
    self.root.after(0, lambda: self.batch_status.set(message))

def integrate_batch_processing(self):
    """
    Integrates batch processing functionality into the VideoTranscriberGUI class.
    First attach methods to the class, then build the UI.
    """
    # First attach all methods to the class
    self.browse_input_directory = browse_input_directory.__get__(self)
    self.browse_output_directory = browse_output_directory.__get__(self)
    self.start_batch_transcription = start_batch_transcription.__get__(self)
    self.batch_transcribe_videos_thread = batch_transcribe_videos_thread.__get__(self)
    self.cancel_batch_transcription = cancel_batch_transcription.__get__(self)
    self.update_batch_log = update_batch_log.__get__(self)
    self._update_batch_log_impl = _update_batch_log_impl.__get__(self)
    self.update_batch_status = update_batch_status.__get__(self)
    
    # Variables for batch processing
    self.batch_directory = tk.StringVar()
    self.batch_output_directory = tk.StringVar()
    self.batch_progress = tk.DoubleVar(value=0)
    self.batch_status = tk.StringVar(value="Ready for batch processing")
    self.is_batch_processing = False
    self.batch_thread = None
    self.processed_count = 0
    self.total_videos = 0
    
    # Create a new tab for batch processing
    batch_tab = ttk.Frame(self.notebook)
    self.notebook.add(batch_tab, text="Batch Processing")
    
    # Directory selection frame
    dir_frame = ttk.LabelFrame(batch_tab, text="Directory Selection", padding="10")
    dir_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Input directory selection
    ttk.Label(dir_frame, text="Video Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
    ttk.Entry(dir_frame, textvariable=self.batch_directory, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    ttk.Button(dir_frame, text="Browse", command=self.browse_input_directory).grid(row=0, column=2, padx=5, pady=5)
    
    # Output directory selection
    ttk.Label(dir_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
    ttk.Entry(dir_frame, textvariable=self.batch_output_directory, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
    ttk.Button(dir_frame, text="Browse", command=self.browse_output_directory).grid(row=1, column=2, padx=5, pady=5)
    
    dir_frame.columnconfigure(1, weight=1)
    
    # Batch options frame (reuse the same options as single file processing)
    batch_options_frame = ttk.LabelFrame(batch_tab, text="Transcription Options", padding="10")
    batch_options_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Copy options from main tab
    model_frame = ttk.Frame(batch_options_frame)
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
    language_frame = ttk.Frame(batch_options_frame)
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
    ttk.Checkbutton(batch_options_frame, text="Include word-level timestamps", 
                  variable=self.word_timestamps_var).pack(anchor=tk.W, pady=5)
    
    # Keep audio checkbox
    ttk.Checkbutton(batch_options_frame, text="Keep extracted audio files", 
                  variable=self.keep_audio_var).pack(anchor=tk.W, pady=5)
    
    # Notion integration checkbox
    notion_frame = ttk.Frame(batch_options_frame)
    notion_frame.pack(fill=tk.X, pady=5)
    
    ttk.Checkbutton(notion_frame, text="Send to Notion after transcription", 
                  variable=self.notion_enabled).pack(side=tk.LEFT, padx=5)
    
    # Groq integration checkbox
    groq_frame = ttk.Frame(batch_options_frame)
    groq_frame.pack(fill=tk.X, pady=5)
    
    ttk.Checkbutton(groq_frame, text="Process with Groq AI after transcription", 
                  variable=self.groq_enabled).pack(side=tk.LEFT, padx=5)
    
    # Action buttons
    batch_button_frame = ttk.Frame(batch_tab)
    batch_button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(batch_button_frame, text="Start Batch Transcription", 
              command=self.start_batch_transcription).pack(side=tk.LEFT, padx=5)
    self.batch_cancel_button = ttk.Button(batch_button_frame, text="Cancel", 
                                         command=self.cancel_batch_transcription, 
                                         state=tk.DISABLED)
    self.batch_cancel_button.pack(side=tk.LEFT, padx=5)
    
    # Batch progress bar
    batch_progress_frame = ttk.Frame(batch_tab)
    batch_progress_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(batch_progress_frame, text="Overall Progress:").pack(side=tk.LEFT, padx=5)
    ttk.Progressbar(batch_progress_frame, orient=tk.HORIZONTAL, length=100, 
                   variable=self.batch_progress, mode='determinate').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # Batch status label
    batch_status_label = ttk.Label(batch_tab, textvariable=self.batch_status, anchor=tk.W)
    batch_status_label.pack(fill=tk.X, pady=5)
    
    # Batch processing log
    ttk.Label(batch_tab, text="Processing Log:").pack(anchor=tk.W, pady=5)
    self.batch_log = scrolledtext.ScrolledText(batch_tab, wrap=tk.WORD, height=15)
    self.batch_log.pack(fill=tk.BOTH, expand=True, pady=5)