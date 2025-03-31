import requests
import json
import os
from datetime import datetime

class NotionIntegration:
    def __init__(self, token=None, database_id=None):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # Use the latest Notion API version
        }
        
    def set_token(self, token):
        """Set or update the Notion API token"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {self.token}"
        
    def set_database_id(self, database_id):
        """Set or update the Notion database ID"""
        self.database_id = database_id
        
    def test_connection(self):
        """Test the connection to Notion API"""
        if not self.token:
            return False, "Notion API token is not set."
            
        try:
            response = requests.get(
                "https://api.notion.com/v1/users/me",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return True, "Connection successful."
            else:
                return False, f"Connection failed: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def add_transcription_to_notion(self, video_path, transcription_text, duration=None, groq_result=None):
        """
        Add a new page to the Notion database with the transcription
        
        Parameters:
            video_path (str): Path to the original video file
            transcription_text (str): The transcription text to add
            duration (float, optional): Duration of the video in seconds
            groq_result (dict, optional): Processed result from Groq API containing title and summary
        
        Returns:
            tuple: (success, message)
        """
        if not self.token or not self.database_id:
            return False, "Notion API token or database ID is not set."
            
        # Get video filename without extension
        video_filename = os.path.basename(video_path)
        video_name = os.path.splitext(video_filename)[0]
        
        # Prepare page data
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Determine the page title - use Groq's title if available, otherwise use default
        page_title = f"Transcription: {video_name}"
        if groq_result and "title" in groq_result:
            page_title = groq_result["title"]
        
        # Create the page properties
        page_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": page_title
                            }
                        }
                    ]
                },
                # Add video name and date properties
                "Video Name": {
                    "rich_text": [
                        {
                            "text": {
                                "content": video_name
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": current_date
                    }
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Transcription of {video_filename}"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Generated on: {current_date}"
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # Add duration information if provided
        if duration:
            duration_mins = int(duration // 60)
            duration_secs = int(duration % 60)
            page_data["children"].append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Duration: {duration_mins}m {duration_secs}s"
                            }
                        }
                    ]
                }
            })
        
        # Add Groq summary if available
        if groq_result and "summary" in groq_result:
            # Add a divider before the summary
            page_data["children"].append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
            
            # Add heading for the summary
            page_data["children"].append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Summary:"
                            }
                        }
                    ]
                }
            })
            
            # Add the summary text - split into paragraphs for better readability
            summary_paragraphs = groq_result["summary"].split('\n\n')
            for paragraph in summary_paragraphs:
                if paragraph.strip():
                    page_data["children"].append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": paragraph.strip()
                                    }
                                }
                            ]
                        }
                    })
        
        # Add a divider before the transcription
        page_data["children"].append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        # Add heading for the transcription
        page_data["children"].append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Original Transcription:"
                        }
                    }
                ]
            }
        })
        
        # Notion API has a limit for block content, so we need to split long transcriptions
        max_block_size = 2000  # Notion has a character limit per block
        
        # Split the transcription into chunks if it's too long
        text_chunks = [transcription_text[i:i+max_block_size] 
                      for i in range(0, len(transcription_text), max_block_size)]
        
        # Add each chunk as a separate paragraph block
        for chunk in text_chunks:
            page_data["children"].append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": chunk
                            }
                        }
                    ]
                }
            })
        
        # Send the request to Notion API
        try:
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                data=json.dumps(page_data)
            )
            
            if response.status_code == 200:
                return True, "Transcription added to Notion successfully."
            else:
                return False, f"Failed to add to Notion: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Error adding to Notion: {str(e)}"