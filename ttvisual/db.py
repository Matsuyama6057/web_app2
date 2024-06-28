# -*- coding: utf-8 -*-
import sqlite3
import time

DATABASE ='data/database.db'


# DBとの接続
def get_connection():
    retries = 5
    while retries > 0:
        try:
            con = sqlite3.connect(DATABASE)
            con.isolation_level = None  # 自動コミットモードを無効にする
            con.row_factory = sqlite3.Row  # 辞書形式でデータを返す
            cur = con.cursor()
            return con, cur
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                time.sleep(1)  # 1秒待機して再試行
                retries -= 1
            else:
                raise
    raise sqlite3.OperationalError("複数回試行してもデータベースに接続できません。")


# テーブル作成
def create_tables():
    con, cur = get_connection()
    cur.execute('''CREATE TABLE IF NOT EXISTS games
                    (id int PRIMARY KEY,
                    date date,
                    name1 text,
                    name2 text,
                    right_left1 CHAR,
                    right_left2 CHAR,
                    contents mediumblob)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL)''')
    cur.close()
    con.commit()
    con.close()


# テーブル削除(要xxx変更)
def delete_tables():
    con, cur = get_connection()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='xxx'")
    result = cur.fetchone()
    if result:
        cur.execute("DROP TABLE xxx")

    con.commit()
    con.close()