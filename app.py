from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from models import db, User, PasswordEntry
from crypto import encrypt_password, decrypt_password, derive_key
import bcrypt
import os
import secrets
import string
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b207-secret-key-do-not-share'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vault.db'
app.config['SESSION_COOKIE_HTTPONLY'] = True

db.init_app(app)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

# decorator to block pages if user is not logged in, wraps keeps the original function name
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('All fields are required.')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken.')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.')
            return render_template('register.html')

        # bcrypt adds its own random salt so we dont need to store one separately
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # separate salt for the encryption key derivation, bcrypt's salt isnt exposed to us
        enc_salt = os.urandom(16).hex()
        new_user = User(username=username, email=email, password_hash=hashed.decode('utf-8'), salt=enc_salt)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully. You can now login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            session['user_id'] = user.id
            session['username'] = user.username
            # derived here since this is the only point we have the plaintext master password
            session['enc_key'] = derive_key(password, user.salt).decode('utf-8')
            return redirect(url_for('dashboard'))
        flash('Incorrect username or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    entries = PasswordEntry.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', entries=entries)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        site_name = request.form.get('site_name', '').strip()
        site_url = request.form.get('site_url', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not site_name or not password:
            flash('Site name and password cannot be empty.')
            return render_template('add.html')

        entry = PasswordEntry(
            user_id=session['user_id'],
            site_name=site_name,
            site_url=site_url,
            username=username,
            encrypted_password=encrypt_password(password, session['enc_key'])
        )
        db.session.add(entry)
        db.session.commit()
        flash('Password entry saved.')
        return redirect(url_for('dashboard'))

    return render_template('add.html')

@app.route('/view/<int:entry_id>')
@login_required
def view(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first_or_404()
    decrypted = decrypt_password(entry.encrypted_password, session['enc_key'])
    return render_template('view.html', entry=entry, decrypted_password=decrypted)

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        entry.site_name = request.form.get('site_name', '').strip()
        entry.site_url = request.form.get('site_url', '').strip()
        entry.username = request.form.get('username', '').strip()
        new_password = request.form.get('password', '')
        if new_password:
            entry.encrypted_password = encrypt_password(new_password, session['enc_key'])
        db.session.commit()
        flash('Entry updated.')
        return redirect(url_for('dashboard'))

    current_password = decrypt_password(entry.encrypted_password, session['enc_key'])
    return render_template('edit.html', entry=entry, current_password=current_password)

@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=session['user_id']).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted.')
    return redirect(url_for('dashboard'))

@app.route('/generate')
@login_required
def generate():
    length = request.args.get('length', 16, type=int)
    length = max(8, min(length, 64))  # clamp so people cant break it with weird numbers
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    # secrets.choice instead of random.choice because its safer for passwords
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return jsonify({'password': password})

if __name__ == '__main__':
    app.run(debug=False)
