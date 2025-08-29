"""
phantomeye_demo_ui.py
Single-file PhantomEye demo:
 - Async socket proxy (port 8080) does header-level inspection and redirects suspicious requests to honeypot.
 - Backend Flask app (port 5000) simulates the real site.
 - Honeypot Flask app (port 7000) logs attacker activity.
 - Dashboard Flask app (port 5001) shows live events from logs (AJAX refresh).

Usage:
  1) pip install flask
  2) Set env vars (optional for email):
       PHANTOM_EMAIL_USER, PHANTOM_EMAIL_PASS, PHANTOM_EMAIL_TO
  3) python phantomeye_demo_ui.py
  4) Open dashboard: http://127.0.0.1:5001/

Test:

Safe request (forwarded to backend):

curl -i http://127.0.0.1:8080/

Suspicious request (redirects instantly to honeypot, logs, and alerts):

curl -i "http://127.0.0.1:8080/?id=1' OR 1=1--"
"""

import os
import threading
import asyncio
import re
import datetime
import smtplib
from flask import Flask, request, jsonify, render_template_string
import logging

# ---------------------
# Configuration
# ---------------------
PROXY_HOST = '0.0.0.0'
PROXY_PORT = int(os.environ.get("PHANTOM_PROXY_PORT", 8080))

BACKEND_HOST = os.environ.get("PHANTOM_BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.environ.get("PHANTOM_BACKEND_PORT", 5000))

HONEYPOT_HOST = os.environ.get("PHANTOM_HONEYPOT_HOST", "127.0.0.1")
HONEYPOT_PORT = int(os.environ.get("PHANTOM_HONEYPOT_PORT", 7000))  # use safe port (7000)

DASH_HOST = os.environ.get("PHANTOM_DASH_HOST", "127.0.0.1")
DASH_PORT = int(os.environ.get("PHANTOM_DASH_PORT", 5001))

# Email (optional)
SMTP_SERVER = os.environ.get("PHANTOM_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("PHANTOM_SMTP_PORT", 587))
EMAIL_USER = os.environ.get("PHANTOM_EMAIL_USER", "rakholiyasahil7@gmail.com") #enter sender email
EMAIL_PASS = os.environ.get("PHANTOM_EMAIL_PASS", "vqlt huyi gdlg vsti") #enter your new app password
EMAIL_TO   = os.environ.get("PHANTOM_EMAIL_TO", "rakholiyasahil78@gmail.com") # enter reciver email

# Logs
ATTACK_LOG = "attack_logs.txt"
HONEYPOT_LOG = "honeypot_logs.txt"

# Quick header-level attack patterns (regex)
ATTACK_PATTERNS = [
    re.compile(r"(union\s+select|or\s+1=1|--|sleep\()", re.I),
    re.compile(r"(<script.*?>|onerror\s*=|alert\()", re.I),
    re.compile(r"(/etc/passwd|\.\./\.\./)", re.I),
    re.compile(r"(sqlmap|nikto|nmap|curl|wget|masscan)", re.I),
]

HEADER_READ_LIMIT = 16 * 1024  # 16 KB

# ---------------------
# Utility: async email alert (non-blocking)
# ---------------------
def send_email_alert(ip, snippet):
    if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
        print("[!] Email not configured; skipping email alert.")
        return
    subject = "PhantomEye Alert"
    body = f"Time: {datetime.datetime.now()}\nSource IP: {ip}\nSnippet:\n{snippet}\n"
    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, message)
        print("[+] Email alert sent")
    except Exception as e:
        print("[!] Failed to send email:", e)

def async_alert(ip, snippet):
    t = threading.Thread(target=send_email_alert, args=(ip, snippet), daemon=True)
    t.start()

# ---------------------
# Honeypot app (Flask)
# ---------------------
honeypot_app = Flask("honeypot_app")
# reduce Flask noise when run in threads
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@honeypot_app.route("/", methods=["GET","POST"])
def hp_home():
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "")
    ts = datetime.datetime.now()
    entry = f"[{ts}] {ip} visited / ; UA={ua}\n"
    with open(HONEYPOT_LOG, "a") as f:
        f.write(entry)
    return """
    <html>
      <head><title>Admin Console</title></head>
      <body style="background:#0b0b0b;color:#c7f9cc;font-family:monospace">
        <h1>Admin Control Panel</h1>
        <p>Login to view settings</p>
        <form action="/login" method="post">
          <input name="username" placeholder="username"><br><br>
          <input name="password" type="password" placeholder="password"><br><br>
          <button style="padding:8px 12px;background:#0f1720;color:#c7f9cc;border:1px solid #1f3d2c">Login</button>
        </form>
      </body>
    </html>
    """

@honeypot_app.route("/login", methods=["POST"])
def hp_login():
    ip = request.remote_addr
    username = request.form.get("username","")
    password = request.form.get("password","")
    ts = datetime.datetime.now()
    entry = f"[{ts}] {ip} POST /login username={username} password={password}\n"
    with open(HONEYPOT_LOG, "a") as f:
        f.write(entry)
    return "<h2 style='font-family:monospace;color:#ff6b6b'>Access Denied</h2><p style='font-family:monospace'>Your activity is monitored.</p>"

def run_honeypot():
    honeypot_app.run(host=HONEYPOT_HOST, port=HONEYPOT_PORT, debug=False, use_reloader=False)

# ---------------------
# Backend app (Flask)
# ---------------------
backend_app = Flask("backend_app")

@backend_app.route("/", methods=["GET","POST"])
def be_home():
    return "<h1 style='font-family:arial'>Main Application</h1><p>This is the real site content.</p>"

@backend_app.route("/login", methods=["POST"])
def be_login():
    username = request.form.get("username","")
    return f"Received login for {username}", 200

def run_backend():
    backend_app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=False, use_reloader=False)

# ---------------------
# Dashboard app (Flask) - simple UI that reads logs
# ---------------------
dash_app = Flask("dash_app")

DASH_HTML = """
<!doctype html>
<html>
<head>
  <title>PhantomEye Dashboard</title>
  <style>
    body {
      background: #050505;
      color: #fff;
      font-family: 'Courier New', monospace;
      padding: 20px;
    }
    h1 {
      font-size: 28px;
      color: #00d4ff;
      text-shadow: 0 0 10px #00d4ff, 0 0 20px #00aacc;
      overflow: hidden;
      white-space: nowrap;
      border-right: 3px solid #00d4ff;
      animation: typing 3s steps(30, end), blink .75s step-end infinite;
    }
    @keyframes typing {
      from { width: 0 }
      to { width: 100% }
    }
    @keyframes blink {
      from, to { border-color: transparent }
      50% { border-color: #00d4ff }
    }
    .status {
      margin: 15px 0;
      font-size: 16px;
      color: #00d4ff;
    }
    .panel {
      padding: 12px;
      border-radius: 10px;
      margin-bottom: 15px;
      background: rgba(0,0,0,0.5);
      border: 2px solid;
      animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .attacks {
      border-color: #ff2e63;
      box-shadow: 0 0 10px #ff2e63, 0 0 20px #ff2e63;
      color: #ff2e63;
    }
    .honeypot {
      border-color: #ffe600;
      box-shadow: 0 0 10px #ffe600, 0 0 20px #ffe600;
      color: #ffe600;
    }
    .safe {
      color: #00ff9d;
      text-shadow: 0 0 5px #00ff9d;
    }
    .attack {
      color: #ff2e63;
      text-shadow: 0 0 5px #ff2e63;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    .status-dot {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 5px;
      animation: pulse 1.5s infinite;
    }
    .green { background: #00ff9d; box-shadow: 0 0 8px #00ff9d; }
    .red { background: #ff2e63; box-shadow: 0 0 8px #ff2e63; }
    @keyframes pulse {
      0% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.2); opacity: 0.7; }
      100% { transform: scale(1); opacity: 1; }
    }
  </style>
</head>
<body>
  <h1><b>🛡 <u>PhantomEye — Live Cyber Defense</u></b></h1>
  <div class="status panel" style="border-color:#00d4ff;box-shadow:0 0 10px #00d4ff;">
    <strong>Status:</strong><br>
    Proxy: <span id="proxy_status"></span>
    Backend: <span id="backend_status"></span>
    Honeypot: <span id="honeypot_status"></span>
  </div>

  <div class="panel attacks">
    <h2><b>🚨 <u>Recent Attacks</b></u></h2>
    <div id="attacks">Loading...</div>
  </div>

  <div class="panel honeypot">
    <h2><b>🎯 <u>Honeypot Captures</b></u></h2>
    <div id="honeypot_logs">Loading...</div>
  </div>

<script>
async function fetchData() {
  try {
    const s = await fetch('/status'); 
    const status = await s.json();
    document.getElementById('proxy_status').innerHTML = status.proxy ? '<span class="status-dot green"></span> Running' : '<span class="status-dot red"></span> Down';
    document.getElementById('backend_status').innerHTML = status.backend ? '<span class="status-dot green"></span> Running' : '<span class="status-dot red"></span> Down';
    document.getElementById('honeypot_status').innerHTML = status.honeypot ? '<span class="status-dot green"></span> Running' : '<span class="status-dot red"></span> Down';

    const a = await fetch('/attacks'); 
    const attacks = await a.text();
    document.getElementById('attacks').innerHTML = attacks ? '<pre>' + colorizeLogs(attacks) + '</pre>' : '<em>No attacks yet</em>';

    const h = await fetch('/honeypot_logs'); 
    const htxt = await h.text();
    document.getElementById('honeypot_logs').innerHTML = htxt ? '<pre>' + htxt + '</pre>' : '<em>No captures yet</em>';
  } catch (e) {
    console.error(e);
  }
}

function colorizeLogs(text) {
  return text
    .replace(/SUSPICIOUS/g, '<span class="attack" color="yellow">SUSPICIOUS</span>')
    .replace(/SAFE/g, '<span class="safe" color="green">SAFE</span>');
}

fetchData();
setInterval(fetchData, 3000);
</script>
</body>
</html>
"""


@dash_app.route("/")
def dash_home():
    return render_template_string(DASH_HTML)

@dash_app.route("/attacks")
def dash_attacks():
    if not os.path.exists(ATTACK_LOG):
        return ""
    with open(ATTACK_LOG, "r") as f:
        data = f.read()[-10000:]  # only last chunk
    # colorize simple markers for display (dashboard handles styles)
    return data

@dash_app.route("/honeypot_logs")
def dash_honeypot_logs():
    if not os.path.exists(HONEYPOT_LOG):
        return ""
    with open(HONEYPOT_LOG, "r") as f:
        data = f.read()[-10000:]
    return data

@dash_app.route("/status")
def dash_status():
    # basic ping: check if backend/honeypot ports are open locally
    import socket
    def is_up(host, port):
        try:
            with socket.create_connection((host, port), timeout=0.4):
                return True
        except:
            return False
    return jsonify({
        "proxy": True,  # proxy runs in same process if this endpoint is reached
        "backend": is_up(BACKEND_HOST, BACKEND_PORT),
        "honeypot": is_up(HONEYPOT_HOST, HONEYPOT_PORT)
    })

def run_dashboard():
    dash_app.run(host=DASH_HOST, port=DASH_PORT, debug=False, use_reloader=False)

# ---------------------
# Proxy code (asyncio-based)
# ---------------------
async def handle_client(reader, writer):
    peer = writer.get_extra_info('peername')
    src_ip = peer[0] if peer else 'unknown'
    try:
        # read headers only (quick)
        buffer = b''
        while b'\r\n\r\n' not in buffer and len(buffer) < HEADER_READ_LIMIT:
            chunk = await reader.read(1024)
            if not chunk:
                break
            buffer += chunk
            if b'\r\n\r\n' in buffer:
                break

        header_text = buffer.decode('latin-1', errors='ignore')
        snippet = '\n'.join(header_text.splitlines()[:20])
        suspicious = False
        for patt in ATTACK_PATTERNS:
            if patt.search(header_text):
                suspicious = True
                break

        ts = datetime.datetime.now()
        if suspicious:
            # log attack quickly
            with open(ATTACK_LOG, "a") as f:
                f.write(f"[{ts}] {src_ip} SUSPICIOUS => {snippet}\n")
            print(f"[!] Suspicious from {src_ip} -> redirecting to honeypot")
            async_alert(src_ip, snippet[:1500])
            # 302 redirect to honeypot
            honeypot_url = f"http://{HONEYPOT_HOST}:{HONEYPOT_PORT}/"
            resp = (
                "HTTP/1.1 302 Found\r\n"
                f"Location: {honeypot_url}\r\n"
                "Content-Length: 0\r\n"
                "Connection: close\r\n\r\n"
            ).encode()
            writer.write(resp)
            await writer.drain()
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            return
        else:
            # log safe request (optional)
            with open(ATTACK_LOG, "a") as f:
                f.write(f"[{ts}] {src_ip} SAFE => {snippet}\n")
            # connect to backend and stream
            try:
                backend_reader, backend_writer = await asyncio.open_connection(BACKEND_HOST, BACKEND_PORT)
            except Exception as e:
                writer.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 11\r\n\r\nBad Gateway")
                await writer.drain()
                try:
                    writer.close(); await writer.wait_closed()
                except:
                    pass
                return

            # send initial header buffer to backend
            if buffer:
                backend_writer.write(buffer)
                await backend_writer.drain()

            # pipe data bi-directionally
            async def pipe(src, dst):
                try:
                    while True:
                        data = await src.read(4096)
                        if not data:
                            break
                        dst.write(data)
                        await dst.drain()
                except Exception:
                    pass
                finally:
                    try:
                        dst.close()
                        await dst.wait_closed()
                    except:
                        pass

            await asyncio.gather(pipe(reader, backend_writer), pipe(backend_reader, writer))

    except Exception as e:
        print("[!] Proxy error:", e)
    finally:
        try:
            writer.close(); await writer.wait_closed()
        except:
            pass

async def start_proxy():
    server = await asyncio.start_server(handle_client, host=PROXY_HOST, port=PROXY_PORT)
    print(f"Proxy listening on {PROXY_HOST}:{PROXY_PORT} -> backend {BACKEND_HOST}:{BACKEND_PORT}, honeypot {HONEYPOT_HOST}:{HONEYPOT_PORT}")
    async with server:
        await server.serve_forever()

# ---------------------
# Start services: backend, honeypot, dashboard in threads; proxy in main loop
# ---------------------
if __name__ == "__main__":
    # warn if email not set
    if not (EMAIL_USER and EMAIL_PASS and EMAIL_TO):
        print("[!] Email not fully configured; email alerts will be skipped. Set PHANTOM_EMAIL_USER, PHANTOM_EMAIL_PASS, PHANTOM_EMAIL_TO to enable.")

    # start backend, honeypot, dashboard in background threads
    t_backend = threading.Thread(target=run_backend, daemon=True)
    t_honeypot = threading.Thread(target=run_honeypot, daemon=True)
    t_dash = threading.Thread(target=run_dashboard, daemon=True)
    t_backend.start()
    t_honeypot.start()
    t_dash.start()

    # run proxy in asyncio main loop
    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        print("Shutting down PhantomEye demo.")
