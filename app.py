import os
import json
import base64
import hashlib
import hmac
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'akshu-super-secret-key-2026')

# ============================
# AKSHU CONFIGURATION
# ============================
ADMIN_USERNAME = "akshu"
ADMIN_PASSWORD_HASH = generate_password_hash("akshu123")

# MASTER XOR KEY
XOR_KEY = "PQRSTU3456789&*CDEFGHIJKLMNOPQRSTUVdefgh',<GHIJKLMNOPQRSTUVWjklmnopqrstuvwxy3456,<>?/`~JKLMNOPQRSTUVFGHIJKLMNOlmn2345^&*()-CDEFGHIJKLMNOPQRSTUVWXefghijklmnopqrst7KLMNOPQRSTU45678[]{}|;:',<>tu2)-_=+[]ij23456IJKLMNQRSTUVWbcdefghijklmnopqrstGHIJKLMNhijklmnopqrstuvwxy01234STUVWXYdefghijklmnopqrstuvw=+[]{}|;:',<>?/CDEFGHI|;:',<>?"

# Data storage files
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

KEYS_FILE = os.path.join(DATA_DIR, 'keys.json')
SCRIPTS_FILE = os.path.join(DATA_DIR, 'scripts.json')

# ============================
# XOR ENCRYPTION / DECRYPTION
# ============================
def xor_encrypt(data, key):
    if isinstance(data, str):
        data = data.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    result = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % key_len])
    
    return bytes(result)

def xor_encrypt_string(text, key):
    encrypted = xor_encrypt(text, key)
    return base64.b64encode(encrypted).decode('utf-8')

def xor_decrypt_string(b64_text, key):
    try:
        encrypted = base64.b64decode(b64_text)
        decrypted = xor_encrypt(encrypted, key)
        return decrypted.decode('utf-8')
    except:
        return None

# ============================
# DATA MANAGEMENT
# ============================
def load_data():
    keys = {}
    scripts = {}
    
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r') as f:
                keys = json.load(f)
        except:
            keys = {}
    
    if os.path.exists(SCRIPTS_FILE):
        try:
            with open(SCRIPTS_FILE, 'r') as f:
                scripts = json.load(f)
        except:
            scripts = {}
    
    return keys, scripts

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def save_scripts(scripts):
    with open(SCRIPTS_FILE, 'w') as f:
        json.dump(scripts, f, indent=2)

# ============================
# AUTHENTICATION
# ============================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================
# ROUTES
# ============================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    keys, scripts = load_data()
    return render_template('dashboard.html', keys=keys, scripts=scripts, admin_name="Akshu")

@app.route('/api/keys', methods=['GET'])
@login_required
def get_keys():
    keys, _ = load_data()
    return jsonify({"success": True, "keys": keys})

@app.route('/api/keys', methods=['POST'])
@login_required
def create_key():
    data = request.get_json()
    key_name = data.get('name', '').strip()
    xor_key = data.get('xor_key', '').strip()
    
    if not key_name or not xor_key:
        return jsonify({"success": False, "error": "Key name and XOR key required"}), 400
    
    keys, _ = load_data()
    
    key_id = hashlib.md5(f"{key_name}{time.time()}".encode()).hexdigest()[:12]
    
    keys[key_id] = {
        "id": key_id,
        "name": key_name,
        "xor_key": xor_key,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    
    save_keys(keys)
    return jsonify({"success": True, "key": keys[key_id]})

@app.route('/api/keys/<key_id>', methods=['DELETE'])
@login_required
def delete_key(key_id):
    keys, _ = load_data()
    if key_id in keys:
        del keys[key_id]
        save_keys(keys)
        return jsonify({"success": True, "message": "Key deleted"})
    return jsonify({"success": False, "error": "Key not found"}), 404

@app.route('/api/scripts', methods=['GET'])
@login_required
def get_scripts():
    _, scripts = load_data()
    return jsonify({"success": True, "scripts": scripts})

@app.route('/api/scripts', methods=['POST'])
@login_required
def create_script():
    data = request.get_json()
    script_name = data.get('name', '').strip()
    script_code = data.get('code', '').strip()
    key_id = data.get('key_id', '').strip()
    
    if not script_name or not script_code:
        return jsonify({"success": False, "error": "Script name and code required"}), 400
    
    keys, scripts = load_data()
    
    script_id = hashlib.md5(f"{script_name}{time.time()}".encode()).hexdigest()[:12]
    
    encrypted_code = None
    xor_key_value = None
    if key_id and key_id in keys:
        xor_key_value = keys[key_id]['xor_key']
        encrypted_code = xor_encrypt_string(script_code, xor_key_value)
    
    scripts[script_id] = {
        "id": script_id,
        "name": script_name,
        "code": script_code,
        "encrypted_code": encrypted_code,
        "key_id": key_id,
        "xor_key": xor_key_value,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    
    script_file = os.path.join(SCRIPTS_DIR, f"{script_id}.lua")
    with open(script_file, 'w') as f:
        f.write(script_code)
    
    save_scripts(scripts)
    return jsonify({"success": True, "script": scripts[script_id]})

@app.route('/api/scripts/<script_id>', methods=['DELETE'])
@login_required
def delete_script(script_id):
    keys, scripts = load_data()
    if script_id in scripts:
        del scripts[script_id]
        save_scripts(scripts)
        script_file = os.path.join(SCRIPTS_DIR, f"{script_id}.lua")
        if os.path.exists(script_file):
            os.remove(script_file)
        return jsonify({"success": True, "message": "Script deleted"})
    return jsonify({"success": False, "error": "Script not found"}), 404

@app.route('/api/run/<script_id>', methods=['POST'])
def run_script(script_id):
    data = request.get_json() or {}
    provided_key = data.get('key', '').strip()
    
    keys, scripts = load_data()
    
    if script_id not in scripts:
        return jsonify({"success": False, "error": "Script not found"}), 404
    
    script = scripts[script_id]
    
    if script.get('key_id'):
        if not provided_key:
            return jsonify({"success": False, "error": "XOR Key required in request body"}), 403
        
        expected_key = script.get('xor_key', '')
        if provided_key != expected_key:
            return jsonify({"success": False, "error": "Invalid XOR Key"}), 403
        
        encrypted = script.get('encrypted_code')
        if encrypted:
            decrypted = xor_decrypt_string(encrypted, provided_key)
            if decrypted:
                return jsonify({
                    "success": True,
                    "script_name": script['name'],
                    "code": decrypted,
                    "encrypted": False,
                    "message": "XOR Key verified! Script decrypted and ready to run",
                    "server": "Akshu Server"
                })
    
    return jsonify({
        "success": True,
        "script_name": script['name'],
        "code": script['code'],
        "encrypted": False,
        "message": "Script ready to run",
        "server": "Akshu Server"
    })

@app.route('/api/validate-key', methods=['POST'])
def validate_key():
    data = request.get_json() or {}
    key_value = data.get('key', '').strip()
    
    if not key_value:
        return jsonify({"success": False, "error": "XOR Key required"}), 400
    
    keys, _ = load_data()
    
    for key_id, key_data in keys.items():
        if key_data.get('xor_key') == key_value and key_data.get('status') == 'active':
            return jsonify({
                "success": True,
                "valid": True,
                "key_name": key_data['name'],
                "key_id": key_id,
                "message": "XOR Key is valid!"
            })
    
    return jsonify({"success": False, "valid": False, "error": "Invalid or expired XOR Key"}), 403

@app.route('/api/scripts/public', methods=['GET'])
def public_scripts():
    _, scripts = load_data()
    public_list = {}
    for sid, sdata in scripts.items():
        public_list[sid] = {
            "id": sid,
            "name": sdata['name'],
            "requires_key": bool(sdata.get('key_id')),
            "created_at": sdata.get('created_at', '')
        }
    return jsonify({"success": True, "scripts": public_list})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "server": "Akshu Server", "version": "1.0"})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
