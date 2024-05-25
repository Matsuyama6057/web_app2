# -*- coding: utf-8 -*-
import sys
import os

# 1つ上の階層のパスを取得
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 1つ上の階層のパスをsys.pathに追加
sys.path.append(parent_dir)

from db import get_connection

def set_user_as_admin(username):
    con, cur = get_connection()
    cur.execute('UPDATE users SET is_admin = TRUE WHERE username = ?', (username,))
    con.commit()
    con.close()

if __name__ == "__main__":
    username = 'admin'  # 管理者にするユーザー名
    set_user_as_admin(username)
    print("completely set to Administrator!")
