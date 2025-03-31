# Video Transcriber

A GUI application that accurately transcribes speech from video files using OpenAI's Whisper speech recognition model, with AI-powered summarization via Groq.

![Video Transcriber Screenshot](https://placeholder-image.com)

## Features

- **High-Quality Transcription**: Uses Whisper AI for state-of-the-art speech recognition
- **AI-Powered Summaries**: Processes transcriptions with Groq API to create clear, jargon-free summaries and titles
- **User-Friendly Interface**: Simple GUI for selecting and transcribing videos
- **Multiple Model Options**: Choose from tiny, base, small, medium, or large models to balance speed and accuracy
- **Multilingual Support**: Works with 99 languages with automatic language detection
- **Timestamp Generation**: Option to include timestamps in the transcription
- **Progress Tracking**: Real-time progress updates during transcription
- **Transcription Preview**: See a preview of the transcription in the application
- **Local Processing**: All transcription happens locally on your machine with no data sent to external servers (except for optional AI processing)
- **Batch Processing**: Process multiple video files in a directory with a single click
- **Notion Integration**: Automatically send transcriptions to your Notion database

## Installation

### Prerequisites

- Python 3.7 or higher
- FFmpeg (required for audio extraction)

### Installing FFmpeg

#### Windows
- Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH, or
- Install via Chocolatey: `choco install ffmpeg`

#### macOS
- Install via Homebrew: `brew install ffmpeg`

#### Linux
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Fedora: `sudo dnf install ffmpeg`

### Installing Python Packages

Install all required packages using pip:

```bash
pip install torch openai-whisper tkinter requests
```

For NVIDIA GPU support (recommended for faster processing):

```bash
pip install torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
pip install openai-whisper requests
```

## Usage

1. Clone or download this repository
2. Run the application:
   ```bash
   python main.py
   ```

### Using the Application

#### Single File Transcription
1. Click on the "Transcription" tab
2. **Select Video File**: Click "Browse" to select the video file you want to transcribe
3. **Choose Output Location**: Specify where to save the transcription text file
4. **Select Whisper Model**:
   - **Tiny**: Fastest but least accurate (~1GB RAM)
   - **Base**: Good balance of speed and accuracy (~1GB RAM)
   - **Small**: Better accuracy, moderate speed (~2GB RAM)
   - **Medium**: High accuracy, slower processing (~5GB RAM)
   - **Large**: Best quality, but slowest processing (~10GB RAM)
5. **Select Language**: Choose the language of the video or use auto-detection
6. **Timestamp Options**: Enable/disable word-level timestamps
7. **Enable AI Processing**: Check "Process with Groq AI after transcription" to generate summaries
8. **Start Transcription**: Click the "Start Transcription" button
9. **Monitor Progress**: Watch the progress bar and status updates
10. **View Results**: See a preview of the transcription and find the complete text in the saved file

#### Batch Processing
1. Click on the "Batch Processing" tab
2. **Select Video Directory**: Click "Browse" to select a folder containing multiple video files
3. **Choose Output Directory**: Specify where to save all the transcription text files
4. **Configure Options**: Select the same model, language, and timestamp options as in single file mode
5. **Enable AI Processing**: Check "Process with Groq AI after transcription" for batch summarization
6. **Start Batch Processing**: Click the "Start Batch Transcription" button
7. **Monitor Progress**: Track the overall progress bar and view the processing log
8. **Batch Results**: Each video will be transcribed and saved as a separate text file in the output directory

#### Notion Integration
1. Click on the "Notion Integration" tab
2. **Set Up Notion**: Follow the instructions to create a Notion integration and get your API token
3. **Configure Integration**:
   - Enter your Notion API Token
   - Enter your Notion Database ID
   - Click "Test Connection" to verify your settings
4. **Enable Integration**: Check "Send to Notion after transcription" in either single file or batch mode
5. **View in Notion**: Transcriptions will be added as new pages in your Notion database

#### AI Processing with Groq
1. Click on the "AI Processing" tab
2. **Set Up Groq**: Sign up for a Groq account and get your API key
3. **Configure Integration**:
   - Enter your Groq API Key
   - Customize the system prompt if desired
   - Click "Test Connection" to verify your settings
4. **Enable Integration**: Check "Process with Groq AI after transcription" in either single file or batch mode
5. **Enhanced Transcripts**: Your transcriptions will be processed to include:
   - A clear, concise title that summarizes the content
   - A jargon-free summary of the key points
   - The original transcript with timestamps (if enabled)

## Technical Details

### How It Works

1. **Audio Extraction**: Uses FFmpeg to extract the audio track from the video file
2. **Speech Recognition**: Processes the audio with OpenAI's Whisper model
3. **AI Processing**: (Optional) Sends the transcript to Groq API for summarization and title generation
4. **Threading**: Runs transcription in a background thread to keep the UI responsive
5. **Progress Updates**: Regularly updates the UI with the current status
6. **Batch Processing**: Processes multiple files sequentially using a dedicated thread
7. **Notion API**: Connects to Notion's API to add transcriptions as database entries

### Components

- **GUI**: Built with Tkinter, Python's standard GUI toolkit
- **Audio Processing**: Uses FFmpeg for reliable audio extraction
- **Speech Recognition**: Leverages OpenAI's Whisper model via the `openai-whisper` Python package
- **GPU Acceleration**: Automatically uses CUDA if available for faster processing
- **Notion Integration**: Uses Notion's official API to create new pages in your database
- **Groq Integration**: Uses Groq's API for AI-powered summarization and title generation

## Troubleshooting

### Common Issues

**Error: FFmpeg not found**
- Make sure FFmpeg is installed and added to your system PATH
- Restart the application after installing FFmpeg

**Error: Missing required packages**
- Run `pip install torch openai-whisper requests` to install the required packages
- Make sure you have a compatible Python version (3.7+)

**Slow Transcription**
- Try a smaller model size (tiny or base)
- Enable GPU acceleration if you have a compatible NVIDIA GPU
- Split long videos into smaller segments before transcription

**Out of Memory Errors**
- Try a smaller model size
- Close other memory-intensive applications
- Increase your system's swap space/virtual memory

**Batch Processing Errors**
- Make sure all videos in the directory are valid and not corrupted
- Ensure sufficient disk space for audio extraction and transcription files
- Check that your Notion API token and database ID are correct if using integration

**Groq API Errors**
- Verify that your API key is correct
- Check if your system prompt follows Groq's guidelines
- Ensure you have an active internet connection

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- [FFmpeg](https://ffmpeg.org/) for audio processing
- [Notion API](https://developers.notion.com/) for database integration
- [Groq API](https://console.groq.com/) for AI-powered text processing
- Python Tkinter for the GUI framework

## Future Improvements

- Export options (SRT, VTT, JSON)
- Audio/video playback integration
- Speaker diarization (identifying different speakers)
- Transcript editing capabilities
- Support for fine-tuned custom models
- Additional third-party integrations (Google Docs, Microsoft Word, etc.)