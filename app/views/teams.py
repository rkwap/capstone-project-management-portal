from flask import Flask, request, render_template, flash, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
from datetime import date
from passlib.hash import sha256_crypt as sha
from flask_session import Session
from validate_email import validate_email
from app import *

teams = Blueprint('teams', __name__, url_prefix='/students')

@teams.route("/register/", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html",SITE_KEY=SITE_KEY)
    else:
        captcha_response = request.form['g-recaptcha-response'] 
        mentor_email = request.form['mentor_id']
        mentor_id = query_db("select mentor_id from Mentors where email = %s",(mentor_email,))
        if is_human(captcha_response):
        # if True:
            if mentor_id is None:
                flash("Wrong Mentor Email", 'danger')
                return redirect(url_for('teams.register'))
            else:
                if not validate_email(request.form['email']):
                    flash("Enter valid email address", 'danger')
                    return redirect(url_for('teams.register'))
                leader_id = query_db("select roll_no from Students where roll_no=%s ",(request.form['leader_id'],))
                student2 = query_db("select roll_no from Students where roll_no=%s ",(request.form['student2'],))
                student3 = query_db("select roll_no from Students where roll_no=%s ",(request.form['student3'],))
                student4 = query_db("select roll_no from Students where roll_no=%s ",(request.form['student4'],))
                if request.form['leader_id'] == request.form['student2'] or request.form['leader_id'] == request.form['student3'] or request.form['leader_id'] == request.form['student4'] or request.form['student2'] == request.form['student3'] or request.form['student2'] == request.form['student4'] or request.form['student4'] == request.form['student3']:
                    flash("Some students have same roll number in the group", 'danger')
                    return redirect(url_for('teams.register'))

                request_leader = query_db("select leader_roll_no from Requests where leader_roll_no=%s ",(request.form['leader_id'],))
                request_student2 = query_db("select student2_roll_no from Requests where student2_roll_no=%s ",(request.form['student2'],))
                request_student3 = query_db("select student3_roll_no from Requests where student3_roll_no=%s ",(request.form['student3'],))
                request_student4 = query_db("select student4_roll_no from Requests where student4_roll_no=%s ",(request.form['student4'],))
                if leader_id is not None or student2 is not None or student3 is not None or student4 is not None:
                    flash("Some students are already registered", 'danger')
                    return redirect(url_for('teams.register'))
                elif request_leader is not None or request_student2 is not None or request_student3 is not None or request_student4 is not None:
                    flash("Some students are already registered", 'danger')
                    return redirect(url_for('teams.register'))
                elif len(str(request.form.get('phone'))) != 10:
                    flash("Enter a valid 10 digit Phone Number!", 'danger')
                    return redirect(url_for('teams.register'))
                elif len(str(request.form.get('leader_id'))) != 9 or len(str(request.form.get('student2'))) != 9 or len(str(request.form.get('student3'))) != 9 or (len(str(request.form.get('student4'))) != 9 and len(str(request.form.get('student4'))) != 0):
                    flash("Enter correct Roll Numbers!", 'danger')
                    return redirect(url_for('teams.register'))
                if request.form['student4']=='':
                    student4 = None
                else:
                    student4 = request.form['student4']

                title=request.form.get('title', False)
                description = request.form.get('description', False)
                title_des = title+"*93-k+5=H]s]V%"+description
                execute_db("INSERT INTO Requests(leader_roll_no, title, student2_roll_no, student3_roll_no, student4_roll_no, email, leader_name, student2_name, student3_name, student4_name, phone, mentor_id) Values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(
                    request.form['leader_id'],
                    title_des,
                    request.form['student2'],
                    request.form['student3'],
                    student4,
                    request.form['email'],
                    request.form['leader_name'],
                    request.form['student2_name'],
                    request.form['student3_name'],
                    request.form['student4_name'],
                    request.form['phone'],
                    mentor_id,
                ))
                flash("Applied Successfully", 'success')
                return redirect(url_for('teams.register'))
        else:
            flash("Sorry. Bots not allowed!","danger")
            return redirect(url_for('teams.register'))

@teams.route("/objective_register/", methods=['POST', 'GET'])
def objective():
    if request.method == 'GET':
        return render_template("objective.html",SITE_KEY=SITE_KEY)
    else:
        captcha_response = request.form['g-recaptcha-response']
        mentor_email = request.form['mentor_id']
        mentor_id = query_db("select mentor_id from Mentors where email = %s",(mentor_email,))
        # if is_human(captcha_response):
        if True:
            if mentor_id is None:
                flash("Wrong Mentor Email", 'danger')
                return redirect(url_for('teams.objective'))
            else:
                if not validate_email(request.form['email']):
                    flash("Enter valid email address", 'danger')
                    return redirect(url_for('teams.objective'))
                query = query_db("select group_id from Teams where leader_roll_no=%s AND phone=%s AND email=%s",(request.form['leader_id'], request.form['phone'], request.form['email'], ))
                if query is None:
                    flash("Wrong Credentials", 'danger')
                    return redirect(url_for('teams.objective'))
                else:
                    group_id = query[0][0]
                    query = query_db("select * from Group_Mentors where group_id=%s AND mentor1_id=%s",(group_id, mentor_id, ))
                    if query is None:
                        flash("Wrong Mentor Email", 'danger')
                        return redirect(url_for('teams.objective'))
                    else:
                        objective = request.form.get('objective_1', "")+"_"+request.form.get('objective_2', "")+"_"+request.form.get('objective_3', "")+"_"+request.form.get('objective_4', "")+"_"+request.form.get('objective_5', "")
                        execute_db("UPDATE Teams SET objective=%s WHERE leader_roll_no=%s;",(
                            objective,
                            request.form['leader_id'],
                        ))
                flash("Objective Added Successfully", 'success')
                return redirect(url_for('teams.objective'))
        else:
            flash("Sorry. Bots not allowed!","danger")
            return redirect(url_for('teams.objective'))

@teams.route('/login', methods=["GET", "POST"])
def login():
    if request.method== 'GET':
        return render_template('teams_login.html',SITE_KEY=SITE_KEY)
    else:
        email=request.form['email']
        password=request.form['password']
        phash = query_db("select password from Teams where email = %s", (email, ))
        groupid = query_db("select group_id from Teams where email = %s", (email, ))
        # captcha_response = request.form['g-recaptcha-response']

        # if is_human(captcha_response):
        if True:
            if phash is None:
                flash("User does not exist","danger")
                return redirect(url_for('teams.login'))

            if sha.verify(password, phash[0][0]):
                session["student_user_id"] = email
                session["group_id"] = groupid[0][0]
                flash("Login Successful", "success")
                return redirect(url_for('teams.dashboard'))
            else:
                flash("Incorrect Password","danger")
                return redirect(url_for('teams.login'))
        else:
            flash("Sorry. Bots not allowed!","danger")
            return redirect(url_for('teams.login'))

@teams.route('/', methods=["GET", "POST"])
@student_login_required
def dashboard():
    query = query_db("SELECT * from Teams where email=%s", (session["student_user_id"], ))[0]
    team_details = {}
    team_details["leader"] = {}
    team_details["member2"] = {}
    team_details["member3"] = {}
    team_details["leader"]["roll_no"] = query[1]
    team_details["leader"]["name"] = query_db("SELECT name from Students where roll_no=%s", (team_details["leader"]["roll_no"], ))[0][0]
    team_details["member2"]["roll_no"] = query[3]
    team_details["member2"]["name"] = query_db("SELECT name from Students where roll_no=%s", (team_details["member2"]["roll_no"], ))[0][0]
    team_details["member3"]["roll_no"] = query[4]
    team_details["member3"]["name"] = query_db("SELECT name from Students where roll_no=%s", (team_details["member3"]["roll_no"], ))[0][0]
    if(query[5] is not None):
        team_details["member4"] = {}
        team_details["member4"]["roll_no"] = query[5]
        team_details["member4"]["name"] = query_db("SELECT name from Students where roll_no=%s", (team_details["member4"]["roll_no"], ))[0][0]
    team_details["email"] = query[6]
    team_details["phone_no"] = query[7]
    team_details["project"] = query[2]
    mentor_details = query_db("Select * from Group_Mentors where group_id=%s", (query[0], ))[0]
    team_details["mentor1"] = query_db("select name from Mentors where mentor_id=%s", (mentor_details[1], ))[0][0]
    if(mentor_details[2] is not None):
        team_details["mentor2"] = query_db("select name from Mentors where mentor_id=%s", (mentor_details[2], ))[0][0]
    return render_template("teams_main.html", **locals())


@teams.route('/logout/')
@student_login_required
def logout():
    session.clear()
    return redirect(url_for("teams.login"))

@teams.route('/change_password', methods=["GET", "POST"])
@student_login_required
def change_password():
    if request.method == "POST":
        rows = query_db("SELECT password FROM Teams WHERE email = %s",(session["student_user_id"],))
        if not sha.verify(request.form.get("oldpassword"), rows[0][0]):
            flash('Incorrect old password', 'danger')
            return redirect(url_for('teams.change_password'))

        # check password match
        if request.form.get("confpassword") != request.form.get("newpassword"):
            flash("Passwords don't match", 'danger')
            return redirect(url_for('teams.change_password'))

        # another check
        if sha.verify(request.form.get("newpassword"), rows[0][0]):
            flash("New password can't be same as old password", 'danger')
            return redirect(url_for('teams.change_password'))

        # password encryption
        phash = sha.encrypt(request.form.get("confpassword"))

        execute_db("UPDATE Teams SET password = %s WHERE email = %s",(phash, session["student_user_id"],))
        flash("Password successfully changed", 'success')
        return redirect(url_for("teams.dashboard"))
    else:
        return render_template("change_teams.html", **locals())

@teams.route('/evals')
@student_login_required
def evaluations():
    query = query_db("SELECT * From Evaluations;")
    now = date.today()
    return render_template("evaluations.html", **locals())

@teams.route('/announcements')
@student_login_required
def announcements():
    query = query_db("SELECT * From Announcements;")
    if(query is None):
        query = []
    return render_template("announcements.html", **locals())