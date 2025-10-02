import logging
import os
from typing import Optional, Dict, Any
from ..whatsapp_client import WhatsAppClient


class MediaService:
    """
    Service for handling media file operations and sending sample media files.
    Manages the sample media files and their upload/sending process.
    """
    
    # Sample media file mappings
    SAMPLE_MEDIA_FILES = {
        "image": {
            "path": "data/media/1497313627961580_image.jpg",
            "mime_type": "image/jpeg",
            "caption": "📸 Here's a sample image from your WhatsApp bot!"
        },
        "video": {
            "path": "data/media/2255528285309786_video.mp4", 
            "mime_type": "video/mp4",
            "caption": "🎬 Here's a sample video from your WhatsApp bot!"
        },
        "audio": {
            "path": "data/media/story.mp3",
            "mime_type": "audio/mpeg",
            "caption": None  # Audio messages don't support captions
        },
        "document": {
            "path": "data/media/698555082545397_airbnb-faq.pdf",
            "mime_type": "application/pdf",
            "filename": "airbnb-faq.pdf",
            "caption": "📄 Here's a sample document from your WhatsApp bot!"
        }
    }
    
    @staticmethod
    def send_sample_media(media_type: str, recipient: str) -> Dict[str, Any]:
        """
        Send a sample media file to the specified recipient.
        
        Args:
            media_type: Type of media to send ('image', 'video', 'audio', 'document')
            recipient: WhatsApp ID of the recipient
            
        Returns:
            Dictionary with success status and details
        """
        try:
            if media_type not in MediaService.SAMPLE_MEDIA_FILES:
                raise ValueError(f"Unsupported media type: {media_type}")
            
            media_config = MediaService.SAMPLE_MEDIA_FILES[media_type]
            file_path = media_config["path"]
            
            # Check if file exists
            if not os.path.exists(file_path):
                logging.error(f"Sample {media_type} file not found: {file_path}")
                return {
                    "success": False,
                    "error": f"Sample {media_type} file not found",
                    "file_path": file_path
                }
            
            # Upload media to WhatsApp and get media ID
            logging.info(f"Uploading sample {media_type}: {file_path}")
            media_id = WhatsAppClient.upload_media(file_path, media_config["mime_type"])
            
            if not media_id:
                raise Exception("Failed to get media ID from upload")
            
            # Send the media using appropriate method
            response = MediaService._send_media_by_type(
                media_type, recipient, media_id, media_config
            )
            
            logging.info(f"Successfully sent sample {media_type} to {recipient}")
            
            return {
                "success": True,
                "media_type": media_type,
                "media_id": media_id,
                "file_path": file_path,
                "response": response
            }
            
        except Exception as e:
            logging.error(f"Failed to send sample {media_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "media_type": media_type
            }
    
    @staticmethod
    def _send_media_by_type(media_type: str, recipient: str, media_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send media using the appropriate WhatsAppClient method based on media type.
        
        Args:
            media_type: Type of media ('image', 'video', 'audio', 'document')
            recipient: WhatsApp ID of the recipient
            media_id: Media ID from WhatsApp upload
            config: Media configuration dictionary
            
        Returns:
            API response from WhatsApp
        """
        if media_type == "image":
            return WhatsAppClient.send_image(
                to=recipient,
                image_id=media_id,
                caption=config.get("caption", "")
            )
        
        elif media_type == "video":
            return WhatsAppClient.send_video(
                to=recipient,
                video_id=media_id,
                caption=config.get("caption", "")
            )
        
        elif media_type == "audio":
            return WhatsAppClient.send_audio(
                to=recipient,
                audio_id=media_id
            )
        
        elif media_type == "document":
            return WhatsAppClient.send_document(
                to=recipient,
                document_id=media_id,
                filename=config.get("filename"),
                caption=config.get("caption", "")
            )
        
        else:
            raise ValueError(f"Unsupported media type: {media_type}")
    
    @staticmethod
    def get_sample_media_info(media_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a sample media file.
        
        Args:
            media_type: Type of media to get info for
            
        Returns:
            Dictionary with media file information or None if not found
        """
        if media_type not in MediaService.SAMPLE_MEDIA_FILES:
            return None
        
        config = MediaService.SAMPLE_MEDIA_FILES[media_type].copy()
        file_path = config["path"]
        
        # Add file size if file exists
        if os.path.exists(file_path):
            config["file_size"] = os.path.getsize(file_path)
            config["exists"] = True
        else:
            config["exists"] = False
        
        return config
    
    @staticmethod
    def list_available_sample_media() -> Dict[str, Dict[str, Any]]:
        """
        List all available sample media files with their information.
        
        Returns:
            Dictionary mapping media types to their information
        """
        available_media = {}
        
        for media_type in MediaService.SAMPLE_MEDIA_FILES:
            info = MediaService.get_sample_media_info(media_type)
            if info and info.get("exists", False):
                available_media[media_type] = info
        
        return available_media
    
    @staticmethod
    def validate_sample_media_files() -> Dict[str, bool]:
        """
        Validate that all sample media files exist and are accessible.
        
        Returns:
            Dictionary mapping media types to their availability status
        """
        validation_results = {}
        
        for media_type, config in MediaService.SAMPLE_MEDIA_FILES.items():
            file_path = config["path"]
            exists = os.path.exists(file_path)
            
            if exists:
                try:
                    # Try to read a small portion to ensure file is accessible
                    with open(file_path, 'rb') as f:
                        f.read(1024)  # Read first 1KB
                    validation_results[media_type] = True
                except Exception as e:
                    logging.warning(f"Sample {media_type} file exists but not readable: {e}")
                    validation_results[media_type] = False
            else:
                logging.warning(f"Sample {media_type} file not found: {file_path}")
                validation_results[media_type] = False
        
        return validation_results