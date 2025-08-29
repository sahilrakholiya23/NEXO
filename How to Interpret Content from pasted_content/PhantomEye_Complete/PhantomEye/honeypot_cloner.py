import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
import time
import random

class AdvancedWebsiteCloner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cloned_assets = set()
        
    def clone_website(self, url):
        """Enhanced website cloning with JavaScript and asset support"""
        try:
            print(f"🕸️ Starting advanced cloning of: {url}")
            
            # Fetch the main page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Clone and modify the website
            modified_soup = self._create_honeypot_version(soup, url)
            
            # Add honeypot JavaScript
            honeypot_js = self._create_honeypot_javascript()
            js_tag = soup.new_tag("script")
            js_tag.string = honeypot_js
            modified_soup.head.append(js_tag)
            
            # Add honeypot CSS for visual deception
            honeypot_css = self._create_honeypot_css()
            css_tag = soup.new_tag("style")
            css_tag.string = honeypot_css
            modified_soup.head.append(css_tag)
            
            # Save the honeypot HTML
            with open("templates/honeypot.html", "w", encoding='utf-8') as f:
                f.write(str(modified_soup))
            
            # Create additional honeypot pages
            self._create_additional_honeypot_pages(soup, url)
            
            print("✅ Advanced website cloning completed successfully!")
            return "Advanced cloning completed with JavaScript support and enhanced deception!"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during cloning: {str(e)}"
            print(f"❌ {error_msg}")
            self._create_fallback_honeypot()
            return error_msg
        except Exception as e:
            error_msg = f"Error during advanced cloning: {str(e)}"
            print(f"❌ {error_msg}")
            self._create_fallback_honeypot()
            return error_msg
    
    def _create_honeypot_version(self, soup, base_url):
        """Create a deceptive honeypot version of the website"""
        
        # Modify all forms to be honeypots
        for form in soup.find_all("form"):
            # Change form action to honeypot endpoint
            form["action"] = "/honeypot"
            form["method"] = "post"
            
            # Add hidden honeypot fields
            honeypot_field = soup.new_tag("input", type="hidden", name="honeypot_trap", value="true")
            form.append(honeypot_field)
            
            # Modify submit buttons
            for submit_btn in form.find_all(["input", "button"], type="submit"):
                submit_btn["onclick"] = "return honeypotSubmit(this.form);"
        
        # Modify all links to point to honeypot
        for link in soup.find_all("a", href=True):
            original_href = link["href"]
            if original_href.startswith("http"):
                # External links - redirect to honeypot with original URL as parameter
                link["href"] = f"/honeypot?redirect={original_href}"
            elif original_href.startswith("/"):
                # Internal links - redirect to honeypot
                link["href"] = f"/honeypot?page={original_href}"
            else:
                # Relative links
                link["href"] = f"/honeypot?page={original_href}"
            
            # Add JavaScript tracking
            link["onclick"] = f"honeypotTrackClick('{original_href}'); return true;"
        
        # Modify images to use placeholder or cached versions
        for img in soup.find_all("img", src=True):
            original_src = img["src"]
            if original_src.startswith("http"):
                # For external images, use a placeholder
                img["src"] = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlPC90ZXh0Pjwvc3ZnPg=="
            
            # Add error tracking
            img["onerror"] = f"honeypotTrackError('image', '{original_src}');"
        
        # Add fake admin/login areas
        self._add_fake_admin_elements(soup)
        
        # Modify JavaScript sources
        for script in soup.find_all("script", src=True):
            original_src = script["src"]
            # Replace with honeypot JavaScript
            script["src"] = "/static/honeypot.js"
            script["data-original"] = original_src
        
        return soup
    
    def _create_honeypot_javascript(self):
        """Create JavaScript for honeypot functionality"""
        js_code = """
        // PhantomEye Honeypot JavaScript
        (function() {
            'use strict';
            
            // Track all user interactions
            let interactions = [];
            let sessionId = 'hp_' + Math.random().toString(36).substr(2, 9);
            
            // Log interaction function
            function logInteraction(type, data) {
                interactions.push({
                    type: type,
                    data: data,
                    timestamp: new Date().toISOString(),
                    sessionId: sessionId
                });
                
                // Send to server
                fetch('/api/honeypot-log', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: type,
                        data: data,
                        sessionId: sessionId
                    })
                }).catch(() => {}); // Silent fail
            }
            
            // Track page load
            logInteraction('page_load', {
                url: window.location.href,
                referrer: document.referrer,
                userAgent: navigator.userAgent,
                screen: {
                    width: screen.width,
                    height: screen.height
                }
            });
            
            // Track clicks
            document.addEventListener('click', function(e) {
                logInteraction('click', {
                    element: e.target.tagName,
                    id: e.target.id,
                    className: e.target.className,
                    text: e.target.textContent ? e.target.textContent.substring(0, 100) : '',
                    coordinates: {
                        x: e.clientX,
                        y: e.clientY
                    }
                });
            });
            
            // Track form submissions
            window.honeypotSubmit = function(form) {
                let formData = {};
                for (let element of form.elements) {
                    if (element.name) {
                        formData[element.name] = element.value;
                    }
                }
                
                logInteraction('form_submit', {
                    action: form.action,
                    method: form.method,
                    data: formData
                });
                
                // Show fake loading and error
                setTimeout(() => {
                    alert('Connection timeout. Please try again later.');
                }, 1000 + Math.random() * 2000);
                
                return false; // Prevent actual submission
            };
            
            // Track link clicks
            window.honeypotTrackClick = function(href) {
                logInteraction('link_click', {
                    href: href,
                    text: event.target.textContent
                });
            };
            
            // Track errors
            window.honeypotTrackError = function(type, source) {
                logInteraction('error', {
                    type: type,
                    source: source
                });
            };
            
            // Track key presses
            document.addEventListener('keydown', function(e) {
                if (e.target.type === 'password' || e.target.type === 'text') {
                    logInteraction('keypress', {
                        element: e.target.name || e.target.id,
                        key: e.key,
                        target: e.target.tagName
                    });
                }
            });
            
            // Track mouse movements (sampled)
            let mouseTrackingInterval = setInterval(() => {
                document.addEventListener('mousemove', function(e) {
                    if (Math.random() < 0.01) { // Sample 1% of movements
                        logInteraction('mouse_move', {
                            x: e.clientX,
                            y: e.clientY
                        });
                    }
                });
            }, 1000);
            
            // Track attempts to access developer tools
            let devtools = {open: false, orientation: null};
            setInterval(() => {
                if (window.outerHeight - window.innerHeight > 200 || 
                    window.outerWidth - window.innerWidth > 200) {
                    if (!devtools.open) {
                        devtools.open = true;
                        logInteraction('devtools_open', {
                            method: 'size_detection'
                        });
                    }
                }
            }, 500);
            
            // Fake admin panel detection
            if (window.location.pathname.includes('admin') || 
                window.location.pathname.includes('wp-admin') ||
                window.location.pathname.includes('login')) {
                logInteraction('admin_access_attempt', {
                    path: window.location.pathname,
                    search: window.location.search
                });
            }
            
            // Fake database queries for SQL injection attempts
            window.query = function(sql) {
                logInteraction('sql_injection_attempt', {
                    query: sql
                });
                return "Error: Access denied";
            };
            
            // Fake file system access
            window.readFile = function(path) {
                logInteraction('file_access_attempt', {
                    path: path
                });
                return "Error: Permission denied";
            };
            
            // Create fake vulnerabilities
            window.eval = function(code) {
                logInteraction('code_injection_attempt', {
                    code: code.substring(0, 500)
                });
                return "Error: Function disabled";
            };
            
        })();
        """
        return js_code
    
    def _create_honeypot_css(self):
        """Create CSS for visual deception"""
        css_code = """
        /* PhantomEye Honeypot CSS */
        
        /* Hide real admin elements and show fake ones */
        .admin-hidden { display: none !important; }
        .fake-admin { display: block !important; }
        
        /* Fake loading animations */
        .fake-loading {
            position: relative;
            overflow: hidden;
        }
        
        .fake-loading::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        /* Fake error states */
        .fake-error {
            border: 1px solid #ff0000 !important;
            background-color: #ffe6e6 !important;
        }
        
        /* Slow down interactions to seem more realistic */
        button, input[type="submit"] {
            transition: all 0.3s ease;
        }
        
        /* Fake security badges */
        .security-badge {
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 9999;
        }
        """
        return css_code
    
    def _add_fake_admin_elements(self, soup):
        """Add fake admin/login elements to attract attackers"""
        
        # Add fake admin link in footer
        footer = soup.find('footer') or soup.find('body')
        if footer:
            admin_link = soup.new_tag("a", href="/honeypot?admin=true", style="display:none;")
            admin_link.string = "Admin Panel"
            admin_link["onclick"] = "honeypotTrackClick('/admin'); return true;"
            footer.append(admin_link)
        
        # Add fake security badge
        security_badge = soup.new_tag("div", class_="security-badge")
        security_badge.string = "🔒 Secured by SSL"
        soup.body.append(security_badge)
        
        # Add fake hidden form for credential harvesting
        hidden_form = soup.new_tag("form", action="/honeypot", method="post", style="display:none;", id="hidden-login")
        
        username_input = soup.new_tag("input", type="text", name="username", placeholder="Username")
        password_input = soup.new_tag("input", type="password", name="password", placeholder="Password")
        submit_btn = soup.new_tag("input", type="submit", value="Login")
        
        hidden_form.append(username_input)
        hidden_form.append(password_input)
        hidden_form.append(submit_btn)
        
        soup.body.append(hidden_form)
    
    def _create_additional_honeypot_pages(self, soup, base_url):
        """Create additional honeypot pages for common attack targets"""
        
        # Create fake admin page
        admin_html = self._create_fake_admin_page()
        with open("templates/admin_honeypot.html", "w", encoding='utf-8') as f:
            f.write(admin_html)
        
        # Create fake login page
        login_html = self._create_fake_login_page()
        with open("templates/login_honeypot.html", "w", encoding='utf-8') as f:
            f.write(login_html)
        
        # Create fake database page
        db_html = self._create_fake_database_page()
        with open("templates/db_honeypot.html", "w", encoding='utf-8') as f:
            f.write(db_html)
    
    def _create_fake_admin_page(self):
        """Create a fake admin panel page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel - Secure Access</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
                .admin-panel { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .nav { display: flex; gap: 20px; margin-bottom: 30px; }
                .nav a { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .content { background: #f8f9fa; padding: 20px; border-radius: 5px; }
                .fake-data { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #28a745; }
            </style>
        </head>
        <body>
            <div class="admin-panel">
                <div class="header">
                    <h1>🔐 Admin Control Panel</h1>
                    <p>Secure Administrative Interface</p>
                </div>
                
                <div class="nav">
                    <a href="/honeypot?page=users" onclick="honeypotTrackClick('/admin/users')">Users</a>
                    <a href="/honeypot?page=settings" onclick="honeypotTrackClick('/admin/settings')">Settings</a>
                    <a href="/honeypot?page=database" onclick="honeypotTrackClick('/admin/database')">Database</a>
                    <a href="/honeypot?page=logs" onclick="honeypotTrackClick('/admin/logs')">Logs</a>
                </div>
                
                <div class="content">
                    <h3>System Status</h3>
                    <div class="fake-data">Server Status: Online</div>
                    <div class="fake-data">Database: Connected</div>
                    <div class="fake-data">Last Backup: 2 hours ago</div>
                    <div class="fake-data">Active Users: 1,247</div>
                    
                    <h3>Quick Actions</h3>
                    <form action="/honeypot" method="post" onsubmit="return honeypotSubmit(this);">
                        <input type="hidden" name="action" value="admin_action">
                        <button type="submit">Backup Database</button>
                        <button type="submit">Clear Cache</button>
                        <button type="submit">Update System</button>
                    </form>
                </div>
            </div>
            
            <script>
                // Fake admin functionality
                function honeypotSubmit(form) {
                    alert('Processing... Please wait.');
                    setTimeout(() => {
                        alert('Operation completed successfully.');
                    }, 2000);
                    return false;
                }
                
                function honeypotTrackClick(url) {
                    console.log('Admin navigation:', url);
                }
            </script>
        </body>
        </html>
        """
    
    def _create_fake_login_page(self):
        """Create a fake login page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Secure Login</title>
            <style>
                body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .login-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); max-width: 400px; width: 100%; }
                .form-group { margin-bottom: 20px; }
                .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
                .btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
                .btn:hover { background: #0056b3; }
                .security-info { margin-top: 20px; padding: 10px; background: #e7f3ff; border-radius: 5px; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>🔐 Secure Access Portal</h2>
                <p>Please enter your credentials to continue</p>
                
                <form action="/honeypot" method="post" onsubmit="return honeypotSubmit(this);">
                    <input type="hidden" name="login_attempt" value="true">
                    
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <button type="submit" class="btn">Login</button>
                </form>
                
                <div class="security-info">
                    🛡️ This connection is secured with 256-bit SSL encryption
                </div>
            </div>
            
            <script>
                function honeypotSubmit(form) {
                    // Simulate authentication delay
                    document.querySelector('.btn').innerHTML = 'Authenticating...';
                    document.querySelector('.btn').disabled = true;
                    
                    setTimeout(() => {
                        alert('Authentication failed. Please check your credentials.');
                        document.querySelector('.btn').innerHTML = 'Login';
                        document.querySelector('.btn').disabled = false;
                    }, 2000);
                    
                    return false;
                }
            </script>
        </body>
        </html>
        """
    
    def _create_fake_database_page(self):
        """Create a fake database interface"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Manager</title>
            <style>
                body { font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; margin: 0; padding: 20px; }
                .terminal { background: #000; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .query-box { width: 100%; background: #333; color: #fff; padding: 10px; border: none; font-family: 'Courier New', monospace; }
                .result { background: #222; padding: 15px; margin: 10px 0; border-left: 3px solid #00ff00; }
                .error { border-left-color: #ff0000; color: #ff6666; }
            </style>
        </head>
        <body>
            <div class="terminal">
                <h2>💾 Database Management Console</h2>
                <p>Connected to: production_db@localhost:3306</p>
                <p>User: admin | Privileges: ALL</p>
            </div>
            
            <form action="/honeypot" method="post" onsubmit="return executeQuery(this);">
                <textarea class="query-box" name="query" placeholder="Enter SQL query..." rows="5"></textarea><br><br>
                <button type="submit">Execute Query</button>
            </form>
            
            <div id="results">
                <div class="result">
                    > SHOW TABLES;<br>
                    +------------------+<br>
                    | Tables_in_db     |<br>
                    +------------------+<br>
                    | users            |<br>
                    | products         |<br>
                    | orders           |<br>
                    | admin_users      |<br>
                    +------------------+<br>
                    4 rows in set (0.001 sec)
                </div>
            </div>
            
            <script>
                function executeQuery(form) {
                    const query = form.query.value;
                    const results = document.getElementById('results');
                    
                    // Log the SQL injection attempt
                    console.log('SQL Query attempt:', query);
                    
                    // Simulate query execution
                    setTimeout(() => {
                        const resultDiv = document.createElement('div');
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = '> ' + query + '<br>ERROR 1045 (28000): Access denied for user \'admin\'@\'localhost\'';
                        results.appendChild(resultDiv);
                    }, 1000);
                    
                    return false;
                }
            </script>
        </body>
        </html>
        """
    
    def _create_fallback_honeypot(self):
        """Create a basic fallback honeypot if cloning fails"""
        fallback_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Secure Portal</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .form-group { margin-bottom: 20px; }
                .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔐 Secure Access Required</h2>
                <form action="/honeypot" method="post" onsubmit="return false;">
                    <div class="form-group">
                        <input type="text" name="username" placeholder="Username" required>
                    </div>
                    <div class="form-group">
                        <input type="password" name="password" placeholder="Password" required>
                    </div>
                    <button type="submit" class="btn">Access System</button>
                </form>
            </div>
        </body>
        </html>
        """
        
        with open("templates/honeypot.html", "w", encoding='utf-8') as f:
            f.write(fallback_html)

# Global cloner instance
advanced_cloner = AdvancedWebsiteCloner()

def clone_website(url):
    """Wrapper function for backward compatibility"""
    return advanced_cloner.clone_website(url)


