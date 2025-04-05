from flask import Flask, render_template, request, redirect, url_for
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

if __name__ == "__main__":
    app.run(debug=True)
