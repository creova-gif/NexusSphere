from flask import Flask, make_response
import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def nocache_file(path):
    try:
        with open(path, 'rb') as f:
            content = f.read()
        resp = make_response(content)
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except FileNotFoundError:
        log.error(f"File not found: {path}")
        return make_response(f"<h1>File not found: {path}</h1>", 404)
    except Exception as e:
        log.error(f"Error serving {path}: {e}")
        return make_response(f"<h1>Server error</h1>", 500)

@app.route('/')
def nexussphere():
    return nocache_file('static_nexussphere.html')

@app.route('/bigmac')
def bigmac():
    return nocache_file('static_bigmac.html')

@app.route('/health')
def health():
    return 'OK'

@app.route('/favicon.ico')
def favicon():
    resp = make_response('', 204)
    return resp

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log.info(f"Starting NexusSphere on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
