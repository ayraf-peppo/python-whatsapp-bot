# WhatsApp Media Feature Documentation

This document provides comprehensive information about the WhatsApp bot's media handling capabilities, including setup, usage, testing, and troubleshooting.

## 🚀 Features

### Supported Media Types

- **Images**: JPEG, PNG, GIF, WebP
- **Audio**: MP3, M4A, AMR, OGG
- **Videos**: MP4, 3GP
- **Documents**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT

### Core Capabilities

1. **Automatic Media Download**: Incoming media is automatically downloaded and saved
2. **Media Processing**: Extract metadata, validate file types, and organize files
3. **Interactive Commands**: Text commands to request sample media
4. **Comprehensive Logging**: Detailed logging for debugging and monitoring
5. **Error Handling**: Graceful error handling with user-friendly messages

## 📁 File Structure

```
app/
├── utils/
│   └── whatsapp_utils.py      # MediaHandler class and utilities
├── webhook_handler.py         # Message processing and routing
├── views.py                   # Flask webhook endpoints
└── whatsapp_client.py         # WhatsApp API client (Contributor 1)

data/
└── media/                     # Downloaded media files storage

test_media.py                  # Testing script
README_MEDIA.md               # This documentation
```

## 🛠️ Setup and Configuration

### Environment Variables

Ensure these environment variables are set in your `.env` file:

```env
ACCESS_TOKEN=your_whatsapp_access_token
PHONE_NUMBER_ID=your_phone_number_id
VERSION=v21.0
VERIFY_TOKEN=your_webhook_verify_token
```

### Directory Structure

The bot automatically creates the `data/media/` directory for storing downloaded files. Ensure your application has write permissions to this location.

### Dependencies

Required Python packages (add to `requirements.txt` if not present):

```
requests>=2.25.0
flask>=2.0.0
```

## 💬 Usage Examples

### Text Commands

Send these text messages to interact with the bot:

- `hello` or `hi` - Get a greeting
- `help` - Show available commands
- `send image` - Request a sample image
- `send audio` - Request a sample audio
- `send video` - Request a sample video

### Media Messages

Simply send any supported media type to the bot:

1. **Images**: Send photos from your gallery or camera
2. **Audio**: Send voice messages or audio files
3. **Videos**: Send video files or recordings
4. **Documents**: Send PDF files, Word documents, etc.
5. **Locations**: Share your location

The bot will:

- Download and save the media
- Extract metadata (file size, MIME type, etc.)
- Respond with confirmation and file details
- Handle captions if provided

## 🧪 Testing

### Automated Testing

Run the test suite:

```bash
# Run all tests
python test_media.py all

# Run specific test categories
python test_media.py media_handler
python test_media.py webhook_sim
python test_media.py integration
```

### Manual Testing

1. **Send Test Messages**: Use WhatsApp to send various media types
2. **Check Logs**: Monitor application logs for processing details
3. **Verify Files**: Check `data/media/` directory for downloaded files
4. **Test Commands**: Try the interactive text commands

### Sample Webhook Payloads

Use the testing script to generate sample webhook payloads:

```bash
python test_media.py webhook_sim
```

## 📊 File Size Limits

WhatsApp has the following file size limits:

- **Images**: 5 MB
- **Audio**: 16 MB
- **Videos**: 16 MB
- **Documents**: 100 MB

The bot handles these limits gracefully and will inform users if files exceed limits.

## 🔧 API Integration

### MediaHandler Class

The `MediaHandler` class provides utilities for media processing:

```python
from app.utils.whatsapp_utils import MediaHandler

# Extract media info from webhook message
media_info = MediaHandler.extract_media_info(message)

# Download and save media
file_path, media_bytes = MediaHandler.process_incoming_media(media_info)

# Parse message content
content = MediaHandler.get_message_content(message)
```

### WebhookHandler Class

The `WebhookHandler` class routes and processes different message types:

```python
from app.webhook_handler import WebhookHandler

# Process incoming webhook
WebhookHandler.process_whatsapp_message(webhook_body)
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Media Download Failures

**Symptoms**: Error messages about failed media downloads

**Solutions**:

- Check ACCESS_TOKEN validity
- Verify network connectivity
- Ensure WhatsApp API quotas aren't exceeded
- Check file permissions for `data/media/` directory

#### 2. Webhook Not Receiving Messages

**Symptoms**: No webhook calls received

**Solutions**:

- Verify VERIFY_TOKEN matches WhatsApp configuration
- Check webhook URL is publicly accessible
- Ensure HTTPS is properly configured
- Verify webhook subscription is active

#### 3. File Storage Issues

**Symptoms**: Files not being saved or permission errors

**Solutions**:

- Check directory permissions: `chmod 755 data/media/`
- Ensure sufficient disk space
- Verify application has write permissions

#### 4. MIME Type Issues

**Symptoms**: Incorrect file extensions or processing errors

**Solutions**:

- Check `MIME_TO_EXTENSION` mapping in `MediaHandler`
- Add new MIME types if needed
- Verify file headers match MIME types

### Debug Mode

Enable detailed logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Analysis

Key log messages to monitor:

- `Received {media_type} from {user}` - Successful media reception
- `Saved {media_type} media: {file_path}` - Successful file save
- `Failed to process incoming media` - Processing errors
- `Failed to get media URL` - API access issues

## 🔒 Security Considerations

### File Validation

- All files are validated by MIME type
- File extensions are mapped from MIME types, not user input
- File size limits are enforced

### Storage Security

- Files are stored with generated names (not user-provided names)
- Directory traversal is prevented
- Access to stored files should be restricted

### API Security

- All API calls use proper authentication
- Webhook signatures should be validated (implement in production)
- Rate limiting should be considered for production use

## 🚀 Production Deployment

### Performance Optimization

1. **Async Processing**: Consider using background tasks for large file downloads
2. **Storage**: Use cloud storage (AWS S3, Google Cloud) for production
3. **Caching**: Implement caching for frequently accessed media
4. **CDN**: Use CDN for serving processed media

### Monitoring

1. **Metrics**: Track media processing success rates
2. **Alerts**: Set up alerts for processing failures
3. **Storage**: Monitor disk usage and cleanup old files
4. **API Limits**: Monitor WhatsApp API usage and quotas

### Scaling

1. **Horizontal Scaling**: Use load balancers for multiple instances
2. **Database**: Consider database storage for media metadata
3. **Queue System**: Use message queues for processing large volumes
4. **Microservices**: Split media processing into separate services

## 📚 Additional Resources

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Webhook Setup Guide](https://developers.facebook.com/docs/whatsapp/webhooks)
- [Media API Reference](https://developers.facebook.com/docs/whatsapp/api/media)

## 🤝 Contributing

When contributing to media functionality:

1. **Test Thoroughly**: Run the test suite before submitting
2. **Update Documentation**: Keep this README updated
3. **Follow Patterns**: Use existing code patterns and structure
4. **Add Tests**: Include tests for new functionality
5. **Log Appropriately**: Add meaningful log messages

## 📝 Changelog

### Version 1.0.0 (Current)

- ✅ Initial media handling implementation
- ✅ Support for images, audio, video, documents
- ✅ Automatic download and storage
- ✅ Interactive text commands
- ✅ Comprehensive testing suite
- ✅ Location and interactive message support
- ✅ Error handling and logging

### Planned Features

- 🔄 Background processing for large files
- 🔄 Media compression and optimization
- 🔄 Cloud storage integration
- 🔄 Media analytics and reporting
- 🔄 Advanced media manipulation (resize, convert, etc.)

---

For questions or support, please check the logs first, then refer to the troubleshooting section above.
