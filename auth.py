from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_user():
    if 'user_id' in session:
        return User.query.filter_by(username=session['user_id']).first()
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
        elif User.query.filter_by(username=username).first():
            error = '이미 존재하는 아이디입니다.'

        if error is None:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, nickname=nickname)
            db.session.add(new_user)
            db.session.commit()
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
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = '존재하지 않는 아이디입니다.'
        elif not check_password_hash(user.password, password):
            error = '비밀번호가 일치하지 않습니다.'

        if error is None:
            session.clear()
            session['user_id'] = user.username
            flash('로그인되었습니다.')
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))