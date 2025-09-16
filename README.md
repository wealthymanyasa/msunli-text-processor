# Multi-Language Text Processor API

A secure FastAPI service for processing text in multiple languages, with built-in authentication, database persistence, and Docker deployment.

## Features

- Multi-language text processing support
  - Automatic language detection
  - Currently supports Shona (more languages can be added)
- Text processing capabilities
  - Text cleaning and normalization
  - Tokenization with punctuation handling
  - Language-specific stopword removal
  - Word frequency analysis
  - Batch processing
- Security features
  - JWT authentication
  - User management
  - Rate limiting
  - API endpoint protection
- Infrastructure
  - PostgreSQL database for data persistence
  - Redis for caching and rate limiting
  - Docker containerization
  - Health monitoring
  - Scalable architecture

## Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/wealthymanyasa/msunli-text-processor.git
cd msunli-text-processor
```

2. **Build and run with Docker:**
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

## Authentication

1. **Register a new user:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","username":"user","password":"password123"}'
```

2. **Login to get access token:**
```bash
curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/form-data" \
     -d "username=user&password=password123"
```

3. **Use the token for authenticated requests:**
```bash
curl -X POST "http://localhost:8000/api/v1/tokenize" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{"text":"Your text here","language":"sn"}'
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get access token
- `GET /auth/users/me` - Get current user info

### Text Processing
- `POST /api/v1/tokenize` - Process single text
- `POST /api/v1/tokenize/batch` - Process multiple texts
- `GET /api/v1/statistics` - Get text processing statistics

### System
- `GET /health` - Check system health

## Environment Variables

The following environment variables can be configured in docker-compose.yml:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `JWT_ALGORITHM` - Algorithm for JWT (default: HS256)
- `JWT_EXPIRATION_MINUTES` - Token expiration time (default: 30)
- `UVICORN_WORKERS` - Number of worker processes
- `UVICORN_HOST` - Host to bind to
- `UVICORN_PORT` - Port to bind to

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run development server:
```bash
uvicorn app.main:app --reload
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.