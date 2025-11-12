"""
Flask URL Shortener - A simple production-leaning URL shortener service.
"""
import os
import secrets
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
DB_PATH = os.getenv('DB_PATH', '/data/shorty.db')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8080')
CODE_LENGTH = int(os.getenv('CODE_LENGTH', '6'))

# Ensure DB directory exists
db_path_obj = Path(DB_PATH)
db_path_obj.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)


def get_conn():
    """Get a SQLite connection with Row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS links (
            code TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def gen_code(n):
    """Generate a random URL-safe alphanumeric code of length n."""
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(secrets.choice(alphabet) for _ in range(n))


def row_to_dict(row):
    """Convert SQLite Row to dictionary."""
    return dict(row)


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with HTML interface."""
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input[type="url"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .result h3 {
            margin-bottom: 10px;
            color: #333;
        }
        .short-url {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
        }
        .short-url input {
            flex: 1;
            padding: 10px;
            border: 2px solid #667eea;
            border-radius: 6px;
            font-size: 14px;
            background: white;
        }
        .copy-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        .copy-btn:hover {
            background: #5568d3;
        }
        .copy-btn.copied {
            background: #28a745;
        }
        .stats-link {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        .stats-link a {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
        }
        .stats-link a:hover {
            text-decoration: underline;
        }
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            margin-top: 10px;
        }
        .loading.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 URL Shortener</h1>
        <p class="subtitle">Shorten your long URLs quickly and easily</p>
        
        <form id="shortenForm">
            <div class="form-group">
                <label for="url">Enter URL to shorten:</label>
                <input 
                    type="url" 
                    id="url" 
                    name="url" 
                    placeholder="https://example.com/very/long/url" 
                    required
                >
            </div>
            <button type="submit" id="submitBtn">Shorten URL</button>
            <div class="loading" id="loading">Shortening...</div>
        </form>
        
        <div class="result" id="result">
            <h3 id="resultTitle"></h3>
            <p id="resultMessage"></p>
            <div class="short-url" id="shortUrlContainer" style="display: none;">
                <input type="text" id="shortUrl" readonly>
                <button class="copy-btn" id="copyBtn" onclick="copyToClipboard()">Copy</button>
            </div>
            <div class="stats-link" id="statsLink" style="display: none;">
                <a href="#" id="statsLinkAnchor" target="_blank">View Statistics</a>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('shortenForm');
        const result = document.getElementById('result');
        const resultTitle = document.getElementById('resultTitle');
        const resultMessage = document.getElementById('resultMessage');
        const shortUrlContainer = document.getElementById('shortUrlContainer');
        const shortUrlInput = document.getElementById('shortUrl');
        const statsLink = document.getElementById('statsLink');
        const statsLinkAnchor = document.getElementById('statsLinkAnchor');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const urlInput = document.getElementById('url');
            const url = urlInput.value.trim();
            
            if (!url) {
                showError('Please enter a URL');
                return;
            }

            // Validate URL starts with http:// or https://
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showError('URL must start with http:// or https://');
                return;
            }

            // Show loading state
            submitBtn.disabled = true;
            loading.classList.add('show');
            result.classList.remove('show');

            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });

                const data = await response.json();

                if (response.ok) {
                    showSuccess(data);
                } else {
                    showError(data.error || 'Failed to shorten URL');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                loading.classList.remove('show');
            }
        });

        function showSuccess(data) {
            result.className = 'result show success';
            resultTitle.textContent = '✅ URL Shortened Successfully!';
            resultMessage.textContent = 'Your shortened URL is ready:';
            
            const baseUrl = window.location.origin;
            const shortUrl = baseUrl + '/' + data.code;
            
            shortUrlInput.value = shortUrl;
            shortUrlContainer.style.display = 'flex';
            
            statsLinkAnchor.href = '/api/stats/' + data.code;
            statsLink.style.display = 'block';
        }

        function showError(message) {
            result.className = 'result show error';
            resultTitle.textContent = '❌ Error';
            resultMessage.textContent = message;
            shortUrlContainer.style.display = 'none';
            statsLink.style.display = 'none';
        }

        function copyToClipboard() {
            const copyBtn = document.getElementById('copyBtn');
            shortUrlInput.select();
            shortUrlInput.setSelectionRange(0, 99999); // For mobile devices
            
            try {
                document.execCommand('copy');
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('copied');
                
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('copied');
                }, 2000);
            } catch (err) {
                // Fallback for older browsers
                alert('Failed to copy. Please copy manually: ' + shortUrlInput.value);
            }
        }
    </script>
</body>
</html>
    '''
    return html, 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return 'ok', 200


@app.route('/api/shorten', methods=['POST'])
def shorten():
    """Shorten a URL."""
    # Handle missing or invalid JSON gracefully
    try:
        data = request.get_json(force=True)  # force=True allows parsing even without Content-Type
    except Exception:
        data = None
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Provide a valid http(s) url'}), 400
    
    url = data['url'].strip()
    
    # Validate URL starts with http:// or https://
    if not (url.startswith('http://') or url.startswith('https://')):
        return jsonify({'error': 'Provide a valid http(s) url'}), 400
    
    # Generate unique code (handle collisions)
    conn = get_conn()
    max_attempts = 10
    code = None
    
    for _ in range(max_attempts):
        candidate = gen_code(CODE_LENGTH)
        try:
            conn.execute(
                'INSERT INTO links (code, url, created_at) VALUES (?, ?, ?)',
                (candidate, url, datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
            )
            conn.commit()
            code = candidate
            break
        except sqlite3.IntegrityError:
            # Collision, try again
            continue
    
    conn.close()
    
    if code is None:
        logger.error("Failed to generate unique code after max attempts")
        return jsonify({'error': 'Failed to generate unique code'}), 500
    
    short_url = f"{BASE_URL.rstrip('/')}/{code}"
    logger.info(f"Shortened URL: {url} -> {code}")
    
    return jsonify({
        'code': code,
        'short_url': short_url
    }), 200


@app.route('/<code>', methods=['GET'])
def redirect_code(code):
    """Redirect to the original URL by code."""
    conn = get_conn()
    row = conn.execute(
        'SELECT url FROM links WHERE code = ?',
        (code,)
    ).fetchone()
    
    if row is None:
        conn.close()
        return jsonify({'error': 'Code not found'}), 404
    
    url = row['url']
    
    # Increment clicks
    conn.execute(
        'UPDATE links SET clicks = clicks + 1 WHERE code = ?',
        (code,)
    )
    conn.commit()
    conn.close()
    
    logger.info(f"Redirecting code {code} to {url}")
    return redirect(url, code=302)


@app.route('/api/stats/<code>', methods=['GET'])
def stats(code):
    """Get statistics for a short code."""
    conn = get_conn()
    row = conn.execute(
        'SELECT code, url, clicks, created_at FROM links WHERE code = ?',
        (code,)
    ).fetchone()
    
    conn.close()
    
    if row is None:
        return jsonify({'error': 'Code not found'}), 404
    
    return jsonify(row_to_dict(row)), 200


# Initialize database on startup
init_db()

if __name__ == '__main__':
    logger.info(f"Starting Flask app on 0.0.0.0:8000")
    logger.info(f"DB_PATH: {DB_PATH}, BASE_URL: {BASE_URL}, CODE_LENGTH: {CODE_LENGTH}")
    app.run(host='0.0.0.0', port=8000, debug=False)

