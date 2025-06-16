# Database Migration Instructions

## Adding Phone Number Field

If you have an existing COMPASS installation and want to add the phone number field to the User model, follow these steps:

### Step 1: Update your code
Make sure you have the latest version of the code with the phone number field additions.

### Step 2: Run the migration script
```bash
python add_phone_migration.py
```

### Step 3: For new installations
If you're setting up COMPASS for the first time, simply run:
```bash
python create_tables.py
```

This will create all tables including the phone field.

### Manual Migration (if script fails)
If the automatic migration script fails, you can manually add the column using your database client:

**For SQLite:**
```sql
ALTER TABLE user ADD COLUMN phone VARCHAR(20);
```

**For PostgreSQL:**
```sql
ALTER TABLE "user" ADD COLUMN phone VARCHAR(20);
```

**For MySQL:**
```sql
ALTER TABLE user ADD COLUMN phone VARCHAR(20);
```

### Verification
After running the migration, existing users will have `NULL` phone numbers, which will display as "Not provided" in their profiles. New users will be required to enter a phone number during registration. 