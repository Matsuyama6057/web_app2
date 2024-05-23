from flask import Blueprint, render_template, redirect, url_for, request, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_connection

login_bp = Blueprint('login_bp', __name__)


# ユーザークラス
class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

    @staticmethod
    def get_by_username(username):
        con, cur = get_connection()
        cur.execute('SELECT id, username, password_hash, is_admin FROM users WHERE username = ?', (username,))
        user_data = cur.fetchone()
        con.close()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        con, cur = get_connection()
        cur.execute('SELECT id, username, password_hash, is_admin FROM users WHERE id = ?', (user_id,))
        user_data = cur.fetchone()
        con.close()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def delete_by_id(user_id):
        con, cur = get_connection()
        cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
        con.commit()
        con.close()


login_manager = LoginManager()
login_manager.login_message = "このページにアクセスするためには、ログインが必要です。"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


#----------ユーザー機能-------------------------
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
        con.commit()
        con.close()
        
        flash('ユーザーは正常に登録されました。', 'success')
        return redirect(url_for('login_bp.login'))
    return render_template('user_register.html')


# ユーザー削除
@login_bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.id != user_id:
        flash('他のユーザーを削除することはできません。', 'error')
        return redirect(url_for('index'))

    User.delete_by_id(user_id)
    logout_user()
    flash('ユーザーは正常に削除されました。', 'success')
    return redirect(url_for('login_bp.login'))
#----------------------------------------------


#----------管理者機能---------------------------
# 管理者ログイン
@login_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)
        if user and user.is_admin and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('管理者としてログインしました。', 'success')
            return redirect(url_for('login_bp.admin_dashboard'))
        else:
            flash('ユーザー名またはパスワードが間違っています。', 'error')
    return render_template('admin_login.html')


# 管理者ダッシュボード
@login_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('アクセスが拒否されました。', 'error')
        return redirect(url_for('login_bp.admin_login'))

    con, cur = get_connection()
    cur.execute('SELECT id, username FROM users')
    users = cur.fetchall()
    con.close()
    return render_template('admin_dashboard.html', users=users)


# ユーザー削除
@login_bp.route('/admin_delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('アクセスが拒否されました。', 'error')
        return redirect(url_for('login_bp.admin_login'))

    User.delete_by_id(user_id)
    flash('ユーザーは正常に削除されました。', 'success')
    return redirect(url_for('login_bp.admin_dashboard'))
#----------------------------------------------