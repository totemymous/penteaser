#!/usr/bin/env python3
"""
Vulnerable Test Application for XSS Testing
This is intentionally vulnerable for testing purposes only!
"""

from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)

# In-memory storage for stored XSS testing
stored_comments = []
stored_guestbook = []

# Initialize SQL database (vulnerable for testing)
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
    ''')
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret123', 'admin@example.com')")
    cursor.execute("INSERT INTO users VALUES (2, 'user', 'pass456', 'user@example.com')")
    conn.commit()
    return conn

db_conn = init_db()

# Intentionally vulnerable HTML template
VULNERABLE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>XSS Test Lab</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        .form-group { margin: 20px 0; }
        input[type="text"] { width: 400px; padding: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        .result { background: #f8f9fa; padding: 20px; margin-top: 20px; border: 1px solid #dee2e6; }
    </style>
</head>
<body>
    <h1>🔒 XSS Vulnerability Test Lab</h1>
    <p><strong>Warning:</strong> This application is intentionally vulnerable for security testing purposes.</p>

    <div class="form-group">
        <h2>Search Form (Vulnerable to XSS)</h2>
        <form method="GET" action="/search">
            <input type="text" name="q" placeholder="Enter search query..." value="{{ query or '' }}">
            <button type="submit">Search</button>
        </form>
    </div>

    {% if query %}
    <div class="result">
        <h3>Search Results</h3>
        <p>You searched for: {{ query|safe }}</p>
        <p><em>No results found for "{{ query|safe }}"</em></p>
    </div>
    {% endif %}

    <hr>

    <div class="form-group">
        <h2>Comment Form (POST - Also Vulnerable)</h2>
        <form method="POST" action="/comment">
            <input type="text" name="author" placeholder="Your name..." required><br><br>
            <textarea name="message" placeholder="Your comment..." rows="4" style="width: 400px; padding: 10px;"></textarea><br><br>
            <button type="submit">Post Comment</button>
        </form>
    </div>

    {% if comment %}
    <div class="result">
        <h3>Posted Comment</h3>
        <p><strong>{{ comment.author|safe }}</strong> wrote:</p>
        <p>{{ comment.message|safe }}</p>
    </div>
    {% endif %}

    <hr>

    <div class="form-group">
        <h2>URL Parameter Test</h2>
        <p>Try: <a href="/reflect?data=test">http://localhost:5000/reflect?data=test</a></p>
    </div>

    <hr>

    <div class="form-group">
        <h2>🔴 Stored XSS - Guestbook (PERSISTENT)</h2>
        <p><strong>Warning:</strong> Comments are stored and displayed to all visitors!</p>
        <p><a href="/guestbook" style="color: #dc3545;">View Guestbook →</a></p>
    </div>

    <hr>

    <div class="form-group">
        <h2>🔴 SQL Injection - Login (CRITICAL)</h2>
        <p><strong>Warning:</strong> This endpoint is vulnerable to SQL injection!</p>
        <p><a href="/login" style="color: #dc3545;">Test Login Form →</a></p>
    </div>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(VULNERABLE_TEMPLATE)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return render_template_string(VULNERABLE_TEMPLATE, query=query)

@app.route('/comment', methods=['POST'])
def comment():
    comment_data = {
        'author': request.form.get('author', ''),
        'message': request.form.get('message', '')
    }
    return render_template_string(VULNERABLE_TEMPLATE, comment=comment_data)

@app.route('/reflect')
def reflect():
    data = request.args.get('data', '')
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Reflection Test</title></head>
    <body>
        <h1>Reflected Data</h1>
        <p>Your input: {data}</p>
        <p><a href="/">Back to home</a></p>
    </body>
    </html>
    """

@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        # Store comment (VULNERABLE - no sanitization!)
        name = request.form.get('name', 'Anonymous')
        message = request.form.get('message', '')
        stored_guestbook.append({
            'name': name,
            'message': message,
            'id': len(stored_guestbook)
        })
        return redirect(url_for('guestbook'))

    # Display all stored comments (VULNERABLE - no escaping!)
    comments_html = ""
    for comment in stored_guestbook:
        comments_html += f"""
        <div class="result" style="margin: 10px 0;">
            <strong>{comment['name']}</strong> wrote:
            <p>{comment['message']}</p>
            <small style="color: #666;">Entry #{comment['id']}</small>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Guestbook - Stored XSS</title>
        <style>
            body {{ font-family: Arial; max-width: 800px; margin: 50px auto; }}
            .form-group {{ margin: 20px 0; }}
            input[type="text"], textarea {{ width: 400px; padding: 10px; }}
            button {{ padding: 10px 20px; background: #dc3545; color: white; border: none; cursor: pointer; }}
            .result {{ background: #f8f9fa; padding: 15px; border: 1px solid #dee2e6; }}
        </style>
    </head>
    <body>
        <h1>📖 Guestbook (Stored XSS Vulnerable)</h1>
        <p><a href="/">← Back to home</a></p>

        <div class="form-group">
            <h2>Leave a Comment</h2>
            <form method="POST">
                <input type="text" name="name" placeholder="Your name..." required><br><br>
                <textarea name="message" placeholder="Your message..." rows="4" required></textarea><br><br>
                <button type="submit">Post Comment</button>
            </form>
        </div>

        <hr>

        <h2>All Comments ({len(stored_guestbook)})</h2>
        {comments_html if comments_html else '<p><em>No comments yet. Be the first!</em></p>'}

    </body>
    </html>
    """


@app.route('/login')
def login():
    """
    VULNERABLE SQL Injection endpoint
    For testing SQL injection detection
    """
    username = request.args.get('username', '')

    if username:
        try:
            # VULNERABLE: Direct SQL concatenation (for testing purposes)
            query = f"SELECT * FROM users WHERE username = '{username}'"
            cursor = db_conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                user_info = f"User found: {result[1]} (Email: {result[3]})"
            else:
                user_info = f"No user found with username: {username}"

            result_html = f"""
            <html>
            <body>
                <h1>User Login</h1>
                <p>{user_info}</p>
                <p><em>Query executed: {query}</em></p>
                <hr>
                <form method="GET">
                    <input type="text" name="username" placeholder="Username" value="{username}">
                    <button type="submit">Login</button>
                </form>
                <p><a href="/">Back to home</a></p>
            </body>
            </html>
            """
            return result_html

        except sqlite3.Error as e:
            # Return SQL error (vulnerable for testing)
            return f"""
            <html>
            <body>
                <h1>Database Error</h1>
                <p style="color: red">SQL Error: {str(e)}</p>
                <p><em>Query: {query}</em></p>
                <p><a href="/login">Try again</a></p>
            </body>
            </html>
            """, 500

    # Login form
    return """
    <html>
    <body>
        <h1>User Login (SQL Injection Test)</h1>
        <form method="GET">
            <input type="text" name="username" placeholder="Username" required>
            <button type="submit">Login</button>
        </form>
        <hr>
        <p><em>Test usernames: admin, user</em></p>
        <p><em>This endpoint is intentionally vulnerable to SQL injection!</em></p>
        <p><a href="/">Back to home</a></p>
    </body>
    </html>
    """


if __name__ == '__main__':
    print("🚀 Starting Vulnerable Test Application...")
    print("⚠️  WARNING: This app is intentionally vulnerable!")
    print("📍 Access at: http://localhost:5000")
    print("🔒 For XSS testing purposes only!")
    app.run(host='0.0.0.0', port=5000, debug=False)
