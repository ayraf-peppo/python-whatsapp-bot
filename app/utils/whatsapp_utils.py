import logging
from flask import current_app, jsonify
import json
import requests

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
            media_url = get_media_url(media_id)
            media_bytes = download_media(media_url)
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

