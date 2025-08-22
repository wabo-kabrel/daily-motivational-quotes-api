# Daily Motivational Quotes API

A robust Flask REST API that provides daily motivational quotes with CRUD support, SQLite storage, rate limiting, and integration capabilities for automated delivery to platforms like Telegram, Slack, or Email via n8n.

## 📁 Project Structure

```
daily-motivational-quotes-api/
├── motivation_api/                 # Main application package
│   ├── __init__.py                # Package initialization
│   ├── app.py                     # Flask application setup and routes
│   ├── models.py                  # SQLAlchemy database models
│   ├── seed.py                    # Database seeding script with sample quotes
│   ├── quotes.db                  # SQLite database (generated)
│   └── migrations/                # Database migrations (Alembic)
│       ├── alembic.ini
│       ├── env.py
│       ├── README
│       ├── script.py.mako
│       └── versions/              # Migration versions
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api.py                # API endpoint tests
│  
├── .env                           # Environment variables (not included in repo)
├── .dockerignore                  # Docker ignore patterns
├── .gitignore                     # Git ignore patterns
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile                     # Docker build configuration
├── gunicorn_config.py             # Gunicorn server configuration
├── LICENSE                        # MIT License
├── pytest.ini                     # Pytest configuration
├── README.md                      # This documentation file
├── render.yaml                    # Render.com deployment configuration
├── requirements.txt               # Python dependencies
└── instance/                      # Flask instance folder
    └── quotes.db                  # Alternative database location
```

## 🚀 Features

- **RESTful API**: Clean, well-documented endpoints following REST conventions
- **Quote of the Day**: Deterministic daily quote selection using SHA-256 hashing
- **Random Quotes**: Get a random motivational quote
- **Pagination**: List quotes with limit/offset parameters
- **Admin CRUD Operations**: Create, read, update, and delete quotes (API key protected)
- **Rate Limiting**: Configurable rate limiting to prevent abuse
- **CORS Support**: Cross-origin resource sharing enabled for API endpoints
- **SQLite Database**: Lightweight database with Alembic migrations
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Testing**: Comprehensive test suite with pytest
- **Production Ready**: Gunicorn WSGI server configuration
- **Render Deployment**: Ready for deployment on Render.com

## 📋 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API documentation and available endpoints |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/api/v1/quote` | Get a random quote |
| `GET` | `/api/v1/qotd` | Get the deterministic quote of the day |
| `GET` | `/api/v1/quotes` | List quotes (supports pagination) |

### Admin Endpoints (Requires API Key)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/quotes` | Create a new quote |
| `PUT` | `/api/v1/quotes/<id>` | Update an existing quote |
| `DELETE` | `/api/v1/quotes/<id>` | Delete a quote |

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- SQLite (included with Python)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/wabo-kabrel/daily-motivational-quotes-api.git  
   cd daily-motivational-quotes-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=sqlite:///quotes.db
   SECRET_KEY=your-secret-key-here
   ADMIN_API_KEY=your-admin-api-key-here
   RATE_LIMIT=60/minute
   FLASK_APP=motivation_api.app
   FLASK_ENV=development
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Seed the database with sample quotes**
   ```bash
   python -m motivation_api.seed
   ```

7. **Run the development server**
   ```bash
   flask run
   ```

The API will be available at `http://localhost:5000`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build with Docker directly**
   ```bash
   docker build -t motivational-quotes-api .
   docker run -p 5000:5000 motivational-quotes-api
   ```

## 📖 Usage Examples

### Get a Random Quote
```bash
curl http://localhost:5000/api/v1/quote
```

Response:
```json
{
  "success": true,
  "data": {
    "id": 42,
    "text": "The best way to get started is to quit talking and begin doing.",
    "author": "Walt Disney"
  },
  "message": null,
  "meta": {
    "generated_at": "2024-01-15T10:30:45.123456",
    "version": "v1"
  }
}
```

### Get Quote of the Day
```bash
curl http://localhost:5000/api/v1/qotd
```

### List Quotes with Pagination
```bash
curl "http://localhost:5000/api/v1/quotes?limit=5&offset=0"
```

### Create a New Quote (Admin)
```bash
curl -X POST http://localhost:5000/api/v1/quotes \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-admin-api-key" \
  -d '{"text": "Your new motivational quote", "author": "Author Name"}'
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

The test suite includes:
- Health check endpoint tests
- Random quote functionality
- Quote of the day deterministic behavior
- Pagination and validation
- Admin CRUD operations
- Error handling

## 🚀 Deployment

### Render.com Deployment

This project includes a `render.yaml` file for easy deployment on Render.com:

1. Connect your GitHub repository to Render
2. Render will automatically detect the configuration
3. Environment variables will be automatically generated

### Environment Variables for Production

- `DATABASE_URL`: SQLite database connection string
- `SECRET_KEY`: Flask secret key for session security
- `ADMIN_API_KEY`: API key for admin operations
- `RATE_LIMIT`: Rate limiting configuration (e.g., "60/minute")
- `FLASK_ENV`: Set to "production"

## 📊 Database Schema

The application uses a simple SQLite database with one table:

### Quotes Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key, auto-incrementing |
| `text` | TEXT | The motivational quote text (required) |
| `author` | VARCHAR(255) | The author of the quote (required) |

## 🔧 Configuration

### Rate Limiting
The API includes configurable rate limiting via Flask-Limiter. Default is 60 requests per minute per IP address.

### CORS Configuration
CORS is enabled for all `/api/*` routes to allow cross-origin requests from any origin.

### Error Handling
The API provides standardized JSON error responses with appropriate HTTP status codes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask framework and ecosystem
- SQLAlchemy for ORM functionality
- Alembic for database migrations
- All the inspirational quote authors

## 📞 Support

For support or questions, please open an issue in the GitHub repository.

---

**Happy coding and stay motivated!** 🚀
