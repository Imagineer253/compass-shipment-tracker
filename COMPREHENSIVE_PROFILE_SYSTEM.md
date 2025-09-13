# COMPASS Comprehensive Profile System Implementation

## Overview
The COMPASS system now includes a comprehensive user profile management system that allows users to complete detailed personal, contact, address, and passport information. This system includes automatic profile completion tracking, file uploads, and verification systems.

## New Features Implemented

### 1. Enhanced User Model
- **Personal Information**: Passport names (first, middle, last), date of birth, gender, nationality, T-shirt size
- **Contact Information**: Phone verification, secondary email verification, organization selection
- **Address Information**: Complete address with line 1, line 2, city, state/province, postal code, country
- **Passport Information**: Passport number, issue/expiry dates, document uploads (front & last page)
- **Profile Tracking**: Completion status, completion percentage, completion timestamp

### 2. Organization Management
- **Organization Model**: Structured organization data with name, short name, description, website, contact details
- **Pre-seeded Organizations**: 13 default organizations including NCPOR, IITs, IISc, CSIR, ISRO, etc.
- **Dropdown Selection**: Users can select their organization from predefined options

### 3. Profile Setup & Management Routes
- **Setup Route** (`/profile/setup`): First-time profile completion for new users
- **View Route** (`/profile/view`): Comprehensive profile viewing with completion status
- **Edit Route** (`/profile/edit`): Profile editing with all fields and verification options
- **Verification Routes**: Phone OTP and secondary email verification endpoints

### 4. File Upload System
- **Profile Pictures**: Image uploads (PNG, JPG, JPEG, GIF) with automatic resizing
- **Passport Documents**: PDF/Image uploads for passport front and last pages
- **Secure Storage**: Files stored in organized directories with unique naming
- **File Management**: Automatic cleanup of old files when new ones are uploaded

### 5. Verification Systems
- **Phone Verification**: OTP-based phone number verification (ready for SMS integration)
- **Secondary Email Verification**: Token-based email verification system
- **Primary Email**: Already verified during signup process

### 6. Login Flow Integration
- **First-time Setup**: New users automatically redirected to profile setup after login
- **Profile Completion Check**: System tracks if profile is complete before allowing full access
- **2FA Integration**: Profile setup redirect works with 2FA flows

### 7. Amazing UI/UX Design
- **Modern Gradient Design**: Blue-to-purple gradients with Arctic theme
- **Card-based Layout**: Organized sections for different information types
- **Progress Tracking**: Visual progress bars and completion percentages
- **Responsive Design**: Mobile-friendly layouts with proper spacing
- **Interactive Elements**: Real-time verification buttons and status indicators

## Technical Implementation

### Database Schema
```sql
-- New fields added to User table
ALTER TABLE user ADD COLUMN middle_name VARCHAR(50);
ALTER TABLE user ADD COLUMN passport_first_name VARCHAR(50);
ALTER TABLE user ADD COLUMN passport_middle_name VARCHAR(50);
ALTER TABLE user ADD COLUMN passport_last_name VARCHAR(50);
ALTER TABLE user ADD COLUMN date_of_birth DATE;
ALTER TABLE user ADD COLUMN gender VARCHAR(10);
ALTER TABLE user ADD COLUMN nationality VARCHAR(50);
ALTER TABLE user ADD COLUMN t_shirt_size VARCHAR(10);
ALTER TABLE user ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN secondary_email VARCHAR(120);
ALTER TABLE user ADD COLUMN secondary_email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN address_line1 VARCHAR(200);
ALTER TABLE user ADD COLUMN address_line2 VARCHAR(200);
ALTER TABLE user ADD COLUMN city VARCHAR(100);
ALTER TABLE user ADD COLUMN state_province VARCHAR(100);
ALTER TABLE user ADD COLUMN postal_code VARCHAR(20);
ALTER TABLE user ADD COLUMN country VARCHAR(100);
ALTER TABLE user ADD COLUMN passport_number VARCHAR(50);
ALTER TABLE user ADD COLUMN passport_issue_date DATE;
ALTER TABLE user ADD COLUMN passport_expiry_date DATE;
ALTER TABLE user ADD COLUMN passport_front_page VARCHAR(255);
ALTER TABLE user ADD COLUMN passport_last_page VARCHAR(255);
ALTER TABLE user ADD COLUMN organization_id INTEGER REFERENCES organization(id);
ALTER TABLE user ADD COLUMN profile_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN profile_completed_at DATETIME;

-- New Organization table
CREATE TABLE organization (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    short_name VARCHAR(50),
    description TEXT,
    website VARCHAR(200),
    contact_email VARCHAR(120),
    contact_phone VARCHAR(20),
    address TEXT,
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES user(id)
);

-- New PhoneOTP table for phone verification
CREATE TABLE phone_otp (
    id INTEGER PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    purpose VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0
);
```

### Helper Methods Added to User Model
- `get_passport_full_name()`: Returns full name as per passport
- `get_complete_address()`: Returns formatted complete address
- `is_profile_complete()`: Checks if all required fields are filled
- `get_profile_completion_percentage()`: Returns completion percentage (0-100)
- `mark_profile_complete()`: Marks profile as complete when all required fields are filled
- `generate_phone_verification_token()`: Creates OTP for phone verification
- `verify_phone_token()`: Verifies phone OTP
- `generate_secondary_email_verification_token()`: Creates token for secondary email
- `verify_secondary_email_token()`: Verifies secondary email token

### File Upload Configuration
```python
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
```

### Upload Directories
- `compass/static/uploads/profile_pictures/`: User profile pictures
- `compass/static/uploads/passports/`: Passport document uploads

## User Experience Flow

### 1. New User Registration
1. User registers with email (existing flow)
2. Email verification (existing flow)
3. **NEW**: First login redirects to profile setup
4. User completes comprehensive profile information
5. Profile completion tracking shows progress
6. System marks profile as complete when all required fields are filled

### 2. Profile Management
1. Users can view their complete profile with visual progress indicators
2. Edit profile functionality allows updating all information
3. Real-time verification for phone numbers and secondary emails
4. File upload capabilities for profile pictures and passport documents

### 3. Admin & Multi-Role Support
- Admins can have additional roles (PI, Field Personnel)
- All users (including admins) go through the same profile setup process
- Role-based access control remains intact while adding comprehensive profile data

## Security & Validation

### Form Validation
- Required field validation for critical information
- Date validation for passport expiry and birth dates
- File type and size validation for uploads
- Email format validation for secondary email addresses

### File Security
- Secure filename generation using UUID
- File type validation based on extensions
- Size limits to prevent abuse
- Organized storage structure

### Data Privacy
- Profile completion is optional but encouraged
- Sensitive information (passport details) properly secured
- File access controlled through application routes

## Integration Points

### Navigation Integration
- Profile link added to user dropdown in navigation bar
- Quick access to profile from anywhere in the application

### Authentication Flow Integration
- Profile setup integrated with login flow
- Works seamlessly with 2FA authentication
- Proper redirects after profile completion

### Email Service Integration
- Secondary email verification uses existing email service
- Consistent email templates with NCPOR branding

## Pre-populated Organizations

The system includes 13 pre-populated organizations:
1. National Centre for Polar and Ocean Research (NCPOR)
2. Indian Institute of Technology (IIT)
3. Indian Institute of Science (IISc)
4. Council of Scientific and Industrial Research (CSIR)
5. Indian Space Research Organisation (ISRO)
6. Ministry of Earth Sciences (MoES)
7. National Institute of Oceanography (NIO)
8. Indian Meteorological Department (IMD)
9. Defence Research and Development Organisation (DRDO)
10. Jawaharlal Nehru University (JNU)
11. University of Delhi
12. International Partner Institution
13. Other Institution

## Future Enhancements

### SMS Integration
- Phone verification currently logs OTP to console
- Ready for SMS service integration (Twilio, AWS SNS, etc.)
- OTP infrastructure already implemented

### Document Processing
- OCR integration for passport data extraction
- Automatic validation of passport information
- Document verification workflows

### Profile Analytics
- Profile completion analytics for administrators
- User engagement tracking
- Incomplete profile reminders

## Files Modified/Created

### New Files
- `compass/profile.py`: Profile management blueprint
- `compass/templates/profile/setup.html`: Profile setup template
- `compass/templates/profile/view.html`: Profile viewing template
- `compass/templates/profile/edit.html`: Profile editing template
- `seed_organizations.py`: Organization seeding script
- `migrations/versions/1bb685565426_add_comprehensive_profile_fields.py`: Database migration

### Modified Files
- `compass/models.py`: Enhanced User model, added Organization and PhoneOTP models
- `compass/__init__.py`: Registered profile blueprint
- `compass/auth.py`: Added profile setup redirect logic
- `compass/two_fa.py`: Added profile setup redirect after 2FA
- `compass/templates/base.html`: Updated profile navigation link

## Usage Instructions

### For New Users
1. Register and verify email (existing process)
2. Login - system will automatically redirect to profile setup
3. Fill in all required information sections:
   - Personal Information (name as per passport, DOB, gender, nationality)
   - Contact Information (phone verification, organization selection)
   - Address Information (complete address details)
   - Passport Information (passport details and document uploads)
4. Upload profile picture and passport documents
5. Complete verification for phone and secondary email
6. System automatically tracks completion and grants full access

### For Existing Users
1. Access profile through user dropdown menu
2. View current profile completion status
3. Edit profile to add missing information
4. Upload missing documents
5. Complete any pending verifications

### For Administrators
1. Admins can manage organizations through database
2. Monitor user profile completion rates
3. Access all profile management features like regular users
4. Maintain dual roles (Admin + PI/Field Personnel)

## Benefits Achieved

1. **Complete User Data**: Comprehensive user information for expedition planning
2. **Passport Integration**: Essential for international travel coordination
3. **Organization Tracking**: Clear institutional affiliations for reporting
4. **File Management**: Centralized document storage and access
5. **Verification Systems**: Multi-channel user verification (email, phone)
6. **User Experience**: Modern, intuitive interface with progress tracking
7. **Scalability**: Extensible system for future enhancements
8. **Security**: Proper validation and secure file handling

The comprehensive profile system transforms COMPASS from a basic shipment management system into a complete user management platform suitable for complex expedition planning and coordination.
