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
cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, date date, name1 text, name2 text, right_left1 CHAR, right_left2 CHAR, contents mediumblob)")

#----------テーブル全削除のときのみ使用----------
'''con = sqlite3.connect(DATABASE)
cur = con.cursor()
cur.execute("DROP table games")'''
#----------------------------------------------


@app.route('/')
def index():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, day text, name1 text, name2 text, right_left1 CHAR, right_left2 CHAR, contents mediumblob)")
    db_games = cur.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    games = []
    for row in db_games:
        games.append({'id':row[0], 'day': row[1], 'name1': row[2], 'name2': row[3], 'right_left1': row[4], 'right_left2': row[5], 'contents': row[6]})
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
    cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, day text, name1 text, name2 text, right_left1 CHAR, right_left2 CHAR, contents mediumblob)")
    if len(date) == 0 and len(search) == 0:
        search_games = cur.execute('SELECT * FROM games ORDER BY id DESC').fetchall()
    elif len(date) != 0 and len(search) == 0:
        search_games = cur.execute("SELECT * from games where date = (?) ORDER BY id DESC",
                [date]).fetchall()
    elif len(date) == 0 and len(search) != 0:
        search_games = cur.execute("SELECT * from games where name1 = (?) or name2 = (?) or right_left1 = (?) or right_left2 = (?) ORDER BY id DESC",
                [search,search]).fetchall()
    else:
        search_games = cur.execute("SELECT * from games where date = (?) and (name1 = (?) or name2 = (?) or (right_left1 = (?) and right_left2 = (?))) ORDER BY id DESC",
                [date,search,search]).fetchall()
    games = []
    for row in search_games:
        games.append({'id':row[0], 'day': row[1], 'name1': row[2], 'name2': row[3],'right_left1': row[4], 'right_left2': row[5], 'contents': row[6]})
    con.commit()
    con.close()
    return render_template(
        'index.html',
        games=games
    )


@app.route('/send',methods = ['post','get'])
def send():
    id = request.form['id']
    name1 = request.form['name1']
    name2 = request.form['name2']
    right_left1 = request.form['right_left1']
    right_left2 = request.form['right_left2']
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * from games where id = (?)",
                [id])
    file_name= cur.fetchall()[0][6]



#----------データ分析の記述---------------------
#----------データの読み込みおよびファイルパス設定-----------------------------
    df = pd.read_csv(file_name)
    dirname = "static/images/"
    os.makedirs(dirname, exist_ok=True)
#----------------------------------------------
    first=str(df['名前'][0])
    for i in range(len(df)):
        row=str(df['名前'][i])
        if row!=first:
            second=row
            break
    if name1 in second:
        second_right_left=right_left1
        first_right_left=right_left2
    else:
        first_right_left=right_left1
        second_right_left=right_left2



#----------コース図-----------------------------


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
    sv03=[]
    sv03_score=[]
    for i in range(sum):
        if i!=0 and (score1[i]>score1[i-1] or score2[i]>score2[i-1]):
            first_result.append(first_score)
            second_result.append(second_score)
            sv03.append(sv03_score)
            first_score=[]
            second_score=[]
            sv03_score=[]


        if df['00_03_Point'][i]==first:
            first_score.append(score1[i])
            second_score.append(-1)
        if df['00_03_Point'][i]==second:
            second_score.append(score2[i])
            first_score.append(-1)
        sv03_score.append(score1[i])
    first_result.append(first_score)
    second_result.append(second_score)
    sv03.append(sv03_score)



    for i in range(len(sv03)):
        F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f,F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s=map(int,[0]*16)
        if i==0:
            tmp_j=0
        if i>0:
            tmp_j=len(sv03[i-1])
            print(tmp_j)
        for j in range(tmp_j,tmp_j+len(sv03[i])):
            row1=df['01_SV_03'][j]
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






        # (1)味方のコース図
        # フォントの設定
        font_path = "arial.ttf"
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)

        # 画像のサイズ設定
        width = 600
        height = 800

        # 画像の作成
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 卓球台の描画
        draw.rectangle((50, 50+400, 550, 350+400), outline="green", width=3)
        draw.line((300, 50+400, 300, 350+400), fill="green", width=3)
        draw.line((50, 200+400, 550, 200+400), fill="green", width=3)
        draw.line((50, 50+400, 550, 50+400), fill="green", width=3)
        draw.line((50, 350+400, 550, 350+400), fill="green", width=3)
        draw.line((170, 50+400, 170, 350+400), fill="green", width=3)
        draw.line((420, 50+400, 420, 350+400), fill="green", width=3)

        # ネットの描画
        draw.line((20, 50+400, 580, 50+400), fill="green", width=3)
        draw.line((20, 30+400, 20, 50+400), fill="green", width=3)
        draw.line((580, 30+400, 580, 50+400), fill="green", width=3)
        draw.line((20, 30+400, 580, 30+400), fill="green", width=3)

        #対面の卓球台の描画
        draw.rectangle((50, 50-20+100, 550, 350-20+100), outline="green", width=3)
        draw.line((300, 50-20+100, 300, 350-20+100), fill="green", width=3)



        # 味方の選手名
        text = first
        x = 0
        y = 5
        draw.text((x, y+400), text, font=font, fill="black")

        if first_right_left=="右":

            # 区分ごとの着弾回数
            text = str(F_f)
            x = 110
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(FM_f)
            x = 230
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(BM_f)
            x = 360
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(B_f)
            x = 480
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(FS_f)
            x = 110
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(FMS_f)
            x = 230
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(BMS_f)
            x = 360
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(BS_f)
            x = 480
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

        if second_right_left=="左":
            pass

        # 画像として保存
        filename=dirname + "plot" + str(i) + "_f_" + str(id) + ".png"
        image.save(filename)


        # (2)相手のコース図
        # フォントの設定
        font_path = "arial.ttf"
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)

        # 画像のサイズ設定
        width = 600
        height = 800

        # 画像の作成
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 卓球台の描画
        draw.rectangle((50, 50+400, 550, 350+400), outline="green", width=3)
        draw.line((300, 50+400, 300, 350+400), fill="green", width=3)
        draw.line((50, 200+400, 550, 200+400), fill="green", width=3)
        draw.line((50, 50+400, 550, 50+400), fill="green", width=3)
        draw.line((50, 350+400, 550, 350+400), fill="green", width=3)
        draw.line((170, 50+400, 170, 350+400), fill="green", width=3)
        draw.line((420, 50+400, 420, 350+400), fill="green", width=3)

        # ネットの描画
        draw.line((20, 50+400, 580, 50+400), fill="green", width=3)
        draw.line((20, 30+400, 20, 50+400), fill="green", width=3)
        draw.line((580, 30+400, 580, 50+400), fill="green", width=3)
        draw.line((20, 30+400, 580, 30+400), fill="green", width=3)

        #対面の卓球台の描画
        draw.rectangle((50, 50-20+100, 550, 350-20+100), outline="green", width=3)
        draw.line((300, 50-20+100, 300, 350-20+100), fill="green", width=3)

        # 相手の選手名
        text = second
        x = 0
        y = 5
        draw.text((x, y+400), text, font=font, fill="black")

        if second_right_left=="右":
            # 区分ごとの着弾回数
            text = str(F_s)
            x = 110
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(FM_s)
            x = 230
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(BM_s)
            x = 360
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(B_s)
            x = 480
            y = 125
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(FS_s)
            x = 110
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(FMS_s)
            x = 230
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(BMS_s)
            x = 360
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

            text = str(BS_s)
            x = 480
            y = 275
            draw.text((x, y+400), text, font=font, fill="black")

        if second_right_left=="左":
            pass

        # 画像として保存
        filename=dirname + "plot" + str(i) + "_s_" + str(id) + ".png"
        image.save(filename)


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
    print(first,second)
#----------------------------------------------


#----------得点率------------------------------
    # 全パターン共通設定
    # 得点率のデータフレームまとめ(4パターンを格納)
    summary_df_score_rate = []

    # 味方と相手の選手名を抽出
    first_player_name = df['名前'][0]
    for row in df['名前']:
        if first_player_name != row:
            second_player_name = row
            break

    # 選手名をまとめたリスト
    player_names = [first_player_name, second_player_name]

    # ゲームカウントのパターンを抽出
    game_count_pattern_list = [
        ["0:00"],
        ["0:01","1:00"],
        ["0:02","1:01","2:00"],
        ["1:02","2:01"],
        ["2,02"]
    ]


    # 味方と相手の処理を繰り返す
    for player_name in player_names:
        # (1)サーブ
        # 得点率の表を作成
        table_score_rate = [
            [player_name,"","","",""],
            ["Service","得点率","サーブ数","得点","失点"]
        ]

        # ゲーム毎の得点率・サーブ数・得点・失点を計算
        game_index = 1  # ゲーム毎のラベル用
        for game_count_pattern in game_count_pattern_list:
            count_serve = 0
            count_my_point = 0
            count_rival_point = 0
            for i in range(len(df)):
                for game_count in game_count_pattern:
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == game_count):  # サーブ数
                        count_serve = count_serve + 1
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == game_count):  # 得点
                        count_my_point = count_my_point + 1
                    if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"00_01_GameCount"] == game_count):  # 失点
                        count_rival_point = count_rival_point + 1

            # 全数値が0でない時のみ、計算結果を表に追加
            if (count_serve != 0) and (count_my_point != 0) and (count_rival_point != 0):
                score_rate = count_my_point / (count_my_point + count_rival_point)  # 得点率
                score_rate = "{:.1%}".format(score_rate)
                table_score_rate.append(["{}ゲーム目".format(game_index),score_rate,count_serve,count_my_point,count_rival_point])
            game_index = game_index + 1

        # トータルの得点率・サーブ数・得点・失点を計算
        count_serve = 0
        count_my_point = 0
        count_rival_point = 0
        for i in range(len(df)):
            if df.at[df.index[i],"01_SV_00"] == player_name:  # サーブ数
                count_serve = count_serve + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_my_point = count_my_point + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival_point = count_rival_point + 1
        score_rate = count_my_point / (count_my_point + count_rival_point)  # 得点率
        score_rate = "{:.1%}".format(score_rate)
        table_score_rate.append(["Total",score_rate,count_serve,count_my_point,count_rival_point])

        # 得点率の表からデータフレームを作成
        df_score_rate = pd.DataFrame(table_score_rate)
        df_score_rate = df_score_rate.to_html(index=False,header=False)
        summary_df_score_rate.append(df_score_rate)


        # (2)レシーブ
        # 得点率の表を作成
        table_score_rate = [
            [player_name,"","","",""],
            ["Receive","得点率","レシーブ数","得点","失点"]
        ]

        # ゲーム毎の得点率・レシーブ数・得点・失点を計算
        game_index = 1  # ゲーム毎のラベル用
        for game_count_pattern in game_count_pattern_list:
            count_serve = 0
            count_my_point = 0
            count_rival_point = 0
            for i in range(len(df)):
                for game_count in game_count_pattern:
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_01_GameCount"] == game_count):  # レシーブ数
                        count_serve = count_serve + 1
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_03_Point"] == player_name) and (df.at[df.index[i],"00_01_GameCount"] == game_count):  # 得点
                        count_my_point = count_my_point + 1
                    if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])) and (df.at[df.index[i],"00_01_GameCount"] == game_count):  # 失点
                        count_rival_point = count_rival_point + 1

            # 全数値が0でない時のみ、計算結果を表に追加
            if (count_serve != 0) and (count_my_point != 0) and (count_rival_point != 0):
                score_rate = count_my_point / (count_my_point + count_rival_point)  # 得点率
                score_rate = "{:.1%}".format(score_rate)
                table_score_rate.append(["{}ゲーム目".format(game_index),score_rate,count_serve,count_my_point,count_rival_point])
            game_index = game_index + 1

        # トータルの得点率・レシーブ数・得点・失点を計算
        count_serve = 0
        count_my_point = 0
        count_rival_point = 0
        for i in range(len(df)):
            if df.at[df.index[i],"01_SV_00"] != player_name and (not pd.isna(df.at[df.index[i],"02_RV_02"])):  # レシーブ数
                count_serve = count_serve + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_my_point = count_my_point + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival_point = count_rival_point + 1
        score_rate = count_my_point / (count_my_point + count_rival_point)  # 得点率
        score_rate = "{:.1%}".format(score_rate)
        table_score_rate.append(["Total",score_rate,count_serve,count_my_point,count_rival_point])

        # 得点率の表からデータフレームを作成
        df_score_rate = pd.DataFrame(table_score_rate)
        df_score_rate = df_score_rate.to_html(index=False,header=False)
        summary_df_score_rate.append(df_score_rate)
#----------------------------------------------


#----------打法出現率---------------------------
    # 全パターン共通設定
    # 打法出現率のデータフレームまとめ(2パターンを格納)
    summary_df_score_method_rate = []

    # 味方と相手の選手名を抽出
    first_player_name = df['名前'][0]
    for row in df['名前']:
        if first_player_name != row:
            second_player_name = row
            break

    # 選手名をまとめたリスト
    player_names = [first_player_name, second_player_name]

    # 打法の種類をまとめたリスト
    service_score_methods = ["Side","(Side)","Back"]
    receive_score_methods = ["Stop","ドライブ","Push","Flick","Chiquita","ミユータ","空振り","不明"]

    # ゲームカウントのパターンを抽出
    game_count_pattern_list = [
        ["0:00"],
        ["0:01","1:00"],
        ["0:02","1:01","2:00"],
        ["1:02","2:01"],
        ["2,02"]
    ]


    # 味方と相手の処理を繰り返す
    for player_name in player_names:
        # (1)サーブ
        # 打法出現率の表を作成
        table_score_method_rate = [
            [player_name,"","","",""],
            ["Service","本数","出現率","得点","失点"]
        ]

        # 全打法の本数を計算
        count_all_method_point = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] == player_name):
                count_all_method_point = count_all_method_point + 1

        # 打法ごとに個別の本数・得点・失点・出現率を計算
        for service_score_method in service_score_methods:
            count_one_method_point = 0
            count_my_point = 0
            count_rival_point = 0
            for i in range(len(df)):
                if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"01_SV_01"] == service_score_method):  # 個別の本数
                    count_one_method_point = count_one_method_point + 1
                if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"01_SV_01"] == service_score_method) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                    count_my_point = count_my_point + 1
                if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"01_SV_01"] == service_score_method) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                    count_rival_point = count_rival_point + 1
            score_method_rate = count_one_method_point / count_all_method_point  # 出現率
            score_method_rate = "{:.1%}".format(score_method_rate)
            table_score_method_rate.append([service_score_method,count_one_method_point,score_method_rate,count_my_point,count_rival_point])

        # 全打法の得点・失点・出現率を計算
        count_my_point = 0
        count_rival_point = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_my_point = count_my_point + 1
            if (df.at[df.index[i],"01_SV_00"] == player_name) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival_point = count_rival_point + 1
        score_method_rate = 1  # 出現率
        score_method_rate = "{:.1%}".format(score_method_rate)
        table_score_method_rate.append(["Total",count_all_method_point,score_method_rate,count_my_point,count_rival_point])

        # 打法出現率の表からデータフレームを作成
        df_score_method_rate = pd.DataFrame(table_score_method_rate)
        df_score_method_rate = df_score_method_rate.to_html(index=False,header=False)
        summary_df_score_method_rate.append(df_score_method_rate)


        # (2)レシーブ
        # 打法出現率の表を作成
        table_score_method_rate = [
            [player_name,"","","",""],
            ["Receive","本数","出現率","得点","失点"]
        ]

        # 全打法の本数を計算
        count_all_method_point = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])):
                count_all_method_point = count_all_method_point + 1

        # 打法ごとに個別の本数・得点・失点・出現率を計算
        for receive_score_method in receive_score_methods:
            count_one_method_point = 0
            count_my_point = 0
            count_rival_point = 0
            for i in range(len(df)):
                if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"02_RV_02"] == receive_score_method):  # 個別の本数
                    count_one_method_point = count_one_method_point + 1
                if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"02_RV_02"] == receive_score_method) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                    count_my_point = count_my_point + 1
                if (df.at[df.index[i],"01_SV_00"] != player_name) and (df.at[df.index[i],"02_RV_02"] == receive_score_method) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                    count_rival_point = count_rival_point + 1
            score_method_rate = count_one_method_point / count_all_method_point  # 出現率
            score_method_rate = "{:.1%}".format(score_method_rate)
            table_score_method_rate.append([receive_score_method,count_one_method_point,score_method_rate,count_my_point,count_rival_point])

        # 全打法の得点・失点・出現率を計算
        count_my_point = 0
        count_rival_point = 0
        for i in range(len(df)):
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_03_Point"] == player_name):  # 得点
                count_my_point = count_my_point + 1
            if (df.at[df.index[i],"01_SV_00"] != player_name) and (not pd.isna(df.at[df.index[i],"02_RV_02"])) and (df.at[df.index[i],"00_03_Point"] != player_name) and (not pd.isna(df.at[df.index[i], "00_03_Point"])):  # 失点
                count_rival_point = count_rival_point + 1
        score_method_rate = 1  # 出現率
        score_method_rate = "{:.1%}".format(score_method_rate)
        table_score_method_rate.append(["Total",count_all_method_point,score_method_rate,count_my_point,count_rival_point])

        # 打法出現率の表からデータフレームを作成
        df_score_method_rate = pd.DataFrame(table_score_method_rate)
        df_score_method_rate = df_score_method_rate.to_html(index=False,header=False)
        summary_df_score_method_rate.append(df_score_method_rate)
#----------------------------------------------


    return render_template('display.html', df_score_list=[df.to_numpy() for df in df_score_list], first=first,second=second,tmp=tmp, summary_df_score_rate=summary_df_score_rate, id=id, summary_df_score_method_rate=summary_df_score_method_rate)
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
    name1 = request.form['name1']
    name2 = request.form['name2']
    right_left1 = request.form['right_left1']
    right_left2 = request.form['right_left2']
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
    cur.execute('INSERT INTO games VALUES(?,?,?,?,?,?,?)',
                [id,date,name1,name2,right_left1,right_left2,fileName])
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
