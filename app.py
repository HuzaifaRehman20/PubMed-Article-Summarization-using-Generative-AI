import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline

secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)

# Load the fine-tuned model and tokenizer
model = T5ForConditionalGeneration.from_pretrained("./fine-tuned-t5")
tokenizer = T5Tokenizer.from_pretrained("./fine-tuned-t5")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return 'Username or email already exists'
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = user.username
            return redirect(url_for('home'))
        return 'Invalid credentials'
    return render_template('login.html')

def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

@app.route('/summarize', methods=['POST'])
def summarize():
    article = request.form['article']
    summary = summarize_text(article)
    return render_template('result.html', article=article, summary=summary)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)