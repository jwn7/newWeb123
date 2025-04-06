import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')

DATABASE = 'user.db'  # app.py에서 관리하거나 설정 파일로 분리하는 것이 좋음

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def get_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    db = get_db()
    return db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

@bp.teardown_request
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@bp.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.login'))  # 블루프린트 이름 명시

        flash(error)
    return render_template('signup.html')  # templates/auth/signup.html

@bp.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('index'))  # 메인 앱의 엔드포인트

        flash(error)
    return render_template('login.html')    # templates/auth/login.html

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))      # 메인 앱의 엔드포인트