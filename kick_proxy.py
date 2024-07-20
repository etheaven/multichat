import requests
from flask import Flask, request, Response
from flask_cors import CORS
import logging
import re

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/kick_proxy')
def kick_proxy():
    username = request.args.get('username')
    if not username:
        return "Username is required", 400

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
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url)
        response.raise_for_status()
        
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response headers: {response.headers}")
        logging.debug(f"Response content (first 500 chars): {response.text[:500]}")
        
        # Modify the content to handle relative URLs
        content = response.text
        content = content.replace('src="/', 'src="https://kick.com/')
        content = content.replace('href="/', 'href="https://kick.com/')
        content = re.sub(r'(src|href)="(?!http)', r'\1="https://kick.com/', content)
        
        # Check if the response contains the expected chat content
        if 'chatroom' not in content.lower():
            logging.error("Response does not contain expected chat content")
            return "Failed to load chat content", 500
        
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
        headers.append(('Set-Cookie', f"{cookie.name}={cookie.value}; Path={cookie.path}; Domain={request.host}"))

    return Response(content, response.status_code, headers)

if __name__ == '__main__':
    app.run(debug=True)
