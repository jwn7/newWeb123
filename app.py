import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'user.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()

        if not username:
            error = '아이디를 입력해주세요.'
        elif not password:
            error = '비밀번호를 입력해주세요.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'{username}은 이미 존재하는 아이디입니다.'

        if error is None:
            hashed_password = generate_password_hash(password)
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            db.commit()
            return redirect(url_for('login'))

        flash(error)
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = '존재하지 않는 아이디입니다.'
        elif not check_password_hash(user['password'], password):
            error = '비밀번호가 일치하지 않습니다.'

        if error is None:
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    return render_template('login.html')

@app.route('/')
def index():
    user = get_user()
    return render_template('index.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

def get_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    db = get_db()
    return db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

if __name__ == '__main__':
    app.run(debug=True)