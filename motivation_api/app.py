# ------------------------
# Import necessary libraries
# ------------------------
from flask import Flask, jsonify, request                  # Core Flask components
from flask_sqlalchemy import SQLAlchemy                  # ORM for database interactions
from flask_migrate import Migrate                        # For handling DB migrations
from flask_cors import CORS                              # Handle Cross-Origin requests
from flask_limiter import Limiter                        # Rate limiting
from flask_limiter.util import get_remote_address        # Helper to get IP for rate limiting
from dotenv import load_dotenv                           # Load environment variables from .env
import os                                                # OS operations (fetch env variables)
import hashlib                                           # For hashing (used in QOTD selection)
from datetime import datetime                            # Work with dates/times
import random                                            # Random selection of quotes
from functools import wraps                              # For API key decorator

# ------------------------
# Load environment variables from .env
# ------------------------
load_dotenv()

# ------------------------
# Flask App Setup
# ------------------------
app = Flask(__name__)  # Initialize Flask app

# Configure Flask app using environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # Database connection string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False               # Disable modification tracking (performance)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")                 # Secret key for session/security

# ------------------------
# Initialize Flask extensions
# ------------------------
db = SQLAlchemy(app)                                     # Initialize SQLAlchemy ORM
migrate = Migrate(app, db)                               # Initialize Flask-Migrate for DB migrations
CORS(app, resources={r"/api/*": {"origins": "*"}})      # Enable CORS only for /api/* routes
'''limiter = Limiter(
    app=app,                                # explicitly assign app
    key_func=get_remote_address,
    default_limits=[os.getenv("RATE_LIMIT")]  # e.g., "60 per minute"
)'''

# limiter configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_url=os.getenv("REDIS_URL", "memory://"),
    default_limits=[os.getenv("RATE_LIMIT", "60/minute")]
)

# ------------------------
# Import database models
# ------------------------
# Use relative import to avoid circular import issues
from .models import Quote  # Import Quote model from models.py

# ------------------------
# Helper Functions
# ------------------------
def standard_response(success, data=None, message=None):
    """
    Standardize API JSON responses.
    Includes a success flag, data payload, message, and meta information.
    """
    return jsonify({
        "success": success,
        "data": data,
        "message": message,
        "meta": {
            "generated_at": datetime.utcnow().isoformat(),  # Timestamp of response in UTC
            "version": "v1"                                 # API version
        }
    })

def get_qotd():
    """
    Deterministically selects the Quote of the Day (QOTD) based on the current date.
    - Fetches all quotes
    - Hashes today's date
    - Uses modulo to pick one quote index
    """
    quotes = Quote.query.all()
    if not quotes:
        return None

    today = datetime.utcnow().strftime("%Y-%m-%d")          # Current UTC date as string
    index = int(hashlib.sha256(today.encode()).hexdigest(), 16) % len(quotes)  # Deterministic index
    return quotes[index]

# ------------------------
# API Key Protection for Admin Endpoints
# ------------------------
def require_api_key(f):
    """
    Decorator to protect admin routes using x-api-key header
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key != os.getenv("ADMIN_API_KEY"):
            return standard_response(False, message="Unauthorized"), 401
        return f(*args, **kwargs)
    return decorated

# ------------------------
# Routes
# ------------------------

# root route
@app.route("/", methods=["GET"])
def index():
    """Root endpoint - API documentation"""
    return standard_response(True, {
        "message": "Welcome to the Daily Motivational Quotes API",
        "endpoints": {
            "health": "/health",
            "random_quote": "/api/v1/quote",
            "quote_of_the_day": "/api/v1/qotd",
            "list_quotes": "/api/v1/quotes"
        },
        "documentation": "https://github.com/wabo-kabrel/daily-motivational-quotes-api"
    })

#---

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint
    Returns simple JSON to verify the server is running
    """
    return standard_response(True, {"status": "ok"})

@app.route("/api/v1/quote", methods=["GET"])
@limiter.limit("10/second")  # Limit to 10 requests per second per IP
def random_quote():
    """
    Returns a random quote from the database
    """
    quote = Quote.query.order_by(db.func.random()).first()  # Randomly select one quote
    if not quote:
        return standard_response(False, message="No quotes found"), 404
    return standard_response(True, {"id": quote.id, "text": quote.text, "author": quote.author})

@app.route("/api/v1/qotd", methods=["GET"])
@limiter.limit("10/second")
def quote_of_the_day():
    """
    Returns the deterministic Quote of the Day (QOTD)
    """
    quote = get_qotd()
    if not quote:
        return standard_response(False, message="No quotes found"), 404
    return standard_response(True, {"id": quote.id, "text": quote.text, "author": quote.author})

@app.route("/api/v1/quotes", methods=["GET"])
@limiter.limit("10/second")
def list_quotes():
    """
    Returns a paginated list of quotes.
    Query Parameters:
      - limit: number of quotes to return (default=10)
      - offset: number of quotes to skip (default=0)
    """
    try:
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return standard_response(False, message="limit and offset must be integers"), 400

    quotes = Quote.query.offset(offset).limit(limit).all()
    data = [{"id": q.id, "text": q.text, "author": q.author} for q in quotes]
    return standard_response(True, data)

# ------------------------
# Admin Routes
# ------------------------

@app.route("/api/v1/quotes", methods=["POST"])
@require_api_key
def create_quote():
    """
    Admin endpoint: Create a new quote
    """
    data = request.get_json()
    text = data.get("text")
    author = data.get("author")
    
    if not text or not author:
        return standard_response(False, message="text and author are required"), 400

    quote = Quote(text=text, author=author)
    db.session.add(quote)
    db.session.commit()

    return standard_response(True, {"id": quote.id, "text": quote.text, "author": quote.author}), 201

@app.route("/api/v1/quotes/<int:quote_id>", methods=["PUT"])
@require_api_key
def update_quote(quote_id):
    """
    Admin endpoint: Update an existing quote
    """
    data = request.get_json()
    quote = Quote.query.get(quote_id)
    if not quote:
        return standard_response(False, message="Quote not found"), 404

    text = data.get("text")
    author = data.get("author")

    if text:
        quote.text = text
    if author:
        quote.author = author

    db.session.commit()
    return standard_response(True, {"id": quote.id, "text": quote.text, "author": quote.author})

@app.route("/api/v1/quotes/<int:quote_id>", methods=["DELETE"])
@require_api_key
def delete_quote(quote_id):
    """
    Admin endpoint: Delete a quote
    """
    quote = Quote.query.get(quote_id)
    if not quote:
        return standard_response(False, message="Quote not found"), 404

    db.session.delete(quote)
    db.session.commit()
    return standard_response(True, {"id": quote.id, "message": "Quote deleted"})

# ------------------------
# Error Handling
# ------------------------
@app.errorhandler(404)
def not_found(e):
    """
    Handles 404 errors (resource not found)
    """
    return standard_response(False, message="Resource not found"), 404

@app.errorhandler(500)
def server_error(e):
    """
    Handles 500 errors (internal server error)
    """
    return standard_response(False, message="Internal server error"), 500

# ------------------------
# Run the Flask App
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
