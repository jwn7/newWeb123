from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from models import db, Comment
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

# 데이터베이스 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bulletin_board.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 게시판 모델 정의
class BulletinBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

# 게시글 목록 조회
@app.route("/")
def index():
    posts = BulletinBoard.query.order_by(BulletinBoard.date_created.desc()).all()
    return render_template("index.html", posts=posts)

# 게시글 작성
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = request.form["author"]

        new_post = BulletinBoard(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("create.html")

# 게시글 수정
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = BulletinBoard.query.get(id)

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("edit.html", post=post)

# 게시글 삭제
@app.route("/delete/<int:id>", methods=["POST"])
def delete_post(id):
    post = BulletinBoard.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for("index"))

# 게시글 상세 보기 및 댓글 표시
@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = BulletinBoard.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    return render_template("post.html", post=post, comments=comments)

# 댓글 또는 대댓글 작성
@app.route("/comment", methods=["POST"])
def add_comment():
    content = request.form['content']
    post_id = request.form['post_id']
    parent_id = request.form.get('parent_id')

    comment = Comment(
        content=content,
        post_id=int(post_id),
        parent_id=int(parent_id) if parent_id else None
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))

# 댓글 수정
@app.route("/edit_comment/<int:comment_id>", methods=["POST"])
def edit_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        comment.content = request.form["content"]
        db.session.commit()
    return redirect(url_for('view_post', post_id=comment.post_id))

# 댓글 삭제
@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        if comment.replies:
            comment.content = "삭제된 댓글입니다."
        else:
            db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('view_post', post_id=comment.post_id))

# 앱 실행
if __name__ == "__main__":
    app.run(debug=True)