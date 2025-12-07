from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import subprocess
import pickle
import jwt
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config['SECRET_KEY'] = 'insecure_secret_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float, default=1000.00)
    ssn = db.Column(db.String(20))

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.String(80))
    to_user = db.Column(db.String(80))
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))

# ============ RUTAS ============

@app.route('/')
def index():
    comments = []
    if os.path.exists('/app/comments.txt'):
        with open('/app/comments.txt', 'r') as f:
            comments = f.readlines()[-3:]
    return render_template('index.html', comments=comments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    
    # SQL Injection
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM user WHERE username LIKE '%{query}%'")
    results = cursor.fetchall()
    conn.close()
    
    return render_template('search.html', results=results, query=query)

@app.route('/ping', methods=['GET'])
def ping_host():
    host = request.args.get('host', '127.0.0.1')
    cmd = f"ping -c 2 {host}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    return f"<pre>{output}</pre>"

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('file', 'test.txt')
    filepath = os.path.join('/app/uploads', filename)
    return send_file(filepath)

@app.route('/user/profile/<int:user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('profile.html', user=user)
    return "User not found", 404

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        to_user = request.form.get('to_user')
        amount = float(request.form.get('amount', 0))
        
        transfer = Transfer(
            from_user=session['username'],
            to_user=to_user,
            amount=amount,
            description=request.form.get('description', '')
        )
        db.session.add(transfer)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('transfer.html')

@app.route('/post_comment', methods=['POST'])
def post_comment():
    comment = request.form.get('comment', '')
    user = session.get('username', 'Anonymous')
    
    with open('/app/comments.txt', 'a') as f:
        f.write(f"{user}: {comment}\n")
    
    return redirect(url_for('index'))

@app.route('/view_comments')
def view_comments():
    comments = []
    if os.path.exists('/app/comments.txt'):
        with open('/app/comments.txt', 'r') as f:
            comments = f.readlines()
    return render_template('comments.html', comments=comments)

@app.route('/exec', methods=['GET'])
def execute_command():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cmd = request.args.get('cmd', '')
    if cmd:
        output = subprocess.check_output(cmd, shell=True, text=True)
        return f"<pre>{output}</pre>"
    return "No command specified"

@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return "Access denied", 403
    
    all_users = User.query.all()
    return render_template('admin.html', all_users=all_users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def init_db():
    with app.app_context():
        db.create_all()
        
        if User.query.count() == 0:
            users = [
                User(username='admin', password=generate_password_hash('admin123'), 
                     email='admin@bank.com', is_admin=True, balance=1000000, ssn='123-45-6789'),
                User(username='alice', password=generate_password_hash('password123'), 
                     email='alice@bank.com', balance=5000, ssn='987-65-4321'),
                User(username='bob', password=generate_password_hash('qwerty'), 
                     email='bob@bank.com', balance=3000, ssn='456-78-9123'),
            ]
            for user in users:
                db.session.add(user)
            db.session.commit()
        
        os.makedirs('/app/uploads', exist_ok=True)
        if not os.path.exists('/app/comments.txt'):
            with open('/app/comments.txt', 'w') as f:
                f.write("Admin: Welcome to SecureBank Online Banking!\n")
        
        if not os.path.exists('/app/uploads/test.txt'):
            with open('/app/uploads/test.txt', 'w') as f:
                f.write("Test file for download functionality\n")

if __name__ == '__main__':
    init_db()
    print("Starting vulnerable bank app on http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)