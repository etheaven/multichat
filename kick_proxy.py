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
    
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    
    return Response(response.content, content_type=response.headers['Content-Type'])

if __name__ == '__main__':
    app.run(debug=True)
