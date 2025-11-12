#!/usr/bin/env python3
"""
Vulnerable Test Application for XSS Testing
This is intentionally vulnerable for testing purposes only!
"""

from flask import Flask, request, render_template_string

app = Flask(__name__)

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

if __name__ == '__main__':
    print("🚀 Starting Vulnerable Test Application...")
    print("⚠️  WARNING: This app is intentionally vulnerable!")
    print("📍 Access at: http://localhost:5000")
    print("🔒 For XSS testing purposes only!")
    app.run(host='0.0.0.0', port=5000, debug=False)
