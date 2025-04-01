import requests
import json
import os
import time
from datetime import datetime

class GroqIntegration:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Track failed processing attempts for reporting
        self.failed_processing = []
        # Maximum number of retries for Groq API calls
        self.max_retries = 1
        # Delay between retries (seconds)
        self.retry_delay = 3
        
    def set_api_key(self, api_key):
        """Set or update the Groq API key"""
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {self.api_key}"
        
    def test_connection(self):
        """Test the connection to Groq API"""
        if not self.api_key:
            return False, "Groq API key is not set."
            
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return True, "Connection successful."
            else:
                return False, f"Connection failed: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def add_failed_processing(self, video_file, error_message):
        """Add a video file to the failed processing list"""
        self.failed_processing.append({
            "file": video_file,
            "error": error_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def save_failed_processing_report(self, directory):
        """Save the failed processing list to a report file"""
        if not self.failed_processing:
            return None
            
        try:
            # Create the report file path
            report_file = os.path.join(directory, f"groq_processing_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(f"Groq Processing Errors Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, entry in enumerate(self.failed_processing, 1):
                    f.write(f"Error #{i}:\n")
                    f.write(f"File: {entry['file']}\n")
                    f.write(f"Time: {entry['timestamp']}\n")
                    f.write(f"Error: {entry['error']}\n")
                    f.write("-" * 50 + "\n\n")
            
            # Clear the failed processing list after saving
            self.failed_processing = []
            
            return report_file
        except Exception as e:
            print(f"Error saving failed processing report: {str(e)}")
            return None
    
    def summarize_transcript(self, transcript_text, system_prompt=None, video_file=None):
        """
        Process a transcript using Groq API to create a clear, jargon-free summary and title
        
        Parameters:
            transcript_text (str): The transcription text to process
            system_prompt (str, optional): Custom system prompt to guide the AI
            video_file (str, optional): The video file path for error tracking
            
        Returns:
            tuple: (success, result_dict or error_message)
        """
        if not self.api_key:
            return False, "Groq API key is not set."
        
        # Check if transcript is empty or too short
        if not transcript_text or len(transcript_text.strip()) < 10:
            error_msg = "Transcript is empty or too short for processing"
            if video_file:
                self.add_failed_processing(video_file, error_msg)
            return False, error_msg
        
        # Define default system prompt if none provided
        if not system_prompt:
            system_prompt = """
            You are an expert at summarizing video transcripts. Given a transcript text:
            1. Create a clear, concise title that accurately represents the core content
            2. Summarize the key points in plain language without jargon
            3. Be straightforward and avoid clickbait language
            4. Don't leave out important details from the transcript
            5. Format your response as JSON with "title" and "summary" fields
            """
        
        # Try processing with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                data = {
                    "model": "llama-3.3-70b-versatile",  # Using one of Groq's models
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": f"Here is the transcript to process:\n\n{transcript_text}"
                        }
                    ],
                    "response_format": {"type": "json_object"}
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    data=json.dumps(data)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract the content from the response
                    content = result["choices"][0]["message"]["content"]
                    
                    # Parse the JSON string into a Python dictionary
                    try:
                        processed_content = json.loads(content)
                        
                        # Check if required fields are present
                        if "title" not in processed_content or "summary" not in processed_content:
                            error_msg = "Groq API response is missing required fields."
                            if retries < self.max_retries:
                                retries += 1
                                time.sleep(self.retry_delay)
                                continue
                            
                            if video_file:
                                self.add_failed_processing(video_file, error_msg)
                            return False, error_msg
                        
                        return True, processed_content
                    except json.JSONDecodeError:
                        error_msg = f"Failed to parse Groq API response as JSON: {content}"
                        if retries < self.max_retries:
                            retries += 1
                            time.sleep(self.retry_delay)
                            continue
                        
                        if video_file:
                            self.add_failed_processing(video_file, error_msg)
                        return False, error_msg
                else:
                    error_msg = f"Groq API request failed: {response.status_code} - {response.text}"
                    if retries < self.max_retries:
                        retries += 1
                        time.sleep(self.retry_delay)
                        continue
                    
                    if video_file:
                        self.add_failed_processing(video_file, error_msg)
                    return False, error_msg
            except Exception as e:
                error_msg = f"Error processing with Groq API: {str(e)}"
                if retries < self.max_retries:
                    retries += 1
                    time.sleep(self.retry_delay)
                    continue
                
                if video_file:
                    self.add_failed_processing(video_file, error_msg)
                return False, error_msg
            
            retries += 1