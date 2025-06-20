# COMPASS Project Structure

## Clean Architecture Overview

The COMPASS shipment management system follows a **clean separation of concerns** with no duplicate files or backup clutter.

## Directory Structure

```
COMPASS/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules (enhanced to prevent duplicates)
├── PROJECT_STRUCTURE.md        # This file
├── MIGRATION_INSTRUCTIONS.md   # Database migration guide
├── UNIQUE_ID_IMPLEMENTATION.md # Unique ID feature documentation
├── template_setup_instructions.md # Template setup guide
├── compass/                    # Main application package
│   ├── __init__.py            # Flask app initialization
│   ├── config.py              # Configuration settings
│   ├── models.py              # Database models
│   ├── auth.py                # Authentication blueprint
│   ├── main.py                # Main routes blueprint
│   ├── static/                # Static assets
│   │   ├── css/               # Stylesheets
│   │   │   ├── style.css      # Main stylesheet
│   │   │   └── export_shipment.css # Export form styles
│   │   ├── js/                # JavaScript files
│   │   │   └── export_shipment.js # Export form functionality
│   │   └── images/            # Static images
│   │       ├── logo.svg       # COMPASS logo
│   │       └── ncpor_logo.png # NCPOR logo
│   └── templates/             # Jinja2 templates
│       ├── base.html          # Base template with Arctic theme
│       ├── index.html         # Home page
│       ├── landing_new.html   # Interactive landing page
│       ├── dashboard.html     # General dashboard
│       ├── auth/              # Authentication templates
│       │   ├── login.html     # Login form
│       │   ├── signup.html    # Registration form
│       │   ├── profile.html   # User profile
│       │   ├── register.html  # Registration page
│       │   ├── forgot_password.html # Password reset
│       │   └── verify_otp.html # OTP verification
│       ├── dashboard/         # Dashboard templates
│       │   ├── admin_dashboard.html # Admin interface
│       │   └── user_dashboard.html  # User interface
│       ├── admin/             # Admin-specific templates
│       │   ├── users.html     # User management
│       │   ├── edit_user.html # User editing
│       │   ├── combine_form.html # Shipment combining
│       │   ├── signing_authorities.html # Authority management
│       │   └── edit_signing_authority.html # Authority editing
│       ├── shipments/         # Shipment templates
│       │   ├── type_selection.html # Shipment type selector
│       │   ├── export_shipment.html # Export form (user)
│       │   ├── admin_export_shipment.html # Export form (admin)
│       │   ├── import_shipment.html # Import form
│       │   ├── reimport_shipment.html # Reimport form
│       │   ├── cold_shipment.html # Cold storage form
│       │   ├── list.html      # Shipment listing
│       │   ├── dashboard.html # Shipment dashboard
│       │   └── tracking.html  # Shipment tracking
│       └── documents/         # Document templates
│           └── cold_shipment/ # Cold shipment documents
├── migrations/                # Flask-Migrate database migrations
│   ├── alembic.ini           # Alembic configuration
│   ├── env.py                # Migration environment
│   ├── script.py.mako        # Migration script template
│   └── versions/             # Migration versions
│       ├── 5cb52fc6d689_initial_migration.py
│       ├── 2c9791241c6b_add_unique_id_field_to_users.py
│       ├── 4af799bc00db_add_pi_id_to_users_and_create_.py
│       ├── 886326e13fe2_add_serial_number_to_shipments.py
│       └── dc9a2244290f_make_pi_id_required_and_add_unique_.py
├── scripts/                  # Utility scripts
│   ├── check_db.py          # Database verification
│   ├── create_tables.py     # Table creation
│   ├── setup_admin.py       # Admin user setup
│   ├── setup_main_admin.py  # Main admin setup
│   ├── setup_signing_authorities.py # Authority setup
│   ├── test_login.py        # Login testing
│   ├── update_base_template.py # Template updates
│   ├── update_landing_layout.ps1 # Layout updates
│   └── legacy_migrations/   # Old migration files
├── templates/               # Document templates
│   ├── export_custom_docs.docx # Custom export template
│   └── invoice_packinglist.docx # Invoice template
├── instance/               # Instance-specific files (ignored)
└── venv/                  # Virtual environment (ignored)
```

## Key Features

### 1. **Unique ID System** ✅
- 6-character alphanumeric IDs for all users
- Cryptographically secure generation
- Integrated into invoice number format
- Examples: `C9O0MU`, `QKSQOM`, `0EFJJE`

### 2. **Serial Number System** ✅
- 4-digit sequential serial numbers (`0001`, `0002`, etc.)
- Automatic assignment per shipment
- Proper handling of existing data

### 3. **Invoice Number Generation** ✅
Current format: `NCPOR/ARC/YYYY/MMM/EXP/TYPE/UNIQUE_ID/SERIAL`

**Formats by Type:**
- **Export**: `NCPOR/ARC/2025/JUN/EXP/RET/C9O0MU/0001`
- **Import**: `NCPOR/IMP/2025/JUN/RET/C9O0MU/0001`
- **Reimport**: `NCPOR/REIMP/2025/JUN/RET/C9O0MU/0001`
- **Cold**: `NCPOR/COLD/2025/JUN/C9O0MU/0001`

### 4. **Package Type System**
Standardized package types with emoji icons:
- 📦 Cardboard Box
- 🗃️ Plastic Crate
- 🗳️ Metal Trunk
- 🧳 Zarges
- 💼 Pelican Case
- 📝 Other

### 5. **Document Generation**
- **Invoice & Packing List** (`invoice_packinglist.docx`)
- **Custom Documents** (`export_custom_docs.docx`)
- Real-time preview with proper formatting
- Arctic-themed professional templates

### 6. **User Management**
- Role-based access control (Admin, Project Incharge, Field Personnel)
- User registration with email verification
- Profile management
- Admin user management interface

### 7. **Shipment Management**
- Multiple shipment types (Export, Import, Reimport, Cold)
- Status tracking and updates
- Admin acknowledgment system
- Combined shipment functionality
- Real-time invoice preview

## Database Models

### Core Models:
- **User**: Authentication and user data with unique IDs
- **Role**: Role-based permissions
- **Shipment**: Shipment tracking with serial numbers
- **SigningAuthority**: Document signing authorities
- **ShipmentSerialCounter**: Serial number tracking
- **CombinedShipmentCounter**: Combined shipment numbering

## API Endpoints

### Key APIs:
- `/api/generate-invoice-preview` - Real-time invoice number generation
- `/admin/*` - Admin management routes
- `/auth/*` - Authentication routes
- `/shipment/*` - Shipment management routes

## Clean Code Principles

### ✅ **No Duplicates Policy**
- All backup and duplicate files removed
- Enhanced `.gitignore` to prevent future duplicates
- Single source of truth for all components

### ✅ **Organized Structure**
- Clear separation of concerns
- Consistent naming conventions
- Logical file organization

### ✅ **Production Ready**
- No test files in production
- Clean template structure
- Proper error handling

## Development Guidelines

### File Organization:
1. **No backup files** - Use version control instead
2. **No test files in root** - Keep in separate test directory
3. **Consistent naming** - Follow Python/Flask conventions
4. **Clean templates** - No backup or reference templates

### Naming Conventions:
- **Python files**: `snake_case.py`
- **Templates**: `snake_case.html`
- **Static files**: `kebab-case.css/js`
- **Directories**: `lowercase`

### Git Workflow:
- Use meaningful commit messages
- No committing of backup files
- Regular cleanup of temporary files
- Use feature branches for new development

## Deployment Notes

The application is ready for deployment with:
- Clean project structure
- No duplicate files
- Proper configuration management
- Enhanced security with unique IDs
- Professional document generation
- Real-time features

---

**Structure Status**: ✅ **CLEAN** - No duplicates, well-organized, production-ready