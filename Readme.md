# Video Transcriber

A GUI application that accurately transcribes speech from video files using OpenAI's Whisper speech recognition model.

![Video Transcriber Screenshot](https://placeholder-image.com)

## Features

- **High-Quality Transcription**: Uses Whisper AI for state-of-the-art speech recognition
- **User-Friendly Interface**: Simple GUI for selecting and transcribing videos
- **Multiple Model Options**: Choose from tiny, base, small, medium, or large models to balance speed and accuracy
- **Multilingual Support**: Works with 99 languages with automatic language detection
- **Timestamp Generation**: Option to include timestamps in the transcription
- **Progress Tracking**: Real-time progress updates during transcription
- **Transcription Preview**: See a preview of the transcription in the application
- **Local Processing**: All transcription happens locally on your machine with no data sent to external servers

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
pip install torch openai-whisper tkinter
```

For NVIDIA GPU support (recommended for faster processing):

```bash
pip install torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
pip install openai-whisper
```

## Usage

1. Clone or download this repository
2. Run the application:
   ```bash
   python whisper_video_transcriber.py
   ```

### Using the Application

1. **Select Video File**: Click "Browse" to select the video file you want to transcribe
2. **Choose Output Location**: Specify where to save the transcription text file
3. **Select Whisper Model**:
   - **Tiny**: Fastest but least accurate (~1GB RAM)
   - **Base**: Good balance of speed and accuracy (~1GB RAM)
   - **Small**: Better accuracy, moderate speed (~2GB RAM)
   - **Medium**: High accuracy, slower processing (~5GB RAM)
   - **Large**: Best quality, but slowest processing (~10GB RAM)
4. **Select Language**: Choose the language of the video or use auto-detection
5. **Timestamp Options**: Enable/disable word-level timestamps
6. **Start Transcription**: Click the "Start Transcription" button
7. **Monitor Progress**: Watch the progress bar and status updates
8. **View Results**: See a preview of the transcription and find the complete text in the saved file

## Technical Details

### How It Works

1. **Audio Extraction**: Uses FFmpeg to extract the audio track from the video file
2. **Speech Recognition**: Processes the audio with OpenAI's Whisper model
3. **Threading**: Runs transcription in a background thread to keep the UI responsive
4. **Progress Updates**: Regularly updates the UI with the current status

### Components

- **GUI**: Built with Tkinter, Python's standard GUI toolkit
- **Audio Processing**: Uses FFmpeg for reliable audio extraction
- **Speech Recognition**: Leverages OpenAI's Whisper model via the `openai-whisper` Python package
- **GPU Acceleration**: Automatically uses CUDA if available for faster processing

## Development History

### Version 1.0
- Initial version using Google Speech Recognition API
- Basic transcription capabilities
- Limited accuracy and language support

### Version 2.0 (Current)
- Switched to OpenAI's Whisper model for significantly improved accuracy
- Added multiple model size options
- Implemented language selection and auto-detection
- Added timestamp generation
- Enhanced the user interface
- Improved progress reporting

## Troubleshooting

### Common Issues

**Error: FFmpeg not found**
- Make sure FFmpeg is installed and added to your system PATH
- Restart the application after installing FFmpeg

**Error: Missing required packages**
- Run `pip install torch openai-whisper` to install the required packages
- Make sure you have a compatible Python version (3.7+)

**Slow Transcription**
- Try a smaller model size (tiny or base)
- Enable GPU acceleration if you have a compatible NVIDIA GPU
- Split long videos into smaller segments before transcription

**Out of Memory Errors**
- Try a smaller model size
- Close other memory-intensive applications
- Increase your system's swap space/virtual memory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- [FFmpeg](https://ffmpeg.org/) for audio processing
- Python Tkinter for the GUI framework

## Future Improvements

- Support for batch processing multiple files
- Export options (SRT, VTT, JSON)
- Audio/video playback integration
- Speaker diarization (identifying different speakers)
- Transcript editing capabilities
- Support for fine-tuned custom models