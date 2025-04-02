# Video Transcriber

A GUI application that accurately transcribes speech from video files using OpenAI's Whisper speech recognition model, with AI-powered summarization via Groq and Instagram video downloading via Instaloader. Now with web interface support for platforms like Google Colab and Kaggle!

![Video Transcriber Screenshot](https://placeholder-image.com)

## Features

- **High-Quality Transcription**: Uses Whisper AI for state-of-the-art speech recognition
- **AI-Powered Summaries**: Processes transcriptions with Groq API to create clear, jargon-free summaries and titles
- **Robust Error Handling**: Gracefully handles empty transcripts and API errors during batch processing
- **User-Friendly Interface**: Simple GUI for selecting and transcribing videos
- **Web Interface**: Run the application in a web browser using Gradio, perfect for cloud notebooks and headless servers
- **Multiple Model Options**: Choose from tiny, base, small, medium, or large models to balance speed and accuracy
- **Multilingual Support**: Works with 99 languages with automatic language detection
- **Timestamp Generation**: Option to include timestamps in the transcription
- **Progress Tracking**: Real-time progress updates during transcription
- **Transcription Preview**: See a preview of the transcription in the application
- **Local Processing**: All transcription happens locally on your machine with no data sent to external servers (except for optional AI processing)
- **Batch Processing**: Process multiple video files in a directory with a single click
- **Error Reporting**: Comprehensive error logs for batch processing with Groq
- **Auto-Delete Videos**: Automatically remove Instagram videos after transcription to save disk space
- **Enhanced Notion Integration**: Automatically send transcriptions to your Notion database with:
  - Video links for Instagram content
  - Video descriptions and extracted hashtags
  - Properly formatted content with clear section headings
  - Multi-select tags from Instagram hashtags
- **Instagram Video Download**: Download videos directly from Instagram posts and reels for transcription
- **Batch Instagram Processing**: Process multiple Instagram URLs from a text file automatically
- **Instagram Saved Posts**: Access and download videos from your Instagram saved collection for transcription

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
pip install torch openai-whisper tkinter requests gradio
```

For NVIDIA GPU support (recommended for faster processing):

```bash
pip install torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
pip install openai-whisper requests gradio
```

For Instagram video download functionality:

```bash
pip install instaloader browser_cookie3
```

## Usage

1. Clone or download this repository
2. Run the application:
   ```bash
   # For desktop GUI mode
   python main.py
   
   # For web interface mode
   python main.py --web
   ```

### Using the Desktop Application

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
9. **Error Reports**: If any Groq processing issues occur, a detailed error report will be saved in the output directory

#### Instagram Video Download
1. Click on the "Instagram Download" tab
2. **Enter Instagram URL**: Paste the URL of an Instagram post or reel containing a video
   - Example formats: `https://www.instagram.com/p/ABC123/` or `https://www.instagram.com/reel/XYZ789/`
3. **Choose Output Directory**: Specify where to save the downloaded video
4. **Auto-Delete Option**: Enable "Auto-delete videos after transcription" to save disk space
5. **Download & Transcribe**: Click to download the video and automatically proceed to transcription
6. **Download Only**: Click to download the video without transcribing
7. **First-time Setup**: If Instaloader is not already installed, the app will offer to install it for you

#### Batch Instagram Processing
1. Click on the "Instagram Download" tab
2. **Prepare URL List**: Create a text file with Instagram URLs, one per line:
   ```
   https://www.instagram.com/p/ABC123/
   https://www.instagram.com/reel/XYZ789/
   https://www.instagram.com/reel/DEF456/
   ```
3. **Load URLs from File**: Click the "Load URLs from File" button and select your text file
4. **Choose Output Directory**: Specify where to save the downloaded videos
5. **Auto-Delete Option**: Enable to automatically remove videos after processing
6. **Confirm Processing**: Review the detected URLs and confirm to start batch processing
7. **Monitor Progress**: Track progress as each video is downloaded and transcribed
8. **Review Log**: Check the processing log for detailed information about each video
9. **Error Handling**: The system will continue processing even if some videos have issues with Groq

#### Instagram Saved Posts
1. Click on the "Instagram Saved" tab
2. **Choose Output Directory**: Specify where to save the downloaded videos
3. **Login**: Use session file (recommended for accounts with 2FA) or enter your username and password
4. **Configure Download Options**:
   - Choose to download all saved posts or specify a count
   - Select content types (pictures, videos, or both)
   - Enable auto-transcription for downloaded videos
   - Enable auto-delete to remove videos after transcription
5. **Download Saved Posts**: Click to begin the download process
6. **Auto-Transcription**: Downloaded videos can be automatically sent to batch processing

#### Notion Integration
1. Click on the "Notion Integration" tab
2. **Set Up Notion**: Follow the instructions to create a Notion integration and get your API token
3. **Configure Integration**:
   - Enter your Notion API Token
   - Enter your Notion Database ID
   - Click "Test Connection" to verify your settings
4. **Enable Integration**: Check "Send to Notion after transcription" in either single file or batch mode
5. **Prepare Notion Database**: Make sure your database has these properties:
   - **Video URL** (type: URL)
   - **Description** (type: Text)
   - **Hashtags** (type: Multi-select)
6. **Content Structure in Notion**:
   - **Summary** (if AI processing is enabled)
   - **Original Transcription** (clearly labeled with heading)
   - **Video Description** (from Instagram, if available)
   - **Video Link** (clickable link to source)

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
6. **Error Handling**: The system handles Groq processing errors gracefully:
   - Empty transcripts are detected and skipped
   - API errors are automatically retried once
   - Processing continues even when Groq encounters issues
   - A detailed error report is generated at the end of batch processing

### Using the Web Interface

The web interface provides all the same functionality as the desktop application but can be accessed through a web browser, making it ideal for use on:
- Google Colab
- Kaggle
- Remote servers
- Headless systems

#### Running in Web Mode

```bash
python main.py --web
```

This will start a Gradio web server and provide a link to access the interface in your browser. When running in a notebook environment like Google Colab, a public URL will be provided for access.

#### Google Colab / Kaggle Integration

1. Upload all application files to your Colab/Kaggle environment
2. Install the required packages:
   ```python
   !pip install torch openai-whisper requests gradio instaloader browser_cookie3
   !apt-get install -y ffmpeg
   ```
3. Run the application in web mode:
   ```python
   !python main.py --web
   ```
4. Click on the Gradio public URL provided in the output to access the interface

For a complete guide to using the web interface on cloud platforms, refer to `web_mode_guide.md` in the repository.

## Managing Disk Space with Auto-Delete

The auto-delete feature helps you manage disk space when working with Instagram videos:

1. **How It Works**:
   - When enabled, videos are automatically deleted after being successfully transcribed
   - Deletion only occurs after all processing (transcription, Groq processing, Notion upload) is complete
   - The transcription file is kept; only the source video is deleted

2. **Where to Enable**:
   - In the "Instagram Download" tab for single videos
   - In the "Instagram Saved" tab for saved posts collection
   - Setting persists across sessions until changed

3. **Batch Processing**:
   - When auto-delete is enabled during batch Instagram URL processing, each video is deleted once its processing is complete
   - Status updates in the log show which videos are being deleted
   - Any errors during deletion are logged but don't stop the overall process

4. **Recommendations**:
   - Enable auto-delete when transcription is the primary goal and keeping source videos isn't necessary
   - Disable auto-delete when you want to keep videos for later reference or editing
   - Double-check that transcription files are saved properly before enabling auto-delete for important content

## Technical Details

### How It Works

1. **Audio Extraction**: Uses FFmpeg to extract the audio track from the video file
2. **Speech Recognition**: Processes the audio with OpenAI's Whisper model
3. **AI Processing**: (Optional) Sends the transcript to Groq API for summarization and title generation
4. **Error Management**: Handles Groq API errors with a retry mechanism and comprehensive logging
5. **Instagram Download**: (Optional) Uses Instaloader to download videos from Instagram posts and reels
6. **Instagram Batch Processing**: (Optional) Processes multiple Instagram URLs from a text file in sequence
7. **Instagram Saved Posts**: (Optional) Downloads videos from your Instagram saved collection
8. **Auto-Delete Feature**: (Optional) Automatically removes downloaded videos after processing to save disk space
9. **Threading**: Runs transcription in a background thread to keep the UI responsive
10. **Progress Updates**: Regularly updates the UI with the current status
11. **Batch Processing**: Processes multiple files sequentially using a dedicated thread
12. **Notion API**: Connects to Notion's API to add transcriptions as database entries with:
    - Video URLs, descriptions, and hashtags
    - Properly formatted transcription content with section headings
    - Multi-select properties for categorization via hashtags
13. **Web Interface**: Provides a browser-based UI using Gradio for cloud environments

### Components

- **GUI**: Built with Tkinter for desktop and Gradio for web interface
- **Audio Processing**: Uses FFmpeg for reliable audio extraction
- **Speech Recognition**: Leverages OpenAI's Whisper model via the `openai-whisper` Python package
- **GPU Acceleration**: Automatically uses CUDA if available for faster processing
- **Notion Integration**: Uses Notion's official API to create new pages in your database
- **Groq Integration**: Uses Groq's API for AI-powered summarization and title generation
- **Error Handling**: Implements retry mechanism and comprehensive error reporting for Groq processing
- **Instagram Integration**: Uses Instaloader to download videos from Instagram posts, reels, and saved collections
- **Disk Management**: Implements auto-delete functionality for cleaning up downloaded videos after processing
- **Web Mode**: Uses Gradio to create a browser-based interface for cloud platforms

## Troubleshooting

### Common Issues

**Error: FFmpeg not found**
- Make sure FFmpeg is installed and added to your system PATH
- For Google Colab, install with `!apt-get install -y ffmpeg`
- Restart the application after installing FFmpeg

**Error: Missing required packages**
- Run `pip install torch openai-whisper requests instaloader browser_cookie3 gradio` to install the required packages
- Make sure you have a compatible Python version (3.7+)

**Error: 'Whisper' object has no attribute 'model'**
- This can happen when transcribing multiple videos in sequence
- The application has been updated to fix this issue by loading a fresh model for each transcription
- If you still encounter this error, try restarting the application between transcriptions

**Groq API Processing Issues**
- For videos with no speech or very short transcripts, the system will skip Groq processing
- If Groq API returns errors, the system will retry once and then continue with the original transcript
- A comprehensive error report is saved at the end of batch processing
- Check the batch log for details on which files had issues

**Instagram Login Issues**
- For accounts with two-factor authentication (2FA), use the session file method
- You may need to create a session file from the command line using: `instaloader --login YOUR_USERNAME`
- If browser cookie login fails, try using username/password method instead
- In web mode on cloud platforms, browser cookie login may not work as expected

**Web Interface Issues**
- If you encounter issues with the Gradio interface, make sure you have the latest version: `pip install --upgrade gradio`
- For older Gradio versions, the application has been updated to be compatible
- If you get module not found errors, ensure all required packages are installed

**Batch Instagram Processing Errors**
- Ensure your text file has one URL per line
- Check that the URLs are valid Instagram post or reel URLs
- Make sure Instaloader is properly installed
- For private posts, you need to login with Instaloader separately

**Auto-Delete Feature Issues**
- If videos aren't being deleted, check if the auto-delete option is properly checked
- The auto-delete process runs after all processing is complete, so be patient with large files
- If a video fails to delete, you'll see an error message in the log, but processing will continue
- Videos are only deleted after successful transcription, ensuring you don't lose content

**Notion Integration Issues**
- Verify your database has all required properties: "Video URL" (URL type), "Description" (Text type), and "Hashtags" (Multi-select type)
- Check your Notion API token and database ID
- Ensure your integration has the proper permissions to modify your database

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
- [Notion API](https://developers.notion.com/) for database integration
- [Groq API](https://console.groq.com/) for AI-powered text processing
- [Instaloader](https://instaloader.github.io/) for Instagram video downloading
- [Gradio](https://gradio.app/) for the web-based UI
- Python Tkinter for the desktop GUI framework