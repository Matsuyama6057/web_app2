#from flaskr import app
from flask import Flask
from waitress import serve
from flask import render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import patches
from werkzeug.utils import secure_filename
from flask import send_from_directory
import os
import numpy as np
import random
from PIL import Image, ImageDraw,ImageFont

app=Flask(__name__)

DATABASE ='database.db'

#--------------テーブル全削除のときのみ使用-------------
'''con = sqlite3.connect(DATABASE)
cur = con.cursor()
cur.execute("DROP table games")'''
#----------------------------------------------------

con = sqlite3.connect(DATABASE)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS games (id int PRIMARY KEY, date date, name text, right_left text, contents mediumblob)")

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
    print(date,len(date))
    print(search,len(search))
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
    num = request.form['id']
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * from games where id = (?)",
                [num])
    file_name= cur.fetchall()[0][4]

#-------------データ分析の記述--------------------
#-------------仮の分析---------------------------
    df = pd.read_csv(file_name)
    B=0
    F=0
    for row in df['02_RV_01']:
        if row=="B":
            B+=1
        elif row=="F":
            F+=1
    fig = plt.figure()
    labels = ['B', 'F']
    values = [B, F]
    lefts = np.arange(len(values))
    plt.bar(lefts, values, tick_label=labels, width=0.5, color="#b2b2b2")
    dirname = "static/images/"
    os.makedirs(dirname, exist_ok=True)
    filename=dirname + "plot.png"
    fig.savefig(filename)
# ----------------仮の分析終わり-----------------------------------------------------
#--------コース図--------------------------------------------------------------------
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
            print("game_point")


        print(i,df['00_03_Point'][i],score1[i],score2[i])
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
    k=0
    print(len(first_result[0]))
    for i in range(len(first_result)):
        F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f,F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s=map(int,[0]*16)
        for j in range(len(first_result[i])):

            row=df['01_SV_03'][j+len(first_result[i])*i]
            print(row)
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

        print(F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f,F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s)
        # 画像のサイズ
        font_path = "arial.ttf"  # フォントファイルのパス
        font_size = 40  # フォントサイズ
        font = ImageFont.truetype(font_path, font_size)

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

        print("firstのコース")
        text = str(F_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 110
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FM_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 230
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(BM_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 360
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(B_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 480
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FS_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 110
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(FMS_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 230
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BMS_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 360
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BS_f)
        print(text)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 480
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        # フォントの設定
        font_path = "arial.ttf"  # フォントファイルのパス
        font_size = 40  # フォントサイズ
        font = ImageFont.truetype(font_path, font_size)

        # 文字列の描画
        text =first
        #text_width, text_height = draw.textsize(text, font=font)
        x = 0
        y = 5
        draw.text((x, y), text, font=font, fill="black")

        filename=dirname + "plot" + str(i) + "_f.png"
        image.save(filename)

        #相手
        # 画像のサイズ
        font_path = "arial.ttf"  # フォントファイルのパス
        font_size = 40  # フォントサイズ
        font = ImageFont.truetype(font_path, font_size)
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

        text = str(F_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 110
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FM_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 230
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(BM_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 360
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(B_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 480
        y = 125
        draw.text((x, y), text, font=font, fill="black")

        text = str(FS_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 110
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(FMS_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 230
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BMS_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 360
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        text = str(BS_s)
        #text_width, text_height = draw.textsize(text, font=font)
        x = 480
        y = 275
        draw.text((x, y), text, font=font, fill="black")

        # フォントの設定
        font_path = "arial.ttf"  # フォントファイルのパス
        font_size = 40  # フォントサイズ
        font = ImageFont.truetype(font_path, font_size)

        # 文字列の描画
        text = second
        #text_width, text_height = draw.textsize(text, font=font)
        x = 0
        y = 5
        draw.text((x, y), text, font=font, fill="black")

        filename=dirname + "plot" + str(i) + "_s.png"
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
    print(len(data_score))
    df_score_list=[]
    names = [first, second]
    i=0
    for data in data_score:
        data=pd.DataFrame(data)
        df_score_list.append(data.transpose())
        i+=1
    print(*df_score_list)
    tmp=len(first)-len(second)
    print(tmp)

    return render_template('display.html', df_score_list=[df.to_numpy() for df in df_score_list], first=first,second=second,tmp=tmp)
    #return render_template('display.html')

#------コース図終わり---------------------------------------------------------

def send2():
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    num = request.form['id']
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * from games where id = (?)",
                [num])
    file_name= cur.fetchall()[0][4]

#-------------データ分析の記述--------------------
#-------------仮の分析---------------------------
    df = pd.read_csv(file_name)
    B=0
    F=0
    for row in df['02_RV_01']:
        if row=="B":
            B+=1
        elif row=="F":
            F+=1
    fig = plt.figure()
    labels = ['B', 'F']
    values = [B, F]
    lefts = np.arange(len(values))
    plt.bar(lefts, values, tick_label=labels, width=0.5, color="#b2b2b2")
    dirname = "static/images/"
    os.makedirs(dirname, exist_ok=True)
    filename=dirname + "plot.png"
    fig.savefig(filename)
    F_f,FM_f,BM_f,B_f,FS_f,FMS_f,BMS_f,BS_f,F_s,FM_s,BM_s,B_s,FS_s,FMS_s,BMS_s,BS_s=map(int,[0]*16)
    first=df['名前'][0]
    for row in df['名前']:
        if first!=row:
            second=row
            break
    i=0
    #----------------得点表------------------------------------------------------
    i=0
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
            print("game_point")


        print(i,df['00_03_Point'][i],score1[i],score2[i])
        if df['00_03_Point'][i]==first:
            first_score.append(score1[i])
            second_score.append(-1)
        if df['00_03_Point'][i]==second:
            second_score.append(score2[i])
            first_score.append(-1)
    first_result.append(first_score)
    second_result.append(second_score)
    print(first_result)
    print(second_result)


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

    app.run(host='0.0.0.0', port=7777)
    # FlaskアプリをWaitressで稼働させる
