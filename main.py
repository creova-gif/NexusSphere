from flask import Flask, make_response, request, jsonify
import os
import logging
import snaptrade_client as st

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_snap_client():
    cid = os.environ.get('SNAPTRADE_CLIENT_ID', '').strip()
    ckey = os.environ.get('SNAPTRADE_CONSUMER_KEY', '').strip()
    if not cid or not ckey:
        return None
    return st.SnapTrade(consumer_key=ckey, client_id=cid)

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
    return nocache_file('static_nexussphere.html')

# ── SnapTrade proxy API ──────────────────────────────────────────────────────

@app.route('/api/snap/status')
def snap_status():
    cid = os.environ.get('SNAPTRADE_CLIENT_ID', '').strip()
    ckey = os.environ.get('SNAPTRADE_CONSUMER_KEY', '').strip()
    return jsonify({'configured': bool(cid and ckey)})

@app.route('/api/snap/register', methods=['POST'])
def snap_register():
    client = get_snap_client()
    if not client:
        return jsonify({'error': 'SnapTrade not configured'}), 503

    data = request.get_json(silent=True) or {}
    user_id = data.get('userId', '').strip()
    if not user_id:
        return jsonify({'error': 'userId required'}), 400

    try:
        resp = client.authentication.register_snap_trade_user(user_id=user_id)
        return jsonify(resp.body)
    except st.ApiException as e:
        log.error(f"SnapTrade register error: {e.status} {e.body}")
        body = e.body if isinstance(e.body, dict) else {'error': str(e.body)[:200]}
        return jsonify(body), e.status
    except Exception as e:
        log.error(f"SnapTrade register exception: {e}")
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/api/snap/connect', methods=['POST'])
def snap_connect():
    client = get_snap_client()
    if not client:
        return jsonify({'error': 'SnapTrade not configured'}), 503

    data = request.get_json(silent=True) or {}
    user_id = data.get('userId', '').strip()
    user_secret = data.get('userSecret', '').strip()
    broker = data.get('broker', 'WEALTHSIMPLE').strip()

    if not user_id or not user_secret:
        return jsonify({'error': 'userId and userSecret required'}), 400

    domains = os.environ.get('REPLIT_DOMAINS', '')
    domain = domains.split(',')[0].strip() if domains else ''
    callback = f'https://{domain}/snap-callback' if domain else ''

    try:
        resp = client.authentication.login_snap_trade_user(
            user_id=user_id,
            user_secret=user_secret,
            broker=broker,
            immediate_redirect=False,
            custom_redirect=callback or None
        )
        return jsonify(resp.body)
    except st.ApiException as e:
        log.error(f"SnapTrade connect error: {e.status} {e.body}")
        body = e.body if isinstance(e.body, dict) else {'error': str(e.body)[:200]}
        return jsonify(body), e.status
    except Exception as e:
        log.error(f"SnapTrade connect exception: {e}")
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/api/snap/accounts')
def snap_accounts():
    client = get_snap_client()
    if not client:
        return jsonify({'error': 'SnapTrade not configured'}), 503

    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    try:
        resp = client.account_information.list_user_accounts(user_id=uid, user_secret=usec)
        return jsonify(resp.body)
    except st.ApiException as e:
        body = e.body if isinstance(e.body, dict) else {'error': str(e.body)[:200]}
        return jsonify(body), e.status
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/api/snap/positions')
def snap_positions():
    client = get_snap_client()
    if not client:
        return jsonify({'error': 'SnapTrade not configured'}), 503

    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    try:
        resp = client.account_information.get_all_user_holdings(user_id=uid, user_secret=usec)
        return jsonify(resp.body)
    except st.ApiException as e:
        body = e.body if isinstance(e.body, dict) else {'error': str(e.body)[:200]}
        return jsonify(body), e.status
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/api/snap/balances')
def snap_balances():
    client = get_snap_client()
    if not client:
        return jsonify({'error': 'SnapTrade not configured'}), 503

    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    acct_id = request.args.get('accountId', '').strip()
    try:
        if acct_id:
            resp = client.account_information.get_user_account_balance(
                user_id=uid, user_secret=usec, account_id=acct_id)
        else:
            resp = client.account_information.list_user_accounts(user_id=uid, user_secret=usec)
        return jsonify(resp.body)
    except st.ApiException as e:
        body = e.body if isinstance(e.body, dict) else {'error': str(e.body)[:200]}
        return jsonify(body), e.status
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/api/snap/activities')
def snap_activities():
    client = get_snap_client()
    if not client:
        return jsonify({'error': 'SnapTrade not configured'}), 503

    uid = request.args.get('userId', '').strip()
    usec = request.args.get('userSecret', '').strip()
    start = request.args.get('startDate', '')
    try:
        kwargs = {'user_id': uid, 'user_secret': usec}
        if start:
            kwargs['start_date'] = start
        resp = client.transactions_and_reporting.get_activities(**kwargs)
        return jsonify(resp.body)
    except st.ApiException as e:
        body = e.body if isinstance(e.body, dict) else {'error': str(e.body)[:200]}
        return jsonify(body), e.status
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    log.info(f"Starting NexusSphere on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
