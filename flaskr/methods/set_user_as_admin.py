from db import get_connection

def set_user_as_admin(username):
    con, cur = get_connection()
    cur.execute('UPDATE users SET is_admin = TRUE WHERE username = ?', (username,))
    con.commit()
    con.close()

if __name__ == "__main__":
    username = 'admin'  # 管理者にするユーザー名
    set_user_as_admin(username)
    print(f"{username} は管理者に設定されました。")
