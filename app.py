from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import logging
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Initialize the logger after creating the app
app.logger.setLevel(logging.DEBUG)

def init_db():
    app.logger.debug("Initializing database...")
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    app.logger.debug("Database initialized.")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    app.logger.debug("Index route called")
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts ORDER BY created_at DESC')
    posts = c.fetchall()
    conn.close()
    app.logger.debug(f"Fetched posts: {posts}")
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        app.logger.debug("New post form submitted")
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)', (title, content, created_at))
        conn.commit()
        conn.close()
        
        app.logger.debug(f"New post created: {title}")
        
        return redirect(url_for('index'))
    app.logger.debug("Rendering new post form")
    return render_template('new_post.html')

@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        app.logger.debug(f"Edit post form submitted for post ID: {post_id}")
        title = request.form['title']
        content = request.form['content']
        
        c.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, post_id))
        conn.commit()
        conn.close()
        
        app.logger.debug(f"Post updated: {post_id}")
        
        return redirect(url_for('index'))
    
    c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    app.logger.debug(f"Rendering edit form for post: {post}")
    
    return render_template('edit_post.html', post=post)

@app.route('/post/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    app.logger.debug(f"Delete request for post ID: {post_id}")
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    app.logger.debug(f"Post deleted: {post_id}")
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'Admin' and password == 'Password':
            session['logged_in'] = True
            flash('You are now logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
