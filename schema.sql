DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nickname TEXT NOT NULL
);

DROP TABLE IF EXISTS bulletin_board;
CREATE TABLE bulletin_board (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT
);

DROP TABLE IF EXISTS comment;
CREATE TABLE comment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    parent_id INTEGER,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    author TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES bulletin_board (id),
    FOREIGN KEY (parent_id) REFERENCES comment (id)
);