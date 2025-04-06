from flask import Flask, render_template, session
from auth import bp as auth_bp  # auth 블루프린트 임포트

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(auth_bp)  # auth 블루프린트 등록

DATABASE = 'user.db'  # auth.py 또는 별도 설정 파일에서 관리하는 것이 좋습니다.

# 필요하다면 여기에 데이터베이스 관련 함수 (get_db, init_db, initdb_command)를 둘 수도 있지만,
# auth.py에서 관리하도록 하는 것이 더 모듈화된 구조입니다.
import sqlite3
from flask import g
import os

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

from auth import get_user  # auth.py에서 get_user 함수 임포트

@app.route('/')
def index():
    user = get_user()
    return render_template('index.html', user=user)

if __name__ == '__main__':
    # 데이터베이스 파일이 없으면 초기화 (선택 사항)
    if not os.path.exists('user.db'):
        with app.app_context():
            init_db()
            print('데이터베이스 초기화 완료 (app.py)')
    app.run(debug=True)