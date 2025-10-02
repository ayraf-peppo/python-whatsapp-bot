import logging
from flask import current_app, jsonify
import json
import requests
import os
from typing import Dict, Any, Optional, Tuple

# from app.services.openai_service import generate_response
import re



def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_response(response):
    # Return text in uppercase
    return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_type = message.get("type", "text")

    # Always mark inbound messages as read for better UX
    try:
        mark_as_read(message.get("id"))
    except Exception as e:
        logging.warning(f"Failed to mark message as read: {e}")

    if message_type == "text":
        message_body = message["text"]["body"]
        response_text = generate_response(message_body)

        # OpenAI Integration
        # response_text = generate_response(message_body, wa_id, name)
        # response_text = process_text_for_whatsapp(response_text)

        data = get_text_message_input(wa_id, response_text)
        send_message(data)
        return

    # Media handling: image, audio, video, document
    if message_type in {"image", "audio", "video", "document"}:
        media_info = message.get(message_type, {})
        media_id = media_info.get("id")
        caption = media_info.get("caption", "")

        try:
            if not media_id:
                raise ValueError("Missing media id in incoming message")
            media_url = MediaHandler._get_media_url(media_id)
            media_bytes = MediaHandler._download_media_content(media_url)
            logging.info(
                f"Received {message_type} from {wa_id}: id={media_id}, url={media_url}, size={len(media_bytes)} bytes"
            )
        except Exception as e:
            logging.error(f"Failed to fetch incoming media: {e}")
            send_text_message(wa_id, "Sorry, I couldn't fetch your media.")
            return

        # Simple acknowledgment reply (echo caption if present)
        ack = f"Got your {message_type}!" + (f" Caption: {caption}" if caption else "")
        try:
            send_text_message(wa_id, ack)
        except Exception as e:
            logging.error(f"Failed to send ack for media: {e}")
        return

    # Fallback for unsupported types
    logging.info(f"Received unsupported message type: {message_type}")
    try:
        send_text_message(wa_id, f"Unsupported message type: {message_type}")
    except Exception as e:
        logging.error(f"Failed to send unsupported type notice: {e}")


def send_text_message(recipient: str, text: str):
    """Send a text message to a WhatsApp user."""
    data = get_text_message_input(recipient, text)
    return send_message(data)


def mark_as_read(message_id: str):
    """Mark a message as read."""
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
    
    data = json.dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    })
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"Failed to mark message as read: {e}")
        raise

class MediaHandler:
    """
    Utility class for processing incoming media from WhatsApp webhooks.
    Handles media download, processing, and file management.
    """
    
    # MIME type to file extension mapping
    MIME_TO_EXTENSION = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'audio/mpeg': '.mp3',
        'audio/mp4': '.m4a',
        'audio/amr': '.amr',
        'audio/ogg': '.ogg',
        'video/mp4': '.mp4',
        'video/3gpp': '.3gp',
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'text/plain': '.txt',
    }
    
    @staticmethod
    def extract_media_info(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract media information from a WhatsApp webhook message.
        
        Args:
            message: The message object from the webhook
            
        Returns:
            Dictionary containing media info or None if no media found
        """
        message_type = message.get("type")
        
        if message_type not in {"image", "audio", "video", "document"}:
            return None
            
        media_data = message.get(message_type, {})
        
        return {
            "type": message_type,
            "id": media_data.get("id"),
            "mime_type": media_data.get("mime_type"),
            "sha256": media_data.get("sha256"),
            "file_size": media_data.get("file_size"),
            "caption": media_data.get("caption", ""),
            "filename": media_data.get("filename") if message_type == "document" else None
        }
    
    @staticmethod
    def process_incoming_media(media_info: Dict[str, Any], save_directory: str = "data/media") -> Tuple[str, bytes]:
        """
        Download and save incoming media from WhatsApp.
        
        Args:
            media_info: Media information dictionary from extract_media_info
            save_directory: Directory to save the media files
            
        Returns:
            Tuple of (file_path, media_bytes)
        """
        if not media_info or not media_info.get("id"):
            raise ValueError("Invalid media info provided")
            
        media_id = media_info["id"]
        media_type = media_info["type"]
        mime_type = media_info.get("mime_type", "")
        
        try:
            # Get media URL from WhatsApp API
            media_url = MediaHandler._get_media_url(media_id)
            
            # Download media content
            media_bytes = MediaHandler._download_media_content(media_url)
            
            # Generate filename
            filename = MediaHandler._generate_filename(media_info)
            
            # Ensure save directory exists
            os.makedirs(save_directory, exist_ok=True)
            
            # Save file
            file_path = os.path.join(save_directory, filename)
            with open(file_path, 'wb') as f:
                f.write(media_bytes)
                
            logging.info(f"Saved {media_type} media: {file_path} ({len(media_bytes)} bytes)")
            
            return file_path, media_bytes
            
        except Exception as e:
            logging.error(f"Failed to process incoming media {media_id}: {e}")
            raise
    
    @staticmethod
    def _get_media_url(media_id: str) -> str:
        """Get media download URL from WhatsApp API."""
        url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{media_id}"
        headers = {
            "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("url")
        except requests.RequestException as e:
            logging.error(f"Failed to get media URL for {media_id}: {e}")
            raise
    
    @staticmethod
    def _download_media_content(media_url: str) -> bytes:
        """Download media content from WhatsApp CDN."""
        headers = {
            "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        }
        
        try:
            response = requests.get(media_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logging.error(f"Failed to download media from {media_url}: {e}")
            raise
    
    @staticmethod
    def _generate_filename(media_info: Dict[str, Any]) -> str:
        """Generate a filename for the media file."""
        media_type = media_info["type"]
        media_id = media_info["id"]
        mime_type = media_info.get("mime_type", "")
        original_filename = media_info.get("filename")
        
        # Use original filename if available (for documents)
        if original_filename and media_type == "document":
            return f"{media_id}_{original_filename}"
        
        # Generate extension from MIME type
        extension = MediaHandler.MIME_TO_EXTENSION.get(mime_type, "")
        if not extension:
            # Fallback extensions based on media type
            fallback_extensions = {
                "image": ".jpg",
                "audio": ".mp3", 
                "video": ".mp4",
                "document": ".pdf"
            }
            extension = fallback_extensions.get(media_type, ".bin")
        
        return f"{media_id}_{media_type}{extension}"
    
    @staticmethod
    def get_message_content(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive message content parser for all message types.
        
        Args:
            message: The message object from webhook
            
        Returns:
            Dictionary with parsed message content
        """
        message_type = message.get("type", "unknown")
        content = {
            "type": message_type,
            "timestamp": message.get("timestamp"),
            "message_id": message.get("id")
        }
        
        if message_type == "text":
            content["text"] = message.get("text", {}).get("body", "")
            
        elif message_type in {"image", "audio", "video", "document"}:
            media_info = MediaHandler.extract_media_info(message)
            content["media"] = media_info
            
        elif message_type == "location":
            location_data = message.get("location", {})
            content["location"] = {
                "latitude": location_data.get("latitude"),
                "longitude": location_data.get("longitude"),
                "name": location_data.get("name"),
                "address": location_data.get("address")
            }
            
        elif message_type == "interactive":
            interactive_data = message.get("interactive", {})
            content["interactive"] = {
                "type": interactive_data.get("type"),
                "button_reply": interactive_data.get("button_reply"),
                "list_reply": interactive_data.get("list_reply")
            }
            
        elif message_type == "contacts":
            content["contacts"] = message.get("contacts", [])
            
        else:
            content["raw"] = message
            
        return content


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

