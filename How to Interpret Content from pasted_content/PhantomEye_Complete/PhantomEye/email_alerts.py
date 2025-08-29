import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json
import threading

from config import SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL

class EmailAlertSystem:
    def __init__(self):
        self.sender_email = SENDER_EMAIL
        self.sender_password = SENDER_PASSWORD
        self.receiver_email = RECEIVER_EMAIL
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_attack_alert(self, attack_data):
        """Send email alert for detected attacks"""
        try:
            # Create email content
            subject = f"🚨 PHANTOMEYE SECURITY ALERT - {attack_data.get('severity_text', 'UNKNOWN')} THREAT DETECTED"
            
            # Create HTML email body
            html_body = self._create_attack_email_html(attack_data)
            text_body = self._create_attack_email_text(attack_data)
            
            # Send email in a separate thread to avoid blocking
            thread = threading.Thread(
                target=self._send_email_async,
                args=(subject, html_body, text_body)
            )
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to send attack alert: {str(e)}")
            return False
    
    def send_system_alert(self, level, message, component=None):
        """Send email alert for system events"""
        try:
            if level not in ['CRITICAL', 'ERROR']:
                return False  # Only send emails for critical/error events
                
            subject = f"🔧 PHANTOMEYE SYSTEM ALERT - {level}"
            
            html_body = self._create_system_email_html(level, message, component)
            text_body = self._create_system_email_text(level, message, component)
            
            # Send email in a separate thread
            thread = threading.Thread(
                target=self._send_email_async,
                args=(subject, html_body, text_body)
            )
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to send system alert: {str(e)}")
            return False
    
    def send_daily_report(self, stats):
        """Send daily security report"""
        try:
            subject = f"📊 PHANTOMEYE DAILY SECURITY REPORT - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_body = self._create_report_email_html(stats)
            text_body = self._create_report_email_text(stats)
            
            # Send email in a separate thread
            thread = threading.Thread(
                target=self._send_email_async,
                args=(subject, html_body, text_body)
            )
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to send daily report: {str(e)}")
            return False
    
    def _send_email_async(self, subject, html_body, text_body):
        """Send email asynchronously"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.receiver_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, "plain")
            html_part = MIMEText(html_body, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.receiver_email, message.as_string())
                
            print(f"✅ Email alert sent successfully: {subject}")
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
    
    def _create_attack_email_html(self, attack_data):
        """Create HTML email body for attack alerts"""
        severity_color = {
            1: "#28a745", 2: "#28a745", 3: "#ffc107", 
            4: "#ffc107", 5: "#fd7e14", 6: "#fd7e14",
            7: "#dc3545", 8: "#dc3545", 9: "#dc3545", 10: "#dc3545"
        }.get(attack_data.get('severity', 1), "#dc3545")
        
        attack_types = attack_data.get('attack_types', [])
        attack_types_str = ', '.join(attack_types) if attack_types else 'Unknown'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff41; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111111; border: 1px solid #333333; border-radius: 10px; padding: 30px; }}
                .header {{ text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 20px; margin-bottom: 30px; }}
                .alert-box {{ background: rgba(255, 7, 58, 0.1); border: 1px solid #ff073a; border-radius: 5px; padding: 20px; margin: 20px 0; }}
                .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: rgba(0, 255, 65, 0.05); border-radius: 5px; }}
                .severity {{ color: {severity_color}; font-weight: bold; font-size: 1.2em; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #333333; color: #888888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ PHANTOMEYE SECURITY ALERT</h1>
                    <p>Real-time Threat Detection System</p>
                </div>
                
                <div class="alert-box">
                    <h2>🚨 ATTACK DETECTED</h2>
                    <p><strong>Timestamp:</strong> {attack_data.get('timestamp', 'Unknown')}</p>
                    <p><strong>Severity Level:</strong> <span class="severity">{attack_data.get('severity', 'Unknown')}/10</span></p>
                    <p><strong>Attack Types:</strong> {attack_types_str}</p>
                </div>
                
                <div class="info-row">
                    <span><strong>Attacker IP:</strong></span>
                    <span>{attack_data.get('ip', 'Unknown')}</span>
                </div>
                
                <div class="info-row">
                    <span><strong>User Agent:</strong></span>
                    <span>{attack_data.get('user_agent', 'Unknown')[:50]}...</span>
                </div>
                
                <div class="info-row">
                    <span><strong>Request Method:</strong></span>
                    <span>{attack_data.get('method', 'Unknown')}</span>
                </div>
                
                <div class="info-row">
                    <span><strong>Target URL:</strong></span>
                    <span>{attack_data.get('url', 'Unknown')}</span>
                </div>
                
                <div class="alert-box">
                    <h3>🔍 ATTACK PAYLOAD</h3>
                    <pre style="background: #000000; padding: 15px; border-radius: 5px; overflow-x: auto; color: #ff073a;">{attack_data.get('payload', 'No payload data')}</pre>
                </div>
                
                <div class="info-row">
                    <span><strong>Status:</strong></span>
                    <span>{'🕸️ Redirected to Honeypot' if attack_data.get('honeypot_log') else '🚫 Attack Blocked'}</span>
                </div>
                
                <div class="footer">
                    <p>This alert was generated by PhantomEye AI-Powered Honeypot Defense System</p>
                    <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_attack_email_text(self, attack_data):
        """Create plain text email body for attack alerts"""
        attack_types = attack_data.get('attack_types', [])
        attack_types_str = ', '.join(attack_types) if attack_types else 'Unknown'
        
        text = f"""
🛡️ PHANTOMEYE SECURITY ALERT
=============================

🚨 ATTACK DETECTED

Timestamp: {attack_data.get('timestamp', 'Unknown')}
Severity Level: {attack_data.get('severity', 'Unknown')}/10
Attack Types: {attack_types_str}

ATTACKER INFORMATION:
- IP Address: {attack_data.get('ip', 'Unknown')}
- User Agent: {attack_data.get('user_agent', 'Unknown')}
- Request Method: {attack_data.get('method', 'Unknown')}
- Target URL: {attack_data.get('url', 'Unknown')}

ATTACK PAYLOAD:
{attack_data.get('payload', 'No payload data')}

STATUS: {'Redirected to Honeypot' if attack_data.get('honeypot_log') else 'Attack Blocked'}

This alert was generated by PhantomEye AI-Powered Honeypot Defense System
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return text
    
    def _create_system_email_html(self, level, message, component):
        """Create HTML email body for system alerts"""
        level_color = {
            'CRITICAL': '#dc3545',
            'ERROR': '#fd7e14',
            'WARNING': '#ffc107',
            'INFO': '#28a745'
        }.get(level, '#ffc107')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff41; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111111; border: 1px solid #333333; border-radius: 10px; padding: 30px; }}
                .header {{ text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 20px; margin-bottom: 30px; }}
                .alert-box {{ background: rgba(255, 170, 0, 0.1); border: 1px solid {level_color}; border-radius: 5px; padding: 20px; margin: 20px 0; }}
                .level {{ color: {level_color}; font-weight: bold; font-size: 1.2em; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #333333; color: #888888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔧 PHANTOMEYE SYSTEM ALERT</h1>
                    <p>System Monitoring & Diagnostics</p>
                </div>
                
                <div class="alert-box">
                    <h2>📊 SYSTEM EVENT</h2>
                    <p><strong>Level:</strong> <span class="level">{level}</span></p>
                    <p><strong>Component:</strong> {component or 'System'}</p>
                    <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="alert-box">
                    <h3>📝 MESSAGE</h3>
                    <pre style="background: #000000; padding: 15px; border-radius: 5px; color: #ffffff;">{message}</pre>
                </div>
                
                <div class="footer">
                    <p>This alert was generated by PhantomEye System Monitor</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_system_email_text(self, level, message, component):
        """Create plain text email body for system alerts"""
        text = f"""
🔧 PHANTOMEYE SYSTEM ALERT
==========================

📊 SYSTEM EVENT

Level: {level}
Component: {component or 'System'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MESSAGE:
{message}

This alert was generated by PhantomEye System Monitor
        """
        return text
    
    def _create_report_email_html(self, stats):
        """Create HTML email body for daily reports"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff41; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111111; border: 1px solid #333333; border-radius: 10px; padding: 30px; }}
                .header {{ text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 20px; margin-bottom: 30px; }}
                .stat-box {{ background: rgba(0, 255, 65, 0.05); border: 1px solid #00ff41; border-radius: 5px; padding: 15px; margin: 10px 0; display: flex; justify-content: space-between; }}
                .stat-number {{ color: #00ff41; font-weight: bold; font-size: 1.5em; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #333333; color: #888888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 PHANTOMEYE DAILY REPORT</h1>
                    <p>Security Summary for {datetime.now().strftime('%Y-%m-%d')}</p>
                </div>
                
                <div class="stat-box">
                    <span>Total Attacks Detected:</span>
                    <span class="stat-number">{stats.get('total_attacks', 0)}</span>
                </div>
                
                <div class="stat-box">
                    <span>Honeypot Captures:</span>
                    <span class="stat-number">{stats.get('honeypot_captures', 0)}</span>
                </div>
                
                <div class="stat-box">
                    <span>Unique Attacker IPs:</span>
                    <span class="stat-number">{stats.get('unique_ips', 0)}</span>
                </div>
                
                <div class="stat-box">
                    <span>High Severity Attacks:</span>
                    <span class="stat-number">{stats.get('high_severity', 0)}</span>
                </div>
                
                <div class="footer">
                    <p>Your infrastructure is protected by PhantomEye</p>
                    <p>Stay vigilant, stay secure! 🛡️</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_report_email_text(self, stats):
        """Create plain text email body for daily reports"""
        text = f"""
📊 PHANTOMEYE DAILY REPORT
==========================

Security Summary for {datetime.now().strftime('%Y-%m-%d')}

STATISTICS:
- Total Attacks Detected: {stats.get('total_attacks', 0)}
- Honeypot Captures: {stats.get('honeypot_captures', 0)}
- Unique Attacker IPs: {stats.get('unique_ips', 0)}
- High Severity Attacks: {stats.get('high_severity', 0)}

Your infrastructure is protected by PhantomEye
Stay vigilant, stay secure! 🛡️
        """
        return text

# Global email alert system instance
email_system = EmailAlertSystem()

