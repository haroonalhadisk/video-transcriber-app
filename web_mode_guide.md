# Video Transcriber - Web Mode Guide

This guide explains how to use the Video Transcriber application in web mode, which is particularly useful for running on platforms like Google Colab and Kaggle where traditional GUIs can't be displayed.

## Getting Started with Web Mode

### Local Installation

If you're running locally:

1. Clone or download the repository
2. Install dependencies: `pip install torch openai-whisper requests gradio`
3. Run with the web flag: `python main.py --web`
4. A local Gradio web server will start, and a public share link will be provided

### Google Colab / Kaggle Setup

1. Upload all application files to your Colab/Kaggle environment (or clone from GitHub)
2. Make sure required packages are installed:
   ```python
   !pip install torch openai-whisper requests gradio
   ```
3. Run the application with the web flag:
   ```python
   !python main.py --web
   ```
4. Gradio will provide a public URL you can use to access the interface

## Using the Web Interface

### Transcription Tab
- Upload a video file
- Choose transcription settings
- Click "Start Transcription"
- View and download the transcription results

### Batch Processing Tab
- Upload multiple video files
- Configure batch processing settings
- Click "Start Batch Transcription"
- Track progress in the log
- Download all transcriptions

### Instagram Download Tab
- Enter an Instagram post/reel URL
- Choose to download only or download and transcribe
- For batch processing, upload a text file with one URL per line
- Track progress in the log

### Instagram Saved Tab
- Specify where to save downloaded posts
- Enter login credentials or use browser cookies (note: browser cookies may not work in some cloud environments)
- Select content types and post limits
- Click "Download Saved Posts"

### AI Processing Tab (Groq)
- Enter your Groq API key
- Customize the system prompt for AI processing
- Test the connection
- Save your settings

### Notion Integration Tab
- Enter your Notion API token and database ID
- Test the connection
- Save your settings
- Enable Notion integration in the Transcription or Batch Processing tabs

## Limitations in Web Mode

When running in web mode, especially on platforms like Google Colab or Kaggle, be aware of these limitations:

1. **File Access**: Files are uploaded to the web server's temporary storage and not directly accessed from your local filesystem
2. **Session Persistence**: Settings are saved but may not persist between Colab/Kaggle sessions
3. **Browser Cookies**: Instagram browser cookie login may not work as expected in cloud environments
4. **Network Constraints**: Downloading large Instagram collections may be limited by timeout restrictions
5. **Security Considerations**: API keys and credentials are stored on the cloud instance

## Tips for Colab/Kaggle Usage

1. **Keep Running**: Use `%cd /content` at the beginning of your notebook to ensure you're in the main directory
2. **Prevent Timeouts**: Add a cell with code to prevent Colab from disconnecting during long processes
3. **Save Outputs**: Download transcriptions promptly as Colab/Kaggle sessions may terminate
4. **API Keys**: Consider using environment variables for sensitive information
5. **Persistent Storage**: Mount Google Drive in Colab to save transcriptions permanently

```python
# Example Colab setup with drive mounting
from google.colab import drive
drive.mount('/content/drive')

# Clone the repository (if not uploaded manually)
!git clone https://github.com/haroonalhadisk/video-transcriber-app.git
%cd video-transcriber

# Install dependencies
!pip install torch openai-whisper requests gradio

# Run in web mode
!python main.py --web
```

## Troubleshooting

### Common Issues

1. **"No module named X"**: Install the missing package with `pip install X`
2. **FFmpeg errors**: Make sure FFmpeg is installed with `!apt-get install -y ffmpeg` in Colab
3. **Memory errors**: Try using a smaller Whisper model like "tiny" or "base"
4. **Instagram login failures**: Use username/password instead of browser cookies in cloud environments
5. **Timeout errors**: For large batches, process files in smaller groups

If you encounter persistent issues, please open an issue on the GitHub repository with a detailed description of the problem.