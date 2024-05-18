from flask import Blueprint, render_template, redirect, url_for, request, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_connection

login_bp = Blueprint('login_bp', __name__)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get_by_username(username):
        con, cur = get_connection()
        cur.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user_data = cur.fetchone()
        cur.close()
        con.close()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        con, cur = get_connection()
        cur.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (user_id,))
        user_data = cur.fetchone()
        cur.close()
        con.close()
        if user_data:
            return User(*user_data)
        return None

login_manager = LoginManager()
login_manager.login_message = "このページにアクセスするためには、ログインが必要です。"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

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
@login_bp.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        # ユーザー名の重複チェック
        if User.get_by_username(username):
            flash('そのユーザー名は既に使用されています。違うユーザー名を登録して下さい。', 'error')
            return redirect(url_for('login_bp.user_register'))

        # ユーザーをデータベースに追加
        con, cur = get_connection()
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        cur.close()
        con.commit()
        con.close()
        
        flash('ユーザーは正常に登録されました。', 'success')
        return redirect(url_for('login_bp.login'))
    return render_template('user_register.html')
