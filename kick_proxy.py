import cloudscraper
from flask import Flask, request, Response
import urllib.parse

app = Flask(__name__)

@app.route('/kick_proxy')
def kick_proxy():
    username = request.args.get('username')
    if not username:
        return "Username is required", 400

    url = f"https://kick.com/{username}/chatroom"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching content: {str(e)}", 500

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.headers.items()
               if name.lower() not in excluded_headers]

    return Response(response.content, response.status_code, headers)

if __name__ == '__main__':
    app.run(debug=True)
