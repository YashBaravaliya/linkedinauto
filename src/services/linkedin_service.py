import requests
import json
import io

class LinkedInImageShare:
    def __init__(self, access_token, person_urn):
        self.access_token = access_token
        self.person_urn = person_urn
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.linkedin.com/v2'

    def register_upload(self):
        """Register the image upload with LinkedIn"""
        endpoint = f"{self.base_url}/assets?action=registerUpload"
        
        data = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-image"
                ],
                "owner": self.person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def upload_image_from_url(self, image_url, upload_url):
        """Upload the image from URL to LinkedIn"""
        # Fetch image from your MongoDB endpoint
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Create file-like object from image data
        image_data = io.BytesIO(image_response.content)
        
        # Upload to LinkedIn
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(upload_url, headers=headers, data=image_data)
        response.raise_for_status()
        return response

    def create_share(self, text, asset_urn=None, title=None, description=None):
        """Create a share with or without image"""
        endpoint = f"{self.base_url}/ugcPosts"
        
        # Base share content
        share_content = {
            "shareCommentary": {
                "text": text
            },
            "shareMediaCategory": "IMAGE" if asset_urn else "NONE"  # Set category based on whether we have an image
        }
        
        # Add media content if image upload was successful
        if asset_urn:
            share_content["media"] = [
                {
                    "status": "READY",
                    "description": {
                        "text": description or ""
                    },
                    "media": asset_urn,
                    "title": {
                        "text": title or ""
                    }
                }
            ]
        
        data = {
            "author": self.person_urn,
            "lifecycleState": "DRAFT",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": share_content
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        # response.raise_for_status()
        # return response.json()
        return response

def share_festival_content_on_linkedin(access_token, person_urn, festival_name, share_text, image_title=None, image_description=None, base_url="http://127.0.0.1:5000"):
    """
    Main function to handle LinkedIn sharing process with fallback to text-only post
    """
    linkedin = LinkedInImageShare(access_token, person_urn)
    
    try:
        # Try to process image first
        image_url = f"{base_url}/image/{festival_name}"
        
        try:
            # Step 1: Register the upload
            register_response = linkedin.register_upload()
            upload_url = register_response['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_response['value']['asset']
            
            # Step 2: Upload the image from MongoDB endpoint
            linkedin.upload_image_from_url(image_url, upload_url)
            
            # Step 3: Create the share with image
            response = linkedin.create_share(
                text=share_text,
                asset_urn=asset_urn,
                title=image_title,
                description=image_description
            )
            
            print("Successfully shared post with image!")
            return response
            
        except requests.exceptions.RequestException as img_error:
            print(f"Warning: Failed to process image: {str(img_error)}")
            print("Falling back to text-only post...")
            
            # Fallback to text-only post
            response = linkedin.create_share(text=share_text)
            print("Successfully shared text-only post!")
            return response
            
    except requests.exceptions.RequestException as e:
        error_message = f"Error sharing content: {str(e)}"
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            error_message += f"\nResponse: {e.response.text}"
        raise Exception(error_message)

# Example usage
if __name__ == "__main__":
    # Configuration
    ACCESS_TOKEN = "AQXUZTFCZdsJH0D8FIOLhQdOkzhcASjcqZQzCi-py2ZyYc370XoOwTz2i5j0tFLQofj4NHF6-e3Ru4fxh4dseKj7pAIkB8UA7mfzP06DTglOFtTFN_0Pv17gTbDV63AFcW5k-xuDNqsC_YSXUHf-QRQuJudUhSL3rtjW8glMDZICYs0aio0rWW17Y5Jsy0825uGp17mf0oGyjLjgr1pOVwKtCzyHnwm7cFejkfSFbDIS3IFYpYNZIbuf9XDgkeYDjHcDKMwDpCXkgY1EFi42Bc_UBVH2V_0qY7CukItnKUXi8KCikCKNej1p5alOzkUCPaCQmScsA7Rf49A24Vis7E0dsEnDHA"
    PERSON_URN = "urn:li:person:4H457_TtZK"
    FESTIVAL_NAME = "Vasant Panchami"
    SHARE_TEXT = "Celebrating Vasant Panchami! #Festival #Celebration"
    IMAGE_TITLE = "Vasant Panchami Celebration"
    IMAGE_DESCRIPTION = "Beautiful festivities of Vasant Panchami"
    BASE_URL = "http://127.0.0.1:5000"  # Change this to your actual server URL
    
    try:
        response = share_festival_content_on_linkedin(
            access_token=ACCESS_TOKEN,
            person_urn=PERSON_URN,
            festival_name=FESTIVAL_NAME,
            share_text=SHARE_TEXT,
            # image_title=IMAGE_TITLE,
            # image_description=IMAGE_DESCRIPTION,
            base_url=BASE_URL
        )
        print("Successfully shared the festival image!")
        print("Response:", json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error sharing festival image: {e}")