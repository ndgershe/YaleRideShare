from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import smtplib
from datetime import datetime

from helpers import apology, login_required
# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use Postgres database
db = SQL("postgres://czznryphemnxjs:4a6625d3983a3befabf184350cfc1d43b1d285b396838bb7255421f1f32c3267@ec2-184-73-206-155.compute-1.amazonaws.com:5432/d36i73dhm3jssb")

@app.route("/")
#@login_required
def home():
    return render_template("home.html")


@app.route("/order", methods=["GET", "POST"])
#@login_required
def order():
    """Makes a request"""

    print("\n\nOrder was called\n\n\n")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # This should return JSON text


        print("\n\nGot to post\n\n\n")
        # checks if user entered airport
        if not request.form.get("airport"):
            return apology("must provide airport", 400)
        else:
            airport = request.form.get("airport")

        if not request.form.get("type"):
            errorJSON = {
                "error": True
            }
            return jsonify(errorJSON)
            return apology("must provide if arrival or departure", 400)
        else:
            if request.form.get("type") == "departure":
                type = 0
            else:
                type = 1

        # checks if user entered date
        if not request.form.get("date"):
            return apology("must provide date", 400)
        else:
            date = request.form.get("date")

        # checks if user entered optimal time
        if not request.form.get("otime"):
            return apology("must provide optimal time", 400)
        else:
            otime = request.form.get("otime")

        # checks if user entered wait time time
        if not request.form.get("etime"):
            return apology("must provide time", 400)
        else:
            etime = request.form.get("etime")

        # checks if user entered number of passengers
        if not request.form.get("number"):
            return apology("must provide number of passengers", 400)
        else:
            number = request.form.get("number")

        if type == 0:
            # checks if entered location
            if not request.form.get("location"):
                return apology("must provide pickup location", 400)
            else:
                location = request.form.get("location")

        id = session["user_id"]

        # add to requests
        db.execute("INSERT INTO requests (userid, airport, date, otime, etime, number, type, location) VALUES (:id, :airport, :date, :otime, :etime, :number, :type, :location)",
                       id=id, airport=airport, date=date, otime=otime, etime=etime, number=number, type=type, location=location)

        # add to orders
        db.execute("INSERT INTO requests (userid, airport, date, otime, etime, number, type) VALUES (:id, :airport, :date, :otime, :etime, :number, :type)",
                   id=id, airport=airport, date=date, otime=otime, etime=etime, number=number, type=type)

        # gets ride number
        rows = db.execute("SELECT rideid FROM requests where userid=:id AND airport=:airport AND date=:date AND otime=:otime AND etime=:etime AND number=:number AND type=:type ",
                          id=id, airport=airport, date=date, otime=otime, etime=etime, number=number, type=type)
        ride = rows[0]
        ride = ride.get('rideid')

        # updates history
        db.execute("INSERT INTO history (rideid, status) VALUES (:ride, 1)",
                   ride=ride)

        # start of matching

        fnumber = 6 - number

        if type == 0:
            # search for matches for departure
            rows = db.execute("SELECT rideid FROM requests WHERE userid=:id AND airport=:airport AND location=:location AND date=:date AND type = :type AND number<=:fnumber AND otime>=:otime AND etime<=:otime OR id=:id AND airport=:airport AND location=:location AND date=:date AND type = :type AND number<=:fnumber AND otime<=:etime AND etime<=:etime ",
                              id=id, airport=airport, date=date, type=type, otime=otime, etime=etime, fnumber=fnumber, location=location)

        else:
            # search for matches for arrival
            rows = db.execute("SELECT rideid FROM requests WHERE (userid=:id AND airport=:airport AND date=:date AND type = :type AND number<=:fnumber AND otime>=:otime AND otime<=:etime) OR (id=:id AND airport=:airport AND date=:date AND type = :type AND number<=:fnumber AND otime<=:otime AND etime>=:otime)",
                              id=id, airport=airport, date=date, type=type, otime=otime, etime=etime, fnumber=fnumber)

            if rows:
                # makes list of times
                times = []
                for i in rows:
                    i = i.get('rideid')
                    time = db.execute("SELECT otime FROM requests WHERE rideid=:rideid", rideid = i)[0]
                    times.append(time.get('otime'))

                # makes list of time differences
                diffs = []
                for i in times:
                    FMT = '%H:%M'
                    diffs.append( abs((datetime.strptime(times[i], FMT) - datetime.strptime(otime, FMT)).total_seconds()/60))

                # makes list of tupples sorted by time difference
                zipped = []
                zipped = list( zip(rows,diffs))
                zipped.sort(key=lambda tup: tup[1])

                # makes list of sorted rideids
                rides = []
                n = len(zipped)
                for i in range(n):
                    rides.append( zipped[i][0])

                # begins message of email
                message = "We found one or more matches:"

                emails = []
                names = []
                phones = []

                # finds information for email
                for i in rides:
                    i = i.get('rideid')
                    email = db.execute("SELECT email FROM requests JOIN users ON requests.userid = users.userid WHERE rideid=:rideid", rideid = i)[0]
                    emails.append(email.get('email'))
                    name = db.execute("SELECT name FROM requests JOIN users ON requests.userid = users.userid WHERE rideid=:rideid", rideid = i)[0]
                    names.append(name.get('name'))
                    phone = db.execute("SELECT phone FROM requests JOIN users ON requests.userid = users.userid WHERE rideid=:rideid", rideid = i)[0]
                    phones.append(phone.get('phone'))

                # creates message of all info
                n = len(rides)
                for i in range(n):
                    message = message + "\n" + names[i] +"'s optimum time is " + times[i]  + "\n     email: " + emails[i] + " phone #: " + phones[i] + "\n"

                # gets user email
                email = db.execute("SELECT email FROM users WHERE userid=:userid", userid = id)[0]
                email = email.get('email')

                # sends email to person who requested a ride
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login("yaleubershare@gmail.com", "najmtwbw")
                server.sendmail("yaleubershare@gmail.com", email, message)

                # gets user name and phone
                name = db.execute("SELECT name FROM users WHERE userid=:userid", userid = id)[0]
                name = name.ger('name')
                phone = db.execute("SELECT phone FROM users WHERE userid=:userid", userid = id)[0]
                phone = phone.get('phone')

                # create message for matches
                message = "Somebody matched with your uber request! Here is their information: \n" + name + "'s optimum time is " + otime  + "\n     email: " + email + " phone #: " + phone + "\n"

                # sends email to all matches
                for i in emails:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login("yaleubershare@gmail.com", "najmtwbw")
                    server.sendmail("yaleubershare@gmail.com", i, message)

        errorJSON = {
            "error": False
        }
        return jsonify(errorJSON)

        # return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("\n\nLol jk it was a GET request\n\n\n")
        return render_template("order.html")


@app.route("/new_order", methods=["GET", "POST"])
@login_required
def new_order():
    """Request an Uber"""

    if request.method == "POST":
        if request.form.get("type") == "0":
            return redirect("/departure")
        elif request.form.get("type") == "1":
            return redirect("/arrival")
        else:
            return apology("Must select arrival or departure", 400)

    if request.method == "GET":
        return render_template("order_D_or_A.html")


@app.route("/departure", methods=["GET", "POST"])
@login_required
def departure():
    """Display and get info from departure form"""

    if request.method == "POST":

        id = session["user_id"]

        # Define the variables from the form
        airport = request.form.get("airport")
        date = request.form.get("date")
        otime = request.form.get("otime")
        number = request.form.get("number")
        etime = request.form.get("etime")
        location = request.form.get("location")

        # Check to make sure info was input
        if not airport or not date or not otime or not number or not etime or not location:
            return aplogy("Must complete form")

        rows = db.execute("INSERT INTO requests (userid, airport, date, otime, number, etime, location, type) VALUES (:userid, :airport, :date, :otime, :number, :etime, :location, 0)",
                   userid=id, airport=airport, date=date, otime=otime, number=number, etime=etime, location=location)

        if not rows:
            return apology("something went wrong", 400)

        return redirect("/")

    if request.method == "GET":
        return render_template("order_departure.html")


@app.route("/arrival", methods=["GET", "POST"])
@login_required
def arrival():
    """Display and get info from arrival form"""

    if request.method == "POST":

        id = session["user_id"]

        # Define the variables from the form
        airport = request.form.get("airport")
        date = request.form.get("date")
        otime = request.form.get("otime")
        number = request.form.get("number")
        etime = request.form.get("etime")

        # Check to make sure info was input
        if not airport or not date or not otime or not number or not etime:
            return aplogy("Must complete form")

        rows = db.execute("INSERT INTO requests (userid, airport, date, otime, number, etime, type) VALUES (:userid, :airport, :date, :otime, :number, :etime, :location, 1)",
                   userid=id, airport=airport, date=date, otime=otime, number=number, etime=etime)

        if not rows:
            return apology("something went wrong", 400)

        return redirect("/")

    if request.method == "GET":
        return render_template("order_arrival.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # stores index
    rides = db.execute("SELECT * FROM requests WHERE userid = :userid", userid=session["user_id"])

    if rides != None:
        return render_template("history.html", rides=rides)
    else:
        return apology("table is empty", 400)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any userid
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        print(rows)

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any userid
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        phone = request.form.get("phone")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords must match", 400)

        # Ensure name was submitted
        elif not request.form.get("name"):
            return apology("Must enter first name", 400)

        # Ensure surname was submitted
        elif not request.form.get("surname"):
            return apology("Must enter last name", 400)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("Must enter email", 400)

        # Ensure phone number was submitted
        elif not request.form.get("phone"):
            return apology("Must enter phone number", 400)

        # checks if valid phone number
        num_digits = 0
        dash = False

        for i in range(len(phone)):
            if (i == 3 or i == 7) and phone[i] == "-":
                dash = True
                continue
            elif not phone[i].isdigit():
                return apology("Must enter valid phone number", 400)

            num_digits = num_digits + 1

        if num_digits != 10:
            return apology("Must enter valid phone number", 400)

        if not dash:
            '-'.join([phone[:4], phone[4:6], phone[6:]])

        # hashes password
        hash = generate_password_hash(request.form.get("password"))



        # inserts new user in data base and checks username
        rows = db.execute("INSERT INTO users ( username, password, name, surname, email, phone ) VALUES( :username, :hash, :name, :surname, :email, :phone )",
                          username=username, hash=hash, name=name, surname=surname, email=email, phone=phone)

        if rows == None:
            return apology("Username is taken :(", 400)

         # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        print(rows)

        # Remember which user has logged in
        session["user_id"] = rows[0]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/cancel", methods=["GET", "POST"])
@login_required
def cancel():
    """Cancel Ride"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        rideid = request.form.get("rideid")
        db.execute("DELETE FROM requests WHERE rideid = rideid")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        id = session["user_id"]
        rides = db.execute(
            "SELECT * FROM requests WHERE userid = :id", id = id)
        return render_template("cancel.html", rides=rides)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Allows user to change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        id=session["user_id"]

        # checks if user entered passwords
        if not request.form.get("oldpass"):
            return apology("must provide old password", 400)
        elif not request.form.get("newpass"):
            return apology("must enter new password", 400)
        elif not request.form.get("verification"):
            return apology("must verify password", 400)
        else:
            # stores passwords
            oldpass = request.form.get("oldpass")
            newpass = request.form.get("newpass")
            verification = request.form.get("verification")

            row = db.execute("SELECT password FROM users WHERE userid = :id", id=id)

            # ensure user inputs valid information
            if not check_password_hash(row[0]["password"], oldpass):
                return apology("old password is incorrect", 400)

            if newpass != verification:
                return apology("new passwords must match", 400)


            # update password
            newpass = generate_password_hash(newpass)
            db.execute("UPDATE users SET password=:newpass WHERE userid = :id", newpass = newpass, id = id)




        return redirect("/")

# User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("settings.html")

@app.route("/closest", methods=["GET", "POST"])
@login_required
def closest():
    #Checks for the closest time

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        id = session["user_id"]

        rideid = request.form.get("rideid")


        type = dict(db.execute("SELECT type FROM requests WHERE rideid = rideid")[0])
        etime = dict(db.execute("SELECT etime FROM requests WHERE rideid = rideid")[0])
        airport = dict(db.execute("SELECT airport FROM requests WHERE rideid = rideid")[0])
        location = dict(db.execute("SELECT location FROM requests WHERE rideid = rideid")[0])
        date = dict(db.execute("SELECT date FROM requests WHERE rideid = rideid")[0])
        number = dict(db.execute("SELECT number FROM requests WHERE rideid = rideid")[0])
        otime = dict(db.execute("SELECT otime FROM requests WHERE rideid = rideid")[0])

        type = type.get('type')
        etime =  etime.get('etime')
        airport =  airport.get('airport')
        location =  location.get('location')
        date =  date.get('date')
        number =  number.get('number')



        fnumber = 6 - number

        if type == 0:
            # search for matches for departure
            rows = db.execute("SELECT rideid FROM requests WHERE  airport = :airport AND location = :location AND date = :date AND type = :type AND userid != :id",
                                 airport = airport, location = location, date = date, type = type, id = id)

        else:
            # search for matches for arrival
            rows = db.execute("SELECT rideid FROM requests WHERE airport = :airport AND date = :date AND type = :type AND userid != :id",
                                airport = airport, date = date, type = type, id = id)
        print(rows)

        if rows:
            # makes list of times
            times = []
            for i in rows:
                i = i.get('rideid')
                print(db.execute("SELECT etime FROM requests WHERE rideid = :i", i = i)[0])
                time = dict(db.execute("SELECT etime FROM requests WHERE rideid = :i", i = i)[0])
                times.append( time.get('etime'))

            # makes list of time differences
            diffs = []
            n = len(times)
            for i in range(n):
                FMT = '%H:%M'
                diffs.append( abs((datetime.strptime(times[i], FMT) - datetime.strptime(etime, FMT)).total_seconds()/60))

            # makes list of tupples sorted by time difference
            zipped = list(zip(rows,diffs))

            closest = min(zipped, key = lambda t: t[1])[0]
            print(closest)

            email = db.execute("SELECT email FROM requests JOIN users ON requests.userid = users.userid WHERE rideid = :closest", closest = closest)[0]
            name = db.execute("SELECT name FROM requests JOIN users ON requests.userid = users.userid WHERE rideid = :closest", closest = closest)[0]
            phone = db.execute("SELECT phone FROM requests JOIN users ON requests.userid = users.userid WHERE rideid = :closest", closest = closest)[0]
            time = db.execute("SELECT etime FROM requests WHERE rideid = :closest", closest = closest)[0]

            message = "Here is the information for the person with the closest match:"
            # creates message for departure
            if type == 0:
                message = message + "\n" + name +"'s earliest time is " + time  + "\n     email: " + email + " phone #: " + phone + "\n"
            # creates message for arrival
            else:
                message = message + "\n" + name +"'s latestt time is " + time  + "\n     email: " + email + " phone #: " + phone + "\n"

        else:
            message = "Sorry, there is nobody who matches your request"


        return render_template("closested.html", message=message)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        id = session["user_id"]
        rides = db.execute(
            "SELECT * FROM requests WHERE userid = :id", id = id)
        return render_template("closest.html", rides=rides)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)



if __name__ == "__main__":
    app.run()
