# 🧭 COMPASS - Comprehensive Management Portal for Arctic Sample Shipments

A sophisticated Flask web application for managing scientific sample shipments, user authentication, and QR code tracking for research organizations.

## ✨ Features

### 🔐 Authentication & Security
- Two-Factor Authentication (2FA) with TOTP
- Email OTP verification
- Backup codes for account recovery
- Trusted device management
- Comprehensive user profiles with passport verification

### 📦 Shipment Management
- Export, Import, Reimport, and Cold shipment types
- Combined shipment processing
- Real-time invoice generation
- Package-level QR code tracking
- Document generation (invoices, packing lists)

### 📱 QR Code Tracking
- Unique QR codes for every package
- Public tracking pages (no login required)
- Organization logo embedded in QR codes
- Mobile-friendly scanning interface

### 👥 User Management
- Role-based access control
- Admin dashboard with comprehensive controls
- User profile management with file uploads
- Signing authority management

### 📊 Admin Features
- User management and verification
- Shipment oversight and approval
- QR code regeneration and bulk operations
- System analytics and reporting

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- SQLite (for development) or PostgreSQL (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/compass.git
   cd compass
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   python scripts/setup_admin.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

Visit `http://localhost:5000` to access the application.

## 🌐 Deployment

### Heroku Deployment
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set environment variables: `heroku config:set SECRET_KEY=your-secret-key`
4. Deploy: `git push heroku main`

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

### Environment Variables
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📁 Project Structure

```
compass/
├── app.py                 # Application entry point
├── compass/               # Main application package
│   ├── __init__.py       # App factory
│   ├── models.py         # Database models
│   ├── routes.py         # Main routes
│   ├── auth.py           # Authentication routes
│   ├── main.py           # Main blueprint
│   ├── tracking.py       # Public tracking routes
│   ├── services/         # Business logic
│   │   └── qr_service.py # QR code generation
│   ├── templates/        # Jinja2 templates
│   └── static/           # CSS, JS, images
├── migrations/           # Database migrations
├── scripts/              # Utility scripts
└── requirements.txt      # Python dependencies
```

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Authentication**: PyOTP, Email verification
- **QR Codes**: qrcode, Pillow
- **Documents**: python-docx, docxtpl
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Heroku, Railway, Docker-ready

## 🔧 Configuration

### Email Setup (Gmail)
1. Enable 2-factor authentication
2. Generate app password
3. Update `.env` with credentials

### Database Configuration
- Development: SQLite (automatic)
- Production: PostgreSQL recommended

## 📖 Usage

### Admin Features
1. **User Management**: Approve registrations, manage roles
2. **Shipment Processing**: Create and manage shipments
3. **QR Code Management**: Generate, regenerate, and download QR codes

### User Features
1. **Profile Management**: Complete profile with verification
2. **Shipment Creation**: Submit shipment requests
3. **2FA Setup**: Secure account with TOTP

### Public Features
1. **Package Tracking**: Scan QR codes for package information
2. **No Login Required**: Public access to tracking pages

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, email admin@compass.com or create an issue on GitHub.

## 🙏 Acknowledgments

- Built for Arctic research sample management
- QR code tracking for enhanced logistics
- Security-first approach with 2FA implementation
