# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_connection

login_bp = Blueprint('login_bp', __name__)


# ユーザークラス
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    # ユーザ名を取得
    @staticmethod
    def get_by_username(username):
        con, cur = get_connection()
        cur.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user_data = cur.fetchone()
        con.close()
        if user_data:
            return User(*user_data)
        return None

    # ユーザIDを取得
    @staticmethod
    def get_by_id(user_id):
        con, cur = get_connection()
        cur.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (user_id,))
        user_data = cur.fetchone()
        con.close()
        if user_data:
            return User(*user_data)
        return None

    # ユーザを削除
    @staticmethod
    def delete_by_id(user_id):
        con, cur = get_connection()
        cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
        con.commit()
        con.close()
    
    # ユーザを並び替え
    @staticmethod
    def order_by_id():
        con, cur = get_connection()
        cur.execute('SELECT id FROM users ORDER BY id')
        users = cur.fetchall()

        for index, user in enumerate(users):
            new_id = index + 1
            cur.execute('UPDATE users SET id = ? WHERE id = ?', (new_id, user['id']))

        con.commit()
        con.close()


# ログイン制限
login_manager = LoginManager()
login_manager.login_message = "このページにアクセスするためには、ログインが必要です。"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


#----------ユーザ機能---------------------------
# ログイン
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('ログインに成功しました。', 'success')
            get_flashed_messages()
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています。', 'error')
    return render_template('login.html')


# ログアウト
@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('login_bp.login'))


# ユーザー登録
@login_bp.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        # ユーザー名の重複チェック
        if User.get_by_username(username):
            flash('そのユーザー名は既に使用されています。違うユーザー名を登録して下さい。', 'error')
            return redirect(url_for('login_bp.register_user'))

        # ユーザーをデータベースに追加
        con, cur = get_connection()
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        con.commit()
        con.close()
        
        User.order_by_id()
        flash('ユーザーは正常に登録されました。', 'success')
        return redirect(url_for('login_bp.login'))
    return render_template('register_user.html')


# ユーザー一覧
@login_bp.route('/list_user')
def list_user():
    con, cur = get_connection()
    cur.execute('SELECT id, username FROM users ORDER BY id ASC')
    users = cur.fetchall()
    con.close()
    return render_template('list_user.html', users=users)


# ユーザー削除
@login_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    User.delete_by_id(user_id)
    User.order_by_id()
    flash('ユーザーは正常に削除されました。', 'success')
    return redirect(url_for('login_bp.list_user'))
#----------------------------------------------