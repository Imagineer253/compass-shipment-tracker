# 🚀 AWS Elastic Beanstalk Deployment Guide for COMPASS

## 📋 Prerequisites
1. **AWS Account** (free tier eligible)
2. **AWS CLI** installed
3. **EB CLI** installed

## 🛠️ Step 1: Install AWS Tools

### Install AWS CLI
```bash
# Download from: https://aws.amazon.com/cli/
# Or using pip:
pip install awscli
```

### Install EB CLI
```bash
pip install awsebcli
```

## 🔑 Step 2: Configure AWS Credentials

1. **Create AWS Account** at https://aws.amazon.com (free tier)
2. **Create IAM User** with Elastic Beanstalk permissions:
   - Go to AWS Console → IAM → Users → Create User
   - Attach policies: `AWSElasticBeanstalkFullAccess`
   - Download Access Key ID and Secret

3. **Configure AWS CLI**:
```bash
aws configure
# Enter: Access Key ID
# Enter: Secret Access Key  
# Region: us-east-1 (or your preferred)
# Output: json
```

## 🚀 Step 3: Initialize EB Application

```bash
# In your project directory
eb init

# Follow prompts:
# - Select region (us-east-1)
# - Application name: compass-shipment-tracker
# - Platform: Python 3.11
# - CodeCommit: No
# - SSH: Yes (recommended)
```

## 🌐 Step 4: Create Environment & Deploy

```bash
# Create environment
eb create compass-production

# Deploy current code
eb deploy

# Open in browser
eb open
```

## ⚙️ Step 5: Set Environment Variables

```bash
# Set production environment variables
eb setenv SECRET_KEY="your-super-secret-key-here"
eb setenv FLASK_ENV="production"
eb setenv MAIL_USERNAME="your-email@gmail.com"
eb setenv MAIL_PASSWORD="your-app-password"
eb setenv DATABASE_URL="sqlite:///compass.db"

# Redeploy with new environment variables
eb deploy
```

## 💾 Step 6: Add RDS Database (Optional - Free Tier)

```bash
# Add RDS PostgreSQL database
eb create compass-production --database.engine postgres --database.username compass --database.password yourpassword

# Update environment variable
eb setenv DATABASE_URL="postgresql://compass:yourpassword@your-rds-endpoint/ebdb"
```

## 🔄 Step 7: Auto-Deploy from GitHub

Create `.github/workflows/aws-deploy.yml`:

```yaml
name: Deploy to AWS Elastic Beanstalk
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install EB CLI
      run: pip install awsebcli
    
    - name: Deploy to EB
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        eb init compass-shipment-tracker --region us-east-1 --platform "Python 3.11"
        eb deploy compass-production
```

## 📊 Monitoring & Management

```bash
# Check status
eb status

# View logs
eb logs

# SSH into instance
eb ssh

# Terminate environment (to save costs)
eb terminate compass-production
```

## 💰 Cost Estimation (AWS Free Tier)

- **EC2 t3.micro**: FREE for 12 months (750 hours/month)
- **RDS db.t3.micro**: FREE for 12 months (750 hours/month)
- **Load Balancer**: ~$18/month (optional)
- **Data Transfer**: 15 GB free/month

**Total Cost**: $0-18/month (FREE for first year!)

## 🔧 Troubleshooting

### Common Issues:
1. **Database errors**: Check migration scripts
2. **Static files**: Verify `.ebextensions/01_flask.config`
3. **Environment variables**: Use `eb printenv` to verify

### Useful Commands:
```bash
eb logs --all        # View all logs
eb config           # Edit configuration
eb restore          # Rollback deployment
eb health           # Check health status
```

## 🚀 Your App Will Be Live At:
`http://compass-production.us-east-1.elasticbeanstalk.com`

With QR codes automatically updating to use your AWS domain! 🎉
