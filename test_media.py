#!/usr/bin/env python3
"""
WhatsApp Media Feature Testing Script

This script provides manual testing utilities for the WhatsApp bot's media handling capabilities.
It includes functions to test media processing, webhook simulation, and integration testing.

Usage:
    python test_media.py [test_type]
    
Test types:
    - media_handler: Test MediaHandler utility functions
    - webhook_sim: Simulate webhook payloads
    - integration: Full integration test
    - all: Run all tests
"""

import json
import os
import sys
import logging
from typing import Dict, Any
from unittest.mock import Mock, patch

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.utils.whatsapp_utils import MediaHandler
    from app.webhook_handler import WebhookHandler
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MediaTester:
    """Test suite for WhatsApp media functionality."""
    
    def __init__(self):
        self.test_results = []
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        print(f"\n🧪 Running test: {test_name}")
        try:
            test_func()
            print(f"✅ {test_name} - PASSED")
            self.test_results.append((test_name, "PASSED", None))
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
            self.test_results.append((test_name, "FAILED", str(e)))
    
    def test_media_handler_extract_info(self):
        """Test MediaHandler.extract_media_info()"""
        # Test image message
        image_message = {
            "type": "image",
            "image": {
                "id": "test_image_123",
                "mime_type": "image/jpeg",
                "sha256": "abc123",
                "file_size": 1024,
                "caption": "Test image"
            }
        }
        
        result = MediaHandler.extract_media_info(image_message)
        assert result is not None
        assert result["type"] == "image"
        assert result["id"] == "test_image_123"
        assert result["caption"] == "Test image"
        
        # Test non-media message
        text_message = {"type": "text", "text": {"body": "Hello"}}
        result = MediaHandler.extract_media_info(text_message)
        assert result is None
        
        print("   ✓ extract_media_info works correctly")
    
    def test_media_handler_filename_generation(self):
        """Test MediaHandler._generate_filename()"""
        media_info = {
            "type": "image",
            "id": "test123",
            "mime_type": "image/jpeg"
        }
        
        filename = MediaHandler._generate_filename(media_info)
        assert filename == "test123_image.jpg"
        
        # Test document with original filename
        doc_info = {
            "type": "document",
            "id": "doc456",
            "mime_type": "application/pdf",
            "filename": "report.pdf"
        }
        
        filename = MediaHandler._generate_filename(doc_info)
        assert filename == "doc456_report.pdf"
        
        print("   ✓ filename generation works correctly")
    
    def test_message_content_parser(self):
        """Test MediaHandler.get_message_content()"""
        # Test text message
        text_msg = {
            "type": "text",
            "id": "msg123",
            "timestamp": "1234567890",
            "text": {"body": "Hello world"}
        }
        
        content = MediaHandler.get_message_content(text_msg)
        assert content["type"] == "text"
        assert content["text"] == "Hello world"
        
        # Test location message
        location_msg = {
            "type": "location",
            "id": "loc456",
            "timestamp": "1234567890",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "name": "San Francisco",
                "address": "San Francisco, CA"
            }
        }
        
        content = MediaHandler.get_message_content(location_msg)
        assert content["type"] == "location"
        assert content["location"]["latitude"] == 37.7749
        assert content["location"]["name"] == "San Francisco"
        
        print("   ✓ message content parser works correctly")
    
    def test_webhook_simulation(self):
        """Test webhook payload processing"""
        # Sample webhook payload for image message
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "ENTRY_ID",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15550559999",
                            "phone_number_id": "PHONE_NUMBER_ID"
                        },
                        "contacts": [{
                            "profile": {"name": "Test User"},
                            "wa_id": "15551234567"
                        }],
                        "messages": [{
                            "from": "15551234567",
                            "id": "wamid.test123",
                            "timestamp": "1234567890",
                            "type": "image",
                            "image": {
                                "id": "media123",
                                "mime_type": "image/jpeg",
                                "sha256": "abc123def456",
                                "file_size": 2048,
                                "caption": "Test image from webhook"
                            }
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        # Mock the external API calls
        with patch('app.utils.whatsapp_utils.mark_as_read'), \
             patch('app.utils.whatsapp_utils.send_text_message') as mock_send, \
             patch.object(MediaHandler, 'process_incoming_media') as mock_process:
            
            mock_process.return_value = ("/tmp/test_image.jpg", b"fake_image_data")
            
            # This would normally make API calls, but we're mocking them
            WebhookHandler.process_whatsapp_message(webhook_payload)
            
            # Verify that send_text_message was called
            assert mock_send.called
            
        print("   ✓ webhook simulation works correctly")
    
    def test_mime_type_mapping(self):
        """Test MIME type to extension mapping"""
        test_cases = [
            ("image/jpeg", ".jpg"),
            ("image/png", ".png"),
            ("audio/mpeg", ".mp3"),
            ("video/mp4", ".mp4"),
            ("application/pdf", ".pdf"),
            ("text/plain", ".txt")
        ]
        
        for mime_type, expected_ext in test_cases:
            actual_ext = MediaHandler.MIME_TO_EXTENSION.get(mime_type)
            assert actual_ext == expected_ext, f"Expected {expected_ext} for {mime_type}, got {actual_ext}"
        
        print("   ✓ MIME type mapping is correct")
    
    def run_all_tests(self):
        """Run all available tests."""
        print("🚀 Starting WhatsApp Media Feature Tests")
        print("=" * 50)
        
        self.run_test("MediaHandler Extract Info", self.test_media_handler_extract_info)
        self.run_test("MediaHandler Filename Generation", self.test_media_handler_filename_generation)
        self.run_test("Message Content Parser", self.test_message_content_parser)
        self.run_test("Webhook Simulation", self.test_webhook_simulation)
        self.run_test("MIME Type Mapping", self.test_mime_type_mapping)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAILED")
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if failed > 0:
            print("\n🔍 Failed Tests:")
            for name, status, error in self.test_results:
                if status == "FAILED":
                    print(f"   • {name}: {error}")
        
        return failed == 0


def create_sample_webhook_payloads():
    """Create sample webhook payloads for manual testing."""
    payloads = {
        "text_message": {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Test User"}, "wa_id": "1234567890"}],
                        "messages": [{
                            "id": "msg_text_123",
                            "type": "text",
                            "timestamp": "1234567890",
                            "text": {"body": "Hello, this is a test message!"}
                        }]
                    }
                }]
            }]
        },
        "image_message": {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Test User"}, "wa_id": "1234567890"}],
                        "messages": [{
                            "id": "msg_img_456",
                            "type": "image",
                            "timestamp": "1234567890",
                            "image": {
                                "id": "media_img_789",
                                "mime_type": "image/jpeg",
                                "sha256": "abc123def456",
                                "file_size": 2048,
                                "caption": "Sample image for testing"
                            }
                        }]
                    }
                }]
            }]
        },
        "location_message": {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Test User"}, "wa_id": "1234567890"}],
                        "messages": [{
                            "id": "msg_loc_789",
                            "type": "location",
                            "timestamp": "1234567890",
                            "location": {
                                "latitude": 37.7749,
                                "longitude": -122.4194,
                                "name": "San Francisco",
                                "address": "San Francisco, CA, USA"
                            }
                        }]
                    }
                }]
            }]
        }
    }
    
    return payloads


def main():
    """Main function to run tests based on command line arguments."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"
    
    tester = MediaTester()
    
    if test_type == "media_handler":
        tester.run_test("MediaHandler Extract Info", tester.test_media_handler_extract_info)
        tester.run_test("MediaHandler Filename Generation", tester.test_media_handler_filename_generation)
        tester.run_test("Message Content Parser", tester.test_message_content_parser)
        tester.run_test("MIME Type Mapping", tester.test_mime_type_mapping)
    
    elif test_type == "webhook_sim":
        tester.run_test("Webhook Simulation", tester.test_webhook_simulation)
        
        print("\n📋 Sample Webhook Payloads:")
        payloads = create_sample_webhook_payloads()
        for name, payload in payloads.items():
            print(f"\n{name.upper()}:")
            print(json.dumps(payload, indent=2))
    
    elif test_type == "integration":
        print("🔗 Integration Test - This would test with real WhatsApp API")
        print("⚠️  Note: Requires valid ACCESS_TOKEN and PHONE_NUMBER_ID in environment")
        # Integration tests would go here
    
    elif test_type == "all":
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown test type: {test_type}")
        print("Available types: media_handler, webhook_sim, integration, all")
        sys.exit(1)


if __name__ == "__main__":
    main()