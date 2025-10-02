import logging
from typing import Dict, Any
from .utils.whatsapp_utils import MediaHandler, send_text_message, mark_as_read
from .services.media_service import MediaService


class WebhookHandler:
    """
    Handles incoming WhatsApp webhook messages and processes different message types.
    """
    
    @staticmethod
    def process_whatsapp_message(body: Dict[str, Any]) -> None:
        """
        Main message processor that routes different message types to appropriate handlers.
        
        Args:
            body: The webhook payload from WhatsApp
        """
        try:
            # Extract basic message info
            wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
            name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            message_type = message.get("type", "text")
            message_id = message.get("id")
            
            # Always mark inbound messages as read for better UX
            try:
                mark_as_read(message_id)
            except Exception as e:
                logging.warning(f"Failed to mark message as read: {e}")
            
            # Route to appropriate handler based on message type
            if message_type == "text":
                WebhookHandler.handle_text_message(wa_id, name, message)
            elif message_type in {"image", "audio", "video", "document"}:
                WebhookHandler.handle_media_message(wa_id, name, message)
            elif message_type == "location":
                WebhookHandler.handle_location_message(wa_id, name, message)
            elif message_type == "interactive":
                WebhookHandler.handle_interactive_message(wa_id, name, message)
            else:
                WebhookHandler.handle_unsupported_message(wa_id, name, message)
                
        except Exception as e:
            logging.error(f"Error processing WhatsApp message: {e}")
            # Try to send error message to user if possible
            try:
                if 'wa_id' in locals():
                    send_text_message(wa_id, "Sorry, I encountered an error processing your message.")
            except:
                pass  # Don't let error handling cause more errors
    
    @staticmethod
    def handle_text_message(wa_id: str, name: str, message: Dict[str, Any]) -> None:
        """
        Handle incoming text messages.
        
        Args:
            wa_id: WhatsApp ID of the sender
            name: Name of the sender
            message: The message object
        """
        message_body = message.get("text", {}).get("body", "").strip().lower()
        
        logging.info(f"Received text message from {name} ({wa_id}): {message_body}")
        
        # Simple command recognition for demo purposes
        if message_body == "hello" or message_body == "hi":
            response = f"Hello {name}! 👋 How can I help you today?"
        elif message_body == "help":
            response = """🤖 Available commands:
• hello - Get a greeting
• help - Show this help message
• send image - Get a sample image
• send audio - Get a sample audio
• send video - Get a sample video
• send document - Get a sample document
• Just send me any media and I'll process it!"""
        elif message_body == "send image":
            WebhookHandler._handle_media_command(wa_id, name, "image")
            return  # Don't send text response, media will be sent instead
        elif message_body == "send audio":
            WebhookHandler._handle_media_command(wa_id, name, "audio")
            return  # Don't send text response, media will be sent instead
        elif message_body == "send video":
            WebhookHandler._handle_media_command(wa_id, name, "video")
            return  # Don't send text response, media will be sent instead
        elif message_body == "send document" or message_body == "send doc":
            WebhookHandler._handle_media_command(wa_id, name, "document")
            return  # Don't send text response, media will be sent instead
        else:
            # Echo the message in uppercase (simple demo behavior)
            response = f"You said: {message_body.upper()}"
        
        try:
            send_text_message(wa_id, response)
        except Exception as e:
            logging.error(f"Failed to send text response: {e}")
    
    @staticmethod
    def handle_media_message(wa_id: str, name: str, message: Dict[str, Any]) -> None:
        """
        Handle incoming media messages (image, audio, video, document).
        
        Args:
            wa_id: WhatsApp ID of the sender
            name: Name of the sender
            message: The message object
        """
        try:
            # Extract media information
            media_info = MediaHandler.extract_media_info(message)
            
            if not media_info:
                send_text_message(wa_id, "Sorry, I couldn't process your media.")
                return
            
            media_type = media_info["type"]
            caption = media_info.get("caption", "")
            
            logging.info(f"Received {media_type} from {name} ({wa_id})")
            
            # Process and download the media
            try:
                file_path, media_bytes = MediaHandler.process_incoming_media(media_info)
                
                # Create response message
                response_parts = [f"✅ Got your {media_type}!"]
                response_parts.append(f"📁 Saved as: {file_path}")
                response_parts.append(f"📊 Size: {len(media_bytes):,} bytes")
                
                if caption:
                    response_parts.append(f"💬 Caption: {caption}")
                
                if media_info.get("filename"):
                    response_parts.append(f"📄 Filename: {media_info['filename']}")
                
                response = "\n".join(response_parts)
                
            except Exception as e:
                logging.error(f"Failed to process media: {e}")
                response = f"❌ Sorry, I couldn't download your {media_type}. Please try again."
            
            send_text_message(wa_id, response)
            
        except Exception as e:
            logging.error(f"Error handling media message: {e}")
            send_text_message(wa_id, "Sorry, I encountered an error processing your media.")
    
    @staticmethod
    def handle_location_message(wa_id: str, name: str, message: Dict[str, Any]) -> None:
        """
        Handle incoming location messages.
        
        Args:
            wa_id: WhatsApp ID of the sender
            name: Name of the sender
            message: The message object
        """
        try:
            location_data = message.get("location", {})
            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")
            location_name = location_data.get("name", "")
            address = location_data.get("address", "")
            
            logging.info(f"Received location from {name} ({wa_id}): {latitude}, {longitude}")
            
            response_parts = ["📍 Thanks for sharing your location!"]
            response_parts.append(f"🌐 Coordinates: {latitude}, {longitude}")
            
            if location_name:
                response_parts.append(f"🏷️ Name: {location_name}")
            
            if address:
                response_parts.append(f"🏠 Address: {address}")
            
            response = "\n".join(response_parts)
            send_text_message(wa_id, response)
            
        except Exception as e:
            logging.error(f"Error handling location message: {e}")
            send_text_message(wa_id, "Sorry, I couldn't process your location.")
    
    @staticmethod
    def handle_interactive_message(wa_id: str, name: str, message: Dict[str, Any]) -> None:
        """
        Handle incoming interactive messages (button replies, list replies).
        
        Args:
            wa_id: WhatsApp ID of the sender
            name: Name of the sender
            message: The message object
        """
        try:
            interactive_data = message.get("interactive", {})
            interactive_type = interactive_data.get("type")
            
            logging.info(f"Received interactive message from {name} ({wa_id}): {interactive_type}")
            
            if interactive_type == "button_reply":
                button_reply = interactive_data.get("button_reply", {})
                button_id = button_reply.get("id")
                button_title = button_reply.get("title")
                
                response = f"🔘 You clicked: {button_title} (ID: {button_id})"
                
            elif interactive_type == "list_reply":
                list_reply = interactive_data.get("list_reply", {})
                list_id = list_reply.get("id")
                list_title = list_reply.get("title")
                list_description = list_reply.get("description", "")
                
                response_parts = [f"📋 You selected: {list_title}"]
                if list_description:
                    response_parts.append(f"📝 Description: {list_description}")
                response_parts.append(f"🆔 ID: {list_id}")
                
                response = "\n".join(response_parts)
                
            else:
                response = f"🤖 Received interactive message of type: {interactive_type}"
            
            send_text_message(wa_id, response)
            
        except Exception as e:
            logging.error(f"Error handling interactive message: {e}")
            send_text_message(wa_id, "Sorry, I couldn't process your interactive message.")
    
    @staticmethod
    def handle_unsupported_message(wa_id: str, name: str, message: Dict[str, Any]) -> None:
        """
        Handle unsupported message types.
        
        Args:
            wa_id: WhatsApp ID of the sender
            name: Name of the sender
            message: The message object
        """
        message_type = message.get("type", "unknown")
        
        logging.info(f"Received unsupported message type from {name} ({wa_id}): {message_type}")
        
        response = f"🤷‍♂️ Sorry, I don't support {message_type} messages yet. Try sending text, images, audio, video, documents, or locations!"
        
        try:
            send_text_message(wa_id, response)
        except Exception as e:
            logging.error(f"Failed to send unsupported message response: {e}")
    
    @staticmethod
    def _handle_media_command(wa_id: str, name: str, media_type: str) -> None:
        """
        Handle media sending commands (send image, send audio, send video, send document).
        
        Args:
            wa_id: WhatsApp ID of the sender
            name: Name of the sender
            media_type: Type of media to send ('image', 'audio', 'video', 'document')
        """
        try:
            logging.info(f"Processing {media_type} command from {name} ({wa_id})")
            
            # Send a quick acknowledgment
            media_emojis = {
                "image": "📸",
                "audio": "🎵", 
                "video": "🎬",
                "document": "📄"
            }
            
            emoji = media_emojis.get(media_type, "📎")
            ack_message = f"{emoji} Sending sample {media_type}... Please wait!"
            
            try:
                send_text_message(wa_id, ack_message)
            except Exception as e:
                logging.warning(f"Failed to send acknowledgment: {e}")
            
            # Send the sample media
            result = MediaService.send_sample_media(media_type, wa_id)
            
            if result["success"]:
                logging.info(f"Successfully sent sample {media_type} to {name} ({wa_id})")
                
                # Send success confirmation
                success_message = f"✅ Sample {media_type} sent successfully!"
                try:
                    send_text_message(wa_id, success_message)
                except Exception as e:
                    logging.warning(f"Failed to send success confirmation: {e}")
                    
            else:
                error_msg = result.get("error", "Unknown error")
                logging.error(f"Failed to send sample {media_type}: {error_msg}")
                
                # Send error message to user
                error_response = f"❌ Sorry, I couldn't send the sample {media_type}. Please try again later."
                try:
                    send_text_message(wa_id, error_response)
                except Exception as e:
                    logging.error(f"Failed to send error message: {e}")
                    
        except Exception as e:
            logging.error(f"Error handling {media_type} command: {e}")
            
            # Send generic error message
            try:
                send_text_message(wa_id, f"❌ Sorry, I encountered an error while processing your {media_type} request.")
            except:
                pass  # Don't let error handling cause more errors