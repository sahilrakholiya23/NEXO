import subprocess
import time
import webbrowser

# Start Backend (port 5000)
backend = subprocess.Popen(["python", "backend.py"])
print("✅ Backend started on http://127.0.0.1:5000")

# Start Honeypot (port 7000)
honeypot = subprocess.Popen(["python", "honeypot.py"])
print("✅ Honeypot started on http://127.0.0.1:7000")

# Start Dashboard (port 5001)
dashboard = subprocess.Popen(["python", "dashboard.py"])
print("✅ Dashboard started on http://127.0.0.1:5001")

# Start Proxy (port 8080)
proxy = subprocess.Popen(["python", "proxy.py"])
print("✅ Proxy started on http://127.0.0.1:8080")

# Wait a bit and open dashboard in browser
time.sleep(3)
webbrowser.open("http://127.0.0.1:5001")

# Keep running until you stop
try:
    backend.wait()
    honeypot.wait()
    dashboard.wait()
    proxy.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping all services...")
    backend.terminate()
    honeypot.terminate()
    dashboard.terminate()
    proxy.terminate()
