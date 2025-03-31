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
    
    def add_transcription_to_notion(self, video_path, transcription_text, duration=None):
        """
        Add a new page to the Notion database with the transcription
        
        Parameters:
            video_path (str): Path to the original video file
            transcription_text (str): The transcription text to add
            duration (float, optional): Duration of the video in seconds
        
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
        
        # Create the page properties based on your actual Notion database fields
        # IMPORTANT: You need to customize these property names to match your Notion database exactly
        # Only keep the "Name" property (which is required) and remove any properties that don't exist
        page_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": f"Transcription: {video_name}"
                            }
                        }
                    ]
                },
                # Remove or comment out properties that don't exist in your database
                # Uncomment and adjust property names to match your database exactly
                # "Created": {  # Replace "Date" with your actual date property name if you have one
                #     "date": {
                #         "start": current_date
                #     }
                # },
                # "Tags": {  # Replace "Status" with your actual status/select property name if you have one
                #     "select": {
                #         "name": "Completed"
                #     }
                # }
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
        
        # Add the transcription text
        # Notion API has a limit for block content, so we need to split long transcriptions
        max_block_size = 2000  # Notion has a character limit per block
        
        # Split the transcription into chunks if it's too long
        text_chunks = [transcription_text[i:i+max_block_size] 
                      for i in range(0, len(transcription_text), max_block_size)]
        
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
                            "content": "Transcription Text:"
                        }
                    }
                ]
            }
        })
        
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