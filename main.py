from flask import Flask, make_response, request, jsonify
import os
import logging
import hmac
import hashlib
import base64
import json
import time
import requests as http

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

SNAP_BASE = 'https://api.snaptrade.com/api/v1'

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

# ── SnapTrade helpers ────────────────────────────────────────────────────────

def _snap_credentials():
    cid = os.environ.get('SNAPTRADE_CLIENT_ID', '').strip()
    ckey = os.environ.get('SNAPTRADE_CONSUMER_KEY', '').strip()
    return cid, ckey

def _snap_sign(consumer_key, body_dict):
    """HMAC-SHA256 over JSON.stringify(body) — must match SnapTrade JS SDK."""
    body_str = json.dumps(body_dict, separators=(',', ':'))
    digest = hmac.new(consumer_key.encode(), body_str.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()

def _snap_call(method, path, body=None, user_id=None, user_secret=None, extra_params=None):
    client_id, consumer_key = _snap_credentials()
    if not client_id or not consumer_key:
        return {'error': 'SnapTrade credentials not configured on server'}, 503

    timestamp = int(time.time())
    sign_body = dict(body or {})
    sign_body['timestamp'] = timestamp
    sig = _snap_sign(consumer_key, sign_body)

    params = [
        ('clientId', client_id),
        ('timestamp', str(timestamp)),
        ('signature', sig),
    ]
    if user_id:
        params.append(('userId', user_id))
    if user_secret:
        params.append(('userSecret', user_secret))
    if extra_params:
        params.extend(extra_params.items())

    url = SNAP_BASE + path
    headers = {'Content-Type': 'application/json'}

    try:
        if method == 'GET':
            resp = http.get(url, params=params, headers=headers, timeout=15)
        elif method == 'DELETE':
            resp = http.delete(url, params=params, headers=headers, timeout=15)
        else:
            resp = http.request(method, url, params=params, json=body, headers=headers, timeout=15)

        if not resp.ok:
            log.error(f"SnapTrade {method} {path} → {resp.status_code}: {resp.text[:300]}")
            try:
                err = resp.json()
            except Exception:
                err = {'error': resp.text[:200]}
            return err, resp.status_code
        return resp.json(), 200
    except Exception as e:
        log.error(f"SnapTrade request failed: {e}")
        return {'error': str(e)}, 500

# ── App routes ───────────────────────────────────────────────────────────────

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
    return make_response('', 204)

@app.route('/snap-callback')
def snap_callback():
    """OAuth return URL — just reload the app; JS detects popup close."""
    return nocache_file('static_nexussphere.html')

# ── SnapTrade proxy API ──────────────────────────────────────────────────────

@app.route('/api/snap/status')
def snap_status():
    cid, ckey = _snap_credentials()
    return jsonify({'configured': bool(cid and ckey)})

@app.route('/api/snap/register', methods=['POST'])
def snap_register():
    data = request.get_json(silent=True) or {}
    user_id = data.get('userId', '').strip()
    if not user_id:
        return jsonify({'error': 'userId required'}), 400
    result, status = _snap_call('POST', '/snapTrade/registerUser', {'userId': user_id})
    return jsonify(result), status

@app.route('/api/snap/connect', methods=['POST'])
def snap_connect():
    data = request.get_json(silent=True) or {}
    user_id = data.get('userId', '').strip()
    user_secret = data.get('userSecret', '').strip()
    broker = data.get('broker', 'WEALTHSIMPLE').strip()
    if not user_id or not user_secret:
        return jsonify({'error': 'userId and userSecret required'}), 400

    # Build callback URL using the public Replit domain
    domains = os.environ.get('REPLIT_DOMAINS', '')
    domain = domains.split(',')[0].strip() if domains else ''
    callback = f'https://{domain}/snap-callback' if domain else 'https://nexussphere.replit.app/snap-callback'

    result, status = _snap_call('POST', '/snapTrade/login',
        {'broker': broker, 'immediateRedirect': False, 'customRedirect': callback},
        user_id=user_id, user_secret=user_secret)
    return jsonify(result), status

@app.route('/api/snap/accounts')
def snap_accounts():
    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    result, status = _snap_call('GET', '/accounts', user_id=uid, user_secret=usec)
    return jsonify(result), status

@app.route('/api/snap/positions')
def snap_positions():
    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    result, status = _snap_call('GET', '/holdings', user_id=uid, user_secret=usec)
    return jsonify(result), status

@app.route('/api/snap/balances')
def snap_balances():
    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    acct_id = request.args.get('accountId', '').strip()
    path = f'/accounts/{acct_id}/balances' if acct_id else '/accounts'
    result, status = _snap_call('GET', path, user_id=uid, user_secret=usec)
    return jsonify(result), status

@app.route('/api/snap/activities')
def snap_activities():
    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    start = request.args.get('startDate', '')
    extra = {'startDate': start} if start else {}
    result, status = _snap_call('GET', '/activities', user_id=uid, user_secret=usec, extra_params=extra if extra else None)
    return jsonify(result), status

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log.info(f"Starting NexusSphere on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
