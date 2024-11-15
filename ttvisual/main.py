# -*- coding: utf-8 -*-
# 必要なモジュールのインポート
import os

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required

from analyze import analyze_bp
from db import get_connection, create_tables, delete_tables
from login import login_bp, login_manager


app=Flask(__name__)

#----------テーブル関連-------------------------
# データベースのテーブル作成
create_tables()

# 使用時はコメントを外す
'''
# テーブル削除(要login.py/xxx変更)
delete_tables()
'''
#----------------------------------------------


#----------ログイン機能-------------------------
app.secret_key = 'your_secret_key'  # セッションのためのシークレットキー

# Flask-Loginの初期化
login_manager.init_app(app)
login_manager.login_view = 'login_bp.login'  # 未ログイン時のリダイレクト先

# ブループリントの登録
app.register_blueprint(analyze_bp)
app.register_blueprint(login_bp)
#----------------------------------------------


#----------ホーム機能---------------------------
# ホーム
@app.route('/')
@login_required
def index():
    con, cur = get_connection()
    db_games = cur.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    games = []
    for row in db_games:
        games.append({'id':row[0], 'date': row[1], 'name1': row[2], 'name2': row[3], 'right_left1': row[4], 'right_left2': row[5], 'contents': row[6]})
    con.commit()
    con.close()

    return render_template(
        'index.html',
        games=games
    )


# データ検索
@app.route('/sear', methods = ['post'])
@login_required
def sear():
    date = request.form['date']
    search = request.form['search']
    con, cur = get_connection()
    if len(date) == 0 and len(search) == 0:
        search_games = cur.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    elif len(date) != 0 and len(search) == 0:
        search_games = cur.execute("SELECT * from games where date = (?) ORDER BY id DESC",
                [date]).fetchall()
    elif len(date) == 0 and len(search) != 0:
        search_games = cur.execute("SELECT * from games where name1 = (?) or name2 = (?) or right_left1 = (?) or right_left2 = (?) ORDER BY id DESC",
                [search,search,search,search]).fetchall()
    else:
        search_games = cur.execute("SELECT * from games where (date = (?) and name1 = (?)) or (date = (?) and name2 = (?)) or right_left1 = (?) or right_left2 = (?) ORDER BY id DESC",
                [date,search,date,search,search,search]).fetchall()
    games = []
    for row in search_games:
        games.append({'id':row[0], 'date': row[1], 'name1': row[2], 'name2': row[3],'right_left1': row[4], 'right_left2': row[5], 'contents': row[6]})
    con.commit()
    con.close()
    return render_template(
        'index.html',
        games=games
    )
#----------------------------------------------


#----------データ登録機能-----------------------
# データ登録画面
@app.route('/form')
@login_required
def form():
    return render_template(
        'form.html'
    )


# データ登録処理
@app.route('/register', methods = ['post','get'])
@login_required
def register():
    date = request.form['date']
    name1 = request.form['name1']
    name2 = request.form['name2']
    right_left1 = request.form['right_left1']
    right_left2 = request.form['right_left2']
    contents = request.files.getlist('contents')

    # ディレクトリパスを設定
    upload_folder = os.path.join('data/files')
    
    # ディレクトリが存在しない場合、作成する
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if contents:
        for file in contents:
            fileName = file.filename
            file_path = os.path.join(upload_folder, fileName)
            file.save(file_path)

    con, cur = get_connection()
    sql = "SELECT count(*) FROM games"
    cur.execute(sql)
    id = cur.fetchall()[0][0]
    if id != 0:
        sql = "SELECT max(id) from games"
        cur.execute(sql)
        id = cur.fetchall()[0][0] + 1
    else:
        id += 1
        
    cur.execute('INSERT INTO games VALUES(?,?,?,?,?,?,?)',
                [id,date,name1,name2,right_left1,right_left2,fileName])
    con.commit()
    con.close()
    return redirect(url_for('index'))
#----------------------------------------------


#----------データ削除機能-----------------------
# データ削除画面
@app.route('/delete')
@login_required
def delete():
    return render_template(
        'delete.html'
    )


# データ削除処理
@app.route('/post_delete',methods = ['post'])
@login_required
def post_delete():
    number=int(request.form['id'])
    con, cur = get_connection()
    cur.execute("DELETE from games where id = (?)",
                [number])
    con.commit()
    con.close()
    return redirect(url_for('index'))
#----------------------------------------------


# 起動処理
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)