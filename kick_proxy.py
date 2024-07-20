import requests
from flask import Flask, request, Response
import urllib.parse
import logging
import time
import re
import js2py

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def solve_cf_challenge(session, response):
    # Extract the challenge
    challenge_form = re.search(r'<form.*?id="challenge-form".*?>(.*?)</form>', response.text, re.DOTALL)
    if not challenge_form:
        logging.error("Cloudflare challenge form not found")
        return None

    # Extract necessary parameters
    params = {}
    for input_tag in re.finditer(r'<input.*?name="(.*?)".*?value="(.*?)"', challenge_form.group(1)):
        params[input_tag.group(1)] = input_tag.group(2)

    # Solve the JavaScript challenge
    js_challenge = re.search(r'setTimeout\(function\(\){\s*(var s,t,o,p,b,r,e,a,k,i,n,g,f.+?\r?\n[\s\S]+?a\.value =.+?)\r?\n', response.text)
    if js_challenge:
        js_code = js_challenge.group(1)
        js_code = js_code.replace('t.length)', 'Object.keys(t).length)')
        context = js2py.EvalJs()
        context.execute(js_code)
        result = context.eval('a.value')
        params['jschl_answer'] = result

    # Wait for the specified time
    time.sleep(5)

    # Make the challenge response request
    challenge_url = f"{response.url.scheme}://{response.url.netloc}/cdn-cgi/l/chk_jschl"
    headers = {
        'User-Agent': session.headers['User-Agent'],
        'Referer': response.url
    }
    r = session.get(challenge_url, params=params, headers=headers)
    return r

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
        
        if response.status_code == 403 and 'cf-browser-verification' in response.text:
            logging.info("Detected Cloudflare challenge, attempting to solve...")
            response = solve_cf_challenge(session, response)
            if response is None:
                return "Failed to solve Cloudflare challenge", 500
        
        response.raise_for_status()
        
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response headers: {response.headers}")
        logging.debug(f"Response content (first 500 chars): {response.text[:500]}")
        
    except Exception as e:
        logging.error(f"Error fetching content: {str(e)}")
        return f"Error fetching content: {str(e)}", 500

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.headers.items()
               if name.lower() not in excluded_headers]

    return Response(response.content, response.status_code, headers)

if __name__ == '__main__':
    app.run(debug=True)
