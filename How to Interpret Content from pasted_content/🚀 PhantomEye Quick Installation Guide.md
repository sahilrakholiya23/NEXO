# 🚀 PhantomEye Quick Installation Guide

## Prerequisites
- Python 3.7 or higher
- Internet connection
- 50MB free disk space

## Installation Steps

### 1. Extract Project
```bash
tar -xzf PhantomEye_Complete.tar.gz
cd PhantomEye
```

### 2. Install Dependencies
```bash
pip install flask requests beautifulsoup4
```

### 3. Configure (Optional)
Edit `config.py` to customize:
- Admin credentials (default: admin/phantom123)
- Email alert settings
- Security parameters

### 4. Run Application
```bash
python app.py
```

### 5. Access System
- Open browser: `http://localhost:5000`
- Login: `admin` / `phantom123`
- Start protecting websites!

## Quick Test
1. Login to dashboard
2. Click "Add Website"
3. Enter: `https://example.com`
4. Click "Initialize Protection"
5. Visit: `http://localhost:5000/honeypot`

## Default Configuration
- **Username**: admin
- **Password**: phantom123
- **Port**: 5000
- **Database**: SQLite (auto-created)
- **Theme**: Dark Cybersecurity

## Need Help?
- Check `PhantomEye_README.md` for detailed documentation
- Review error messages in terminal
- Ensure all dependencies are installed

**🛡️ Your cybersecurity defense system is ready!**

