from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask import g

bp = Blueprint('auth', __name__, url_prefix='/auth')

DATABASE = "bulletin_board.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()

def get_user():
    if 'user_id' in session:
        return query_db("SELECT id, username, nickname FROM user WHERE username = ?", (session['user_id'],), one=True)
    return None

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        nickname = request.form['nickname']
        password = request.form['password']
        error = None

        if not username:
            error = '아이디를 입력해주세요.'
        elif not nickname:
            error = '사용자 이름을 입력해주세요.'
        elif not password:
            error = '비밀번호를 입력해주세요.'
        elif query_db("SELECT id FROM user WHERE username = ?", (username,), one=True):
            error = '이미 존재하는 아이디입니다.'

        if error is None:
            hashed_password = generate_password_hash(password)
            query = f"INSERT INTO user (username, password, nickname) VALUES ('{username}', '{hashed_password}', '{nickname}')"
            execute_db(query)
            flash('회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = query_db("SELECT id, username, password, nickname FROM user WHERE username = ?", (username,), one=True)

        if user is None:
            error = '존재하지 않는 아이디입니다.'
        elif not check_password_hash(user['password'], password):
            error = '비밀번호가 일치하지 않습니다.'

        if error is None:
            session.clear()
            session['user_id'] = user['username']
            flash('로그인되었습니다.')
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))