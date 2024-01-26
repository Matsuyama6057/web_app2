# 必要なモジュールのインポート
import os
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, redirect, url_for


app=Flask(__name__)

DATABASE ='database.db'
con = sqlite3.connect(DATABASE)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, date date, name text, right_left text, contents mediumblob)")

#----------テーブル全削除のときのみ使用----------
'''con = sqlite3.connect(DATABASE)
cur = con.cursor()
cur.execute("DROP table games")'''
#----------------------------------------------


@app.route('/')
def index():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, day text, name text, right_left text, contents mediumblob)")
    db_games = cur.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    games = []
    for row in db_games:
        games.append({'id':row[0], 'day': row[1], 'name': row[2], 'right_left': row[3], 'contents': row[4]})
    con.commit()
    con.close()

    return render_template(
        'index.html',
        games=games
    )


@app.route('/sear', methods = ['post'])
def sear():
    date = request.form['date']
    search = request.form['search']
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, day text, name text, right_left text, contents mediumblob)")
    if len(date) == 0 and len(search) == 0:
        search_games = cur.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    elif len(date) != 0 and len(search) == 0:
        search_games = cur.execute("SELECT * from games where date = (?) ORDER BY id DESC",
                [date]).fetchall()
    elif len(date) == 0 and len(search) != 0:
        search_games = cur.execute("SELECT * from games where name = (?) or right_left = (?) ORDER BY id DESC",
                [search,search]).fetchall()
    else:
        search_games = cur.execute("SELECT * from games where date = (?) and (name = (?) or right_left = (?)) ORDER BY id DESC",
                [date,search,search]).fetchall()
    games = []
    for row in search_games:
        games.append({'id':row[0], 'day': row[1], 'name': row[2], 'right_left': row[3], 'contents': row[4]})
    con.commit()
    con.close()
    return render_template(
        'index.html',
        games=games
    )


@app.route('/send',methods = ['post','get'])
def send():
    id = request.form['id']
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * from games where id = (?)",
                [id])
    file_name= cur.fetchall()[0][4]

#----------データ分析の記述---------------------
#----------データの読み込みおよびファイルパス設定-----------------------------
    df = pd.read_csv(file_name)
    dirname = "static/images/"
    os.makedirs(dirname, exist_ok=True)
#----------------------------------------------


#----------コース図-----------------------------
    first=df['名前'][0]
    for row in df['名前']:
        if first!=row:
            second=row
            break

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

    first_score=[]
    second_score=[]
    first_result=[]
    second_result=[]
    for i in range(sum):
        if i!=0 and (score1[i]>score1[i-1] or score2[i]>score2[i-1]):
            first_result.append(first_score)
            second_result.append(second_score)
            first_score=[]
            second_score=[]

        if df['00_03_Point'][i]==first:
            first_score.append(score1[i])
            second_score.append(-1)
        if df['00_03_Point'][i]==second:
            second_score.append(score2[i])
            first_score.append(-1)
    first_result.append(first_score)
    second_result.append(second_score)
    first=df['名前'][0]
    for row in df['名前']:
        if first!=row:
            second=row
            break
    for i in range(len(first_result)):
        F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f,F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s=map(int,[0]*16)
        for j in range(len(first_result[i])):
            row=df['01_SV_03'][j+len(first_result[i])*i]

            if df['名前'][j+len(first_result[i])*i]==first:
                if row=="F":
                    F_f+=1
                elif row=="FM":
                    FM_f+=1
                elif row=="BM":
                    BM_f+=1
                elif row=="B":
                    B_f+=1
                elif row=="FS":
                    FS_f+=1
                elif row=="FMS":
                    FMS_f+=1
                elif row=="BMS":
                    BMS_f+=1
                elif row=="BS":
                    BS_f+=1
            if df['名前'][j+len(first_result[i])*i]==second:
                if row=="F":
                    F_s+=1
                elif row=="FM":
                    FM_s+=1
                elif row=="BM":
                    BM_s+=1
                elif row=="B":
                    B_s+=1
                elif row=="FS":
                    FS_s+=1
                elif row=="FMS":
                    FMS_s+=1
                elif row=="BMS":
                    BMS_s+=1
                elif row=="BS":
                    BS_s+=1



        # (1)味方のコース図
        # フォントの設定
        font_path = "fonts/arial.ttf"
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)

        # 画像のサイズ設定
        width = 600
        height = 400

        # 画像の作成
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 卓球台の描画
        draw.rectangle((50, 50, 550, 350), outline="green", width=3)
        draw.line((300, 50, 300, 350), fill="green", width=3)
        draw.line((50, 200, 550, 200), fill="green", width=3)
        draw.line((50, 50, 550, 50), fill="green", width=3)
        draw.line((50, 350, 550, 350), fill="green", width=3)
        draw.line((170, 50, 170, 350), fill="green", width=3)
        draw.line((420, 50, 420, 350), fill="green", width=3)

        # 味方の選手名
        text = first
        x = 0
        y = 5
        draw.text((x, y), text, font=font, fill="black")

        # 区分ごとの着弾回数
        text = str(F_f)
        x = 110
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FM_f)
        x = 230
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(BM_f)
        x = 360
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(B_f)
        x = 480
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FS_f)
        x = 110
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(FMS_f)
        x = 230
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BMS_f)
        x = 360
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BS_f)
        x = 480
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        # 画像として保存
        filename=dirname + "plot" + str(i) + "_f_" + str(id) + ".png"
        image.save(filename)


        # (2)相手のコース図
        # フォントの設定
        font_path = "fonts/arial.ttf"
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)

        # 画像のサイズ設定
        width = 600
        height = 400

        # 画像の作成
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 卓球台の描画
        draw.rectangle((50, 50, 550, 350), outline="green", width=3)
        draw.line((300, 50, 300, 350), fill="green", width=3)
        draw.line((50, 200, 550, 200), fill="green", width=3)
        draw.line((50, 50, 550, 50), fill="green", width=3)
        draw.line((50, 350, 550, 350), fill="green", width=3)
        draw.line((170, 50, 170, 350), fill="green", width=3)
        draw.line((420, 50, 420, 350), fill="green", width=3)

        # 相手の選手名
        text = second
        x = 0
        y = 5
        draw.text((x, y), text, font=font, fill="black")

        # 区分ごとの着弾回数
        text = str(F_s)
        x = 110
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FM_s)
        x = 230
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(BM_s)
        x = 360
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(B_s)
        x = 480
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FS_s)
        x = 110
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(FMS_s)
        x = 230
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BMS_s)
        x = 360
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BS_s)
        x = 480
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        # 画像として保存
        filename=dirname + "plot" + str(i) + "_s_" + str(id) + ".png"
        image.save(filename)


    for i in range(len(first_result)):
        for j in range(len(first_result[i])):
            if first_result[i][j]!=-1:
                first_result[i][j]="O"
            else:
                first_result[i][j]="X"
            if second_result[i][j]!=-1:
                second_result[i][j]="O"
            else:
                second_result[i][j]="X"

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
#----------------------------------------------


#----------得点率------------------------------
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
        score_rate = count_me / (count_me + count_rival)  # 得点率
        score_rate = "{:.1%}".format(score_rate)
        score_rate_serve.append(["Total",score_rate,count_all,count_me,count_rival])

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
        score_rate = count_me / (count_me + count_rival)  # 得点率
        score_rate = "{:.1%}".format(score_rate)
        score_rate_receive.append(["Total",score_rate,count_all,count_me,count_rival])
        
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
                score_rate = count_me / (count_me + count_rival)  # 得点率
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
                score_rate = count_me / (count_me + count_rival)  # 得点率
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
#----------------------------------------------


#----------打法出現率---------------------------
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
        score_method_rate = 1  # 出現率
        score_method_rate = "{:.1%}".format(score_method_rate)
        score_method_rate_serve.append(["Total",score_method_rate,count_all_method,count_me,count_rival])

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
        score_method_rate = 1  # 出現率
        score_method_rate = "{:.1%}".format(score_method_rate)
        score_method_rate_receive.append(["Total",score_method_rate,count_all_method,count_me,count_rival])

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
#----------------------------------------------


    return render_template('display.html', df_score_list=[df.to_numpy() for df in df_score_list], first=first,second=second,tmp=tmp, summary_score_rate=summary_score_rate, id=id, summary_score_method_rate=summary_score_method_rate)
#----------------------------------------------
#----------ここまでデータ分析の記述--------------


@app.route('/form')
def form():
    return render_template(
        'form.html'
    )


@app.route('/display')
def display():
    return render_template(
        'display.html'
    )


@app.route('/register',methods = ['post','get'])
def register():
    date = request.form['date']
    name = request.form['name']
    right_left = request.form['right_left']
    contents = request.files.getlist('contents')

    if contents:
        for file in contents:
            fileName = file.filename
            file.save(fileName)
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    sql = "SELECT count(*) FROM games"
    cur.execute(sql)
    id=cur.fetchall()[0][0]
    if id!=0:
        sql = "SELECT max(id) from games"
        cur.execute(sql)
        id=cur.fetchall()[0][0]+1
    else:
        id+=1
    cur.execute('INSERT INTO games VALUES(?,?,?,?,?)',
                [id,date,name,right_left,fileName])
    con.commit()
    con.close()
    return redirect(url_for('index'))



@app.route('/delete')
def delete():
    return render_template(
        'delete.html'
    )


@app.route('/post_delete',methods = ['post'])
def post_delete():
    number=int(request.form['id'])
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("DELETE from games where id = (?)",
                [number])
    con.commit()
    con.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
