import requests
import json
import os
from datetime import datetime

class GroqIntegration:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
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
    
    def summarize_transcript(self, transcript_text, system_prompt=None):
        """
        Process a transcript using Groq API to create a clear, jargon-free summary and title
        
        Parameters:
            transcript_text (str): The transcription text to process
            system_prompt (str, optional): Custom system prompt to guide the AI
            
        Returns:
            tuple: (success, result_dict or error_message)
        """
        if not self.api_key:
            return False, "Groq API key is not set."
        
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
        
        # Prepare request to Groq API
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
                        return False, "Groq API response is missing required fields."
                    
                    return True, processed_content
                except json.JSONDecodeError:
                    return False, f"Failed to parse Groq API response as JSON: {content}"
            else:
                return False, f"Groq API request failed: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Error processing with Groq API: {str(e)}"