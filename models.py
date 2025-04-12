from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# 게시판 모델 정의
class BulletinBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=func.current_timestamp())
    comments = db.relationship('Comment', backref='post', lazy=True)

# 댓글 모델 정의
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('bulletin_board.id'), nullable=False)  # 게시글 ID
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # 대댓글의 부모 ID
    date_created = db.Column(db.DateTime, default=func.current_timestamp())  # 댓글 작성 시간 추가

    # 대댓글 관계 설정
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )