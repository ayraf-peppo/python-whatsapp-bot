import logging
import os
from typing import Optional, Dict, Any
from ..whatsapp_client import WhatsAppClient


class MediaService:
    """
    Service for handling media file operations and sending sample media files.
    Manages the sample media files and their upload/sending process.
    """
    
    # Sample media file mappings - using reliable public URLs
    SAMPLE_MEDIA_FILES = {
        "image": {
            "url": "https://picsum.photos/500/400.jpg",
            "mime_type": "image/jpeg",
            "caption": "📸 Here's a sample image from your WhatsApp bot!"
        },
        "video": {
            "url": "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
            "mime_type": "video/mp4",
            "caption": "🎬 Here's a sample video from your WhatsApp bot!"
        },
        "audio": {
            "url": "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
            "mime_type": "audio/mpeg",
            "caption": None  # Audio messages don't support captions
        },
        "document": {
            "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "mime_type": "application/pdf",
            "filename": "sample-document.pdf",
            "caption": "📄 Here's a sample document from your WhatsApp bot!"
        }
    }
    
    @staticmethod
    def send_sample_media(media_type: str, recipient: str) -> Dict[str, Any]:
        """
        Send a sample media file to the specified recipient using public URLs.
        
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
            media_url = media_config["url"]
            
            logging.info(f"Sending sample {media_type} from URL: {media_url}")
            
            # Send the media directly using URL
            response = MediaService._send_media_by_url(
                media_type, recipient, media_url, media_config
            )
            
            logging.info(f"Successfully sent sample {media_type} to {recipient}")
            
            return {
                "success": True,
                "media_type": media_type,
                "media_url": media_url,
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
    def _send_media_by_url(media_type: str, recipient: str, media_url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send media using public URLs with the appropriate WhatsAppClient method.
        
        Args:
            media_type: Type of media ('image', 'video', 'audio', 'document')
            recipient: WhatsApp ID of the recipient
            media_url: Public URL of the media file
            config: Media configuration dictionary
            
        Returns:
            API response from WhatsApp
        """
        if media_type == "image":
            return WhatsAppClient.send_image(
                to=recipient,
                image_url=media_url,
                caption=config.get("caption", "")
            )
        
        elif media_type == "video":
            return WhatsAppClient.send_video(
                to=recipient,
                video_url=media_url,
                caption=config.get("caption", "")
            )
        
        elif media_type == "audio":
            return WhatsAppClient.send_audio(
                to=recipient,
                audio_url=media_url
            )
        
        elif media_type == "document":
            return WhatsAppClient.send_document(
                to=recipient,
                document_url=media_url,
                filename=config.get("filename"),
                caption=config.get("caption", "")
            )
        
        else:
            raise ValueError(f"Unsupported media type: {media_type}")
    
    @staticmethod
    def _send_media_by_type(media_type: str, recipient: str, media_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send media using the appropriate WhatsAppClient method based on media type.
        (Legacy method for uploaded media IDs)
        
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
        Get information about a sample media URL.
        
        Args:
            media_type: Type of media to get info for
            
        Returns:
            Dictionary with media URL information or None if not found
        """
        if media_type not in MediaService.SAMPLE_MEDIA_FILES:
            return None
        
        config = MediaService.SAMPLE_MEDIA_FILES[media_type].copy()
        media_url = config["url"]
        
        # For URLs, we assume they're accessible (no local file check needed)
        config["accessible"] = True
        config["source"] = "public_url"
        
        return config
    
    @staticmethod
    def list_available_sample_media() -> Dict[str, Dict[str, Any]]:
        """
        List all available sample media URLs with their information.
        
        Returns:
            Dictionary mapping media types to their information
        """
        available_media = {}
        
        for media_type in MediaService.SAMPLE_MEDIA_FILES:
            info = MediaService.get_sample_media_info(media_type)
            if info and info.get("accessible", False):
                available_media[media_type] = info
        
        return available_media
    
    @staticmethod
    def validate_sample_media_urls() -> Dict[str, bool]:
        """
        Validate that all sample media URLs are accessible.
        
        Returns:
            Dictionary mapping media types to their accessibility status
        """
        import requests
        validation_results = {}
        
        for media_type, config in MediaService.SAMPLE_MEDIA_FILES.items():
            media_url = config["url"]
            
            try:
                # Make a HEAD request to check if URL is accessible
                response = requests.head(media_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    validation_results[media_type] = True
                    logging.info(f"Sample {media_type} URL is accessible: {media_url}")
                else:
                    validation_results[media_type] = False
                    logging.warning(f"Sample {media_type} URL returned {response.status_code}: {media_url}")
            except Exception as e:
                logging.warning(f"Sample {media_type} URL not accessible: {e}")
                validation_results[media_type] = False
        
        return validation_results
    
    @staticmethod
    def validate_sample_media_files() -> Dict[str, bool]:
        """
        Legacy method - now redirects to URL validation.
        
        Returns:
            Dictionary mapping media types to their availability status
        """
        return MediaService.validate_sample_media_urls()