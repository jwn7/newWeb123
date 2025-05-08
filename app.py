from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from extensions import db  # extensions.py에서 db 인스턴스 임포트
from models import Comment, BulletinBoard, User
from auth import bp as auth_bp, get_user
import os
1
app = Flask(__name__)

# 데이터베이스 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bulletin_board.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'your_secret_key'
app.config['UPLOADED_FILES_DEST'] = 'uploads'

# DB 초기화 (app과 연결)
db.init_app(app)


# 데이터베이스 테이블 생성 (애플리케이션 컨텍스트 내에서)
def init_db():
    with app.app_context():
        db.create_all()
# 블루프린트 등록
app.register_blueprint(auth_bp)  # auth 블루프린트 등록

# 게시글 목록 조회
@app.route("/")
def index():
    posts = BulletinBoard.query.order_by(BulletinBoard.date_created.desc()).all()
    user = get_user()  # 현재 로그인한 사용자 정보 가져오기
    return render_template("index.html", posts=posts, user=user)

# 게시글 작성
@app.route("/create", methods=["GET", "POST"])
def create():
    user = get_user()
    if not user:
        flash("로그인 후 게시글을 작성할 수 있습니다.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = user.username  # 현재 로그인한 사용자의 이름으로 설정

        new_post = BulletinBoard(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("create_post.html")

# 게시글 수정
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    user = get_user()
    post = BulletinBoard.query.get_or_404(id)

    if not user or post.author != user.username:
        flash("게시글 수정 권한이 없습니다.")
        return redirect(url_for("view_post", post_id=id))

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()

        return redirect(url_for("view_post", post_id=id))

    return render_template("edit.html", post=post)

# 게시글 삭제
@app.route("/delete/<int:id>", methods=["POST"])
def delete_post(id):
    user = get_user()
    post = BulletinBoard.query.get_or_404(id)

    if not user or post.author != user.username:
        flash("게시글 삭제 권한이 없습니다.")
        return redirect(url_for("view_post", post_id=id))

    if post:
        if post.file_path:
            try:
                os.remove(os.path.join(app.config['UPLOADED_FILES_DEST'], post.file_path))
            except FileNotFoundError:
                pass  # 파일이 이미 없는 경우 무시
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for("index"))

# 게시글 상세 보기 및 댓글 표시
@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = BulletinBoard.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    user = get_user()
    return render_template("post.html", post=post, comments=comments, user=user)

# 댓글 또는 대댓글 작성
@app.route("/comment", methods=["POST"])
def add_comment():
    user = get_user()
    if not user:
        flash("로그인 후 댓글을 작성할 수 있습니다.")
        return redirect(request.referrer)  # 이전 페이지로 리다이렉트

    content = request.form['content']
    post_id = request.form['post_id']
    parent_id = request.form.get('parent_id')

    comment = Comment(
        content=content,
        post_id=int(post_id),
        author=user.username,  # 댓글 작성자 설정
        parent_id=int(parent_id) if parent_id else None
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))

# 댓글 수정
@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    user = get_user()
    comment = Comment.query.get_or_404(comment_id)

    if not user or comment.author != user.username:
        flash("댓글 수정 권한이 없습니다.")
        return redirect(url_for('view_post', post_id=comment.post_id))

    if request.method == "POST":
        comment.content = request.form["content"]
        db.session.commit()
        return redirect(url_for('view_post', post_id=comment.post_id))

    return redirect(url_for('view_post', post_id=comment.post_id))

#댓글 삭제
@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    user = get_user()
    comment = Comment.query.get_or_404(comment_id)

    if not user or comment.author != user.username:
        flash("댓글 삭제 권한이 없습니다.")
        return redirect(url_for('view_post', post_id=comment.post_id))

    if comment:
        if comment.replies:  # 대댓글이 있으면 내용만 표시
            comment.content = "삭제된 댓글입니다."
        else:
            db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('view_post', post_id=comment.post_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_FILES_DEST'], filename)


# 앱 실행 시 데이터베이스 초기화 (한 번만 수행하도록 권장)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#파일 업로드 이미지 iframe 처리
@app.route("/download/<filename>")
def download_image(filename):
    return render_template("download.html", filename=filename)
