from flask import Flask, send_file, redirect

app = Flask(__name__)

@app.route('/')
def nexussphere():
    return send_file('static_nexussphere.html')

@app.route('/bigmac')
def bigmac():
    return send_file('static_bigmac.html')

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
