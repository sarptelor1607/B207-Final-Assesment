from app import app
from models import db, User, PasswordEntry
from crypto import derive_key, encrypt_password
import bcrypt
import os

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='demo').first():
        demo_password = 'DemoPass123!'
        hashed = bcrypt.hashpw(demo_password.encode('utf-8'), bcrypt.gensalt())
        salt = os.urandom(16).hex()

        demo_user = User(
            username='demo',
            email='demo@example.com',
            password_hash=hashed.decode('utf-8'),
            salt=salt
        )
        db.session.add(demo_user)
        db.session.commit()

        key = derive_key(demo_password, salt)
        demo_entry = PasswordEntry(
            user_id=demo_user.id,
            site_name='Example Site',
            site_url='https://example.com',
            username='demo_user',
            encrypted_password=encrypt_password('ExamplePassword1', key)
        )
        db.session.add(demo_entry)
        db.session.commit()

        print('Seeded database with demo user (username: demo, password: DemoPass123!)')
    else:
        print('Demo user already exists, skipping seed.')
