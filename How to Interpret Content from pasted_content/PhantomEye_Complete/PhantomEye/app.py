
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import re
import os
from datetime import datetime
import json

from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL
from detection_engine import detector
from honeypot_cloner import clone_website
from email_alerts import email_system

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db_connection()
        
        # Enhanced attacks table with more detailed information
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                user_agent TEXT,
                payload TEXT NOT NULL,
                attack_types TEXT,
                severity INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL,
                honeypot_log TEXT,
                blocked BOOLEAN DEFAULT 1,
                country TEXT,
                city TEXT,
                request_method TEXT,
                request_url TEXT,
                headers TEXT
            )
        ''')
        
        # Table for tracking protected websites
        conn.execute('''
            CREATE TABLE IF NOT EXISTS protected_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                added_timestamp TEXT NOT NULL,
                last_cloned TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Table for system logs
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                component TEXT
            )
        ''')
        
        # Table for honeypot interactions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS honeypot_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attack_id INTEGER,
                interaction_type TEXT,
                interaction_data TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (attack_id) REFERENCES attacks (id)
            )
        ''')
        
        conn.commit()
        conn.close()

def log_system_event(level, message, component=None):
    """Log system events"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO system_logs (level, message, timestamp, component) VALUES (?, ?, ?, ?)',
        (level, message, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), component)
    )
    conn.commit()
    conn.close()

@app.before_request
def before_request():
    init_db()
    
    # Check for attacks in all requests
    if request.endpoint not in ['login', 'static']:
        check_request_for_attacks()

def check_request_for_attacks():
    """Check incoming requests for potential attacks"""
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Combine all request data for analysis
    payload_parts = []
    
    # Check URL parameters
    for key, value in request.args.items():
        payload_parts.append(f"{key}={value}")
    
    # Check form data
    if request.method == 'POST':
        for key, value in request.form.items():
            payload_parts.append(f"{key}={value}")
    
    # Check URL path
    payload_parts.append(request.path)
    
    payload = " ".join(payload_parts)
    
    if payload.strip():
        is_attack, attack_types = detector.detect_attack(payload, ip_address, user_agent)
        
        if is_attack:
            severity = detector.get_attack_severity(attack_types)
            log_attack(
                ip_address, 
                payload, 
                attack_types, 
                severity,
                user_agent,
                request.method,
                request.url,
                dict(request.headers)
            )
            
            # Redirect to honeypot for high-severity attacks
            if severity >= 7:
                return redirect(url_for('honeypot'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            log_system_event('INFO', f'Successful login from {request.remote_addr}', 'AUTH')
            return redirect(url_for('dashboard'))
        else:
            log_system_event('WARNING', f'Failed login attempt from {request.remote_addr}', 'AUTH')
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    log_system_event('INFO', f'User logged out from {request.remote_addr}', 'AUTH')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    attacks = conn.execute(
        'SELECT * FROM attacks ORDER BY timestamp DESC LIMIT 50'
    ).fetchall()
    conn.close()
    
    return render_template('dashboard.html', attacks=attacks)

@app.route('/input_url', methods=['GET', 'POST'])
def input_url():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        url = request.form['url']
        
        # Add to protected sites
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO protected_sites (url, added_timestamp) VALUES (?, ?)',
                (url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
            
            # Clone the website
            result = clone_website(url)
            
            # Update last cloned timestamp
            conn.execute(
                'UPDATE protected_sites SET last_cloned = ? WHERE url = ?',
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), url)
            )
            conn.commit()
            
            log_system_event('INFO', f'Website cloned successfully: {url}', 'CLONER')
            message = f'Website cloned successfully! {result}'
            
        except sqlite3.IntegrityError:
            message = 'Website already exists in protected sites.'
        except Exception as e:
            log_system_event('ERROR', f'Failed to clone website {url}: {str(e)}', 'CLONER')
            message = f'Error cloning website: {str(e)}'
        finally:
            conn.close()
            
        return render_template('input_url.html', message=message)
    
    return render_template('input_url.html')

@app.route('/honeypot')
def honeypot():
    payload = request.args.get('payload', '')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Log honeypot access
    log_attack(
        ip_address, 
        payload or 'Direct honeypot access', 
        ['Honeypot Access'],
        3,
        user_agent,
        request.method,
        request.url,
        dict(request.headers),
        'Redirected to honeypot'
    )
    
    log_system_event('WARNING', f'Honeypot accessed by {ip_address}', 'HONEYPOT')
    return render_template('honeypot.html')

@app.route('/api/honeypot-log', methods=['POST'])
def honeypot_log():
    """API endpoint for logging honeypot interactions"""
    try:
        data = request.get_json()
        
        # Find the most recent attack from this IP
        conn = get_db_connection()
        attack = conn.execute(
            'SELECT id FROM attacks WHERE ip = ? ORDER BY timestamp DESC LIMIT 1',
            (request.remote_addr,)
        ).fetchone()
        
        if attack:
            # Log the interaction
            conn.execute(
                'INSERT INTO honeypot_interactions (attack_id, interaction_type, interaction_data, timestamp) VALUES (?, ?, ?, ?)',
                (attack['id'], data.get('action'), json.dumps(data.get('data')), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
        
        conn.close()
        return jsonify({'status': 'logged'})
    except Exception as e:
        log_system_event('ERROR', f'Failed to log honeypot interaction: {str(e)}', 'HONEYPOT')
        return jsonify({'status': 'error'}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    # Get attack statistics
    total_attacks = conn.execute('SELECT COUNT(*) as count FROM attacks').fetchone()['count']
    honeypot_captures = conn.execute('SELECT COUNT(*) as count FROM attacks WHERE honeypot_log IS NOT NULL').fetchone()['count']
    unique_ips = conn.execute('SELECT COUNT(DISTINCT ip) as count FROM attacks').fetchone()['count']
    
    # Get recent attacks
    recent_attacks = conn.execute(
        'SELECT * FROM attacks ORDER BY timestamp DESC LIMIT 10'
    ).fetchall()
    
    # Get attack types distribution
    attack_types = conn.execute(
        'SELECT attack_types, COUNT(*) as count FROM attacks WHERE attack_types IS NOT NULL GROUP BY attack_types'
    ).fetchall()
    
    conn.close()
    
    return jsonify({
        'total_attacks': total_attacks,
        'honeypot_captures': honeypot_captures,
        'unique_ips': unique_ips,
        'recent_attacks': [dict(attack) for attack in recent_attacks],
        'attack_types': [dict(at) for at in attack_types]
    })

def log_attack(ip, payload, attack_types=None, severity=1, user_agent=None, method=None, url=None, headers=None, honeypot_log=None):
    """Enhanced attack logging with detailed information and email alerts"""
    conn = get_db_connection()
    
    # Convert attack_types list to JSON string
    attack_types_json = json.dumps(attack_types) if attack_types else None
    headers_json = json.dumps(headers) if headers else None
    
    conn.execute('''
        INSERT INTO attacks (
            ip, user_agent, payload, attack_types, severity, timestamp, 
            honeypot_log, request_method, request_url, headers
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ip, user_agent, payload, attack_types_json, severity,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        honeypot_log, method, url, headers_json
    ))
    
    conn.commit()
    conn.close()
    
    # Log system event
    attack_type_str = ', '.join(attack_types) if attack_types else 'Unknown'
    log_system_event(
        'CRITICAL' if severity >= 8 else 'WARNING',
        f'Attack detected from {ip}: {attack_type_str}',
        'DETECTION'
    )
    
    # Send email alert for high-severity attacks
    if severity >= 6:  # Send email for medium to high severity attacks
        severity_text = {
            1: 'LOW', 2: 'LOW', 3: 'LOW',
            4: 'MEDIUM', 5: 'MEDIUM', 6: 'MEDIUM',
            7: 'HIGH', 8: 'HIGH', 9: 'CRITICAL', 10: 'CRITICAL'
        }.get(severity, 'UNKNOWN')
        
        attack_data = {
            'ip': ip,
            'payload': payload,
            'attack_types': attack_types,
            'severity': severity,
            'severity_text': severity_text,
            'user_agent': user_agent,
            'method': method,
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'honeypot_log': honeypot_log
        }
        
        # Send email alert asynchronously
        email_system.send_attack_alert(attack_data)
    
    print(f"🚨 ATTACK DETECTED: {ip} - {attack_type_str} - Severity: {severity}")

def log_system_event(level, message, component=None):
    """Log system events with email alerts for critical events"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO system_logs (level, message, timestamp, component) VALUES (?, ?, ?, ?)',
        (level, message, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), component)
    )
    conn.commit()
    conn.close()
    
    # Send email alert for critical system events
    if level in ['CRITICAL', 'ERROR']:
        email_system.send_system_alert(level, message, component)