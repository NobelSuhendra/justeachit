from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from cs50 import SQL

app = Flask(__name__)
app.config["SECRET_KEY"] = "ML74f3EkFLE3wqmQ5T6L37mqUsYXAZ8n"
db = SQL("sqlite:///data.db")

temp = []

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

day_times = ["12 AM - 1AM", "1 AM - 2 AM", "2 AM - 3 AM", "3 AM - 4 AM", "4 AM - 5 AM", "5 AM - 6 AM", "6 AM - 7 AM", "7 AM - 8 AM", "8 AM - 9 AM", "9 AM - 10 AM", "10 AM - 11 AM", "11 AM - 12 PM", "12 PM - 1 PM", "1 PM - 2 PM", "2 PM - 3 PM", "3 PM - 4 PM", "4 PM - 5 PM", "5 PM - 6 PM", "6 PM - 7 PM", "7 PM - 8 PM", "8 PM - 9 PM", "9 PM - 10 PM", "10 PM - 11 PM", "11 PM - 12 AM"]
 
months = [
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December"
]

day_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

day_count_leap = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

days = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    "Sunday"
]


class Day:
    def __init__(self, month, day_num, year):
        self.month = month
        self.day_num = day_num
        self.year = year

    def day_otw(self):

        rd = [
            "Friday", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday"
        ]

        if int(self.year) % 4 == 0:
            dc = day_count_leap.copy()
        else:
            dc = day_count.copy()

        fdc = 0
        for y in range(2021, int(self.year) - 1, 1):
            if y % 4 == 0:
                fdc += 366
            else:
                fdc += 365

        for z in range(int(self.month) - 1):
            fdc += dc[z]

        fdc += int(self.day_num)
        fdc %= 7
        return rd[fdc]

    def final_date(self):
        day_txt = str(self.day_otw())

        fd = day_txt + ", " + str(
            self.day_num) + " " + months[int(self.month) - 1] + " " + str(
                self.year)

        return fd

    def tomorrow(self):
        if int(self.year) % 4 == 0:
            dc = day_count_leap.copy()
        else:
            dc = day_count.copy()

        if dc[int(self.month) - 1] == int(self.day_num):
            if int(self.month) == 12:
                obj = Day(1, 1, int(self.year) + 1)
            else:
                obj = Day(int(self.month) + 1, 1, int(self.year))
        else:
            obj = Day(int(self.month), int(self.day_num) + 1, int(self.year))

        return obj

    def yesterday(self):
        if int(self.year) % 4 == 0:
            dc = day_count_leap.copy()
        else:
            dc = day_count.copy()

        if int(self.day_num) == 1:
            if int(self.month) == 1:
                obj = Day(12, 31, int(self.year) - 1)
            else:
                obj = Day(
                    int(self.month) - 1, dc[int(self.month) - 2],
                    int(self.year))
        else:
            obj = Day(int(self.month), int(self.day_num) - 1, int(self.year))

        return obj


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            flash("Please enter an email.")
            return redirect("/register")
        else:
            data = db.execute("SELECT * FROM users WHERE email = ?;", email)
            if not password:
                flash("Please enter a password.")
                return redirect("/register")
            elif len(data) != 0:
                flash("Sorry. The email has been taken.")
                return redirect("/register")
            else:
                hashed_pw = generate_password_hash(password,
                                                   method="pbkdf2:sha256",
                                                   salt_length=8)
                db.execute(
                    "INSERT INTO users (email, password, logged, type, username, age) VALUES (?, ?, ?, ?, ?, ?);",
                    email, hashed_pw, "False", "None", "None", "None")
                datanew = db.execute("SELECT * FROM users WHERE email = ?;", email)
                session["user_id"] = datanew[0]["id"]
                return redirect("/customise")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            flash("Please input an email.")
            return redirect("/login")
        elif not password:
            flash("Please input a password.")
            return redirect("/login")
        else:
            login_data = db.execute("SELECT * FROM users WHERE email = ?;", email)
            if len(login_data) != 1:
                flash("Your email is invalid.")
                return redirect("/login")
            elif not check_password_hash(login_data[0]["password"], password):
                flash("You password is invalid")
                return redirect("/login")
            else:
                session["user_id"] = login_data[0]["id"]
                return redirect("/dashboard/January/1")
    else:
        return render_template("login.html")


@app.route("/customise", methods=["GET", "POST"])
def customise():
    if session.get('user_id') == None:
        return redirect("/")
    if request.method == "POST":
        acc_type = request.form.get("type")
        username = request.form.get("name")
        age = request.form.get("age")
        data = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not acc_type:
            flash("Please select an account type!")
            return redirect("/customise")
        elif not username:
            flash("Please input a username!")
            return redirect("/customise")
        elif len(data) != 0:
            flash("Sorry. The username has been taken.")
            return redirect("/customise")
        else:
            db.execute(
                    "UPDATE users SET username = ?, type = ?, age = ?, logged = ? WHERE id = ?",
                    username, acc_type, age, "True", session["user_id"])
            return redirect("/dashboard/January/1")

    else:
        return render_template("customise.html")

@app.route("/users/<search_data>", methods=["GET", "POST"])
def users(search_data):
    if session.get('user_id') == False:
        return redirect("/")
    if request.method == "POST":
        profilekey = list(dict(request.form).keys())[0]
        return redirect("/@" + profilekey + "/January/1")
    else:
        users = db.execute("SELECT * FROM users WHERE username LIKE ?;", search_data)
        return render_template("dashboard2.html", users=users, searchdat=search_data[1:len(search_data)-1])

@app.route("/@<username>/<month>/<day>", methods=["GET", "POST"])
def userday(username, month, day):
    if session.get('user_id') == None:
        return redirect("/")
    persondata = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if persondata[0]["logged"] == "False":
        return redirect("/customise")
    if request.method == "POST":
        if "srch" in request.form:
            search_data = "%" + request.form.get("srch") + "%"
            return redirect(f"/users/{search_data}")
        else:
            timekey = list(dict(request.form).keys())[0]
            currt = db.execute("SELECT * FROM users WHERE id  = ?", session["user_id"])[0]["username"]
            data1 = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?", timekey, month, day, session["user_id"])
            if len(data1) == 0:
                db.execute("INSERT INTO times (time, month, date, id, status, student, teacher) VALUES (?, ?, ?, ?, ?, ?, ?)", timekey, month, day, session["user_id"], "s", username, currt)
            else:
                if data1[0]["status"] == "n":
                    db.execute("UPDATE times SET status = ?, student = ?, teacher = ? WHERE time = ? AND month = ? AND date = ? AND id = ?", "s", username, currt, timekey, month, day, session["user_id"])
                else:
                    db.execute("UPDATE times SET status = ?, student = ?, teacher = ? WHERE time = ? AND month = ? AND date = ? AND id = ?", "n", "None", "None", timekey, month, day, session["user_id"])

            return redirect("/@" + username + "/" + month + "/" + day)
    else:
        inday = Day(1, 3, 2022)
        year = []
        counter = [0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        monthc = 0
        for x in range(12):
            year.append({"name": months[x], "weeks": []})

        year[0]["weeks"].append(["none", "none", "none", "none", "none", "1", "2"])

        for _ in range(363):
            yest = inday.yesterday()
            if inday.day_num == 1:
                monthc += 1
                counter[monthc] += 1
                year[monthc]["weeks"].append([])
            elif yest.day_otw() == "Sunday":
                counter[monthc] += 1
                year[monthc]["weeks"].append([])

            year[monthc]["weeks"][counter[monthc]].append(inday.day_num)
            if inday.day_otw() == "Sunday":
                if len(year[monthc]["weeks"][counter[monthc]]) < 7:
                    if inday.day_num < 7:
                        while len(year[monthc]["weeks"][counter[monthc]]) < 7:
                            year[monthc]["weeks"][counter[monthc]].insert(0, "none")
                    else:
                        while len(year[monthc]["weeks"][counter[monthc]]) < 7:
                            year[monthc]["weeks"][counter[monthc]].append("none")
            if inday.day_num == day_count[monthc]:
                if len(year[monthc]["weeks"][counter[monthc]]) < 7:
                        while len(year[monthc]["weeks"][counter[monthc]]) < 7:
                            year[monthc]["weeks"][counter[monthc]].append("none")
            inday = inday.tomorrow()

        timelist = []
        usern = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        for t in day_times:
            data = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?;", t, month, day, usern)
            data2 = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?;", t, month, day, session["user_id"])
            if len(data) == 0 and len(data2) == 0:
                timelist.append({"name": t, "status": "n"})
            elif len(data) > 0 and len(data2) == 0:
                timelist.append({"name": t, "status": data[0]["status"]})
            elif len(data) == 0 and len(data2) > 0:
                timelist.append({"name": t, "status": data2[0]["status"]})
            elif data2[0]["status"] == "n" and data[0]["status"] == "n":
                timelist.append({"name": t, "status": "n"})
            elif data2[0]["status"] == "y" and data[0]["status"] == "n":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "n" and data[0]["status"] == "y":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "y" and data[0]["status"] == "y":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "s" and data[0]["status"] == "n":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "s" and data[0]["status"] == "y":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "n" and data[0]["status"] == "s":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "y" and data[0]["status"] == "s":
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "s" and data[0]["status"] == "s" and data2[0]["student"] != username:
                timelist.append({"name": t, "status": "y"})
            elif data2[0]["status"] == "s" and data[0]["status"] == "s" and data2[0]["student"] == username:
                timelist.append({"name": t, "status": "s"})
        
        for m in range(len(year)):
            if year[m]["name"] == month:
                year = [year[m]]
                break
        
        inday = Day(months.index(month) + 1, day, 2022)
        monthin = months.index(month)
        nextmonth = months[(monthin + 1) % 12]
        prevmonth = months[(monthin - 1) % 12]
        tommonth = months[inday.tomorrow().month - 1]
        tomday = inday.tomorrow().day_num
        yestmonth = months[inday.yesterday().month - 1]
        yestday = inday.yesterday().day_num
        
        persondata = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        types = persondata[0]["type"]
        
        return render_template("usertime.html", year=year, weekday=days, timelist=timelist, month=month, day=day, nextmonth=nextmonth, prevmonth=prevmonth, tommonth=tommonth, tomday=tomday, yestmonth=yestmonth, yestday=yestday, type=types, username=username)

@app.route("/dashboard/<month>/<day>", methods = ["GET", "POST"])
def dashboard(month, day):
    print(session.get('user_id'))
    if session.get('user_id') == None:
        return redirect("/")
    persondata = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if persondata[0]["logged"] == "False":
        return redirect("/customise")
    if request.method == "POST":    
        if "srch" in request.form:
            search_data = "%" + request.form.get("srch") + "%"
            return redirect(f"/users/{search_data}")
        else:
            persondata = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            timekey = list(dict(request.form).keys())[0]
            if persondata[0]["type"] == "Teacher":
                data1 = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?", timekey, month, day, session["user_id"])
                if len(data1) == 0:
                    db.execute("INSERT INTO times (time, month, date, id, status, student, teacher) VALUES (?, ?, ?, ?, ?, ?, ?)", timekey, month, day, session["user_id"], "y", "None", "None")
                else:
                    if data1[0]["status"] == "y":
                        db.execute("UPDATE times SET status = ? WHERE time = ? AND month = ? AND date = ? AND id = ?", "n", timekey, month, day, session["user_id"])
                    else:
                        db.execute("UPDATE times SET status = ? WHERE time = ? AND month = ? AND date = ? AND id = ?", "y", timekey, month, day, session["user_id"])
            else:
                data1 = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?", timekey, month, day, persondata[0]["id"])
                print(data1)
                if len(data1) == 0:
                    db.execute("INSERT INTO times (time, month, date, id, status, student, teacher) VALUES (?, ?, ?, ?, ?, ?, ?)", timekey, month, day, session["user_id"], "y", "None", "None")
                else:
                    if data1[0]["status"] == "y":
                        db.execute("UPDATE times SET status = ? WHERE time = ? AND month = ? AND date = ? AND id = ?", "n", timekey, month, day, persondata[0]["id"])
                    else:
                        db.execute("UPDATE times SET status = ? WHERE time = ? AND month = ? AND date = ? AND id = ?", "y", timekey, month, day, persondata[0]["id"])

            return redirect("/dashboard/" + month + "/" + day)
    else:
        inday = Day(1, 3, 2022)
        year = []
        counter = [0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        monthc = 0
        for x in range(12):
            year.append({"name": months[x], "weeks": []})

        year[0]["weeks"].append(["none", "none", "none", "none", "none", "1", "2"])

        for _ in range(363):
            yest = inday.yesterday()
            if inday.day_num == 1:
                monthc += 1
                counter[monthc] += 1
                year[monthc]["weeks"].append([])
            elif yest.day_otw() == "Sunday":
                counter[monthc] += 1
                year[monthc]["weeks"].append([])

            year[monthc]["weeks"][counter[monthc]].append(inday.day_num)
            if inday.day_otw() == "Sunday":
                if len(year[monthc]["weeks"][counter[monthc]]) < 7:
                    if inday.day_num < 7:
                        while len(year[monthc]["weeks"][counter[monthc]]) < 7:
                            year[monthc]["weeks"][counter[monthc]].insert(0, "none")
                    else:
                        while len(year[monthc]["weeks"][counter[monthc]]) < 7:
                            year[monthc]["weeks"][counter[monthc]].append("none")
            if inday.day_num == day_count[monthc]:
                if len(year[monthc]["weeks"][counter[monthc]]) < 7:
                        while len(year[monthc]["weeks"][counter[monthc]]) < 7:
                            year[monthc]["weeks"][counter[monthc]].append("none")
            inday = inday.tomorrow()
        
        persondata = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        timelist = []
        for t in day_times:
            if persondata[0]["type"] == "Teacher":
                data = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?;", t, month, day, session["user_id"])
                if len(data) == 0 or data[0]["status"] == "n":
                    timelist.append({"name": t, "status": "n"})
                elif data[0]["status"] == "y":
                    timelist.append({"name": t, "status": data[0]["status"]})
                elif data[0]["status"] == "s":
                    timelist.append({"name": t + " | " + "Teacher: " + data[0]["teacher"] + " | " + "Student: " + data[0]["student"], "status": data[0]["status"]})
            elif persondata[0]["type"] == "Student":
                data = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND student = ?;", t, month, day, persondata[0]["username"])
                data2 = db.execute("SELECT * FROM times WHERE time = ? AND month = ? AND date = ? AND id = ?;", t, month, day, persondata[0]["id"])
                if len(data) > 0:
                    timelist.append({"name": t + " | " + "Teacher: " + data[0]["teacher"] + " | " + "Student: " + data[0]["student"], "status": data[0]["status"]})
                elif len(data2) == 0 or data2[0]["status"] == "n":
                    timelist.append({"name": t, "status": "n"})
                elif data2[0]["status"] == "y":
                    timelist.append({"name": t, "status": data2[0]["status"]})
        for m in range(len(year)):
            if year[m]["name"] == month:
                year = [year[m]]
                break
        
        inday = Day(months.index(month) + 1, day, 2022)
        monthin = months.index(month)
        nextmonth = months[(monthin + 1) % 12]
        prevmonth = months[(monthin - 1) % 12]
        tommonth = months[inday.tomorrow().month - 1]
        tomday = inday.tomorrow().day_num
        yestmonth = months[inday.yesterday().month - 1]
        yestday = inday.yesterday().day_num

        if persondata[0]["type"] == "Teacher":
            tasks = []
            taskdata = db.execute("SELECT * FROM times WHERE id = ? AND status = ?", session["user_id"], "s")
            for d in range(len(taskdata)):
                p = d + 1
                maintext = str(p) + ". " + taskdata[d]["month"] + " " + taskdata[d]["date"] + " at " + taskdata[d]["time"] + ": " + taskdata[d]["student"]
                tasks.append({"text": maintext, "month": taskdata[d]["month"], "day": taskdata[d]["date"], "student": taskdata[d]["student"]})
        else:
            tasks = []
            taskdata = db.execute("SELECT * FROM times WHERE student = ? AND status = ?", persondata[0]["username"], "s")
            for j in range(len(taskdata)):
                p = j + 1
                maintext = str(p) + ". " + taskdata[j]["month"] + " " + taskdata[j]["date"] + " at " + taskdata[j]["time"] + ": " + taskdata[j]["teacher"]
                tasks.append({"text": maintext, "month": taskdata[j]["month"], "day": taskdata[j]["date"], "student": taskdata[j]["student"]})
        
        types = persondata[0]["type"]
        
        return render_template("dashboard.html", year=year, weekday=days, timelist=timelist, month=month, day=day, nextmonth=nextmonth, prevmonth=prevmonth, tommonth=tommonth, tomday=tomday, yestmonth=yestmonth, yestday=yestday, tasks=tasks, type=types)

@app.route("/account", methods=["GET","POST"])
def account():
    if session.get('user_id') == None:
        return redirect("/")
    persondata = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if persondata[0]["logged"] == "False":
        return redirect("/customise")
    if request.method == "POST":
        if "logout" in request.form:
            session.clear()
            return redirect("/")
        else:    
            username = request.form.get("username")
            email = request.form.get("email")
            npassword = request.form.get("npassword")
            age = request.form.get("age")
            data = db.execute("SELECT * FROM users WHERE email = ? AND id != ?;", email, session["user_id"])
            data2 = db.execute("SELECT * FROM users WHERE username = ? AND id != ?;", username, session["user_id"])
            persondata = db.execute("SELECT * FRom times WHERE id = ?", session["user_id"]) 
            if len(data) != 0:
                flash("Sorry. The email has been taken.")
                return redirect("/account")
            elif len(data2) != 0:
                flash("Sorry. The username has been taken.")
                return redirect("/account")
            else:
                hashed_pw = generate_password_hash(npassword, method="pbkdf2:sha256", salt_length=8)
                db.execute("UPDATE users SET username = ?, email = ?, password = ?, age = ? WHERE id = ?", username, email, hashed_pw, age, session["user_id"])
                flash("Change successful!")
                return redirect("/account")
    else:
        data =  db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("account.html", data=data[0], type=persondata[0]["type"])