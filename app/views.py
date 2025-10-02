import logging
import json

from flask import Blueprint, request, jsonify, current_app

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)
from .whatsapp_client import WhatsAppClient
from .webhook_handler import WebhookHandler

webhook_blueprint = Blueprint("webhook", __name__)


def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    logging.info(f"Received webhook payload: {json.dumps(body, indent=2) if body else 'None'}")

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            # Use the new WebhookHandler for comprehensive message processing
            WebhookHandler.process_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


# Required webhook verifictaion for WhatsApp
def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    # Enhanced logging for debugging
    logging.info(f"Webhook verification attempt:")
    logging.info(f"  Mode: {mode}")
    logging.info(f"  Token received: {token}")
    logging.info(f"  Challenge: {challenge}")
    logging.info(f"  Expected token: {current_app.config.get('VERIFY_TOKEN', 'NOT_SET')}")
    
    # Check if a token and mode were sent
    if mode and token:
        expected_token = current_app.config.get("VERIFY_TOKEN")
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == expected_token:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED - Success!")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.error(f"VERIFICATION_FAILED - Token mismatch. Expected: {expected_token}, Got: {token}")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.error("MISSING_PARAMETER - Mode or token not provided")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()

@webhook_blueprint.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "whatsapp-bot"}), 200

@webhook_blueprint.route("/debug", methods=["GET"])
def debug_info():
    """Debug endpoint to check configuration"""
    return jsonify({
        "status": "running",
        "verify_token": current_app.config.get("VERIFY_TOKEN", "NOT_SET"),
        "phone_number_id": current_app.config.get("PHONE_NUMBER_ID", "NOT_SET"),
        "access_token_set": bool(current_app.config.get("ACCESS_TOKEN")),
        "app_id": current_app.config.get("APP_ID", "NOT_SET")
    }), 200


