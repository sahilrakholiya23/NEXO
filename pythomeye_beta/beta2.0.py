"""
PhantomEye: Hackathon-Ready Honeypot + Proxy + Dashboard
Single file version.

Features:
 - Proxy (8080): inspects incoming traffic for suspicious patterns.
 - Backend (5000): normal site.
 - Honeypot (7000): serves cloned site or fake admin panel, logs attacker activity.
 - Dashboard (5001): shows live attack logs + honeypot captures.
 - Email Alerts (Gmail App Password required).
 - First run: asks user for target website, clones it (pywebcopy), stores config.json.
"""

import os, re, asyncio, threading, datetime, smtplib, json
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from pywebcopy import save_website
import logging

# ------------------------
# Configurable Ports
# ------------------------
PROXY_PORT = 8080
BACKEND_PORT = 5000
HONEYPOT_PORT = 7000
DASH_PORT = 5001

# Email config (from env vars)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.environ.get("PHANTOM_EMAIL_USER")
EMAIL_PASS = os.environ.get("PHANTOM_EMAIL_PASS")
EMAIL_TO   = os.environ.get("PHANTOM_EMAIL_TO")

# Log files
ATTACK_LOG = "attack_logs.txt"
HONEYPOT_LOG = "honeypot_logs.txt"

# Attack patterns
ATTACK_PATTERNS = [
    re.compile(r"(union\s+select|or\s+1=1|--|sleep\()", re.I),
    re.compile(r"(<script.*?>|onerror\s*=|alert\()", re.I),
    re.compile(r"(/etc/passwd|\.\./\.\./)", re.I),
    re.compile(r"(sqlmap|nikto|nmap|curl|wget|masscan)", re.I),
]

# ------------------------
# Helper: Email Alerts
# ------------------------
def send_email_alert(ip, snippet):
    if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
        print("[!] Email not configured, skipping")
        return
    subject = "🚨 PhantomEye Attack Alert 🚨"
    body = f"Time: {datetime.datetime.now()}\nIP: {ip}\nSnippet:\n{snippet}\n"
    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, message)
        print("[+] Email alert sent")
    except Exception as e:
        print("[!] Email send failed:", e)

def async_alert(ip, snippet):
    threading.Thread(target=send_email_alert, args=(ip, snippet), daemon=True).start()

# ------------------------
# Honeypot App
# ------------------------
honeypot_app = Flask("honeypot_app")
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# check config for cloned site
CLONE_FOLDER = "honeypot_clone/clone_site"
CONFIG_FILE = "config.json"
CLONE_MODE = os.path.exists(CONFIG_FILE)

if CLONE_MODE:
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
        CLONE_URL = cfg["url"]
else:
    CLONE_URL = None

@honeypot_app.route("/", defaults={"path": ""})
@honeypot_app.route("/<path:path>", methods=["GET","POST"])
def serve_clone(path):
    ip = request.remote_addr
    ts = datetime.datetime.now()
    entry = f"[{ts}] {ip} visited {path} | UA={request.headers.get('User-Agent','')}\n"
    with open(HONEYPOT_LOG, "a") as f: f.write(entry)

    if CLONE_MODE:
        local_path = os.path.join(CLONE_FOLDER, path)
        if os.path.isdir(local_path):
            return send_from_directory(local_path, "index.html")
        if os.path.exists(local_path):
            return send_from_directory(CLONE_FOLDER, path)
        return "404 page", 404
    else:
        # fallback fake admin panel
        return """
        <h1 style="color:#ff2e63">Admin Panel</h1>
        <form action="/login" method="post">
          <input name="username" placeholder="user"><br><br>
          <input type="password" name="password" placeholder="pass"><br><br>
          <button>Login</button>
        </form>
        """

@honeypot_app.route("/login", methods=["POST"])
def hp_login():
    ip = request.remote_addr
    ts = datetime.datetime.now()
    entry = f"[{ts}] {ip} POST /login username={request.form.get('username')} password={request.form.get('password')}\n"
    with open(HONEYPOT_LOG, "a") as f: f.write(entry)
    return "<p style='color:red'>Access Denied. Activity logged.</p>"

def run_honeypot():
    honeypot_app.run(port=HONEYPOT_PORT, debug=False, use_reloader=False)

# ------------------------
# Backend App
# ------------------------
backend_app = Flask("backend_app")

@backend_app.route("/")
def home():
    return "<h1>Main Website ✅</h1><p>This is the real backend.</p>"

def run_backend():
    backend_app.run(port=BACKEND_PORT, debug=False, use_reloader=False)

# ------------------------
# Dashboard App
# ------------------------
dash_app = Flask("dash_app")

DASH_HTML = """<!doctype html><html><head><title>PhantomEye Dashboard</title></head>
<body style="background:#111;color:#eee;font-family:monospace">
<h1>🛡 PhantomEye Dashboard</h1>
<h2>Recent Attacks</h2><pre id="attacks">Loading...</pre>
<h2>Honeypot Captures</h2><pre id="honeypot">Loading...</pre>
<script>
async function refresh(){
  let a=await fetch('/attacks');document.getElementById('attacks').innerText=await a.text();
  let h=await fetch('/honeypot_logs');document.getElementById('honeypot').innerText=await h.text();
}
refresh();setInterval(refresh,3000);
</script></body></html>"""

@dash_app.route("/")
def dash():
    return DASH_HTML

@dash_app.route("/attacks")
def attacks():
    if not os.path.exists(ATTACK_LOG): return ""
    return open(ATTACK_LOG).read()[-5000:]

@dash_app.route("/honeypot_logs")
def hplogs():
    if not os.path.exists(HONEYPOT_LOG): return ""
    return open(HONEYPOT_LOG).read()[-5000:]

def run_dash():
    dash_app.run(port=DASH_PORT, debug=False, use_reloader=False)

# ------------------------
# Proxy (Async)
# ------------------------
async def handle_client(reader, writer):
    src_ip = writer.get_extra_info('peername')[0]
    try:
        data = await reader.read(2048)
        if not data: return
        header = data.decode(errors="ignore")
        snippet = "\n".join(header.splitlines()[:10])
        suspicious = any(p.search(header) for p in ATTACK_PATTERNS)

        ts = datetime.datetime.now()
        if suspicious:
            with open(ATTACK_LOG,"a") as f: f.write(f"[{ts}] {src_ip} SUSPICIOUS => {snippet}\n")
            async_alert(src_ip, snippet)
            resp = f"HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1:{HONEYPOT_PORT}/\r\n\r\n"
            writer.write(resp.encode()); await writer.drain()
        else:
            with open(ATTACK_LOG,"a") as f: f.write(f"[{ts}] {src_ip} SAFE => {snippet}\n")
            backend = await asyncio.open_connection("127.0.0.1", BACKEND_PORT)
            backend[1].write(data); await backend[1].drain()
            async def pipe(src,dst):
                while True:
                    chunk=await src.read(4096)
                    if not chunk: break
                    dst.write(chunk); await dst.drain()
            await asyncio.gather(pipe(reader,backend[1]),pipe(backend[0],writer))
    except Exception as e:
        print("Proxy error:",e)
    finally:
        writer.close()

async def start_proxy():
    server = await asyncio.start_server(handle_client,"0.0.0.0",PROXY_PORT)
    print(f"Proxy on :{PROXY_PORT} (backend {BACKEND_PORT}, honeypot {HONEYPOT_PORT})")
    async with server: await server.serve_forever()

# ------------------------
# Main Runner
# ------------------------
if __name__ == "__main__":
    # First-run clone prompt
    if not CLONE_MODE:
        url = input("Enter your website URL to clone for honeypot (or press Enter to skip): ").strip()
        if url:
            save_website(url=url, project_folder="honeypot_clone", project_name="clone_site", bypass_robots=True)
            with open(CONFIG_FILE,"w") as f: json.dump({"url":url},f)
            print("Cloned site saved for honeypot.")

    threading.Thread(target=run_backend,daemon=True).start()
    threading.Thread(target=run_honeypot,daemon=True).start()
    threading.Thread(target=run_dash,daemon=True).start()
    try: asyncio.run(start_proxy())
    except KeyboardInterrupt: print("Shutting down PhantomEye.")
