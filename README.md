# Flask URL Shortener

A simple, production-leaning Flask URL shortener service that shortens URLs, tracks redirects, and provides statistics.

## Overview

This Flask application provides a RESTful API and a beautiful web interface for shortening URLs and tracking their usage. It stores data in SQLite and is designed to be single-container friendly with environment-based configuration.

**Features:**
- 🎨 Modern web interface for easy URL shortening
- 🔗 RESTful API for programmatic access
- 📊 Click statistics tracking
- 💾 SQLite database persistence
- ⚡ Fast and lightweight

## Endpoints

### `POST /api/shorten`
Shortens a URL and returns a short code.

**Request:**
```json
{
  "url": "https://example.com/very/long/url"
}
```

**Response (200):**
```json
{
  "code": "Ab3kX9",
  "short_url": "http://localhost:8080/Ab3kX9"
}
```

**Error (400):**
```json
{
  "error": "Provide a valid http(s) url"
}
```

### `GET /<code>`
Redirects to the original URL associated with the short code.

- Returns `302 Found` with `Location` header pointing to the original URL
- Automatically increments the click counter
- Returns `404` if code is not found

### `GET /api/stats/<code>`
Returns statistics for a short code.

**Response (200):**
```json
{
  "code": "Ab3kX9",
  "url": "https://example.com/very/long/url",
  "clicks": 42,
  "created_at": "2024-01-15T10:30:00.123456Z"
}
```

**Error (404):**
```json
{
  "error": "Code not found"
}
```

### `GET /`
Web interface for shortening URLs.

- Returns an HTML page with a form to shorten URLs
- Displays shortened URLs with copy-to-clipboard functionality
- Shows error messages for invalid URLs
- Provides links to view statistics

### `GET /health`
Health check endpoint.

**Response (200):**
```
ok
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `/data/shorty.db` | Path to SQLite database file |
| `BASE_URL` | `http://localhost:8080` | Base URL for generating short URLs |
| `CODE_LENGTH` | `6` | Length of generated short codes |

## Quickstart

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://0.0.0.0:8000`.

### 5. Using the Application

#### Web Interface (Recommended)

1. **Open your browser** and visit:
   ```
   http://localhost:8000
   ```

2. **Enter a URL** in the form (must start with `http://` or `https://`)

3. **Click "Shorten URL"** - the shortened URL will appear with a copy button

4. **Click "Copy"** to copy the shortened URL to your clipboard

5. **Click "View Statistics"** to see click counts and other stats

The web interface provides:
- ✅ Beautiful, modern UI
- ✅ Real-time feedback
- ✅ One-click copy functionality
- ✅ Direct links to statistics
- ✅ Error handling with clear messages

#### API Usage (Command Line)

**Shorten a URL:**
```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

**Use shortened URL (redirects automatically):**
```bash
# In browser: http://localhost:8000/Ab3kX9
# Or with curl:
curl -L http://localhost:8000/Ab3kX9
```

**Get statistics:**
```bash
curl http://localhost:8000/api/stats/Ab3kX9
```

**Health check:**
```bash
curl http://localhost:8000/health
```

## Docker Usage (3 Steps)

You can go from source to running container with three quick commands.

1. **Create your environment file**
   ```powershell
   # PowerShell
   Copy-Item .env.example .env
   ```
   ```bash
   # macOS / Linux
   cp .env.example .env
   ```

2. **Build the image from the Dockerfile**
   ```bash
   docker build -t url-shortner:latest .
   ```

3. **Run the container (detached)**
   ```bash
   docker run -d --name url-shortner -p 8000:8000 --env-file .env url-shortner:latest
   ```

4. **Stop the container when you’re done**
   ```bash
   docker stop url-shortner
   ```

The app is now available at `http://localhost:8000`. To view logs run `docker logs -f url-shortner`. Remove the stopped container with `docker rm url-shortner` if desired. To rebuild after code changes, rerun step 2 then step 3.

## Running Tests

The test suite uses pytest and creates temporary SQLite databases for each test run, ensuring tests don't interfere with your development database.

**Run all tests:**
```bash
pytest tests/ -p no:asyncio
```

Or if you have pytest-asyncio compatibility issues, you can also use:
```bash
python -m pytest tests/ -p no:asyncio
```

**Run with verbose output:**
```bash
pytest -v tests/ -p no:asyncio
```

**Run specific test:**
```bash
pytest tests/test_app.py::test_health_ok -p no:asyncio
```

**Note:** The `-p no:asyncio` flag disables the pytest-asyncio plugin which can cause compatibility issues. All tests pass without it since this project doesn't use async code.

### Test Configuration

Tests automatically configure the app to use a temporary database file (via `tmp_path` fixture) instead of the default `/data/shorty.db`. This ensures:
- Tests don't modify your development database
- Each test run starts with a clean database
- Tests can run in parallel without conflicts

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Make sure to:
- Set appropriate environment variables
- Ensure the database directory exists and is writable
- Use a reverse proxy (nginx, etc.) for HTTPS
- Set up proper logging and monitoring

## Persistence and Database

The application uses SQLite for data persistence. The database file is created automatically on first run in the directory specified by `DB_PATH`.

**Database Schema:**
```sql
CREATE TABLE links (
    code TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
)
```

**Important Notes:**
- The database directory is created automatically if it doesn't exist
- The database file persists between application restarts
- For production, consider using PostgreSQL or another production-grade database
- Backup your database file regularly

## Code Quality

- Python 3.11+ compatible
- PEP8 compliant
- Defensive error handling
- Comprehensive logging
- Collision-resistant code generation (retries on conflicts)

## License

This project is provided as-is for educational and development purposes.

