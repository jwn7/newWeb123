from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User  # User 모델을 가져오기 위해 수정

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')

# 세션에서 사용자 정보를 가져오는 함수
def get_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return User.query.get(user_id)  # Flask-SQLAlchemy 방식으로 수정

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        # 아이디와 비밀번호 검증
        if not username:
            error = '아이디를 입력해주세요.'
        elif not password:
            error = '비밀번호를 입력해주세요.'
        elif User.query.filter_by(username=username).first() is not None:
            error = f'{username}은 이미 존재하는 아이디입니다.'

        if error is None:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))  # 로그인 페이지로 리다이렉트

        flash(error)  # 에러 메시지 출력
    return render_template('signup.html')  # 템플릿 경로 수정

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
            session['user_id'] = user.id  # 세션에 사용자 ID 저장
            return redirect(url_for('index'))  # 메인 페이지로 리다이렉트

        flash(error)  # 에러 메시지 출력
    return render_template('login.html')  # 템플릿 경로 수정

@bp.route('/logout')
def logout():
    session.pop('user_id', None)  # 세션에서 user_id를 제거하여 로그아웃 처리
    return redirect(url_for('index'))  # 메인 페이지로 리다이렉트
