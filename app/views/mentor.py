import csv
import math
import os
from datetime import date
from functools import wraps
from tempfile import mkdtemp
from flask_mail import Mail, Message

from app import *
from flask import (Blueprint, Flask, flash, g, redirect, render_template,
                   request, send_file, session, url_for)
from flask_mysqldb import MySQL
from flask_session import Session
from passlib.hash import sha256_crypt as sha

mentor = Blueprint('mentor', __name__, url_prefix='/mentor')

panel = {}
students = []
s_marks = []
eval_details = ()

@mentor.route("/change/", methods=["GET", "POST"])
@mentor_login_required
def change():
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    requests = query_db("select * from Requests where mentor_id = %s",(session["mentor_id"],))
    if requests is None:
        requests = []
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    if request.method == "POST":

        # query database for user
        rows = query_db("SELECT password FROM Mentors WHERE email = %s",(session["user_id"],))

        # ensure old password is correct
        if not sha.verify(request.form.get("oldpassword"), rows[0][0]):
            flash('Incorrect old password', 'danger')
            return redirect(url_for('mentor.change'))

        # check password match
        if request.form.get("confpassword") != request.form.get("newpassword"):
            flash("Passwords don't match", 'danger')
            return redirect(url_for('mentor.change'))

        # another check
        if sha.verify(request.form.get("newpassword"), rows[0][0]):
            flash("New password can't be same as old password", 'danger')
            return redirect(url_for('mentor.change'))

        # password encryption
        phash = sha.encrypt(request.form.get("confpassword"))

        execute_db("UPDATE Mentors SET password = %s WHERE email = %s",(phash, session["user_id"],))
        flash("Password successfully changed", 'success')
        return redirect(url_for("mentor.mygroups"))
    else:
        return render_template("change.html", user=session["user_id"], **locals())

@mentor.route('/', methods=["GET","POST"])
@mentor_login_required
def mygroups():
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    requests = query_db("select * from Requests where mentor_id = %s",(session["mentor_id"],))
    if requests is None:
        requests = []
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    eval_details = query_db('select * from Evaluations')
    now = date.today()
    if request.args.get('group'):
        sel_grp=False
    else:
        sel_grp=True
    all_groups = query_db("select group_id from Group_Mentors where mentor1_id= %s or mentor2_id=%s", (session["mentor_id"],session["mentor_id"],))
    if all_groups is None:
        all_groups = []
    group_id = request.args.get('group')
    students = []
    proj_title = []
    maxmarks = []
    for i in range(1, 7):
        maxmarks.append(int(query_db('select max_marks from Evaluations where evaluation_no=%s',(i,))[0][0]))
    group_is = query_db("select group_id from Group_Mentors where group_id=%s and (mentor1_id=%s or mentor2_id=%s)", (group_id,session["mentor_id"],session["mentor_id"]))
    if group_is is not None:
        temp = query_db("select * from Students where group_id = %s", (group_id,))
        ptitle = query_db("select title from Teams where group_id = %s", (group_id,))
        proj_title.append(ptitle)
        students.extend(temp)
        temp2 = []
        for a in students:
            temp3=[]
            for b in a:
                if b is None:
                    temp3.append(0)
                else:
                    temp3.append(b)
            temp2.append(temp3)
        students = temp2
    requests = query_db("select * from Requests where mentor_id = %s" ,(session["mentor_id"],))
    if requests is None:
        requests = []
    if proj_title is None:
        proj_title = []
    if (request.form.get("action") == 'sub_marks'):
        sel_grp= False
        groups = query_db("select group_id from Group_Mentors where mentor1_id= %s or mentor2_id=%s", (session["mentor_id"],session["mentor_id"],))
        for student in students:
            eval1=request.form.get(str(student[1])+"_eval1", None)
            eval2=request.form.get(str(student[1])+"_eval2", None)
            eval3=request.form.get(str(student[1])+"_eval3", None)
            eval4=request.form.get(str(student[1])+"_eval4", None)
            eval5=request.form.get(str(student[1])+"_eval5", None)
            eval6=request.form.get(str(student[1])+"_eval6", None)
            if eval1 is not None:
                execute_db("update Students set evaluation1_marks= %s where roll_no=%s",(eval1,student[1],))
            if eval2 is not None:
                execute_db("update Students set evaluation2_marks= %s where roll_no=%s",(eval2,student[1],))
            if eval3 is not None:
                execute_db("update Students set evaluation3_marks= %s where roll_no=%s",(eval3,student[1],))
            if eval4 is not None:
                execute_db("update Students set evaluation4_marks= %s where roll_no=%s",(eval4,student[1],))
            if eval5 is not None:
                execute_db("update Students set evaluation5_marks= %s where roll_no=%s",(eval5,student[1],))
            if eval6 is not None:
                execute_db("update Students set evaluation6_marks= %s where roll_no=%s",(eval6,student[1],))
        flash("Marks Updated Successfully","success")
        return redirect(url_for('mentor.mygroups'))
    return render_template("mygroups.html", **locals(), user=session["user_id"], mentor_id=session["mentor_id"])

@mentor.route('/searchgroup/', methods=["GET","POST"])
@mentor_login_required
def searchgroup():
    requests = query_db("select * from Requests where mentor_id = %s",(session["mentor_id"],))
    if requests is None:
        requests = []
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    if request.method== 'GET':
        return render_template('searchgroups.html', available_limit=available_limit, requests=requests, user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        grpid = request.form['groupid']
        grpid = query_db("select group_id from Teams where group_id = %s", (grpid, ))
        if grpid is None:
            flash("Group not Found", "warning")
            return redirect(url_for('mentor.searchgroup'))
        else:
            grpid = grpid[0][0]
            proj_title = query_db("select title from Teams where group_id = %s", (grpid,))
            tempmentorid = query_db("select mentor1_id, mentor2_id from Group_Mentors where group_id = %s", (grpid,))
            if tempmentorid[0][1] is None:
                mentor_name = query_db("select name from Mentors where mentor_id = %s", (tempmentorid[0][0],))
            else:
                mentor_name = query_db("select name from Mentors where mentor_id=%s OR mentor_id=%s", (tempmentorid[0][0],tempmentorid[0][1],))
            students = query_db("select * from Students where group_id = %s", (grpid,))
            if proj_title is None:
                proj_title = []
            return render_template('searchgroups.html', **locals(), user=session["user_id"], mentor_id=session["mentor_id"])

@mentor.route('/searchstudent/', methods=["GET","POST"])
@mentor_login_required
def searchstudent():
    requests = query_db("select * from Requests where mentor_id = %s",(session["mentor_id"],))
    if requests is None:
        requests = []
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    if request.method== 'GET':
        return render_template('searchstudent.html', **locals() , user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        rollno = request.form['rollno']
        student = query_db("select * from Students where roll_no = %s",(rollno,))
        grpid = query_db("select group_id from Students where roll_no = %s",(rollno,))
        proj_title = query_db("select title, email, phone from Teams where group_id = %s", (grpid,))
        if proj_title is None:
            proj_title = []
        mentorname = ""
        if student is not None:
            mentor = query_db("select mentor1_id, mentor2_id from Group_Mentors where group_id = %s", (student[0][0],))
            if mentor[0][1] is None:
                mentorname = query_db("select name from Mentors where mentor_id = %s", (mentor[0][0],))
            else:
                mentorname = query_db("select name from Mentors where mentor_id = %s OR mentor_id=%s", (mentor[0][0], mentor[0][1],))
            return render_template("searchstudent.html", **locals(), user=session["user_id"],mentor_id=session["mentor_id"])
        else:
            flash("Student Not Found", "warning")
            return redirect(url_for('mentor.searchstudent'))

@mentor.route("/request/<int:lead_id>/", methods=["GET", "POST"])
@mentor_login_required
def show_request(lead_id):
    requests = query_db("select * from Requests where mentor_id = %s" ,(session["mentor_id"],))
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    leaderid = lead_id
    request_grp = query_db("select * from Requests where leader_roll_no = %s",(leaderid,))
    if request.method== 'GET':
        if requests is None:
            requests =[]
            request_grp = []
        return render_template("requests.html", **locals(), user=session["user_id"],mentor_id=session["mentor_id"])
    else:
        if request.form.get("add", False):
            password = sha.encrypt(str(request_grp[0][1]))
            execute_db('insert into Teams (leader_roll_no,title,student2_roll_no,student3_roll_no,student4_roll_no,email,phone, password) values(%s,%s,%s,%s,%s,%s,%s,%s)',(
                request_grp[0][1],
                request_grp[0][2],
                request_grp[0][3],
                request_grp[0][4],
                request_grp[0][5],
                request_grp[0][6],
                request_grp[0][11],
                password,
                ))
            grp_id = query_db("select group_id from Teams where leader_roll_no=%s",(request_grp[0][1], ))
            grp_id = grp_id[0]
            execute_db('insert into Group_Mentors (group_id,mentor1_id) values(%s,%s)',(
                grp_id,
                request_grp[0][12],
                ))
            execute_db('insert into Students (group_id,roll_no,name) values(%s,%s,%s)',(
                grp_id,
                request_grp[0][1],
                request_grp[0][1+6],
                ))
            for j in range(1,4):
                execute_db('insert into Panel_Marks (roll_no,panel_no) values(%s,%s)',(
                    request_grp[0][1],
                    j,
                    ))
            for i in range(3, 5):
                if i==2:
                    continue
                execute_db('insert into Students (group_id,roll_no,name) values(%s,%s,%s)',(
                    grp_id,
                    request_grp[0][i],
                    request_grp[0][i+5],
                    ))
                for j in range(1,4):
                    execute_db('insert into Panel_Marks (roll_no,panel_no) values(%s,%s)',(
                        request_grp[0][i],
                        j,
                        ))
            if request_grp[0][10]:
                execute_db('insert into Students (group_id,roll_no,name) values(%s,%s,%s)',(
                    grp_id,
                    request_grp[0][5],
                    request_grp[0][10],
                    ))
                for j in range(1, 4):
                    execute_db('insert into Panel_Marks (roll_no,panel_no) values(%s,%s)',(
                        request_grp[0][5],
                        j,
                        ))

            execute_db("DELETE FROM Requests WHERE leader_roll_no = %s",(lead_id,))
            ## Composing Mail
            title="Capstone Project Group Request"
            sender="no-reply@thapar.edu"
            recipients = [request_grp[0][6]]
            mentor_name=query_db("SELECT name FROM Mentors WHERE mentor_id=%s",(session["mentor_id"],))
            message_html = "<h3>Your Capstone Project Group request was successfully accepted by "+str(mentor_name[0][0])+".</h3><br> Kindly Login on the given link with Credentials:-<br><b> Username:- Email ID of Leader</b><br><b>Password:- Roll No of Leader</b>"
            #send_mail(title,sender,recipients,message_html) # Sending Mail
            ## End of Mail
            flash("Group Added Successfully!", 'success')

        elif request.form.get('remove') == 'remove':
            execute_db("DELETE FROM Requests WHERE leader_roll_no = %s",(lead_id,))
            ## Composing Mail
            title="Capstone Project Group Request"
            sender="no-reply@thapar.edu"
            recipients = [request_grp[0][6]]
            mentor_name=query_db("SELECT name FROM Mentors WHERE mentor_id=%s",(session["mentor_id"],))
            message_html = "<b>Your Capstone Project Group request was rejected by "+str(mentor_name[0][0])+".</b>"
            #send_mail(title,sender,recipients,message_html) # Sending Mail
            ## End of Mail
            flash("Group Rejected!", 'success')
    return redirect(url_for("mentor.mygroups"))

@mentor.route('/panel_marks/', methods=["GET","POST"])
@mentor_login_required
def panel_marks():
    panel={}
    students=[]
    eval_details=()
    sel_groups = False
    now = str(date.today())
    group_marks = False
    requests = query_db("select * from Requests where mentor_id = %s",(session["mentor_id"],))
    if requests is None:
        requests = []
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    mentorid = query_db("select mentor_id from Mentors where email = %s",(session["user_id"],))
    query = query_db("select panel_no, panel_id from Panelists where mentor_id=%s and head=1",(mentorid, ))

    if request.method=="GET":
        if query is None:
            query = []
        else:
            for p in query:
                if p[0] in panel:
                    panel[p[0]].append(p[1])
                else:
                    panel[p[0]] = [p[1]]
        return render_template("panel_marks.html", **locals(), user=session["user_id"],mentor_id=session["mentor_id"])


    else:
        follow_up1 = False
        follow_up2= False

        if request.form['btn']=="sel_panel" or follow_up1:
            if follow_up1==False:
                panel_id = request.form["panel_id"]
                eval_id, panel_id = panel_id.split('_')
            sel_groups = True
            groups = list(query_db("select group_id, filled from Panel_Group where panel_id=%s and panel_no=%s",(panel_id, eval_id,)))
            for i in range(len(groups)):
                groups[i] = list(groups[i])
                groups[i].append(eval_id+"_"+panel_id+"_"+str(groups[i][0]))
            return render_template("panel_marks.html", **locals(), user=session["user_id"],mentor_id=session["mentor_id"])

        if request.form['btn']=="sel_group" or follow_up2:
            group_marks = True
            follow_up1 = True
            if follow_up2==False:
                group_id = request.form["group_id"]
                eval_id, panel_id, group_id = group_id.split('_')
            group_details = query_db("select * from Teams where group_id=%s",(group_id, ))
            students = []
            s_marks = []
            date_details = []
            for i in range(7,10):
                k = list(query_db("select evaluation_no, start_date, end_date from Evaluations where evaluation_no=%s",(i,))[0])
                k[1] = str(k[1])
                k[2] = str(k[2])
                date_details.append(k)
            for i in range(1, 6):
                if i==2:
                    continue
                if group_details[0][i] is not None:
                    k = query_db("select roll_no, name from Students where roll_no=%s",(group_details[0][i], ))
                    if k is not None:
                        students.append(k[0])
                    else:
                        students.append(())
                    s_marks_param = []
                    for j in range(1, 11):
                        k = query_db("select parameter%s_marks from Panel_Marks where roll_no=%s and panel_no=%s",(j, group_details[0][i], eval_id, ))
                        if k is not None:
                            if k[0][0] is not None:
                                s_marks_param.append(k[0][0])
                    s_marks.append(s_marks_param)
                else:
                    students.append(())
                    s_marks.append([])
            eval_details = query_db("select parameter_no, name, max_marks from Panel_Parameter where panel_no=%s",(eval_id, ))
            if eval_details is None:
                eval_details = ()
            mentorid = query_db("select mentor1_id from Group_Mentors where group_id=%s",(group_id, ))[0][0]
            mentor = query_db("select name from Mentors where mentor_id=%s",(mentorid, ))[0][0]
            return render_template("panel_marks.html", **locals(), user=session["user_id"],mentor_id=session["mentor_id"])


        if request.form['btn']=="marks":
            follow_up2 = True
            eval_id= request.form.get("eval_id")
            rolls = [request.form.get("roll"+"_"+str(i)) for i in range(1,5) if request.form.get("roll"+"_"+str(i)) is not None]
            names = [request.form.get("name"+"_"+str(i)) for i in range(1,5) if request.form.get("name"+"_"+str(i)) is not None]
            students=[(rolls[i],names[i]) for i in range(0,len(rolls))]
            eval_details = query_db("select parameter_no, name, max_marks from Panel_Parameter where panel_no=%s",(eval_id, ))
            filled = True
            for student in students:
                if len(student)>0:
                    for i in eval_details:
                        marks = request.form[str(student[0])+"_"+str(i[0])]
                        eval_id, panel_id, group_id, marks = marks.split('_')
                        if marks=='NULL':
                            filled = False
                        if query_db("select parameter%s_marks from Panel_Marks where panel_no=%s and roll_no=%s",(i[0], eval_id, student[0], )):
                            if marks=='NULL':
                                execute_db("UPDATE Panel_Marks set parameter%s_marks=NULL where panel_no=%s and roll_no=%s",(i[0], eval_id, student[0], ))
                            else:
                                execute_db("UPDATE Panel_Marks set parameter%s_marks=%s where panel_no=%s and roll_no=%s",(i[0], marks,  eval_id, student[0], ))
                        else:
                            if marks=='NULL':
                                execute_db("Insert into Panel_Marks(parameter%s_marks, panel_no, roll_no) values(NULL, %s, %s)",(i[0], eval_id, student[0], ))
                            else:
                                execute_db("Insert into Panel_Marks(parameter%s_marks, panel_no, roll_no) values(%s, %s, %s)",(i[0], marks, eval_id, student[0], ))
            print(eval_id, panel_id, group_id)
            if filled==True:
                execute_db("UPDATE Panel_Group set filled=1 where panel_no=%s and panel_id=%s and group_id=%s",(eval_id, panel_id, group_id, ))
            else:
                execute_db("UPDATE Panel_Group set filled=0 where panel_no=%s and panel_id=%s and group_id=%s",(eval_id, panel_id, group_id, ))
    flash("Marks Updated Successfully!", 'success')
    return redirect(url_for('mentor.panel_marks'))

@mentor.route('/add_mentor/', methods=['GET', 'POST'])
@mentor_login_required
def add_mentor():
    requests = query_db("select * from Requests where mentor_id = %s" ,(session["mentor_id"],))
    if requests is None:
        requests = []
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    groups = query_db("select group_id from Group_Mentors where mentor1_id=%s",(session["mentor_id"], ))
    team_details = []
    if groups is not None:
        for group in groups:
            leaderid = query_db("select leader_roll_no from Teams where group_id=%s",(group[0],))
            leader_name = query_db("select name from Students where roll_no=%s",(leaderid[0], ))[0][0]
            team_details.append([group[0], leader_name])
    else:
        team_details= []
    if request.method=="GET":
        return render_template("add_mentor.html", **locals() , user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        group_id = request.form['grp_id']
        mentor_email = request.form['email']
        password = request.form['password']
        mentor = query_db("select mentor_id, email from Mentors where email=%s",(mentor_email, ))
        phash = query_db("select password from Mentors where mentor_id = %s", (session["mentor_id"], ))
        if sha.verify(password, phash[0][0]):
            if mentor is not None:
                mentor = mentor[0]
            else:
                flash("Invalid Mentor Email", 'danger')
                return redirect(url_for("mentor.add_mentor"))
            if mentor:
                if query_db("select mentor2_id from Group_Mentors where group_id=%s",(group_id, ))[0][0] is not None:
                    flash("Group Already Has Second Mentor", 'danger')
                elif mentor == session["mentor_id"]:
                    flash("Mentor1 and Mentor2 can't be same", 'danger')
                else:
                    execute_db("update Group_Mentors set mentor2_id=%s where group_id=%s",(mentor[0], group_id, ))
                    flash("Mentor Added Successfully", "success")
            else:
                flash("Mentor Not Found", "danger")
        else:
            flash("Incorrect Password", 'danger')
        return redirect(url_for("mentor.add_mentor"))

@mentor.route('/edit_group/', methods=["GET", "POST"])
@mentor_login_required
def edit_group():
    mentor_limit = query_db("select group_limit from Mentors where mentor_id=%s", (session["mentor_id"], ))[0][0]
    mentor_first = query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(session["mentor_id"],))[0][0]
    mentor_second= query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(session["mentor_id"],))[0][0] - mentor_first
    mentor_second= mentor_second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(session["mentor_id"],))[0][0]
    mentor_second= mentor_second/2
    available_limit = float(mentor_limit)-(mentor_first+mentor_second)
    requests = query_db("select * from Requests where mentor_id = %s",(session["mentor_id"],))
    if requests is None:
        requests = []
    panel_head = query_db("select * from Panelists where mentor_id=%s AND head=1",(session["mentor_id"], ))
    is_panel_head = False
    if panel_head is None:
        is_panel_head = False
    else:
        is_panel_head = True
    if request.method=="POST":
        sel_grp=False
        group_id= request.form.get('group',False)
        title= request.form.get('title',False)
        description = request.form.get('description',False)
        title_des = title+"*93-k+5=H]s]V%"+description
        execute_db("update Teams set title=%s where group_id=%s",(title_des,group_id))
        flash("Details updated successfully !","success")
        return redirect(url_for('mentor.mygroups'))
    else:
        group_id = request.args.get('group')
        if session["admin"] == True:
            all_groups = query_db("select group_id from Group_Mentors")
        else:
            all_groups = query_db("select group_id from Group_Mentors where mentor1_id= %s or mentor2_id=%s", (session["mentor_id"],session["mentor_id"],))
        sel_grp=True
        edit_params=False
        if group_id is not None:
            if session["admin"] == True:
                group_is = True
            else:
                group_is = query_db("select group_id from Group_Mentors where group_id=%s and (mentor1_id=%s or mentor2_id=%s)", (group_id,session["mentor_id"],session["mentor_id"]))
            if group_is is not None:
                sel_grp = False
                title = query_db("select title from Teams where group_id=%s",(group_id,))
                edit_params = True
        return render_template("edit_group.html", **locals())
    return render_template("edit_group.html", **locals())

@mentor.route('/download/')
@mentor_login_required
def download():
    rows = query_db("select s.group_id, s.roll_no, s.name, s.evaluation1_marks, s.evaluation2_marks, s.evaluation3_marks, s.evaluation4_marks, s.evaluation5_marks, s.evaluation6_marks, t.title, (select name from Mentors where mentor_id = gm.mentor1_id), (select name from Mentors where mentor_id = gm.mentor2_id) from Students s, Teams t, Group_Mentors gm, Mentors m where s.group_id = t.group_id and t.group_id = gm.group_id and (gm.mentor1_id = m.mentor_id or gm.mentor2_id = m.mentor_id) and m.mentor_id = %s", (session["mentor_id"], ))
    if rows is None:
        flash("No Student Found", "danger")
        return redirect(url_for("mentor.mygroups"))
    with open('app/static/capstoneGroups' + str(session["mentor_id"]) + '.csv', 'w') as csvfile:
        fieldnames = ['Group', 'Project Title', 'Project Description', 'Mentor1', 'Mentor2', 'Roll Number', 'Name', 'Eval1', 'Eval2', 'Eval3', 'Eval4', 'Eval5', 'Eval6', 'Total']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            total = 0
            for i in range(6):
                if row[3+i] is not None:
                    total += row[3+i]
            group = 'CPG '+str(row[0])
            writer.writerow({'Group' : group, 'Project Title' : title_split(row[9]),'Project Description' : description_split(row[9]), 'Mentor1' : row[10], 'Mentor2' : row[11], 'Roll Number': row[1], 'Name' : row[2], 'Eval1' : row[3], 'Eval2' : row[4], 'Eval3' : row[5], 'Eval4' : row[6], 'Eval5' : row[7], 'Eval6' : row[8], 'Total' : total})
    return send_file('static/capstoneGroups' + str(session["mentor_id"]) + '.csv', mimetype='text/csv', attachment_filename='capstoneGroups.csv',as_attachment=True)
