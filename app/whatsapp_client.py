import logging
import requests
from requests.exceptions import RequestException
import os
import json
from flask import current_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Helper function to get config values
def _get_config_value(key: str, default=None):
    """Get configuration value from Flask app context or environment variables."""
    try:
        # Try to get from Flask app config first
        if current_app:
            return current_app.config.get(key, os.getenv(key, default))
    except RuntimeError:
        # If no app context, fall back to environment variables
        pass
    return os.getenv(key, default)

def _get_api_url():
    """Get the API URL with proper version."""
    version = _get_config_value("VERSION", "v21.0")
    return f"https://graph.facebook.com/{version}"


class WhatsAppClient:
    """WhatsApp Business API client (Contributor 1)"""

    @staticmethod
    def send_image(to: str, image_url: str = None, image_id: str = None, caption: str = "") -> dict:
        """
        Send an image message

        Args:
            to: Recipient's phone number
            image_url: Public URL of the image (or use image_id)
            image_id: Media ID from WhatsApp upload (or use image_url)
            caption: Optional caption for the image

        Returns:
            API response dict
        """
        api_url = _get_api_url()
        phone_number_id = _get_config_value("PHONE_NUMBER_ID")
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        image_data = {}
        if image_url:
            image_data["link"] = image_url
        elif image_id:
            image_data["id"] = image_id
        else:
            raise ValueError("Either image_url or image_id must be provided")

        if caption:
            image_data["caption"] = caption

        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": image_data,
        }

        try:
            logging.info(f"Sending image request to WhatsApp API:")
            logging.info(f"URL: {url}")
            logging.info(f"Data: {json.dumps(data, indent=2)}")
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logging.info(f"WhatsApp API Response: {json.dumps(result, indent=2)}")
            
            return result
        except RequestException as e:
            logging.error(f"Failed to send image: {e}")
            if hasattr(e, 'response') and e.response:
                logging.error(f"Response content: {e.response.text}")
            raise

    @staticmethod
    def send_audio(to: str, audio_url: str = None, audio_id: str = None) -> dict:
        """
        Send an audio message

        Args:
            to: Recipient's phone number
            audio_url: Public URL of the audio file (or use audio_id)
            audio_id: Media ID from WhatsApp upload (or use audio_url)

        Returns:
            API response dict
        """
        api_url = _get_api_url()
        phone_number_id = _get_config_value("PHONE_NUMBER_ID")
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        audio_data = {}
        if audio_url:
            audio_data["link"] = audio_url
        elif audio_id:
            audio_data["id"] = audio_id
        else:
            raise ValueError("Either audio_url or audio_id must be provided")

        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": audio_data,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logging.error(f"Failed to send audio: {e}")
            raise

    @staticmethod
    def send_video(to: str, video_url: str = None, video_id: str = None, caption: str = "") -> dict:
        """
        Send a video message

        Args:
            to: Recipient's phone number
            video_url: Public URL of the video (or use video_id)
            video_id: Media ID from WhatsApp upload (or use video_url)
            caption: Optional caption for the video

        Returns:
            API response dict
        """
        api_url = _get_api_url()
        phone_number_id = _get_config_value("PHONE_NUMBER_ID")
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        video_data = {}
        if video_url:
            video_data["link"] = video_url
        elif video_id:
            video_data["id"] = video_id
        else:
            raise ValueError("Either video_url or video_id must be provided")

        if caption:
            video_data["caption"] = caption

        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "video",
            "video": video_data,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logging.error(f"Failed to send video: {e}")
            raise

    @staticmethod
    def send_document(
        to: str,
        document_url: str = None,
        document_id: str = None,
        filename: str = None,
        caption: str = "",
    ) -> dict:
        """
        Send a document message

        Args:
            to: Recipient's phone number
            document_url: Public URL of the document (or use document_id)
            document_id: Media ID from WhatsApp upload (or use document_url)
            filename: Optional filename for the document
            caption: Optional caption for the document

        Returns:
            API response dict
        """
        api_url = _get_api_url()
        phone_number_id = _get_config_value("PHONE_NUMBER_ID")
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        document_data = {}
        if document_url:
            document_data["link"] = document_url
        elif document_id:
            document_data["id"] = document_id
        else:
            raise ValueError("Either document_url or document_id must be provided")

        if filename:
            document_data["filename"] = filename
        if caption:
            document_data["caption"] = caption

        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": document_data,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logging.error(f"Failed to send document: {e}")
            raise

    @staticmethod
    def upload_media(file_path: str, media_type: str) -> str:
        """
        Upload media to WhatsApp and get media ID

        Args:
            file_path: Path to the local file
            media_type: MIME type (e.g., 'image/jpeg', 'video/mp4', 'audio/mpeg')

        Returns:
            Media ID that can be used in send_* methods
        """
        api_url = _get_api_url()
        phone_number_id = _get_config_value("PHONE_NUMBER_ID")
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{phone_number_id}/media"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            with open(file_path, "rb") as file:
                files = {
                    "file": (os.path.basename(file_path), file, media_type),
                    "messaging_product": (None, "whatsapp"),
                    "type": (None, media_type),
                }
                response = requests.post(url, headers=headers, files=files, timeout=30)
                response.raise_for_status()
                data = response.json()
                return data.get("id")
        except RequestException as e:
            logging.error(f"Failed to upload media: {e}")
            raise
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise

    @staticmethod
    def get_media_url(media_id: str) -> str:
        """
        Get the download URL for a media file

        Args:
            media_id: The media ID from the webhook

        Returns:
            Download URL for the media
        """
        api_url = _get_api_url()
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{media_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("url")
        except RequestException as e:
            logging.error(f"Failed to get media URL: {e}")
            raise

    @staticmethod
    def download_media(media_url: str) -> bytes:
        """
        Download media content from WhatsApp

        Args:
            media_url: The download URL obtained from get_media_url()

        Returns:
            Media content as bytes
        """
        access_token = _get_config_value("ACCESS_TOKEN")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(media_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.content
        except RequestException as e:
            logging.error(f"Failed to download media: {e}")
            raise

    @staticmethod
    def mark_as_read(message_id: str) -> dict:
        """
        Mark a message as read

        Args:
            message_id: The message ID to mark as read

        Returns:
            API response dict
        """
        api_url = _get_api_url()
        phone_number_id = _get_config_value("PHONE_NUMBER_ID")
        access_token = _get_config_value("ACCESS_TOKEN")
        
        url = f"{api_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logging.error(f"Failed to mark message as read: {e}")
            raise