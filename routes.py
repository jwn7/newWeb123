from flask import render_template, request, redirect, url_for,Flask
from models import db, BulletinBoard
from app import app
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', post=post)

if __name__ == '__main__':
    app.run(debug=True)

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
