import os
from datetime import date
from flask import Flask, request, render_template, flash, redirect, url_for, session, send_file
from flask import Blueprint, g
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt as sha
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
import csv
from app import *

admin = Blueprint('admin', __name__, url_prefix='/admin')

p_mentors = []
p_panel = []
p_panel_id = []
p_head = []
panel_id = 0
panel_no = 0


@admin.route('/view_mentors/', methods=["GET"])
@mentor_login_required
@admin_required
def view_mentors():
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
    mentors=query_db("select mentor_id,email,name from Mentors")
    numberofgroups=[]
    for mentor in mentors:
        temp=[]
        temp.extend((mentor[0],mentor[1],mentor[2]))
        first=query_db("select count(group_id) from Group_Mentors where mentor1_id=%s AND mentor2_id is Null;",(mentor[0],))[0][0]
        second=query_db("select count(group_id) from Group_Mentors where mentor1_id=%s;",(mentor[0],))[0][0] - first
        second=second + query_db("select count(group_id) from Group_Mentors where mentor2_id=%s;",(mentor[0],))[0][0]
        second=second/2
        temp.append(first+second)
        numberofgroups.append(temp)
    return render_template("view_mentors.html", **locals(), user=session["user_id"], mentor_id=session["mentor_id"])


@admin.route('/clear_all/', methods=["GET"])
@mentor_login_required
@admin_required
def clear_all():
    execute_db("delete from Teams where 1=1")
    execute_db("delete from Students where 1=1")
    execute_db("delete from Group_Mentors where 1=1")
    execute_db("delete from Requests where 1=1")
    execute_db("delete from Panel_group where 1=1")
    execute_db("delete from Panelists where 1=1")
    execute_db("delete from Panel_Marks where 1=1")
    execute_db("delete from Panel_parameter where 1=1")
    execute_db("alter table Teams auto_increment=1")
    flash("Data cleared!", 'success')
    return redirect(url_for("mentor.mygroups"))


@admin.route('/full_marks/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def full_marks():
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
    if request.method=='GET':
        return render_template('full_marks.html', **locals(), user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        full_marks = request.form['full_marks']
        eval_id = request.form['eval_id']
        if int(eval_id)<7:
            execute_db("UPDATE Evaluations SET max_marks = %s WHERE evaluation_no = %s",(full_marks, eval_id,))
        else:
            eval_id-=6
            execute_db("UPDATE panel_dates SET maxmarks = %s WHERE eval_id = %s",(full_marks, eval_id,))
        flash("Successfully updated full marks", "success")
        return redirect(url_for("mentor.mygroups"))


@admin.route('/add_admin/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def add_admin():
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
    if request.method=='GET':
        return render_template('add_admin.html', **locals(), user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        email = request.form['email']
        password=request.form['password']
        mentorid = query_db("select mentor_id from Mentors where email = %s",(email,))
        phash = query_db("select password from Mentors where mentor_id = %s", (mentorid, ))
        if sha.verify(password, phash[0][0]):
            if mentorid is None:
                flash("Mentor not Found", "danger")
                return redirect(url_for("admin.add_admin"))
            is_admin = query_db("select mentor_id from Heads where mentor_id=%s",(mentorid,))
            if is_admin:
                flash("Already an admin", "warning")
                return redirect(url_for("admin.add_admin"))
            else:
                execute_db("INSERT INTO Heads(mentor_id) VALUES(%s)",(mentorid[0][0], ))
                flash("Successfully added Admin", "success")
                return redirect(url_for("mentor.mygroups"))
        else:
            flash("Incorrect Password", 'danger')
            return redirect(url_for("admin.add_admin"))


@admin.route('/eval_period/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def eval_period():
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
    if request.method=='GET':
        return render_template('eval_time.html', **locals(), user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        eval_id = int(request.form['eval_id'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        if not eval_id or not start_date or not end_date:
            flash("All Fields are Compulsary", "danger")
        else:
            if query_db("SELECT * from Evaluations where evaluation_no=%s",(eval_id,)):
                execute_db("UPDATE Evaluations SET start_date=%s, end_date=%s where evaluation_no=%s", (start_date, end_date, eval_id, ))
            else:
                execute_db("INSERT INTO Evaluations(start_date, end_date, evaluation_no, max_marks) values(%s,%s,%s, 5)", (start_date, end_date, eval_id, ))
        flash("Evaluation Period Updated Successfully", "success")
        return redirect(url_for("admin.eval_period"))

@admin.route("/create_panel/", methods=["GET", "POST"])
@mentor_login_required
@admin_required
def panel():
    global p_mentors, p_panel, panel_no, p_head, p_panel_id, panel_id, panels_no
    p_panel_id = []
    follow_up = False
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
    if request.method=="GET":
        panels = query_db("select max(panel_id) from Panel_Group")[0][0]
        panel_created  = False
        if panels is not None:
            panel_created = True
            panels_no = panels
        else:
            show_panel = False
            grp_limit = 15
            groups = query_db("select * from Teams")
            panels  = []
            count = 0
            panel_temp = []
            if groups is None:
                flash("No groups formed yet", "danger")
                return redirect(url_for("mentor.mygroups"))
            for i in groups:
                count+=1
                if count<=grp_limit:
                    panel_temp.append(i)
                else:
                    panels.append(panel_temp)
                    panel_temp = []
                    panel_temp.append(i)
                    count = 1
            panels.append(panel_temp)
            panels_no = len(panels)
            for i in range(1, panels_no+1):
                for j in panels[i-1]:
                    for z in range(1, 4):
                        execute_db("insert into Panel_Group(panel_no, panel_id, group_id) values(%s,%s, %s)",(z,i, j[0], ))
            panel_created = True
            flash("Panels Created Successfully!","success")
            return redirect(url_for('admin.panel'))
    else:
        follow_up = False
        if request.form['btn']=="panelists":
            p_head = request.form['panel_head']
            panelist = request.form.getlist('panelist')
            if len(panelist)<4:
                flash("Select 4 Panelists and 1 Panel Head", "danger")
            else:
                if query_db("select * from Panelists where head=1 and panel_id=%s and panel_no=%s",(panel_id, panel_no, )):
                    execute_db("update Panelists set mentor_id=%s where head=1 and panel_id=%s and panel_no=%s",(p_head, panel_id, panel_no, ))
                else:
                    execute_db("insert into Panelists(panel_no, panel_id, mentor_id, head) values(%s,%s, %s, 1)",(panel_no, panel_id, p_head, ))
                execute_db("delete from Panelists where head=0 and panel_id=%s and panel_no=%s",(panel_id, panel_no, ))
                for x in range(4):
                    execute_db("insert into Panelists(panel_no, panel_id, mentor_id, head) values(%s,%s, %s, 0)",(panel_no, panel_id, panelist[x], ))
            panel_created = True
            follow_up = True
        if request.form['btn']=="sel_panel" or follow_up:
            show_panel = True
            panel_created = True
            if not follow_up:
                panel_no = request.form["eval_id"]
                panel_id = request.form["panel_id"]
            panel = query_db("select group_id from Panel_Group where panel_no=%s and panel_id =%s", (panel_no, panel_id))
            panels_no = query_db("select max(panel_id) from Panel_Group")[0][0]
            panel_temp = []
            p_panel = query_db("select mentor_id from Panelists where panel_no=%s and panel_id=%s and head=0",(panel_no, panel_id, ))
            p_head = query_db("select mentor_id from Panelists where panel_no=%s and panel_id=%s and head=1",(panel_no, panel_id, ))
            if p_head is not None:
                p_head = p_head[0][0]
                p_head = query_db("select mentor_id, name from Mentors where mentor_id=%s", (p_head ,))
                if p_head is not None:
                    p_head = p_head[0]
            if p_panel is None:
                p_panel = []
            else:
                p_panel=list(p_panel)
                for i in range(len(p_panel)):
                    p_panel_id.append(p_panel[i][0])
                    p_panel[i] = query_db("select mentor_id, name from Mentors where mentor_id=%s", (p_panel[i] ,))
                    if p_panel[i] is not None:
                        p_panel[i] = p_panel[i][0]
            p_mentors = query_db("select mentor_id, name from Mentors")
            for i in panel:
                group = query_db("select * from Teams where group_id=%s", (i, ))
                mentor = query_db("select mentor1_id from Group_Mentors where group_id=%s", (i, ))
                if mentor is None:
                    mentor = []
                mentor_name = query_db("select name from Mentors where mentor_id=%s",(mentor[0][0], ))
                leader_name = query_db("select name from Students where roll_no=%s", (group[0][1], ))
                gp = group[0]+mentor_name[0]+leader_name[0]
                panel_temp.append(gp)
    return render_template("panels.html", p_mentors=p_mentors, panels_no=panels_no, p_panel=p_panel, p_panel_id=p_panel_id, p_head=p_head, **locals())


@admin.route('/define_params/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def define_params():
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
    if request.method=="POST":
        panel_id = request.form['eval_id']
        param_id = request.form['param_id']
        param_name = request.form['param_name']
        param_marks = request.form['full_marks']
        if query_db("select name from Panel_Parameter where panel_no = %s and parameter_no = %s", (panel_id, param_id)) is not None:
            execute_db("update Panel_Parameter set name = %s, max_marks = %s where panel_no = %s and parameter_no = %s", (param_name, param_marks, panel_id, param_id))
            execute_db("UPDATE Panel_Marks set parameter%s_marks=0 where panel_no=%s", (int(param_id), panel_id))
            flash("Successfully updated paramater", "success")
        else:
            execute_db("insert into Panel_Parameter values(%s, %s, %s, %s)", (panel_id, param_id, param_name, param_marks))
            flash("Successfully added paramater", "success")
        execute_db("UPDATE Panel_Group set filled=0;")
    param_details = query_db("select * from Panel_Parameter")
    if param_details is None:
        param_details=[]
    return render_template("def_params.html", **locals())

@admin.route('/delete_param/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def delete_param():
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
    if request.method=="POST":
        key_id = list(request.form)[0]
        val = int(request.form[key_id])
        # password = request.form['password']
        # phash = query_db("select password from Mentors where mentor_id = %s", (session["mentor_id"], ))
        if True:
            print(val)
            panel_id = (val//8) + 1
            param_id = (val%8) + 1
            execute_db("delete from Panel_Parameter where panel_no = %s and parameter_no = %s", (panel_id, param_id))
            execute_db("UPDATE Panel_Marks set parameter%s_marks=NULL where panel_no=%s", (param_id, panel_id))
            execute_db("UPDATE Panel_Group set filled=0;")
            flash("Successfully deleted paramater", "warning")
        else:
            flash("Incorrect Password", "danger")
    param_details = query_db("select * from Panel_Parameter")
    return render_template("def_params.html", **locals())

@admin.route('/group_limit/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def group_limit():
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
    if request.method=='GET':
        return render_template('group_limit.html', **locals(), user=session["user_id"], mentor_id=session["mentor_id"])
    else:
        email = request.form['email']
        password=request.form['password']
        limit = request.form['limit']
        mentorid = query_db("select mentor_id from Mentors where email = %s",(email,))
        phash = query_db("select password from Mentors where mentor_id = %s", (session["mentor_id"], ))
        if sha.verify(password, phash[0][0]):
            if mentorid is None:
                flash("Mentor not Found", "danger")
                return redirect(url_for("admin.group_limit"))
            execute_db("Update Mentors SET group_limit=%s where mentor_id=%s",(limit, mentorid[0][0], ))
            flash("Successfully updated Mentor's limit", "success")
            return redirect(url_for("mentor.mygroups"))
        else:
            flash("Incorrect Password", 'danger')
            return redirect(url_for("admin.group_limit"))

@admin.route('/delete_group/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def delete_group():
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
        leader_roll = request.form['roll']
        leader_email = request.form['email']
        group_id = query_db("select group_id from Teams where leader_roll_no = %s and email = %s", (leader_roll, leader_email))
        if group_id is None:
            flash("Leader's Roll Number and Email didn't match", "danger")
            return redirect(url_for("admin.delete_group"))
        team = query_db("select * from Teams where group_id = %s", (group_id,))
        execute_db("delete from Group_Mentors where group_id = %s", (group_id,))
        execute_db("delete from Students where group_id = %s", (group_id,))
        execute_db("delete from Teams where group_id = %s", (group_id,))
        execute_db("delete from Panel_Group where group_id = %s", (group_id,))
        execute_db("delete from Panel_Marks where roll_no = %s or roll_no = %s or roll_no = %s", (leader_roll, team[0][3], team[0][4]))
        if team[0][5] is not None:
            execute_db("delete from Panel_Marks where roll_no = %s", (team[0][5],))
        flash("Group Deleted Successfully", "success")
        return redirect(url_for("admin.delete_group"))
    else:
        return render_template("delete_group.html", **locals())

@admin.route('/add_announcement/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def add_announcement():
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
    if(request.method=="POST"):
        now = date.today()
        execute_db("Insert into Announcements(title, description, dated) values (%s, %s, %s);",( request.form["title"], request.form["desc"], now))

        ## Composing Mail
        title= "Announcement - " + request.form["title"]
        sender="no-reply@thapar.edu"
        query = query_db("Select email from Teams;")
        recipients = []
        for record in query:
            recipients.append(record[0])
        message_html = request.form["desc"]
        # send_mail(title,sender,recipients,message_html) # Sending Mail
        ## End of Mail

        flash("Added Announcement Successfully", "success")
        return redirect(url_for('mentor.mygroups'))
    return render_template("add_announcements.html", **locals())

@admin.route('/download_all/', methods=["GET", "POST"])
@mentor_login_required
@admin_required
def download_all():
    no = query_db("select count(group_id) from Teams")
    if no[0][0] is 0:
        flash("No groups created yet", "warning")
        return redirect(url_for("mentor.mygroups"))
    rows = query_db("select a.group_id, a.roll_no, a.Student, a.evaluation1_marks,a.evaluation2_marks,a.evaluation3_marks,a.evaluation4_marks,a.evaluation5_marks,a.evaluation6_marks,a.title, a.Mentor1, m.name as2 from (select st.group_id,st.roll_no,st.name Student,st.evaluation1_marks,st.evaluation2_marks,st.evaluation3_marks,st.evaluation4_marks,st.evaluation5_marks,st.evaluation6_marks,t.title,m.name as Mentor1, gm.mentor2_id from Students st, Group_Mentors gm, Mentors m, Teams t where st.group_id = gm.group_id and m.mentor_id = gm.mentor1_id and st.group_id = t.group_id) a left join Mentors m on a.mentor2_id = m.mentor_id;")
    panel1 = query_db("select parameter1_marks, parameter2_marks, parameter3_marks, parameter4_marks, parameter5_marks, parameter6_marks, parameter7_marks, parameter8_marks from Panel_Marks pm, Students s where pm.roll_no = s.roll_no and panel_no = 1 order by s.group_id, s.roll_no, s.name")
    panel2 = query_db("select parameter1_marks, parameter2_marks, parameter3_marks, parameter4_marks, parameter5_marks, parameter6_marks, parameter7_marks, parameter8_marks from Panel_Marks pm, Students s where pm.roll_no = s.roll_no and panel_no = 2 order by s.group_id, s.roll_no, s.name")
    panel3 = query_db("select parameter1_marks, parameter2_marks, parameter3_marks, parameter4_marks, parameter5_marks, parameter6_marks, parameter7_marks, parameter8_marks from Panel_Marks pm, Students s where pm.roll_no = s.roll_no and panel_no = 3 order by s.group_id, s.roll_no, s.name")
    params = query_db("select CONCAT('P1_', name) from Panel_Parameter where panel_no = 1")
    if params is None:
        params = []
    p1_params = [x[0] for x in params]
    params = query_db("select CONCAT('P2_', name) from Panel_Parameter where panel_no = 2")
    if params is None:
        params = []
    p2_params = [x[0] for x in params]
    params = query_db("select CONCAT('P3_', name) from Panel_Parameter where panel_no = 3")
    if params is None:
        params = []
    p3_params = [x[0] for x in params]
    with open('app/static/capstoneFullReport.csv', 'w') as csvfile:
        fieldnames = ['Group', 'Project Title', 'Project Description', 'Mentor1', 'Mentor2', 'Roll Number', 'Name', 'Eval1', 'Eval2', 'Eval3', 'Eval4', 'Eval5', 'Eval6', 'ME_Total', ]
        if p1_params is not None:
            fieldnames.extend(p1_params)
            fieldnames.append('P1_Total')
        if p2_params is not None:
            fieldnames.extend(p2_params)
            fieldnames.append('P2_Total')
        if p2_params is not None:
            fieldnames.extend(p3_params)
            fieldnames.append('P3_Total')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row, p1, p2, p3 in zip(rows, panel1, panel2, panel3):
            me_total = p1_total = p2_total = p3_total = 0
            for i in range(6):
                if row[3+i] is not None:
                    me_total += int(row[3+i])
            for i in  range(8):
                if p1[i] is not None:
                    p1_total += int(p1[i])
                if p2[i] is not None:
                    p2_total += int(p2[i])
                if p3[i] is not None:
                    p3_total += int(p3[i])
            group = 'CPG '+str(row[0])
            data = {'Group' : group, 'Project Title' : title_split(row[9]), 'Project Description' : description_split(row[9]), 'Mentor1' : row[10], 'Mentor2' : row[11], 'Roll Number': row[1], 'Name' : row[2], 'Eval1' : row[3], 'Eval2' : row[4], 'Eval3' : row[5], 'Eval4' : row[6], 'Eval5' : row[7], 'Eval6' : row[8], 'ME_Total' : me_total}
            for i in range(len(p1_params)):
                data[p1_params[i]] = p1[i]
            data['P1_Total'] = p1_total
            for i in range(len(p2_params)):
                data[p2_params[i]] = p2[i]
            data['P2_Total'] = p2_total
            for i in range(len(p3_params)):
                data[p3_params[i]] = p3[i]
            data['P3_Total'] = p3_total
            writer.writerow(data)
    return send_file('static/capstoneFullReport.csv', mimetype='text/csv', attachment_filename='capstoneFullReport.csv',as_attachment=True)
