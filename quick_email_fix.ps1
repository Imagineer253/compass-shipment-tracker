# Quick Email Fix for COMPASS
# Run this PowerShell script to set up email temporarily

Write-Host "🧭 COMPASS Email Configuration Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`n📧 Current email configuration:" -ForegroundColor Yellow
Write-Host "MAIL_SERVER: smtp.gmail.com"
Write-Host "MAIL_USERNAME: arctic.ncpor@gmail.com" 
Write-Host "MAIL_PASSWORD: " -NoNewline
if ($env:MAIL_PASSWORD) {
    Write-Host "✅ Set" -ForegroundColor Green
} else {
    Write-Host "❌ NOT SET" -ForegroundColor Red
}

if (-not $env:MAIL_PASSWORD) {
    Write-Host "`n🔑 Gmail App Password Setup Required:" -ForegroundColor Yellow
    Write-Host "1. Go to https://myaccount.google.com/security"
    Write-Host "2. Enable 2-Factor Authentication if not enabled"
    Write-Host "3. Go to '2-Step Verification' → 'App passwords'"
    Write-Host "4. Generate new app password for 'COMPASS NCPOR System'"
    Write-Host "5. Copy the 16-character password (like: abcd efgh ijkl mnop)"
    
    Write-Host "`n🔧 Enter your Gmail App Password:" -ForegroundColor Green
    $appPassword = Read-Host "App Password"
    
    if ($appPassword) {
        # Remove spaces from the password
        $appPassword = $appPassword -replace '\s', ''
        
        # Set environment variable for current session
        $env:MAIL_PASSWORD = $appPassword
        
        Write-Host "✅ Environment variable set for current session!" -ForegroundColor Green
        Write-Host "📧 Email should now work for account creation." -ForegroundColor Green
        
        # Test the configuration
        Write-Host "`n🧪 Testing email configuration..." -ForegroundColor Yellow
        python test_email.py
        
    } else {
        Write-Host "❌ No password entered. Email will not work." -ForegroundColor Red
    }
} else {
    Write-Host "✅ MAIL_PASSWORD already configured!" -ForegroundColor Green
    Write-Host "🧪 Running email test..." -ForegroundColor Yellow
    python test_email.py
}

Write-Host "`n📚 For permanent setup, see: email_setup_instructions.md" -ForegroundColor Cyan
