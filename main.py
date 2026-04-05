from flask import Flask, make_response

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def nocache_file(path):
    with open(path, 'rb') as f:
        content = f.read()
    resp = make_response(content)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/')
def nexussphere():
    return nocache_file('static_nexussphere.html')

@app.route('/bigmac')
def bigmac():
    return nocache_file('static_bigmac.html')

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
