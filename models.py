from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)  # 게시글 ID
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # 대댓글의 부모 ID

    # 대댓글 관계 설정
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )