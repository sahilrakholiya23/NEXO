# 🛡️ PhantomEye - AI-Powered Honeypot Defense System

**Advanced Cybersecurity Solution with Dark Theme Interface**

PhantomEye is a sophisticated honeypot defense system that protects your web infrastructure by creating deceptive clones of your websites to trap and analyze attackers. Built with Flask and featuring a professional dark cybersecurity theme.

## 🌟 Features

### 🔒 Core Security Features
- **Real-time Attack Detection**: AI-powered pattern recognition for various attack types
- **Advanced Website Cloning**: Creates realistic honeypot versions with JavaScript support
- **Intelligent Honeypot System**: Traps attackers with convincing fake interfaces
- **Comprehensive Attack Logging**: Detailed database storage of all security incidents
- **Email Alert System**: Instant notifications for high-severity threats
- **Interactive Dashboard**: Real-time monitoring and analytics

### 🎨 User Interface
- **Dark Cybersecurity Theme**: Professional Matrix-style green/red color scheme
- **Animated Elements**: Glowing borders, scan lines, and Matrix rain effects
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Terminal Aesthetic**: Courier New monospace font for authentic hacker feel
- **Command Center Layout**: Professional security operations center interface

### 🕸️ Honeypot Capabilities
- **Multi-page Honeypots**: Admin panels, login pages, database interfaces
- **JavaScript Tracking**: Comprehensive user interaction monitoring
- **Form Harvesting**: Captures attacker credentials and inputs
- **Behavioral Analysis**: Tracks mouse movements, clicks, and keystrokes
- **Fake Vulnerabilities**: Simulated SQL injection and XSS endpoints

## 📁 Project Structure

```
PhantomEye/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── detection_engine.py   # AI attack detection system
├── honeypot_cloner.py    # Advanced website cloning
├── email_alerts.py       # Email notification system
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── login.html       # Dark themed login page
│   ├── dashboard.html   # Command center dashboard
│   ├── input_url.html   # Website protection setup
│   └── honeypot.html    # Dynamic honeypot page
├── static/              # CSS and JavaScript
│   ├── style.css        # Dark cybersecurity theme
│   ├── app.js          # Frontend functionality
│   └── honeypot.js     # Honeypot JavaScript
└── clone_storage/       # Cloned website storage
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7+
- Flask
- SQLite3
- Internet connection for website cloning

### Quick Start

1. **Extract the project:**
   ```bash
   tar -xzf PhantomEye_Complete.tar.gz
   cd PhantomEye
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure email alerts (optional):**
   Edit `config.py` and update email settings:
   ```python
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-app-password"
   RECEIVER_EMAIL = "alerts@yourcompany.com"
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the system:**
   - Open browser to `http://localhost:5000`
   - Login with: `admin` / `phantom123`

## 🎯 Usage Guide

### 1. Initial Login
- Navigate to the login page
- Use default credentials: `admin` / `phantom123`
- Experience the Matrix-themed authentication interface

### 2. Dashboard Overview
- **Real-time Monitoring**: View live attack detection status
- **Statistics Cards**: Track total attacks, honeypot captures, unique IPs
- **Threat Level Indicator**: Current security status display
- **Quick Actions**: Access to all system functions

### 3. Adding Website Protection
- Click "Add Website" from the dashboard
- Enter the target website URL (e.g., `https://example.com`)
- Click "Initialize Protection" to create honeypot clone
- System automatically creates deceptive version with tracking

### 4. Monitoring Attacks
- All attacks are logged in real-time to SQLite database
- Email alerts sent for medium to high severity threats
- Dashboard displays recent attack activity
- Detailed logs include IP, payload, attack type, and severity

### 5. Honeypot Interaction
- Attackers redirected to `/honeypot` endpoint
- All interactions tracked and logged
- Fake admin panels and login forms capture credentials
- JavaScript monitors all user behavior

## 🔧 Configuration

### Email Alerts
Configure SMTP settings in `config.py`:
```python
SENDER_EMAIL = "security@yourcompany.com"
SENDER_PASSWORD = "your-app-password"  # Use app-specific password
RECEIVER_EMAIL = "admin@yourcompany.com"
```

### Admin Credentials
Update default login in `config.py`:
```python
ADMIN_USERNAME = "your-username"
ADMIN_PASSWORD = "your-secure-password"
```

### Attack Detection
Customize detection patterns in `detection_engine.py`:
- SQL injection patterns
- XSS attack signatures
- Directory traversal attempts
- Command injection patterns
- Suspicious user agents

## 🛡️ Security Features

### Attack Detection Engine
- **SQL Injection**: Detects various SQL injection attempts
- **XSS Protection**: Identifies cross-site scripting attacks
- **Directory Traversal**: Catches path traversal attempts
- **Command Injection**: Blocks command execution attempts
- **Brute Force**: Identifies repeated login attempts
- **Bot Detection**: Recognizes automated scanning tools

### Honeypot Deception
- **Visual Cloning**: Pixel-perfect website replicas
- **Interactive Elements**: Functional forms and buttons
- **Fake Errors**: Realistic error messages and timeouts
- **Admin Traps**: Hidden admin panels to attract attackers
- **Database Simulation**: Fake database interfaces for SQL injection

### Data Collection
- **IP Geolocation**: Track attacker locations
- **User Agent Analysis**: Identify attack tools and browsers
- **Behavioral Patterns**: Mouse movements and click patterns
- **Session Tracking**: Complete attack session recording
- **Payload Analysis**: Detailed attack vector examination

## 📊 Database Schema

### Attacks Table
- `id`: Unique attack identifier
- `ip`: Attacker IP address
- `user_agent`: Browser/tool information
- `payload`: Attack payload content
- `attack_types`: JSON array of detected attack types
- `severity`: Threat level (1-10)
- `timestamp`: Attack occurrence time
- `honeypot_log`: Honeypot interaction details

### System Logs
- `level`: Log level (INFO, WARNING, ERROR, CRITICAL)
- `message`: Log message content
- `timestamp`: Log entry time
- `component`: System component (AUTH, DETECTION, HONEYPOT)

### Protected Sites
- `url`: Protected website URL
- `added_timestamp`: Protection setup time
- `last_cloned`: Last cloning update
- `status`: Protection status

## 🎨 Theme Customization

### Color Scheme
The dark cybersecurity theme uses:
- **Primary Green**: `#00ff41` (Matrix green)
- **Danger Red**: `#ff073a` (Alert red)
- **Background**: `#0a0a0a` (Deep black)
- **Cards**: `#1a1a1a` (Dark gray)
- **Borders**: `#333333` (Medium gray)

### Animations
- **Matrix Rain**: Login page background effect
- **Scan Lines**: Moving scan line animations
- **Glow Effects**: Pulsing glow on interactive elements
- **Glitch Effects**: High-threat level indicators

## 🚨 Alert System

### Email Notifications
Automatic email alerts for:
- **Medium Severity** (6+): Attack attempts with potential impact
- **High Severity** (7+): Serious attack attempts
- **Critical Severity** (8+): Advanced persistent threats
- **System Events**: Critical errors and failures

### Alert Content
- **Attack Details**: IP, payload, attack type, severity
- **Visual Formatting**: HTML emails with cybersecurity styling
- **Actionable Information**: Clear threat assessment
- **System Status**: Current protection status

## 🔍 Monitoring & Analytics

### Real-time Dashboard
- **Live Attack Feed**: Recent attack attempts
- **Statistics Overview**: Key security metrics
- **Threat Level**: Current security status
- **System Health**: Component status monitoring

### Attack Analytics
- **Attack Type Distribution**: Most common attack vectors
- **Geographic Analysis**: Attacker location mapping
- **Time-based Patterns**: Attack frequency over time
- **Severity Trends**: Threat level progression

## 🛠️ Advanced Features

### Website Cloning
- **HTML Parsing**: BeautifulSoup-based content extraction
- **Asset Handling**: Images, CSS, JavaScript processing
- **Link Modification**: Automatic honeypot redirection
- **Form Hijacking**: Credential harvesting setup
- **JavaScript Injection**: Tracking code insertion

### Behavioral Analysis
- **Mouse Tracking**: Movement pattern analysis
- **Keystroke Logging**: Input pattern recognition
- **Click Mapping**: User interaction heatmaps
- **Session Recording**: Complete attack session capture
- **Device Fingerprinting**: Browser and device identification

## 🔒 Security Considerations

### Production Deployment
- Change default admin credentials
- Use HTTPS with valid SSL certificates
- Configure firewall rules appropriately
- Regular security updates and monitoring
- Backup database and logs regularly

### Legal Compliance
- Ensure compliance with local laws
- Implement proper data retention policies
- Consider privacy implications
- Document security procedures
- Regular security audits

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Check Python version (3.7+ required)
- Verify all dependencies installed
- Check port 5000 availability

**Email alerts not working:**
- Verify SMTP settings in config.py
- Check email credentials and app passwords
- Test network connectivity

**Website cloning fails:**
- Check internet connectivity
- Verify target website accessibility
- Review error logs in terminal

**Database errors:**
- Ensure write permissions in project directory
- Check SQLite installation
- Verify database file creation

## 📈 Performance Optimization

### Database Optimization
- Regular database cleanup
- Index optimization for queries
- Log rotation policies
- Archive old attack data

### Memory Management
- Monitor Flask application memory usage
- Implement session cleanup
- Optimize image and asset storage
- Regular garbage collection

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request with documentation

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Comment complex logic
- Maintain consistent formatting

## 📄 License

This project is provided for educational and security research purposes. Use responsibly and in compliance with applicable laws and regulations.

## 🆘 Support

For technical support or questions:
- Review this documentation thoroughly
- Check the troubleshooting section
- Examine application logs for errors
- Test with minimal configuration first

## 🔮 Future Enhancements

### Planned Features
- **Machine Learning**: Advanced attack pattern recognition
- **API Integration**: Third-party threat intelligence
- **Mobile App**: Remote monitoring capabilities
- **Cluster Support**: Multi-server deployment
- **Advanced Analytics**: Predictive threat modeling

### Community Requests
- **Custom Themes**: Additional UI themes
- **Plugin System**: Extensible architecture
- **Cloud Deployment**: AWS/Azure integration
- **Reporting**: Automated security reports
- **Integration**: SIEM system compatibility

---

**⚠️ Important Security Notice:**
PhantomEye is a powerful security tool. Use it responsibly and ensure compliance with all applicable laws and regulations. Always obtain proper authorization before deploying honeypots or monitoring systems.

**🛡️ Stay Secure, Stay Vigilant!**

