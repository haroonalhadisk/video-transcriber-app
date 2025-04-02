import os
import sys
import tempfile
import whisper
import torch
import time
import gradio as gr
import subprocess
from datetime import datetime

from notion_integration import NotionIntegration
from groq_integration import GroqIntegration
from instagram_integration import InstaloaderIntegration

class WebTranscriberUI:
    def __init__(self):
        """Initialize the web-based transcriber UI using Gradio"""
        # Initialize integrations
        self.notion_api = NotionIntegration()
        self.groq_api = GroqIntegration()
        self.instaloader_api = InstaloaderIntegration()
        
        # State variables
        self.whisper_model = None
        self.current_model_name = None
        
        # Create the Gradio interface
        self.create_ui()
    
    def create_ui(self):
        """Create the Gradio UI"""
        with gr.Blocks(title="Video Transcriber") as self.interface:
            gr.Markdown("# Video Transcriber - Whisper AI")
            
            with gr.Tabs() as tabs:
                # Transcription Tab
                with gr.TabItem("Transcription"):
                    self.create_transcription_tab()
                
                # Batch Processing Tab
                with gr.TabItem("Batch Processing"):
                    self.create_batch_tab()
                
                # Instagram Download Tab
                with gr.TabItem("Instagram Download"):
                    self.create_instagram_tab()
                
                # Instagram Saved Posts Tab
                with gr.TabItem("Instagram Saved"):
                    self.create_saved_posts_tab()
                
                # Notion Integration Tab
                with gr.TabItem("Notion Integration"):
                    self.create_notion_tab()
                
                # Groq AI Tab
                with gr.TabItem("AI Processing"):
                    self.create_groq_tab()
    
    def create_transcription_tab(self):
        """Create the transcription tab"""
        with gr.Row():
            with gr.Column(scale=3):
                video_file = gr.File(label="Video File", file_types=["video"])
                
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large"],
                        value="base",
                        label="Whisper Model"
                    )
                    language_dropdown = gr.Dropdown(
                        choices=["en", "es", "fr", "de", "ja", "ko", "zh", None],
                        value="en",
                        label="Language"
                    )
                
                with gr.Row():
                    timestamps_checkbox = gr.Checkbox(value=True, label="Include word-level timestamps")
                    keep_audio_checkbox = gr.Checkbox(value=False, label="Keep extracted audio file")
                
                with gr.Row():
                    notion_checkbox = gr.Checkbox(value=False, label="Send to Notion after transcription")
                    groq_checkbox = gr.Checkbox(value=False, label="Process with Groq AI after transcription")
                
                transcribe_button = gr.Button("Start Transcription", variant="primary")
                
                progress = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    step=1,
                    label="Progress",
                    interactive=False
                )
                status = gr.Textbox(value="Ready", label="Status")
            
            with gr.Column(scale=2):
                transcript_output = gr.Textbox(
                    label="Transcription Preview", 
                    lines=20,
                    max_lines=30
                )
                download_button = gr.Button("Download Transcript")
                transcript_file = gr.File(label="Transcript File", interactive=False, visible=False)
        
        # Wire up the transcription process
        transcribe_button.click(
            fn=self.process_video_file,
            inputs=[
                video_file, 
                model_dropdown, 
                language_dropdown, 
                timestamps_checkbox, 
                keep_audio_checkbox,
                notion_checkbox,
                groq_checkbox
            ],
            outputs=[progress, status, transcript_output, transcript_file]
        )
        
        download_button.click(
            fn=lambda x: x,
            inputs=[transcript_file],
            outputs=[transcript_file]
        )
    
    def create_batch_tab(self):
        """Create the batch processing tab"""
        with gr.Row():
            with gr.Column(scale=3):
                batch_files = gr.File(
                    label="Video Files", 
                    file_types=["video"],
                    file_count="multiple"
                )
                
                with gr.Row():
                    batch_model_dropdown = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large"],
                        value="base",
                        label="Whisper Model"
                    )
                    batch_language_dropdown = gr.Dropdown(
                        choices=["en", "es", "fr", "de", "ja", "ko", "zh", None],
                        value="en",
                        label="Language"
                    )
                
                with gr.Row():
                    batch_timestamps_checkbox = gr.Checkbox(value=True, label="Include word-level timestamps")
                    batch_keep_audio_checkbox = gr.Checkbox(value=False, label="Keep extracted audio files")
                
                with gr.Row():
                    batch_notion_checkbox = gr.Checkbox(value=False, label="Send to Notion after transcription")
                    batch_groq_checkbox = gr.Checkbox(value=False, label="Process with Groq AI after transcription")
                
                batch_transcribe_button = gr.Button("Start Batch Transcription", variant="primary")
                
                batch_progress = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    step=1,
                    label="Overall Progress",
                    interactive=False
                )
                batch_status = gr.Textbox(value="Ready for batch processing", label="Status")
            
            with gr.Column(scale=2):
                batch_log = gr.Textbox(
                    label="Processing Log", 
                    lines=20,
                    max_lines=30
                )
                batch_download = gr.Button("Download All Transcripts")
                batch_files_output = gr.File(
                    label="Transcription Files", 
                    interactive=False,
                    file_count="multiple",
                    visible=False
                )
        
        # Wire up the batch transcription process
        batch_transcribe_button.click(
            fn=self.process_batch_files,
            inputs=[
                batch_files, 
                batch_model_dropdown, 
                batch_language_dropdown, 
                batch_timestamps_checkbox, 
                batch_keep_audio_checkbox,
                batch_notion_checkbox,
                batch_groq_checkbox
            ],
            outputs=[batch_progress, batch_status, batch_log, batch_files_output]
        )
        
        batch_download.click(
            fn=lambda x: x,
            inputs=[batch_files_output],
            outputs=[batch_files_output]
        )
    
    def create_instagram_tab(self):
        """Create the Instagram download tab"""
        with gr.Row():
            with gr.Column(scale=3):
                instagram_url = gr.Textbox(
                    label="Instagram URL",
                    placeholder="https://www.instagram.com/p/ABC123/ or https://www.instagram.com/reel/XYZ789/"
                )
                
                # URL text file for batch processing
                instagram_url_file = gr.File(
                    label="Or Upload a Text File with URLs (one per line)",
                    file_types=["text"]
                )
                
                auto_delete_checkbox = gr.Checkbox(
                    value=False, 
                    label="Auto-delete videos after transcription"
                )
                
                with gr.Row():
                    download_transcribe_button = gr.Button("Download & Transcribe", variant="primary")
                    download_only_button = gr.Button("Download Only")
                    batch_instagram_button = gr.Button("Process URL File")
                
                instagram_progress = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    step=1,
                    label="Progress",
                    interactive=False
                )
                instagram_status = gr.Textbox(value="Ready to download", label="Status")
            
            with gr.Column(scale=2):
                instagram_log = gr.Textbox(
                    label="Download Log", 
                    lines=20,
                    max_lines=30
                )
                instagram_download = gr.Button("Download Results")
                instagram_files_output = gr.File(
                    label="Downloaded Files", 
                    interactive=False,
                    file_count="multiple",
                    visible=False
                )
        
        # Wire up the Instagram download processes
        download_transcribe_button.click(
            fn=self.process_instagram_url,
            inputs=[instagram_url, auto_delete_checkbox, gr.Checkbox(value=True, visible=False)],
            outputs=[instagram_progress, instagram_status, instagram_log, instagram_files_output]
        )
        
        download_only_button.click(
            fn=self.process_instagram_url,
            inputs=[instagram_url, auto_delete_checkbox, gr.Checkbox(value=False, visible=False)],
            outputs=[instagram_progress, instagram_status, instagram_log, instagram_files_output]
        )
        
        batch_instagram_button.click(
            fn=self.process_instagram_batch,
            inputs=[instagram_url_file, auto_delete_checkbox],
            outputs=[instagram_progress, instagram_status, instagram_log, instagram_files_output]
        )
        
        instagram_download.click(
            fn=lambda x: x,
            inputs=[instagram_files_output],
            outputs=[instagram_files_output]
        )
    
    def create_notion_tab(self):
        """Create the Notion integration tab"""
        with gr.Row():
            with gr.Column():
                notion_token = gr.Textbox(
                    label="Notion API Token",
                    type="password",
                    placeholder="Enter your Notion API Token"
                )
                
                notion_database_id = gr.Textbox(
                    label="Notion Database ID",
                    placeholder="Enter your Notion Database ID"
                )
                
                with gr.Row():
                    test_notion_button = gr.Button("Test Connection")
                    save_notion_button = gr.Button("Save Settings")
                
                notion_status = gr.Textbox(value="Not configured", label="Status")
                
                gr.Markdown("""
                ## How to set up Notion integration:

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
        
        # Wire up Notion integration
        test_notion_button.click(
            fn=self.test_notion_connection,
            inputs=[notion_token, notion_database_id],
            outputs=[notion_status]
        )
        
        save_notion_button.click(
            fn=self.save_notion_settings,
            inputs=[notion_token, notion_database_id],
            outputs=[notion_status]
        )
    
    def create_groq_tab(self):
        """Create the Groq AI tab"""
        with gr.Row():
            with gr.Column():
                groq_api_key = gr.Textbox(
                    label="Groq API Key",
                    type="password",
                    placeholder="Enter your Groq API Key"
                )
                
                groq_system_prompt = gr.Textbox(
                    label="System Prompt",
                    lines=8,
                    placeholder="Enter the system prompt for Groq AI",
                    value="""You are an expert at summarizing video transcripts. Given a transcript text:
1. Create a clear, concise title that accurately represents the core content
2. Summarize the key points in plain language without jargon
3. Be straightforward and avoid clickbait language
4. Don't leave out important details from the transcript
5. Format your response as JSON with "title" and "summary" fields"""
                )
                
                with gr.Row():
                    test_groq_button = gr.Button("Test Connection")
                    save_groq_button = gr.Button("Save Settings")
                    reset_prompt_button = gr.Button("Reset to Default Prompt")
                
                groq_status = gr.Textbox(value="Not configured", label="Status")
                
                gr.Markdown("""
                ## How to set up Groq API integration:

                1. Sign up for a Groq account at https://console.groq.com
                2. Create an API key in your Groq dashboard
                3. Copy the API key and paste it in the field above
                4. Customize the system prompt if desired
                5. Click "Test Connection" to verify your API key works
                6. Click "Save Settings" to store your configuration

                The Groq API will:
                - Create a clear, readable title for your transcription
                - Generate a summary that removes jargon and filler content
                - Enhance the readability of the transcription
                - Both the title and summary will be included when saving to Notion
                """)
        
        # Wire up Groq integration
        test_groq_button.click(
            fn=self.test_groq_connection,
            inputs=[groq_api_key],
            outputs=[groq_status]
        )
        
        save_groq_button.click(
            fn=self.save_groq_settings,
            inputs=[groq_api_key, groq_system_prompt],
            outputs=[groq_status]
        )
        
        reset_prompt_button.click(
            fn=self.reset_groq_prompt,
            inputs=[],
            outputs=[groq_system_prompt]
        )
    
    def extract_audio_with_ffmpeg(self, video_file, audio_file):
        """Extract audio from video file using FFmpeg"""
        try:
            subprocess.run([
                "ffmpeg", "-i", video_file, "-q:a", "0", "-map", "a", audio_file, "-y"
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {str(e)}")
            return False
        except FileNotFoundError:
            print("Error: FFmpeg not found. Please install FFmpeg.")
            return False
    
    def format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS.MS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def transcribe_with_whisper(self, audio_file, model_name, language, word_timestamps):
        """Transcribe audio file using Whisper"""
        try:
            # Check if we need to load a new model or reuse an existing one
            if self.whisper_model is None or model_name != self.current_model_name:
                # Check for GPU
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                # Load the model
                self.whisper_model = whisper.load_model(model_name, device=device)
                self.current_model_name = model_name
            
            # Set up transcription options
            transcribe_options = {
                "task": "transcribe",
                "verbose": False,
                "word_timestamps": word_timestamps,
            }
            
            if language:
                transcribe_options["language"] = language
            
            # Run transcription
            start_time = time.time()
            result = self.whisper_model.transcribe(audio_file, **transcribe_options)
            elapsed = time.time() - start_time
            
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
                
                return {
                    'text': result['text'],
                    'detailed': '\n'.join(timestamped_text),
                    'duration': result.get('duration', None),
                    'elapsed': elapsed
                }
            else:
                # Simple output without timestamps
                return {
                    'text': result['text'],
                    'detailed': result['text'],
                    'duration': result.get('duration', None),
                    'elapsed': elapsed
                }
                
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise e
    
    def process_with_groq(self, transcript_text, system_prompt=None):
        """Process transcript with Groq AI"""
        if not system_prompt:
            system_prompt = """You are an expert at summarizing video transcripts. Given a transcript text:
1. Create a clear, concise title that accurately represents the core content
2. Summarize the key points in plain language without jargon
3. Be straightforward and avoid clickbait language
4. Don't leave out important details from the transcript
5. Format your response as JSON with "title" and "summary" fields"""
        
        # Process with Groq
        success, result = self.groq_api.summarize_transcript(transcript_text, system_prompt)
        
        return success, result
    
    def process_video_file(self, video_file, model_name, language, word_timestamps, keep_audio, notion_enabled, groq_enabled):
        """Process a single video file"""
        if video_file is None:
            return 0, "Error: No video file selected", "", None
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_updates = []
            
            # Get video file path
            video_file_path = video_file.name
            video_basename = os.path.basename(video_file_path)
            
            # Create audio file path
            audio_file = os.path.join(temp_dir, os.path.splitext(video_basename)[0] + ".wav")
            
            # Create output file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(temp_dir, f"{os.path.splitext(video_basename)[0]}_{timestamp}_transcript.txt")
            
            # Extract audio
            progress_updates.append(f"Extracting audio from {video_basename}...")
            if not self.extract_audio_with_ffmpeg(video_file_path, audio_file):
                return 0, "Error extracting audio from video", "", None
            
            progress_updates.append(f"Audio extracted successfully")
            
            # Transcribe audio
            progress_updates.append(f"Loading Whisper {model_name} model...")
            progress_updates.append(f"Transcribing audio...")
            
            try:
                transcription = self.transcribe_with_whisper(audio_file, model_name, language, word_timestamps)
                
                progress_updates.append(f"Transcription completed in {transcription['elapsed']:.2f} seconds")
                
                # Process with Groq if enabled
                groq_result = None
                if groq_enabled:
                    progress_updates.append("Processing transcription with Groq AI...")
                    # Get system prompt from settings
                    system_prompt = None  # We'd load this from saved settings
                    
                    # Process with Groq
                    success, result = self.process_with_groq(transcription['text'], system_prompt)
                    
                    if success:
                        groq_result = result
                        progress_updates.append("Groq AI processing complete")
                        
                        # Write enhanced transcription to file
                        with open(output_file, "w", encoding="utf-8") as file:
                            file.write(f"Title: {groq_result['title']}\n\n")
                            file.write(f"Summary: {groq_result['summary']}\n\n")
                            file.write("--- Original Transcript ---\n\n")
                            file.write(transcription['detailed'])
                        
                        progress_updates.append(f"Enhanced transcription saved to file")
                        
                        # Preview text
                        preview_text = f"Title: {groq_result['title']}\n\n"
                        preview_text += f"Summary: {groq_result['summary']}\n\n"
                        preview_text += "--- Original Transcript ---\n\n"
                        preview_text += transcription['detailed']
                    else:
                        progress_updates.append(f"Groq AI processing issue - using original transcription")
                        
                        # Write original transcription to file
                        with open(output_file, "w", encoding="utf-8") as file:
                            file.write(transcription['detailed'])
                        
                        progress_updates.append(f"Original transcription saved to file")
                        
                        # Preview text
                        preview_text = transcription['detailed']
                else:
                    # Write original transcription to file
                    with open(output_file, "w", encoding="utf-8") as file:
                        file.write(transcription['detailed'])
                    
                    progress_updates.append(f"Transcription saved to file")
                    
                    # Preview text
                    preview_text = transcription['detailed']
                
                # Add to Notion if enabled
                if notion_enabled:
                    progress_updates.append("Adding transcription to Notion...")
                    
                    success, message = self.notion_api.add_transcription_to_notion(
                        video_file_path, 
                        transcription['detailed'], 
                        transcription.get('duration', None), 
                        groq_result
                    )
                    
                    if success:
                        progress_updates.append("Transcription added to Notion successfully")
                    else:
                        progress_updates.append(f"Error adding to Notion: {message}")
                
                # Clean up audio file if not keeping
                if not keep_audio and os.path.exists(audio_file):
                    try:
                        os.remove(audio_file)
                    except Exception as e:
                        progress_updates.append(f"Warning: Could not remove temporary audio file: {str(e)}")
                
                # Truncate preview if too long
                if len(preview_text) > 10000:
                    preview_text = preview_text[:10000] + "...\n\n[Content truncated in preview. Full text in downloaded file.]"
                
                # Return results
                status_text = "Transcription completed"
                log_text = "\n".join(progress_updates)
                
                return 100, status_text, preview_text, output_file
                
            except Exception as e:
                return 0, f"Error during transcription: {str(e)}", "\n".join(progress_updates), None
    
    def process_batch_files(self, batch_files, model_name, language, word_timestamps, keep_audio, notion_enabled, groq_enabled):
        """Process multiple video files in batch"""
        if not batch_files:
            return 0, "Error: No video files selected", "No files to process", []
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_updates = []
            output_files = []
            
            total_files = len(batch_files)
            processed_count = 0
            
            # Process each video file
            for video_file in batch_files:
                video_file_path = video_file.name
                video_basename = os.path.basename(video_file_path)
                
                progress_updates.append(f"\nProcessing ({processed_count+1}/{total_files}): {video_basename}")
                
                # Create audio file path
                audio_file = os.path.join(temp_dir, os.path.splitext(video_basename)[0] + ".wav")
                
                # Create output file path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(temp_dir, f"{os.path.splitext(video_basename)[0]}_{timestamp}_transcript.txt")
                
                # Extract audio
                progress_updates.append(f"Extracting audio from {video_basename}...")
                if not self.extract_audio_with_ffmpeg(video_file_path, audio_file):
                    progress_updates.append(f"✗ Error extracting audio from {video_basename}")
                    continue
                
                # Transcribe audio
                try:
                    progress_updates.append(f"Transcribing audio...")
                    transcription = self.transcribe_with_whisper(audio_file, model_name, language, word_timestamps)
                    
                    progress_updates.append(f"✓ Transcription completed in {transcription['elapsed']:.2f} seconds")
                    
                    # Process with Groq if enabled
                    groq_result = None
                    if groq_enabled:
                        progress_updates.append(f"Processing with Groq AI: {video_basename}")
                        
                        # Get system prompt from settings
                        system_prompt = None  # We'd load this from saved settings
                        
                        # Process with Groq
                        success, result = self.process_with_groq(transcription['text'], system_prompt)
                        
                        if success:
                            groq_result = result
                            progress_updates.append(f"✓ Groq processing successful: {video_basename}")
                            
                            # Write enhanced transcription to file
                            with open(output_file, "w", encoding="utf-8") as file:
                                file.write(f"Title: {groq_result['title']}\n\n")
                                file.write(f"Summary: {groq_result['summary']}\n\n")
                                file.write("--- Original Transcript ---\n\n")
                                file.write(transcription['detailed'])
                            
                            progress_updates.append(f"✓ Saved enhanced transcription: {os.path.basename(output_file)}")
                        else:
                            progress_updates.append(f"✗ Groq processing issue: {result}")
                            
                            # Write original transcription to file
                            with open(output_file, "w", encoding="utf-8") as file:
                                file.write(transcription['detailed'])
                            
                            progress_updates.append(f"✓ Saved original transcription: {os.path.basename(output_file)}")
                    else:
                        # Write original transcription to file
                        with open(output_file, "w", encoding="utf-8") as file:
                            file.write(transcription['detailed'])
                        
                        progress_updates.append(f"✓ Saved transcription: {os.path.basename(output_file)}")
                    
                    # Add to Notion if enabled
                    if notion_enabled:
                        if groq_result:
                            success, message = self.notion_api.add_transcription_to_notion(
                                video_file_path, 
                                transcription['detailed'], 
                                transcription.get('duration', None), 
                                groq_result
                            )
                        else:
                            success, message = self.notion_api.add_transcription_to_notion(
                                video_file_path, 
                                transcription['detailed'], 
                                transcription.get('duration', None)
                            )
                            
                        if success:
                            progress_updates.append(f"✓ Added to Notion: {video_basename}")
                        else:
                            progress_updates.append(f"✗ Notion error: {message}")
                    
                    # Clean up audio file if not keeping
                    if not keep_audio and os.path.exists(audio_file):
                        try:
                            os.remove(audio_file)
                        except Exception as e:
                            progress_updates.append(f"Warning: Could not remove temporary audio file: {str(e)}")
                    
                    # Add output file to results
                    output_files.append(output_file)
                    
                except Exception as e:
                    progress_updates.append(f"✗ Error transcribing {video_basename}: {str(e)}")
                
                # Update progress
                processed_count += 1
                progress_percent = (processed_count / total_files) * 100
                
            # Complete batch processing
            completion_message = f"Batch processing completed. Processed {processed_count} of {total_files} files."
            log_text = "\n".join(progress_updates)
            
            return progress_percent, completion_message, log_text, output_files
    
    def process_instagram_url(self, url, auto_delete, transcribe_after):
        """Process a single Instagram URL"""
        if not url or not url.strip():
            return 0, "Error: No Instagram URL provided", "Please enter an Instagram URL", []
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_updates = []
            output_files = []
            
            # Ensure Instaloader is installed
            if not self.instaloader_api.ensure_instaloader_installed():
                # Try to install Instaloader
                progress_updates.append("Instaloader not installed. Attempting to install...")
                success, message = self.instaloader_api.install_instaloader()
                
                if not success:
                    return 0, "Error: Failed to install Instaloader", message, []
                
                progress_updates.append("✓ Instaloader installed successfully")
            
            # Download Instagram post
            progress_updates.append(f"Starting download of: {url}")
            
            try:
                success, result, description = self.instaloader_api.download_instagram_post(
                    url, 
                    temp_dir,
                    None  # No callback in web mode
                )
                
                if success:
                    video_path = result
                    progress_updates.append(f"✓ Downloaded: {os.path.basename(video_path)}")
                    output_files.append(video_path)
                    
                    # Store the original URL and description for Notion integration
                    self.notion_api.store_video_metadata(video_path, url, description)
                    
                    if transcribe_after:
                        # Transcribe the video
                        progress_updates.append(f"Starting transcription of downloaded video...")
                        
                        # Extract audio
                        audio_file = os.path.join(temp_dir, os.path.splitext(os.path.basename(video_path))[0] + ".wav")
                        if self.extract_audio_with_ffmpeg(video_path, audio_file):
                            # Set up transcription parameters
                            model_name = "base"  # Default model
                            language = "en"  # Default language
                            word_timestamps = True
                            
                            # Transcribe audio
                            try:
                                transcription = self.transcribe_with_whisper(audio_file, model_name, language, word_timestamps)
                                
                                # Create output file path
                                output_file = os.path.splitext(video_path)[0] + "_transcript.txt"
                                
                                # Write transcription to file
                                with open(output_file, "w", encoding="utf-8") as file:
                                    file.write(transcription['detailed'])
                                
                                progress_updates.append(f"✓ Transcribed: {os.path.basename(output_file)}")
                                output_files.append(output_file)
                                
                            except Exception as e:
                                progress_updates.append(f"✗ Error transcribing video: {str(e)}")
                        else:
                            progress_updates.append("✗ Failed to extract audio for transcription")
                    
                    # Auto-delete the video if requested and transcription is complete
                    if auto_delete and transcribe_after and len(output_files) > 1:
                        try:
                            os.remove(video_path)
                            progress_updates.append(f"✓ Deleted video after transcription: {os.path.basename(video_path)}")
                            # Remove the video from output files
                            output_files.remove(video_path)
                        except Exception as e:
                            progress_updates.append(f"✗ Error deleting video: {str(e)}")
                else:
                    error_message = result
                    progress_updates.append(f"✗ Download failed: {error_message}")
                    return 0, f"Download failed: {error_message}", "\n".join(progress_updates), []
                
                return 100, "Download complete", "\n".join(progress_updates), output_files
                
            except Exception as e:
                return 0, f"Error: {str(e)}", f"An unexpected error occurred:\n{str(e)}", []
    
    def process_instagram_batch(self, url_file, auto_delete):
        """Process a batch of Instagram URLs from a file"""
        if url_file is None:
            return 0, "Error: No URL file selected", "Please upload a text file with Instagram URLs (one per line)", []
        
        # Read URLs from file
        try:
            with open(url_file.name, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]
            
            # Filter valid URLs
            instagram_urls = []
            for url in urls:
                if "instagram.com" in url and ("/p/" in url or "/reel/" in url or "/tv/" in url):
                    instagram_urls.append(url)
            
            if not instagram_urls:
                return 0, "Error: No valid Instagram URLs found", "No valid Instagram URLs found in the file. URLs should contain 'instagram.com/p/', 'instagram.com/reel/', or 'instagram.com/tv/'.", []
            
        except Exception as e:
            return 0, f"Error reading URL file: {str(e)}", f"Failed to read URLs from file: {str(e)}", []
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_updates = []
            output_files = []
            
            # Ensure Instaloader is installed
            if not self.instaloader_api.ensure_instaloader_installed():
                # Try to install Instaloader
                progress_updates.append("Instaloader not installed. Attempting to install...")
                success, message = self.instaloader_api.install_instaloader()
                
                if not success:
                    return 0, "Error: Failed to install Instaloader", message, []
                
                progress_updates.append("✓ Instaloader installed successfully")
            
            total_urls = len(instagram_urls)
            processed_count = 0
            
            # Process each URL
            for url in instagram_urls:
                progress_updates.append(f"\nProcessing ({processed_count+1}/{total_urls}): {url}")
                
                try:
                    success, result, description = self.instaloader_api.download_instagram_post(
                        url, 
                        temp_dir,
                        None  # No callback in web mode
                    )
                    
                    if success:
                        video_path = result
                        progress_updates.append(f"✓ Downloaded: {os.path.basename(video_path)}")
                        output_files.append(video_path)
                        
                        # Store the original URL and description for Notion integration
                        self.notion_api.store_video_metadata(video_path, url, description)
                        
                        # Transcribe the video
                        progress_updates.append(f"Starting transcription of downloaded video...")
                        
                        # Extract audio
                        audio_file = os.path.join(temp_dir, os.path.splitext(os.path.basename(video_path))[0] + ".wav")
                        if self.extract_audio_with_ffmpeg(video_path, audio_file):
                            # Set up transcription parameters
                            model_name = "base"  # Default model
                            language = "en"  # Default language
                            word_timestamps = True
                            
                            # Transcribe audio
                            try:
                                transcription = self.transcribe_with_whisper(audio_file, model_name, language, word_timestamps)
                                
                                # Create output file path
                                output_file = os.path.splitext(video_path)[0] + "_transcript.txt"
                                
                                # Write transcription to file
                                with open(output_file, "w", encoding="utf-8") as file:
                                    file.write(transcription['detailed'])
                                
                                progress_updates.append(f"✓ Transcribed: {os.path.basename(output_file)}")
                                output_files.append(output_file)
                                
                                # Auto-delete the video if requested and transcription is complete
                                if auto_delete:
                                    try:
                                        os.remove(video_path)
                                        progress_updates.append(f"✓ Deleted video after transcription: {os.path.basename(video_path)}")
                                        # Remove the video from output files if it was successfully deleted
                                        if video_path in output_files:
                                            output_files.remove(video_path)
                                    except Exception as e:
                                        progress_updates.append(f"✗ Error deleting video: {str(e)}")
                                
                            except Exception as e:
                                progress_updates.append(f"✗ Error transcribing video: {str(e)}")
                        else:
                            progress_updates.append("✗ Failed to extract audio for transcription")
                    else:
                        error_message = result
                        progress_updates.append(f"✗ Download failed: {error_message}")
                
                except Exception as e:
                    progress_updates.append(f"✗ Error processing {url}: {str(e)}")
                
                # Update progress
                processed_count += 1
                progress_percent = (processed_count / total_urls) * 100
            
            # Complete batch processing
            completion_message = f"Batch processing completed. Processed {processed_count} of {total_urls} URLs."
            log_text = "\n".join(progress_updates)
            
            return progress_percent, completion_message, log_text, output_files
    
    def test_notion_connection(self, token, database_id):
        """Test the connection to Notion API"""
        if not token or not database_id:
            return "Error: Please enter both Notion API Token and Database ID."
        
        # Update the Notion API with the new credentials
        self.notion_api.set_token(token)
        self.notion_api.set_database_id(database_id)
        
        # Test the connection
        success, message = self.notion_api.test_connection()
        
        if success:
            return "✓ Connection successful"
        else:
            return f"✗ Error: {message}"
    
    def save_notion_settings(self, token, database_id):
        """Save Notion settings to a config file"""
        if not token or not database_id:
            return "Error: Please enter both Notion API Token and Database ID."
        
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.join(os.path.expanduser("~"), ".videotranscriber")
            os.makedirs(config_dir, exist_ok=True)
            
            # Save settings to config file
            config_file = os.path.join(config_dir, "notion_config.txt")
            with open(config_file, "w") as f:
                f.write(f"{token}\n{database_id}")
            
            # Update the Notion API with the new credentials
            self.notion_api.set_token(token)
            self.notion_api.set_database_id(database_id)
            
            return "✓ Notion settings saved successfully"
        except Exception as e:
            return f"✗ Failed to save settings: {str(e)}"
    
    def test_groq_connection(self, api_key):
        """Test the connection to Groq API"""
        if not api_key:
            return "Error: Please enter your Groq API Key."
        
        # Update the Groq API with the new credentials
        self.groq_api.set_api_key(api_key)
        
        # Test the connection
        success, message = self.groq_api.test_connection()
        
        if success:
            return "✓ Connection successful"
        else:
            return f"✗ Error: {message}"
    
    def save_groq_settings(self, api_key, system_prompt):
        """Save Groq settings to a config file"""
        if not api_key:
            return "Error: Please enter your Groq API Key."
        
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.join(os.path.expanduser("~"), ".videotranscriber")
            os.makedirs(config_dir, exist_ok=True)
            
            # Save settings to config file
            config_file = os.path.join(config_dir, "groq_config.txt")
            with open(config_file, "w") as f:
                f.write(f"{api_key}\n{system_prompt}")
            
            # Update the Groq API with the new credentials
            self.groq_api.set_api_key(api_key)
            
            return "✓ Groq settings saved successfully"
        except Exception as e:
            return f"✗ Failed to save settings: {str(e)}"
    
    def reset_groq_prompt(self):
        """Reset the Groq system prompt to default"""
        default_prompt = """You are an expert at summarizing video transcripts. Given a transcript text:
1. Create a clear, concise title that accurately represents the core content
2. Summarize the key points in plain language without jargon
3. Be straightforward and avoid clickbait language
4. Don't leave out important details from the transcript
5. Format your response as JSON with "title" and "summary" fields"""
        
        return default_prompt
        
    def create_saved_posts_tab(self):
        """Create the Instagram saved posts tab"""
        with gr.Row():
            with gr.Column(scale=3):
                output_dir = gr.Textbox(
                    label="Save Directory",
                    placeholder="Directory to save downloaded saved posts",
                    value=os.path.join(os.path.expanduser("~"), "Downloads", "Instagram_Saved")
                )
                
                with gr.Row():
                    with gr.Column():
                        username = gr.Textbox(label="Instagram Username")
                        password = gr.Textbox(label="Instagram Password", type="password")
                    
                    with gr.Column():
                        browser_dropdown = gr.Dropdown(
                            choices=["firefox", "chrome", "safari", "edge", "brave", "opera"],
                            value="firefox",
                            label="Browser for Cookie Login"
                        )
                        use_browser_cookies = gr.Checkbox(
                            value=True, 
                            label="Use browser cookies for login (recommended)"
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Content Options")
                        download_pictures = gr.Checkbox(value=True, label="Download pictures")
                        download_videos = gr.Checkbox(value=True, label="Download videos")
                    
                    with gr.Column():
                        gr.Markdown("### Post Limit")
                        post_count_radio = gr.Radio(
                            choices=["All posts", "Specific number"],
                            value="All posts",
                            label="Number of posts to download"
                        )
                        post_count = gr.Number(value=20, label="Post count (if limited)")
                
                with gr.Row():
                    auto_transcribe = gr.Checkbox(value=True, label="Auto-transcribe downloaded videos")
                    saved_auto_delete = gr.Checkbox(value=False, label="Auto-delete videos after transcription")
                
                with gr.Row():
                    test_login_button = gr.Button("Test Login")
                    download_saved_button = gr.Button("Download Saved Posts", variant="primary")
                
                saved_progress = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    step=1,
                    label="Progress",
                    interactive=False
                )
                saved_status = gr.Textbox(value="Ready to download saved posts", label="Status")
            
            with gr.Column(scale=2):
                saved_log = gr.Textbox(
                    label="Download Log", 
                    lines=20,
                    max_lines=30
                )
                saved_download_button = gr.Button("Download Results")
                saved_files_output = gr.File(
                    label="Downloaded Files", 
                    interactive=False,
                    file_count="multiple",
                    visible=False
                )
        
        # Add information about web limitations
        gr.Markdown("""
        ## Note: Instagram Saved Posts Functionality in Web Mode
        
        When running in web mode (especially on platforms like Google Colab or Kaggle), Instagram login has some limitations:
        
        1. **Browser cookie login** might not work as expected when running in a cloud environment
        2. **Login sessions** are not persistent between runs
        3. For **Two-Factor Authentication accounts**, use username/password login and be prepared to enter the code
        
        For the best experience with Instagram Saved Posts, consider using the desktop application instead.
        """)
        
        # Wire up the saved posts functions
        test_login_button.click(
            fn=self.test_instagram_login,
            inputs=[
                username, 
                password, 
                use_browser_cookies, 
                browser_dropdown
            ],
            outputs=[saved_status, saved_log]
        )
        
        download_saved_button.click(
            fn=self.download_saved_posts,
            inputs=[
                username,
                password,
                use_browser_cookies,
                browser_dropdown, 
                output_dir,
                post_count_radio,
                post_count,
                download_pictures,
                download_videos,
                auto_transcribe,
                saved_auto_delete
            ],
            outputs=[saved_progress, saved_status, saved_log, saved_files_output]
        )
        
        saved_download_button.click(
            fn=lambda x: x,
            inputs=[saved_files_output],
            outputs=[saved_files_output]
        )
    
    def test_instagram_login(self, username, password, use_browser_cookies, browser):
        """Test Instagram login credentials"""
        log_messages = ["Testing Instagram login..."]
        
        try:
            import instaloader
        except ImportError:
            # Try to install instaloader
            log_messages.append("Instaloader not installed. Attempting to install...")
            success, message = self.instaloader_api.install_instaloader()
            if not success:
                log_messages.append(f"✗ Failed to install Instaloader: {message}")
                return "Failed to install Instaloader", "\n".join(log_messages)
            
            log_messages.append("✓ Instaloader installed successfully")
            
            try:
                import instaloader
            except ImportError:
                log_messages.append("✗ Failed to import Instaloader after installation")
                return "Failed to import Instaloader", "\n".join(log_messages)
        
        try:
            # Create a new instance for login testing
            L = instaloader.Instaloader()
            
            if use_browser_cookies:
                # Check if the browser cookie function exists
                has_browser_cookie_support = hasattr(L, 'load_session_from_browser')
                
                if not has_browser_cookie_support:
                    version = getattr(instaloader, '__version__', 'unknown')
                    log_messages.append(f"✗ Browser cookie login not supported in Instaloader version {version}")
                    return f"Browser cookie login not supported in version {version}", "\n".join(log_messages)
                
                # Login with browser cookies
                log_messages.append(f"Trying to login with {browser} cookies...")
                
                try:
                    try:
                        # Try importing browser_cookie3
                        import browser_cookie3
                    except ImportError:
                        log_messages.append(f"✗ Missing browser_cookie3 package")
                        return "Missing browser_cookie3 package", "\n".join(log_messages)
                    
                    # Now try the actual login
                    L.load_session_from_browser(browser)
                    test_user = L.test_login()
                    
                    if test_user:
                        log_messages.append(f"✓ Login successful as {test_user}")
                        return f"Login successful as {test_user}", "\n".join(log_messages)
                    else:
                        log_messages.append("✗ Login failed with browser cookies")
                        return "Login failed with browser cookies", "\n".join(log_messages)
                except Exception as e:
                    error_message = str(e)
                    log_messages.append(f"✗ Error loading cookies: {error_message}")
                    return f"Error loading cookies: {error_message}", "\n".join(log_messages)
            else:
                # Login with username and password
                if not username or not password:
                    log_messages.append("✗ Username or password is missing")
                    return "Username or password is missing", "\n".join(log_messages)
                
                log_messages.append(f"Trying to login as {username}...")
                
                try:
                    L.login(username, password)
                    test_user = L.test_login()
                    
                    if test_user:
                        log_messages.append(f"✓ Login successful as {test_user}")
                        return f"Login successful as {test_user}", "\n".join(log_messages)
                    else:
                        log_messages.append("✗ Login failed with username/password")
                        return "Login failed with username/password", "\n".join(log_messages)
                except Exception as e:
                    error_message = str(e)
                    log_messages.append(f"✗ Login error: {error_message}")
                    return f"Login error: {error_message}", "\n".join(log_messages)
        except Exception as e:
            error_message = str(e)
            log_messages.append(f"✗ Error initializing Instaloader: {error_message}")
            return f"Error initializing Instaloader: {error_message}", "\n".join(log_messages)
    
    def download_saved_posts(self, username, password, use_browser_cookies, browser, output_dir, 
                           count_option, count_value, download_pictures, download_videos, 
                           auto_transcribe, auto_delete):
        """Download saved posts from Instagram"""
        log_messages = []
        
        # Validate inputs
        if not output_dir:
            return 0, "Error: No output directory specified", "Please specify an output directory", []
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return 0, f"Error creating output directory: {str(e)}", f"Failed to create output directory: {str(e)}", []
        
        # Check if instaloader is installed
        try:
            import instaloader
        except ImportError:
            # Try to install instaloader
            log_messages.append("Instaloader not installed. Attempting to install...")
            success, message = self.instaloader_api.install_instaloader()
            if not success:
                return 0, "Failed to install Instaloader", message, []
            
            log_messages.append("✓ Instaloader installed successfully")
            
            try:
                import instaloader
            except ImportError:
                return 0, "Failed to import Instaloader", "Failed to import Instaloader after installation", []
        
        try:
            # Create Instaloader instance with custom settings
            L = instaloader.Instaloader(
                dirname_pattern=output_dir + "/{profile}",
                filename_pattern="{date_utc}_UTC_{shortcode}",
                download_pictures=download_pictures,
                download_videos=download_videos,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=True,
                post_metadata_txt_pattern="{caption}"
            )
            
            log_messages.append("Instaloader initialized with custom settings")
            
            # Login to Instagram
            if use_browser_cookies:
                # Login with browser cookies
                log_messages.append(f"Logging in with {browser} cookies...")
                
                try:
                    L.load_session_from_browser(browser)
                    username = L.test_login()
                    
                    if not username:
                        return 0, "Login failed with browser cookies", "Error: Login failed with browser cookies", []
                    
                    log_messages.append(f"Logged in as {username}")
                except Exception as e:
                    return 0, f"Error loading cookies: {str(e)}", f"Error loading cookies: {str(e)}", []
            else:
                # Login with username and password
                if not username or not password:
                    return 0, "Username or password is missing", "Error: Username or password is missing", []
                
                log_messages.append(f"Logging in as {username}...")
                
                try:
                    L.login(username, password)
                    if not L.test_login():
                        return 0, "Login failed with username/password", "Error: Login failed with username/password", []
                    
                    log_messages.append(f"Logged in successfully as {username}")
                except Exception as e:
                    return 0, f"Login error: {str(e)}", f"Login error: {str(e)}", []
            
            # Determine post count
            post_count = None
            if count_option == "Specific number":
                try:
                    post_count = int(count_value)
                    log_messages.append(f"Will download up to {post_count} saved posts")
                except (ValueError, TypeError):
                    return 0, "Invalid count value", "Error: Please enter a valid number for post count", []
            else:
                log_messages.append("Will download all saved posts")
            
            # Start downloading saved posts
            log_messages.append("Fetching list of saved posts...")
            
            # Track videos for transcription
            downloaded_videos = []
            downloaded_files = []
            counter = 0
            
            try:
                saved_posts = L.get_saved_posts()
                total_posts = post_count if post_count else 999999  # Arbitrarily large number if downloading all
                
                # Main download loop
                for post in saved_posts:
                    if counter >= total_posts:
                        break
                    
                    try:
                        # Skip non-video posts if only downloading videos
                        if not download_pictures and not post.is_video:
                            log_messages.append(f"Skipping post {post.shortcode} (not a video)")
                            continue
                        
                        # Skip videos if not downloading videos
                        if not download_videos and post.is_video:
                            log_messages.append(f"Skipping post {post.shortcode} (is a video)")
                            continue
                        
                        log_messages.append(f"Downloading post {post.shortcode} from {post.owner_username}...")
                        
                        # Download the post
                        L.download_post(post, target=f"{post.owner_username}_{post.shortcode}")
                        
                        # Track files
                        if post.is_video and download_videos:
                            # Determine filename based on instaloader pattern
                            date_str = post.date_utc.strftime("%Y-%m-%d_%H-%M-%S")
                            video_filename = f"{output_dir}/{post.owner_username}/{date_str}_UTC_{post.shortcode}.mp4"
                            if os.path.exists(video_filename):
                                downloaded_videos.append(video_filename)
                                downloaded_files.append(video_filename)
                                log_messages.append(f"✓ Downloaded video: {post.shortcode}")
                                
                                # Store metadata for Notion
                                description = post.caption if post.caption else ""
                                self.notion_api.store_video_metadata(video_filename, f"https://www.instagram.com/p/{post.shortcode}/", description)
                        
                        counter += 1
                    except Exception as e:
                        log_messages.append(f"Error downloading post {post.shortcode}: {str(e)}")
                        continue
                
                # Process videos if needed
                if auto_transcribe and downloaded_videos:
                    for i, video_path in enumerate(downloaded_videos):
                        log_messages.append(f"\nTranscribing video {i+1}/{len(downloaded_videos)}: {os.path.basename(video_path)}")
                        
                        # Extract audio
                        audio_file = os.path.splitext(video_path)[0] + ".wav"
                        if self.extract_audio_with_ffmpeg(video_path, audio_file):
                            # Transcribe with default settings
                            model_name = "base"
                            language = "en"
                            word_timestamps = True
                            
                            try:
                                transcription = self.transcribe_with_whisper(audio_file, model_name, language, word_timestamps)
                                output_file = os.path.splitext(video_path)[0] + "_transcript.txt"
                                
                                # Write transcription to file
                                with open(output_file, "w", encoding="utf-8") as file:
                                    file.write(transcription['detailed'])
                                
                                downloaded_files.append(output_file)
                                log_messages.append(f"✓ Transcribed: {os.path.basename(output_file)}")
                                
                                # Delete video if auto-delete is enabled
                                if auto_delete:
                                    try:
                                        os.remove(video_path)
                                        log_messages.append(f"✓ Deleted video after transcription: {os.path.basename(video_path)}")
                                        # Remove from downloaded files
                                        if video_path in downloaded_files:
                                            downloaded_files.remove(video_path)
                                    except Exception as e:
                                        log_messages.append(f"✗ Error deleting video: {str(e)}")
                            except Exception as e:
                                log_messages.append(f"✗ Error transcribing video: {str(e)}")
                        else:
                            log_messages.append(f"✗ Error extracting audio from video")
                
                # Complete download process
                if counter == 0:
                    return 100, "No posts were downloaded", "No posts were downloaded. Check your download settings.", []
                else:
                    return 100, f"Download complete - {counter} posts downloaded", "\n".join(log_messages), downloaded_files
            
            except Exception as e:
                return 0, f"Error fetching saved posts: {str(e)}", f"Error fetching saved posts: {str(e)}", []
        
        except Exception as e:
            return 0, f"Error: {str(e)}", f"An unexpected error occurred: {str(e)}", []
            
    def load_settings(self):
        """Load saved settings for Notion and Groq"""
        # Load Notion settings
        try:
            config_file = os.path.join(os.path.expanduser("~"), ".videotranscriber", "notion_config.txt")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        token = lines[0].strip()
                        database_id = lines[1].strip()
                        
                        # Update the Notion API with the loaded credentials
                        self.notion_api.set_token(token)
                        self.notion_api.set_database_id(database_id)
        except Exception as e:
            print(f"Error loading Notion settings: {str(e)}")
        
        # Load Groq settings
        try:
            config_file = os.path.join(os.path.expanduser("~"), ".videotranscriber", "groq_config.txt")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    content = f.read()
                    parts = content.split("\n", 1)
                    
                    api_key = parts[0].strip()
                    
                    # Update the Groq API with the loaded credentials
                    self.groq_api.set_api_key(api_key)
        except Exception as e:
            print(f"Error loading Groq settings: {str(e)}")
    
    def launch(self):
        """Launch the web UI"""
        # Load settings first
        self.load_settings()
        
        # Launch the Gradio interface
        self.interface.launch(share=True)

def create_web_ui():
    """Create and launch the web UI"""
    app = WebTranscriberUI()
    return app