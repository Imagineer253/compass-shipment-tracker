from flask import current_app, render_template_string
from flask_mail import Message, Mail
from .models import EmailOTP
import logging

# Email templates
EMAIL_VERIFICATION_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COMPASS Email Verification</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .email-container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            color: #0b5394;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .arctic-theme {
            background: linear-gradient(135deg, #0b5394, #1c7ed6);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }
        .otp-code {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 5px;
            color: #0b5394;
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
            border: 2px solid #0b5394;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">🧭 COMPASS</div>
            <h2>NCPOR Shipment Management System</h2>
        </div>
        
        <div class="arctic-theme">
            <h3>Email Verification Required</h3>
            <p>Welcome to COMPASS! Please verify your email address to complete your registration.</p>
        </div>
        
        <p>Hello {{ user_name }},</p>
        
        <p>Thank you for registering with COMPASS (NCPOR Shipment Management System). To complete your account setup, please use the verification code below:</p>
        
        <div class="otp-code">{{ otp_code }}</div>
        
        <div class="warning">
            <strong>⚠️ Important:</strong>
            <ul>
                <li>This code will expire in 15 minutes</li>
                <li>Use this code only once</li>
                <li>Do not share this code with anyone</li>
                <li>If you didn't request this verification, please ignore this email</li>
            </ul>
        </div>
        
        <p>If you have any issues, please contact the NCPOR support team.</p>
        
        <div class="footer">
            <p><strong>National Centre for Polar and Ocean Research (NCPOR)</strong></p>
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>Generated at {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
'''

TWO_FA_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COMPASS Login Verification</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .email-container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            color: #0b5394;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .arctic-theme {
            background: linear-gradient(135deg, #0b5394, #1c7ed6);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }
        .otp-code {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 5px;
            color: #0b5394;
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
            border: 2px solid #0b5394;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        .security-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">🧭 COMPASS</div>
            <h2>NCPOR Shipment Management System</h2>
        </div>
        
        <div class="arctic-theme">
            <h3>🔐 Login Verification</h3>
            <p>A login attempt was made to your COMPASS account</p>
        </div>
        
        <p>Hello {{ user_name }},</p>
        
        <p>Someone attempted to log into your COMPASS account. If this was you, please use the verification code below to complete your login:</p>
        
        <div class="otp-code">{{ otp_code }}</div>
        
        <div class="security-info">
            <strong>🛡️ Security Information:</strong>
            <ul>
                <li>Login attempt time: {{ timestamp }}</li>
                <li>This code expires in 15 minutes</li>
                <li>If this wasn't you, change your password immediately</li>
            </ul>
        </div>
        
        <p>If you didn't attempt to log in, please secure your account immediately and contact NCPOR support.</p>
        
        <div class="footer">
            <p><strong>National Centre for Polar and Ocean Research (NCPOR)</strong></p>
            <p>This is an automated security email. Please do not reply to this message.</p>
        </div>
    </div>
</body>
</html>
'''

def send_verification_email(user_email, user_name, otp_code):
    """Send email verification OTP"""
    try:
        mail = current_app.extensions.get('mail')
        if not mail:
            logging.error("Flask-Mail not initialized")
            return False
        
        from datetime import datetime
        
        subject = "COMPASS - Email Verification Required"
        html_body = render_template_string(
            EMAIL_VERIFICATION_TEMPLATE,
            user_name=user_name,
            otp_code=otp_code,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        logging.info(f"Verification email sent to {user_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send verification email to {user_email}: {str(e)}")
        return False

def send_2fa_login_email(user_email, user_name, otp_code):
    """Send 2FA login verification OTP"""
    try:
        mail = current_app.extensions.get('mail')
        if not mail:
            logging.error("Flask-Mail not initialized")
            return False
        
        from datetime import datetime
        
        subject = "COMPASS - Login Verification Code"
        html_body = render_template_string(
            TWO_FA_LOGIN_TEMPLATE,
            user_name=user_name,
            otp_code=otp_code,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        logging.info(f"2FA login email sent to {user_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send 2FA login email to {user_email}: {str(e)}")
        return False

def send_otp_email(email, name, otp_code, purpose='registration'):
    """Generic function to send OTP emails"""
    if purpose == 'registration':
        return send_verification_email(email, name, otp_code)
    elif purpose == 'login':
        return send_2fa_login_email(email, name, otp_code)
    else:
        logging.error(f"Unknown OTP purpose: {purpose}")
        return False
