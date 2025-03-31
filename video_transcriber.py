import os
import subprocess
import argparse
import speech_recognition as sr
import time

def extract_audio_with_ffmpeg(video_file, audio_file):
    """Extract audio from video file using FFmpeg directly."""
    print(f"Extracting audio from {video_file}...")
    try:
        # Use FFmpeg to extract audio
        subprocess.run([
            "ffmpeg", "-i", video_file, "-q:a", "0", "-map", "a", audio_file, "-y"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Audio extracted successfully to {audio_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {str(e)}")
        return False
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and make sure it's in your PATH.")
        return False

def transcribe_audio(audio_file, language="en-US"):
    """Transcribe audio file using SpeechRecognition."""
    print(f"Transcribing audio file: {audio_file}")
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            
        print("Recognizing speech (this may take some time)...")
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        print("Speech recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def transcribe_video(video_file, output_file=None, language="en-US", keep_audio=False):
    """Process a video file: extract audio and transcribe it."""
    # Create output file name if not provided
    if not output_file:
        output_file = os.path.splitext(video_file)[0] + "_transcription.txt"
    
    # Create audio file name
    audio_file = os.path.splitext(video_file)[0] + ".wav"
    
    start_time = time.time()
    
    # Extract audio from video
    if extract_audio_with_ffmpeg(video_file, audio_file):
        # Transcribe the audio
        transcription = transcribe_audio(audio_file, language)
        
        if transcription:
            # Write transcription to file
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(transcription)
            print(f"Transcription saved to {output_file}")
        else:
            print("Transcription failed.")
        
        # Clean up
        if not keep_audio and os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Temporary audio file removed: {audio_file}")
        
        elapsed_time = time.time() - start_time
        print(f"Total processing time: {elapsed_time:.2f} seconds")
        
        return transcription
    
    return None

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Transcribe video files to text')
    parser.add_argument('video_file', help='Path to the video file')
    parser.add_argument('--output', '-o', help='Output file for transcription (optional)')
    parser.add_argument('--language', '-l', default='en-US', help='Language code (default: en-US)')
    parser.add_argument('--keep-audio', '-k', action='store_true', help='Keep extracted audio file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video_file):
        print(f"Error: Video file '{args.video_file}' not found")
        return
    
    transcribe_video(
        args.video_file, 
        output_file=args.output,
        language=args.language,
        keep_audio=args.keep_audio
    )

if __name__ == "__main__":
    main()