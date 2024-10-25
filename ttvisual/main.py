# -*- coding: utf-8 -*-
# 必要なモジュールのインポート
import os

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required

from login import login_bp, login_manager
from db import get_connection, create_tables, delete_tables


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


#----------データ分析機能-----------------------
# データ分析画面
@app.route('/display')
@login_required
def display():
    return render_template(
        'display.html'
    )


# 分析処理
@app.route('/send',methods = ['post','get'])
@login_required
def send():
    # 変数設定
    id = request.form['id']
    name1 = request.form['name1']
    name2 = request.form['name2']
    right_left1 = request.form['right_left1']
    right_left2 = request.form['right_left2']
    con, cur = get_connection()
    cur.execute("SELECT * from games where id = (?)",
                [id])
    data_folder = os.path.join('data/files')
    file_name= os.path.join(data_folder, cur.fetchall()[0][6])
    con.commit()
    con.close()

    # データ読み込み、パス設定
    df = pd.read_csv(file_name)
    dirname = "static/images/"
    os.makedirs(dirname, exist_ok=True)

    # 選手名・利き手を取得
    first=df['名前'][0]
    for i in range(len(df['名前'])):
        if df['名前'][i]!=first:
            second=df['名前'][i]
            break
    flag=0
    if name1 in first:
        pass
    else:
        flag+=1
    if name2 in second:
        pass
    else:
        flag+=1

    if flag==2:
        tmp_name=first
        first=second
        second=tmp_name

    first_right_left=right_left1
    second_right_left=right_left2


    # 1.得点計算
    # 1-1.ゲームカウント・総得点数の取得
    score1=[]
    score2=[]

    for i in range(len(df)):
        row=str(df['00_01_GameCount'][i])
        if row[0]=="n":
            break
        score1.append(int(row[0]))
        tmp=row[2:len(str(row))]
        score2.append(int(tmp))
        i+=1
    sum=i

    # 1-2.各選手の得点・総得点リストの計算
    first_score=[]
    second_score=[]
    first_result=[]
    second_result=[]
    sv03=[]
    sv03_score=[]
    score_name=[]

    for i in range(sum):
        if i!=0 and (score1[i]>score1[i-1] or score2[i]>score2[i-1]):
            first_result.append(first_score)
            second_result.append(second_score)
            sv03.append(sv03_score)

            first_score=[]
            second_score=[]
            sv03_score=[]

        if df['00_03_Point'][i]==first:
            score_name.append(df['名前'][i])
            first_score.append(score1[i])
            second_score.append(-1)
        if df['00_03_Point'][i]==second:
            score_name.append(df['名前'][i])
            second_score.append(score2[i])
            first_score.append(-1)

        sv03_score.append(score1[i])
    first_result.append(first_score)
    second_result.append(second_score)
    sv03.append(sv03_score)


    #----------得点率--------------------------
    # 1.全パターン共通設定
    # 1-1.抽出
    # 選手名(味方・相手)を抽出
    first_player_name = df['名前'][0]
    for row in df['名前']:
        if first_player_name != row:
            second_player_name = row
            break
    # 1-2.リスト
    # 選手名リスト
    player_names = [first_player_name, second_player_name]

    # ゲームカウントリスト
    game_counts = [
        ["0:00"],
        ["0:01","1:00"],
        ["0:02","1:01","2:00"],
        ["0:03","1:02","2:01","3:00"],
        ["0:04","1:03","2:02","3:01","4:00"],
        ["0:05","1:04","2:03","3:02","4:01","5:00"],
        ["0:06","1:05","2:04","3:03","4:02","5:01","6:00"]
    ]

    # 2.データ処理
    # 全データ処理リスト
    summary_score_rate = []
    # 2-1.全ゲーム処理
    # 全プレイヤー情報リスト
    score_rate_players = []
    for player_name in player_names:
        # プレイヤー情報リスト
        score_rate_player = []

        # 2-1-1.サーブ
        # サーブ情報リスト
        score_rate_serve = [
            [player_name,"","","",""],
            ["Service","得点率","本数","得点","失点"]
        ]
        # 計算
        count_all = 0
        count_me = 0
        count_rival = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let"):  # 本数
                count_all = count_all + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_me = count_me + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival = count_rival + 1
        # 本数が0でない時のみ、計算結果を追加
        if count_all != 0:
            score_rate = count_me / count_all  # 得点率
            score_rate = "{:.1%}".format(score_rate)
            score_rate_serve.append(["Total",score_rate,count_all,count_me,count_rival])
        else:
            score_rate_serve = []

        # サーブ情報追加
        score_rate_serve_df = pd.DataFrame(score_rate_serve)
        score_rate_serve_df = score_rate_serve_df.to_html(index=False,header=False)
        score_rate_player.append(score_rate_serve_df)
        # 2-1-2.レシーブ
        # レシーブ情報リスト
        score_rate_receive = [
            [player_name,"","","",""],
            ["Receive","得点率","本数","得点","失点"]
        ]
        # 計算
        count_all = 0
        count_me = 0
        count_rival = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let"):  # 本数
                count_all = count_all + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_me = count_me + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival = count_rival + 1

        # 本数が0でない時のみ、計算結果を追加
        if count_all != 0:
            score_rate = count_me / count_all  # 得点率
            score_rate = "{:.1%}".format(score_rate)
            score_rate_receive.append(["Total",score_rate,count_all,count_me,count_rival])
        else:
            score_rate_receive = []

        # レシーブ情報追加
        score_rate_receive_df = pd.DataFrame(score_rate_receive)
        score_rate_receive_df = score_rate_receive_df.to_html(index=False,header=False)
        score_rate_player.append(score_rate_receive_df)
        # プレイヤー情報追加
        score_rate_players.append(score_rate_player)

    # 全プレイヤー情報追加
    summary_score_rate.append(score_rate_players)

    # 2-2.ゲーム毎処理
    for game_count in game_counts:
        # 全プレイヤー情報リスト
        score_rate_players = []
        for player_name in player_names:
            # プレイヤー情報リスト
            score_rate_player = []

            # 2-1-1.サーブ
            # サーブ情報リスト
            score_rate_serve = [
                [player_name,"","","",""],
                ["Service","得点率","本数","得点","失点"]
            ]
            # 計算
            count_all = 0
            count_me = 0
            count_rival = 0
            for gc in game_count:
                for i in range(len(df)):
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 本数
                        count_all = count_all + 1
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 得点
                        count_me = count_me + 1
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 失点
                        count_rival = count_rival + 1

            # 本数が0でない時のみ、計算結果を追加
            if count_all != 0:
                score_rate = count_me / count_all  # 得点率
                score_rate = "{:.1%}".format(score_rate)
                score_rate_serve.append(["Total",score_rate,count_all,count_me,count_rival])
            else:
                score_rate_serve = []
            # サーブ情報追加
            score_rate_serve_df = pd.DataFrame(score_rate_serve)
            score_rate_serve_df = score_rate_serve_df.to_html(index=False,header=False)
            score_rate_player.append(score_rate_serve_df)
            # 2-1-2.レシーブ
            # レシーブ情報リスト
            score_rate_receive = [
                [player_name,"","","",""],
                ["Receive","得点率","本数","得点","失点"]
            ]
            # 計算
            count_all = 0
            count_me = 0
            count_rival = 0
            for gc in game_count:
                for i in range(len(df)):
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 本数
                        count_all = count_all + 1
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 得点
                        count_me = count_me + 1
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 失点
                        count_rival = count_rival + 1

            # 本数が0でない時のみ、計算結果を追加
            if count_all != 0:
                score_rate = count_me / count_all  # 得点率
                score_rate = "{:.1%}".format(score_rate)
                score_rate_receive.append(["Total",score_rate,count_all,count_me,count_rival])
            else:
                score_rate_receive = []

            # レシーブ情報追加
            score_rate_receive_df = pd.DataFrame(score_rate_receive)
            score_rate_receive_df = score_rate_receive_df.to_html(index=False,header=False)
            score_rate_player.append(score_rate_receive_df)
            # プレイヤー情報追加
            score_rate_players.append(score_rate_player)

        # 全プレイヤー情報追加
        summary_score_rate.append(score_rate_players)

        # 空ゲームを削除
        if count_all == 0:
            del summary_score_rate[-1]
    #------------------------------------------


    #------------得点表-------------------------
    for i in range(len(first_result)):
        first_num=0
        second_num=0
        for j in range(len(first_result[i])):
            if first_result[i][j]!=-1:
                first_num+=1
                first_result[i][j]=first_num
            else:
                first_result[i][j]=" "
            if second_result[i][j]!=-1:
                second_num+=1
                second_result[i][j]=second_num
            else:
                second_result[i][j]=" "


    first_score_data=[]
    second_score_data=[]
    for i in range(len(first_result)):
        first_score_data.append(first_result[i])
        second_score_data.append(second_result[i])
    data_score=[]
    for i in range(len(first_score_data)):
        data_score.append({first:first_score_data[i],second:second_score_data[i]})
    df_score_list=[]
    i=0
    for data in data_score:
        data=pd.DataFrame(data)
        df_score_list.append(data.transpose())
        i+=1
    tmp=len(first)-len(second)
    #------------------------------------------


    #----------コース図-------------------------
    first_sv03_course=[]
    first_sv02_course=[]
    second_sv03_course=[]
    second_sv02_course=[]
    for i in range(len(sv03)):
        F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f,F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s=map(int,[0]*16)
        F_f_sv02,B_f_sv02,F_s_sv02,B_s_sv02=map(int,[0]*4)
        if i==0:
            tmp_j=0
        if i>0:
            tmp_j=len(sv03[i-1])

        for j in range(tmp_j,tmp_j+len(sv03[i])):
            row1=df['01_SV_03'][j]
            row2=df['01_SV_02'][j]
            if df['名前'][j]==first:
                if row1=="F":
                    F_f+=1
                elif row1=="FM":
                    FM_f+=1
                elif row1=="BM":
                    BM_f+=1
                elif row1=="B":
                    B_f+=1
                elif row1=="FS":
                    FS_f+=1
                elif row1=="FMS":
                    FMS_f+=1
                elif row1=="BMS":
                    BMS_f+=1
                elif row1=="BS":
                    BS_f+=1

                if row2=="F":
                    F_f_sv02+=1
                elif row2=="B":
                    B_f_sv02+=1


            if df['名前'][j]==second:
                if row1=="F":
                    F_s+=1
                elif row1=="FM":
                    FM_s+=1
                elif row1=="BM":
                    BM_s+=1
                elif row1=="B":
                    B_s+=1
                elif row1=="FS":
                    FS_s+=1
                elif row1=="FMS":
                    FMS_s+=1
                elif row1=="BMS":
                    BMS_s+=1
                elif row1=="BS":
                    BS_s+=1

                if row2=="F":
                    F_s_sv02+=1
                elif row2=="B":
                    B_s_sv02+=1

        first_sv03_course.append([F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f])
        first_sv02_course.append([F_f_sv02,B_f_sv02])

        second_sv03_course.append([F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s])
        second_sv02_course.append([F_s_sv02,B_s_sv02])

    first_sv03_course_len=len(first_sv03_course)
    second_sv03_course_len=len(second_sv03_course)
    first_sv02_course_len=len(first_sv02_course)
    second_sv02_course_len=len(second_sv02_course)
    #------------------------------------------

    
    #----------打法出現率-----------------------
    # 1.全パターン共通設定
    # 1-1.抽出
    # 選手名(味方・相手)を抽出
    first_player_name = df['名前'][0]
    for row in df['名前']:
        if first_player_name != row:
            second_player_name = row
            break
    # 1-2.リスト
    # 選手名リスト
    player_names = [first_player_name, second_player_name]
    # 打法種類リスト
    service_score_methods = ["Side","(Side)","Back"]
    receive_score_methods = ["Stop","ドライブ","Push","Flick","Chiquita","ミユータ","空振り","不明"]

    # ゲームカウントリスト
    game_counts = [
        ["0:00"],
        ["0:01","1:00"],
        ["0:02","1:01","2:00"],
        ["0:03","1:02","2:01","3:00"],
        ["0:04","1:03","2:02","3:01","4:00"],
        ["0:05","1:04","2:03","3:02","4:01","5:00"],
        ["0:06","1:05","2:04","3:03","4:02","5:01","6:00"]
    ]

    # 2.データ処理
    # 全データ処理リスト
    summary_score_method_rate = []
    # 2-1.全ゲーム処理
    # 全プレイヤー情報リスト
    score_method_rate_players = []
    for player_name in player_names:
        # プレイヤー情報リスト
        score_method_rate_player = []

        # 2-1-1.サーブ
        # サーブ情報リスト
        score_method_rate_serve = [
            [player_name,"","","",""],
            ["Service","出現率","本数","得点","失点"]
        ]
        # 全打法計算
        count_all_method = 0
        count_me = 0
        count_rival = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let"):  # 本数
                count_all_method = count_all_method + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_me = count_me + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival = count_rival + 1

        # 本数が0でない時のみ、計算結果を追加
        if count_all_method != 0:
            score_method_rate = 1  # 出現率
            score_method_rate = "{:.1%}".format(score_method_rate)
            score_method_rate_serve.append(["Total",score_method_rate,count_all_method,count_me,count_rival])
        else:
            score_method_rate_serve = []

        # 打法毎計算
        for service_score_method in service_score_methods:
            count_one_method = 0
            count_me = 0
            count_rival = 0
            for i in range(len(df)):
                if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"01_SV_01"] == service_score_method):  # 個別の本数
                    count_one_method = count_one_method + 1
                if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"01_SV_01"] == service_score_method):  # 得点
                    count_me = count_me + 1
                if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"01_SV_01"] == service_score_method):  # 失点
                    count_rival = count_rival + 1

            # 本数が0でない時のみ、計算結果を追加
            if count_all_method != 0:
                score_method_rate = count_one_method / count_all_method  # 出現率
                score_method_rate = "{:.1%}".format(score_method_rate)
                score_method_rate_serve.append([service_score_method,score_method_rate,count_one_method,count_me,count_rival])

        # サーブ情報追加
        score_method_rate_serve_df = pd.DataFrame(score_method_rate_serve)
        score_method_rate_serve_df = score_method_rate_serve_df.to_html(index=False,header=False)
        score_method_rate_player.append(score_method_rate_serve_df)
        # 2-1-2.レシーブ
        # レシーブ情報リスト
        score_method_rate_receive = [
            [player_name,"","","",""],
            ["Receive","出現率","本数","得点","失点"]
        ]
        # 全打法計算
        count_all_method = 0
        count_me = 0
        count_rival = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let"):  # 本数
                count_all_method = count_all_method + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_me = count_me + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival = count_rival + 1

        # 本数が0でない時のみ、計算結果を追加
        if count_all_method != 0:
            score_method_rate = 1  # 出現率
            score_method_rate = "{:.1%}".format(score_method_rate)
            score_method_rate_receive.append(["Total",score_method_rate,count_all_method,count_me,count_rival])
        else:
            score_method_rate_receive = []

        # 打法毎計算
        for receive_score_method in receive_score_methods:
            count_one_method = 0
            count_me = 0
            count_rival = 0
            for i in range(len(df)):
                if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"02_RV_02"] == receive_score_method):  # 個別の本数
                    count_one_method = count_one_method + 1
                if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"02_RV_02"] == receive_score_method):  # 得点
                    count_me = count_me + 1
                if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"02_RV_02"] == receive_score_method):  # 失点
                    count_rival = count_rival + 1

            # 本数が0でない時のみ、計算結果を追加
            if count_all_method != 0:
                score_method_rate = count_one_method / count_all_method  # 出現率
                score_method_rate = "{:.1%}".format(score_method_rate)
                score_method_rate_receive.append([receive_score_method,score_method_rate,count_one_method,count_me,count_rival])

        # レシーブ情報追加
        score_method_rate_receive_df = pd.DataFrame(score_method_rate_receive)
        score_method_rate_receive_df = score_method_rate_receive_df.to_html(index=False,header=False)
        score_method_rate_player.append(score_method_rate_receive_df)
        # プレイヤー情報追加
        score_method_rate_players.append(score_method_rate_player)

    # 全プレイヤー情報追加
    summary_score_method_rate.append(score_method_rate_players)

    # 2-2.ゲーム毎処理
    for game_count in game_counts:
        # 全プレイヤー情報リスト
        score_method_rate_players = []
        for player_name in player_names:
            # プレイヤー情報リスト
            score_method_rate_player = []

            # 2-1-1.サーブ
            # サーブ情報リスト
            score_method_rate_serve = [
                [player_name,"","","",""],
                ["Service","出現率","本数","得点","失点"]
            ]
            # 全打法計算
            count_all_method = 0
            count_me = 0
            count_rival = 0
            for gc in game_count:
                for i in range(len(df)):
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 本数
                        count_all_method = count_all_method + 1
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 得点
                        count_me = count_me + 1
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 失点
                        count_rival = count_rival + 1

            # 本数が0でない時のみ、計算結果を追加
            if count_all_method != 0:
                score_method_rate = 1  # 出現率
                score_method_rate = "{:.1%}".format(score_method_rate)
                score_method_rate_serve.append(["Total",score_method_rate,count_all_method,count_me,count_rival])
            else:
                score_method_rate_serve = []
            # 打法毎計算
            for service_score_method in service_score_methods:
                count_one_method = 0
                count_me = 0
                count_rival = 0
                for gc in game_count:
                    for i in range(len(df)):
                        if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"01_SV_01"] == service_score_method) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 個別の本数
                            count_one_method = count_one_method + 1
                        if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"01_SV_01"] == service_score_method) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 得点
                            count_me = count_me + 1
                        if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"01_SV_01"] == service_score_method) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 失点
                            count_rival = count_rival + 1

                # 本数が0でない時のみ、計算結果を追加
                if count_all_method != 0:
                    score_method_rate = count_one_method / count_all_method  # 出現率
                    score_method_rate = "{:.1%}".format(score_method_rate)
                    score_method_rate_serve.append([service_score_method,score_method_rate,count_one_method,count_me,count_rival])
            # サーブ情報追加
            score_method_rate_serve_df = pd.DataFrame(score_method_rate_serve)
            score_method_rate_serve_df = score_method_rate_serve_df.to_html(index=False,header=False)
            score_method_rate_player.append(score_method_rate_serve_df)
            # 2-1-2.レシーブ
            # レシーブ情報リスト
            score_method_rate_receive = [
                [player_name,"","","",""],
                ["Receive","出現率","本数","得点","失点"]
            ]
            # 全打法計算
            count_all_method = 0
            count_me = 0
            count_rival = 0
            for gc in game_count:
                for i in range(len(df)):
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 本数
                        count_all_method = count_all_method + 1
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 得点
                        count_me = count_me + 1
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 失点
                        count_rival = count_rival + 1

            # 本数が0でない時のみ、計算結果を追加
            if count_all_method != 0:
                score_method_rate = 1  # 出現率
                score_method_rate = "{:.1%}".format(score_method_rate)
                score_method_rate_receive.append(["Total",score_method_rate,count_all_method,count_me,count_rival])
            else:
                score_method_rate_receive = []
            # 打法毎計算
            for receive_score_method in receive_score_methods:
                count_one_method = 0
                count_me = 0
                count_rival = 0
                for gc in game_count:
                    for i in range(len(df)):
                        if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_04_#"] != "SV Let") and (df.at[df.index[i],"02_RV_02"] == receive_score_method) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 個別の本数
                            count_one_method = count_one_method + 1
                        if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"02_RV_02"] == receive_score_method) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 得点
                            count_me = count_me + 1
                        if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"02_RV_02"] == receive_score_method) and (df.at[df.index[i],"00_01_GameCount"] == gc):  # 失点
                            count_rival = count_rival + 1

                # 本数が0でない時のみ、計算結果を追加
                if count_all_method != 0:
                    score_method_rate = count_one_method / count_all_method  # 出現率
                    score_method_rate = "{:.1%}".format(score_method_rate)
                    score_method_rate_receive.append([receive_score_method,score_method_rate,count_one_method,count_me,count_rival])

            # レシーブ情報追加
            score_method_rate_receive_df = pd.DataFrame(score_method_rate_receive)
            score_method_rate_receive_df = score_method_rate_receive_df.to_html(index=False,header=False)
            score_method_rate_player.append(score_method_rate_receive_df)
            # プレイヤー情報追加
            score_method_rate_players.append(score_method_rate_player)

        # 全プレイヤー情報追加
        summary_score_method_rate.append(score_method_rate_players)

        # 空ゲームを削除
        if count_all_method == 0:
            del summary_score_method_rate[-1]
    #------------------------------------------


    # 全データをreturn
    return render_template('display.html', df_score_list=[df.to_numpy() for df in df_score_list], first=first,second=second,tmp=tmp, summary_score_rate=summary_score_rate, id=id, summary_score_method_rate=summary_score_method_rate,
                           first_sv03_course=first_sv03_course,second_sv03_course=second_sv03_course,
                           first_sv02_course=first_sv02_course,second_sv02_course=second_sv02_course,
                           first_sv03_course_len=first_sv03_course_len,second_sv03_course_len=second_sv03_course_len,
                           first_sv02_course_len=first_sv02_course_len,second_sv02_course_len=second_sv02_course_len,
                           first_right_left=first_right_left,second_right_left=second_right_left,
                           score_name=score_name)
#----------------------------------------------


# 起動処理
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)