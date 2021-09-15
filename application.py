from datetime import datetime,date,timedelta
import os
from flask import Flask,flash,redirect,render_template,request,session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from helpers import apology,login_required
from cs50 import SQL

app= Flask(__name__)

#テンプレートの自動読み込みがされることを確認する
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




#Cookie1の代わりにファイルシステムを用いてセッションを作成
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db=SQL("sqlite:///Log.db")


@app.route("/",methods=["GET","POST"])
@login_required
def index():
    if request.method == "POST":
        user = session['user_id']
        date = request.form.get("date")
        task = request.form.get("task")
        time = request.form.get("time")
        money = request.form.get("money")
        time_list = list(map(int,time.split(":")))
        sum_time = (time_list[0]*int(money))+((time_list[1]/60)*int(money))
        sum_time = int(sum_time)
        db.execute("INSERT INTO log (userid,date,task,time,unit,sum) VALUES(?,?,?,?,?,?)",user,date,task,time,money,sum_time)
        
        
        #1日ごとの集計データを取得
        today = datetime.today()
        day_weeks=[]
        for i in range(7):
            day = today - timedelta(days=i)
            day_weeks.append(datetime.strftime(day, '%Y-%m-%d'))
        day_rows=db.execute("SELECT SUM(sum) as sum, strftime('%Y-%m-%d', date) as day FROM log WHERE userid = ? GROUP BY day ORDER BY date DESC LIMIT 7",user)
        day_units=[0]*7
        for i in range(7):
            for j in range(len(day_rows)):
                if day_weeks[i] == day_rows[j]['day']:
                   day_units[i] = day_rows[j]['sum']
        day_weeks.reverse()
        day_units.reverse()

        #1週間ごとの集計データを取得
        weeks = []
        weeks_dates = []
        for i in range(7):
            week = today - timedelta(days=i*7)
            weeks_dates.append(datetime.strftime(week-timedelta(days=week.weekday()),'%Y-%m-%d'))
            weeks.append(datetime.strftime(week, '%Y-%W'))
        week_rows=db.execute("SELECT SUM(sum) as sum, strftime('%Y-%W', date) as week FROM log WHERE userid = ? GROUP BY week ORDER BY week DESC LIMIT 7",user)
        week_units=[0]*7
        for i in range(7):
            for j in range(len(week_rows)):
                if weeks[i] == week_rows[j]['week']:
                    week_units[i] = week_rows[j]['sum']
        weeks_dates.reverse()
        week_units.reverse()

        #月ごとの集計データを取得
        months = []
        month = today
        for i in range(7):
            month = datetime(month.year, month.month, 1 )
            if i != 0:
                month = month + timedelta(days = -1)
            months.append(month.strftime("%Y-%m"))
        month_rows=db.execute("SELECT SUM(sum) as sum, strftime('%Y-%m', date) as month FROM log  WHERE userid = ? GROUP BY month ORDER BY month DESC LIMIT 7 ",user)
        month_units = [0]*7
        for i in range(7):
            for j in range(len(month_rows)):
                if months[i] == month_rows[j]['month']:
                    month_units[i] = month_rows[j]['sum']
        months.reverse()
        month_units.reverse()
        
        #年ごとの集計データを取得
        years = []
        for i in range(7):
            year = datetime(today.year -i, today.month, 1)
            years.append(year.strftime("%Y"))
        year_rows = db.execute("SELECT SUM(sum) as sum, strftime('%Y', date) as year FROM log WHERE userid = ? GROUP BY year ORDER BY year DESC LIMIT 7",user)
        year_units = [0]*7
        for i in range(7):
            for j in range(len(year_rows)):
                if years[i] == year_rows[j]['year']:
                    year_units[i] = year_rows[j]['sum']
        years.reverse()
        year_units.reverse()
        
        
        #総資産を計算
        gross = db.execute("SELECT SUM(sum) as sum FROM log WHERE userid = ?",user)[0]['sum']
        if not gross:
            gross = 0


        return render_template("index.html",day_rows=day_rows,day_weeks=day_weeks,day_units=day_units,weeks=weeks,week_units=week_units,weeks_dates=weeks_dates,months=months,month_units=month_units,years=years,year_units=year_units,gross=gross,message="お疲れ様!")


        
    else:
        
        user = session["user_id"]

        #1日ごとの集計データを取得
        today = datetime.today()
        day_weeks=[]
        for i in range(7):
            day = today - timedelta(days=i)
            day_weeks.append(datetime.strftime(day, '%Y-%m-%d'))
        day_rows=db.execute("SELECT SUM(sum) as sum, strftime('%Y-%m-%d', date) as day FROM log WHERE userid = ? GROUP BY day ORDER BY date DESC LIMIT 7",user)
        day_units=[0]*7
        for i in range(7):
            for j in range(len(day_rows)):
                if day_weeks[i] == day_rows[j]['day']:
                   day_units[i] = day_rows[j]['sum']
        day_weeks.reverse()
        day_units.reverse()

        #1週間ごとの集計データを取得
        weeks = []
        weeks_dates = []
        for i in range(7):
            week = today - timedelta(days=i*7)
            weeks_dates.append(datetime.strftime(week-timedelta(days=week.weekday()),'%Y-%m-%d'))
            weeks.append(datetime.strftime(week, '%Y-%W'))
        week_rows=db.execute("SELECT SUM(sum) as sum, strftime('%Y-%W', date) as week FROM log WHERE userid = ? GROUP BY week ORDER BY week DESC LIMIT 7",user)
        week_units=[0]*7
        for i in range(7):
            for j in range(len(week_rows)):
                if weeks[i] == week_rows[j]['week']:
                    week_units[i] = week_rows[j]['sum']
        weeks_dates.reverse()
        week_units.reverse()

        #月ごとの集計データを取得
        months = []
        month = today
        for i in range(7):
            month = datetime(month.year, month.month, 1 )
            if i != 0:
                month = month + timedelta(days = -1)
            months.append(month.strftime("%Y-%m"))
        month_rows=db.execute("SELECT SUM(sum) as sum, strftime('%Y-%m', date) as month FROM log  WHERE userid = ? GROUP BY month ORDER BY month DESC LIMIT 7 ",user)
        month_units = [0]*7
        for i in range(7):
            for j in range(len(month_rows)):
                if months[i] == month_rows[j]['month']:
                    month_units[i] = month_rows[j]['sum']
        months.reverse()
        month_units.reverse()
        
        #年ごとの集計データを取得
        years = []
        for i in range(7):
            year = datetime(today.year -i, today.month, 1)
            years.append(year.strftime("%Y"))
        year_rows = db.execute("SELECT SUM(sum) as sum, strftime('%Y', date) as year FROM log WHERE userid = ? GROUP BY year ORDER BY year DESC LIMIT 7",user)
        year_units = [0]*7
        for i in range(7):
            for j in range(len(year_rows)):
                if years[i] == year_rows[j]['year']:
                    year_units[i] = year_rows[j]['sum']
        years.reverse()
        year_units.reverse()
        
        
        #総資産を計算
        gross = db.execute("SELECT SUM(sum) as sum FROM log WHERE userid = ?",user)[0]['sum']
        if not gross:
            gross = 0


        return render_template("index.html",day_rows=day_rows,day_weeks=day_weeks,day_units=day_units,weeks=weeks,week_units=week_units,weeks_dates=weeks_dates,months=months,month_units=month_units,years=years,year_units=year_units,gross=gross)


@app.route("/how")
def how():
   
    return render_template("howuse.html")

@app.route("/passbook")
@login_required
def passbook():
    user = session["user_id"]
    rows = db.execute("SELECT * FROM log WHERE userid = ? ORDER BY date DESC",user)
    gross = db.execute("SELECT SUM(sum) as sum FROM log WHERE userid = ?",user)[0]['sum']
    if not gross:
        gross = 0
    return render_template("passbook.html",rows=rows,gross=gross)


@app.route("/delete/<int:id>")
@login_required
def show(id):
    db.execute("DELETE FROM log WHERE id = ?",id)
    return redirect("/passbook")
    
@app.route("/edit/<int:id>",methods=["GET","POST"])
@login_required
def edit(id):
    if request.method =="POST":
        date = request.form.get("date")
        task = request.form.get("task")
        time = request.form.get("time")
        money = request.form.get("money")
        time_list = list(map(int,time.split(":")))
        sum_time = (time_list[0]*int(money))+((time_list[1]/60)*int(money))
        sum_time = int(sum_time)
        
        db.execute("UPDATE log SET date = ?, task = ?, time = ?, unit = ?, sum = ? WHERE id = ?",date,task,time,money,sum_time,id)
        
        
        return redirect("/passbook")
    else:
        row = db.execute("SELECT * FROM log WHERE id = ?",id)[0]
        return render_template("edit.html",row=row)


@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("Please enter username")
        elif not request.form.get("password"):
            return apology("Please enter password")
        rows = db.execute("SELECT * FROM user WHERE username = ?",request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"],request.form.get("password")):
            return apology("Wrong username or password")

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Please enter username")
        elif len(db.execute("SELECT * FROM user WHERE username = ?",request.form.get("username"))) == 1:
            return apology("This username is exist")
        elif not request.form.get("password"):
            return apology("Please enter password")
        elif not request.form.get("confirmation"):
            return apology("Please enter confirmation password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match")
        else:
            password=request.form.get("password")
            db.execute("INSERT INTO user (username,hash) VALUES(?, ?)",request.form.get("username"), generate_password_hash(password))
            session["user_id"]=request.form.get("username")
            return redirect("/how")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")
