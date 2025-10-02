import logging
import os

from app import create_app


app = create_app()

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    logging.info(f"Flask app starting on port {port}")
    
    # Run in production mode for Railway
    app.run(
        host="0.0.0.0", 
        port=port,
        debug=False  # Disable debug mode in production
    )
