import requests
from flask import Flask, request, Response
from flask_cors import CORS
import logging
import re
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers="*")
logging.basicConfig(level=logging.DEBUG)

def rewrite_urls(content, proxy_url):
    # Rewrite URLs to go through our proxy
    content = re.sub(r'(src|href)="(https?://[^"]+)"', lambda m: f'{m.group(1)}="{proxy_url}?url={m.group(2)}"', content)
    content = re.sub(r'(src|href)="(/[^"]+)"', lambda m: f'{m.group(1)}="{proxy_url}?url=https://kick.com{m.group(2)}"', content)
    content = re.sub(r"(src|href)='(https?://[^']+)'", lambda m: f"{m.group(1)}='{proxy_url}?url={m.group(2)}'", content)
    content = re.sub(r"(src|href)='(/[^']+)'", lambda m: f"{m.group(1)}='{proxy_url}?url=https://kick.com{m.group(2)}'", content)
    return content

def modify_csp_header(csp_value, request_url_root):
    csp_parts = csp_value.split(';')
    modified_parts = []
    for part in csp_parts:
        if 'script-src' in part or 'style-src' in part or 'img-src' in part or 'connect-src' in part:
            part = part.strip() + f" {request_url_root.rstrip('/')} http: https: 'unsafe-inline' 'unsafe-eval' http://localhost:5000"
        modified_parts.append(part)
    return '; '.join(modified_parts)

@app.route('/kick_proxy', methods=['GET', 'POST', 'OPTIONS'])
def kick_proxy():
    if request.method == 'OPTIONS':
        response = handle_preflight()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    url = request.args.get('url')
    if not url:
        username = request.args.get('username')
        if not username:
            return "Username or URL is required", 400
        url = f"https://kick.com/{username}/chatroom"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Origin': 'https://kick.com',
        'Referer': 'https://kick.com/',
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        if request.method == 'POST':
            response = session.post(url, data=request.form, allow_redirects=True)
        else:
            response = session.get(url, allow_redirects=True)
        
        response.raise_for_status()
        
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response headers: {response.headers}")
        logging.debug(f"Response content (first 500 chars): {response.text[:500]}")
        
        # Rewrite URLs in the content
        content = rewrite_urls(response.text, request.url_root + 'kick_proxy')
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {str(e)}")
        return f"Error fetching content: {str(e)}", 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return f"Unexpected error occurred: {str(e)}", 500

    # Forward all headers except those that might cause issues
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.headers.items()
               if name.lower() not in excluded_headers]

    # Forward cookies
    for cookie in response.cookies:
        headers.append(('Set-Cookie', f"{cookie.name}={cookie.value}; Path={cookie.path}; Domain={request.host}; SameSite=None; Secure"))

    # Add CORS headers
    headers.extend([
        ('Access-Control-Allow-Origin', 'http://localhost:5000'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', '*'),
        ('Access-Control-Allow-Credentials', 'true'),
    ])

    # Modify Content-Security-Policy header
    csp_header = next((header for header in headers if header[0].lower() == 'content-security-policy'), None)
    if csp_header:
        csp_value = csp_header[1]
        csp_value = modify_csp_header(csp_value, request.url_root)
        headers = [header for header in headers if header[0].lower() != 'content-security-policy']
        headers.append(('Content-Security-Policy', csp_value))

    return Response(content, response.status_code, headers)

def handle_preflight():
    response = Response()
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.errorhandler(404)
def not_found(error):
    if 'cdn-cgi/challenge-platform/scripts/jsd/main.js' in request.path:
        # Return an empty JavaScript file instead of 404
        return Response("", mimetype="application/javascript")
    return "Not Found", 404

@app.route('/en.75a71d0c.js')
def serve_en_js():
    return Response("", mimetype="application/javascript")

@app.route('/<path:filename>')
def serve_static(filename):
    return Response("", mimetype="application/javascript")

@app.route('/sanctum/csrf-cookie', methods=['GET', 'POST', 'OPTIONS'])
def handle_csrf_cookie():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    response = Response()
    response.set_cookie('XSRF-TOKEN', 'dummy-token', secure=True, httponly=True, samesite='None')
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    app.run(debug=True)
