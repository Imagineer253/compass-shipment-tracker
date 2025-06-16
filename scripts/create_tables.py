from compass import create_app, db
from compass.models import User, Role

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db() 