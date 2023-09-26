#################################### Imports ###################################

import os, re
from flask import Flask
from flask import render_template, request, url_for, redirect, abort, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from datetime import datetime
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('Agg')


curr_dir = os.path.abspath(os.path.dirname(__file__))



# Creating a Flask instance 
app = Flask(__name__)
app.secret_key = 'dolly'



#adding the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(curr_dir, 'ticketshow_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False





#setting uploading types of images & the folder to upload images
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['UPLOAD_PATH'] = 'static/img'


db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
app.secret_key = 'dolly'







def username_validation(username):
    if len(username)<4 or len(username)>20:
        return False
    if not username.isalnum():
        return False
    return True
    
def password_validation(password):
    if len(password)<8 or len(password)>20:
        return False
    return True


def date_validation(date):
    try:
        date_obj = datetime.strptime(date, '%d-%m-%Y')
        if date_obj.date() <= datetime.now().date():
            raise ValueError('Date should be greater than today.')
    except ValueError:
        return False
    return True
    



def email_validation(email):
     pattern = r'^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-z]{2,}$'
     if re.match(pattern, email):
        return True
     return False




########################################### Tables #################################################

class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_fname = db.Column(db.String(35), nullable=False)
    admin_lname = db.Column(db.String(35), nullable=False)
    admin_username = db.Column(db.String(35), nullable=False, unique=True)
    admin_password = db.Column(db.String(35), nullable=False)
    admin_email = db.Column(db.String(35), nullable=False)
    admin_loc = db.Column(db.String(25), nullable=False)
    admin_img = db.Column(db.String(50), nullable=False)





class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_fname = db.Column(db.String(35), nullable=False)
    user_lname = db.Column(db.String(35), nullable=False)
    user_username = db.Column(db.String(35), nullable=False, unique=True)
    user_password = db.Column(db.String(35), nullable=False)
    user_location = db.Column(db.String(35), nullable=False)
    user_img = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(25), nullable=False)




class Shows(db.Model):
    __tablename__ = "shows"
    show_id = db.Column(db.Integer, nullable=False,
                        primary_key=True, autoincrement=True)
    show_name = db.Column(db.String(35), nullable=False)
    show_rating = db.Column(db.Numeric(precision=2, scale=1), nullable=False)
    show_tag = db.Column(db.String(35), nullable=False)
    show_price = db.Column(db.Integer, nullable=False)
    show_time = db.Column(db.String(35), nullable=False)
    show_venue_id = db.Column(db.Integer, nullable=False)
    show_date = db.Column(db.String(35), nullable=False)
    show_img = db.Column(db.String(30), nullable=False)
    show_cap=db.Column(db.Integer, nullable=False)
    show_admin_id=db.Column(db.Integer, nullable=False)
    show_revenue=db.Column(db.Integer, nullable=False)




class Venue(db.Model):
    __tablename__ = "venue"
    venue_id = db.Column(db.Integer, nullable=False,
                         primary_key=True, autoincrement=True)
    venue_name = db.Column(db.String(30), nullable=False)
    venue_loc = db.Column(db.String(30), nullable=False)
    venue_place = db.Column(db.String(20), nullable=False)
    venue_capa = db.Column(db.Integer, nullable=False)
    venue_creator_id = db.Column(db.Integer, nullable=False)
    venue_img = db.Column(db.String(50), nullable=False)




class Bookings(db.Model):
    __tablename__ = "bookings"
    booking_id = db.Column(db.Integer, nullable=False,
                           autoincrement=True, primary_key=True)
    booking_user_id = db.Column(db.Integer, nullable=False)
    booking_show_id = db.Column(db.Integer, nullable=False)
    booking_venue_id = db.Column(db.Integer, nullable=False)
    booking_date_time = db.Column(db.String(30), nullable=False)



class Ratings(db.Model):
    __tablename__="ratings"
    rating_id=db.Column(db.Integer, nullable=False, primary_key=True)
    ratings=db.Column(db.Integer, nullable=False)
    ruser_id=db.Column(db.Integer, nullable=False)
    rshow_id=db.Column(db.Integer, nullable=False)
    rvenue_id=db.Column(db.Integer, nullable=False)


#create database if  does not already exists
if os.path.exists("/ticketshow_database.sqlite3")==False:
    db.create_all()






###################################### Welcome Page #############################################

@app.route('/', methods=["GET", "POST"])
def welcome():
    if request.method == "GET":
        return render_template("welcome.html")
    if request.method == "POST":
        login_form = request.form.get("login_type")
        if login_form == "admin":
            return redirect("/admin_login")
        if login_form == "user":
            return redirect("/user_login")






###################################### Admin Login #############################################

@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("Admin_Login.html")
    if request.method == 'POST':
        username = request.form["admin_username"]
        password = request.form["admin_password"]
        if not username_validation(username):
            flash("Username length must be between 4 and 20 alphanumeric characters","username_error")
            return render_template("Admin_Login_new.html", username=username)
        admin_name = Admin.query.filter_by(admin_username=username).all()
        # checks whether entered username exists in the admin table or not.
        if len(admin_name) == 0:
            flash("No Admin exists with this Username! Enter correct credentials or Register as New Admin", "user_absent")
            return render_template("Admin_Login_new.html", username=username)
        
        if len(admin_name) == 1:
            aduser = Admin.query.filter_by(admin_username=username).first()
            pw = aduser.admin_password
            session['usr'] = username
            session['logged_in'] = True
            if pw == password:
                flash("Log in Successfull! Welcome to your Dashboard","dashboard_success")
                return redirect("/admin_dashboard")
            if  not password_validation(password):
                flash("Required Length of password should be at least 8 and maximum 20 characters","password_error")
                return render_template("Admin_Login_new.html", username=username)
            flash("Incorrect Password!","error")
            return render_template("Admin_Login_new.html", username=username)







###################################### Admin Logout #############################################

@app.route('/admin_logout', methods=['GET', 'POST'])
def admin_logout():
    if request.method == 'GET':
        session.pop('usr', None)
        session['logged_in'] = False
        flash("Logged out successfully!", "dashboard_success")
        return redirect('/')




###################################### Admin Signup Page #############################################

@app.route("/admin_signup", methods=["POST", "GET"])
def admin_signup():
    if request.method == "GET":
        return render_template("Admin_Signup.html")
    if request.method == "POST":
        admin_fname = request.form["admin_fname"]
        admin_lname = request.form["admin_lname"]
        admin_loc = request.form['admin_loc']
        admin_email = request.form['admin_email']

        if not email_validation(admin_email):
            flash("Enter a valid email.","email_error")
            return render_template("Admin_Signup_new.html", admin_fname=admin_fname, admin_lname=admin_lname, admin_loc=admin_loc)
        
        admin_username = request.form["admin_username"]
        if  not username_validation(admin_username):
            flash("Length of username should be between 4 and 20 alphanumeric characters","username_error")
            return render_template("Admin_Signup_new.html",admin_fname=admin_fname, admin_lname=admin_lname, admin_loc=admin_loc, admin_email=admin_email)
        
        admin_password = request.form["admin_password"]
        if not password_validation(admin_password):
            flash("Length of Password should be at least 8 characters and at maximum 20 characters","password_error")
            return render_template("Admin_Signup_new.html", admin_username=admin_username,admin_fname=admin_fname, admin_lname=admin_lname, admin_loc=admin_loc, admin_email=admin_email)
        
        admin_img = request.files['admin_img']
        file_name = secure_filename(admin_img.filename)
        if file_name != '':
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            admin_img.save(os.path.join(app.config['UPLOAD_PATH'], file_name))
        adusr = Admin.query.filter_by(admin_username=admin_username).all()
        if len(adusr) != 0:
            flash("Username already exists! Try some other username.","username_exist")
            return render_template("Admin_Signup_new.html", admin_fname=admin_fname, admin_lname=admin_lname, admin_username=admin_username, admin_loc=admin_loc, admin_email=admin_email )
        adm = Admin(admin_username=admin_username, admin_fname=admin_fname, admin_lname=admin_lname,
                    admin_password=admin_password, admin_email=admin_email, admin_loc=admin_loc, admin_img=file_name)
        db.session.add(adm)
        db.session.commit()
        flash("Signed up as admin successfully", "dashboard_success")
        return redirect("/admin_login")







###################################### User Login #############################################

@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        return render_template("User_Login.html")
    if request.method == "POST":
        username = request.form["user_username"]
        password = request.form["user_password"]
        if not username_validation(username):
            flash("Length of username must be between 4 and 20 alphanumeric characters","username_error")
            return render_template("User_Login_new.html", username=username)
        user_name = Users.query.filter_by(user_username=username).all()
       
        if len(user_name) == 0:
            flash("No User Exists with this Username! Enter correct credentials or Register as New User", "user_absent")
            return render_template("User_Login_new.html", username=username)
        if len(user_name) == 1:
            ususername = Users.query.filter_by(user_username=username).first()
            session["user"]=username
            session["user_logged_in"]=True
            pw = ususername.user_password
            if pw == password:
                flash("Logged in successfully! Welcome to your dashboard", "dashboard_success")
                return redirect("/user_dashboard")
            if not password_validation(password):
                flash("Length of password must be at least 8 characters and at maximum 20 characters","password_error")
                return render_template("User_Login_new.html", username=username)
            flash("Incorrect Password!", "error")
            return render_template("User_Login_new.html",username=username)
        



###################################### User Logout Page #############################################

@app.route('/user_logout', methods=['GET', 'POST'])
def user_logout():
    if request.method == 'GET':
        session.pop('user', None)
        session['user_logged_in'] = False
        flash("Logged out successfully!", "dashboard_success")
        return redirect('/user_login')




###################################### User Signup Page #############################################

@app.route("/user_signup", methods=["POST", "GET"])
def user_signup():
    if request.method == "GET":
        return render_template("User_Signup.html")
    if request.method == "POST":
        user_fname = request.form["user_fname"]
        user_lname = request.form["user_lname"]
        location = request.form["user_location"]
        username = request.form["user_username"]
        user_email=request.form['user_email']
        if not email_validation(user_email):
            flash("Enter a valid email-id.","email_error")
            return render_template("User_Signup_New.html", user_fname=user_fname, user_lname=user_lname,  location=location, user_username=username)
        
        if not username_validation(username):
            flash("Length of username should be between 4 and 20 alphanumeric characters", "username_error")
            return render_template("User_Signup_New.html", user_email=user_email,  user_fname=user_fname, user_lname=user_lname,  location=location, user_username=username)
        
        password = request.form["user_password"]
        if not password_validation(password):
            flash("Length of password should be at least 8 and at max 20 characters", "password_error")
            return render_template("User_Signup_New.html", user_email=user_email, user_fname=user_fname, user_lname=user_lname,  location=location, user_username=username)
        user_img = request.files['user_img']
        user_username = Users.query.filter_by(user_username=username).all()
        if len(user_username) != 0:
            flash("Username already exists! Try some other username.","username_exist")
            return render_template("User_Signup_New.html", user_fname=user_fname,user_email=user_email, user_lname=user_lname,  location=location, username=username)
        
        file_name = secure_filename(user_img.filename)
        if file_name != '':
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            user_img.save(os.path.join(app.config['UPLOAD_PATH'], file_name))
        usr = Users(user_username=username, user_password=password,
                    user_location=location, user_fname=user_fname, user_lname=user_lname, user_img=file_name, user_email=user_email)
        db.session.add(usr)
        db.session.commit()
        flash("Signed up as user successfully", "dashboard_success")
        return redirect("/user_login")




###################################### Admin Dashboard Page #############################################

@app.route("/admin_dashboard", methods=["POST", "GET"])
def admin_dashboard():
    if request.method == "GET":
        if session['logged_in']:
            username = session['usr']
            ad_name = Admin.query.filter_by(admin_username=username).first()
            ad_id = ad_name.admin_id
            venue_details = Venue.query.filter_by(venue_creator_id=ad_id).all()
        # if len(venue_details)!=0:
            return render_template("admin_dashboard.html", ven_detls=venue_details, adusrname=username)
        # return render_template("no_venue.html",adusrname=username)
        else:
            return redirect('/admin_login')




###################################### Admin Profile Page #############################################

@app.route('/admin_profile', methods=['GET', 'POST'])
def admin_profile():
    if session['logged_in']:
        username = session['usr']
        admin_profile = Admin.query.filter_by(admin_username=username).first()
        return render_template('admin_profile.html', admin_det=admin_profile)
    return redirect("/admin_login")




###################################### Create Venue Page #############################################

@app.route("/admin_dashboard/create_venue", methods=["GET", "POST"])
def create_venue():
    if request.method == "GET":
        if session['logged_in']:
            username = session['usr']
            return render_template("venue_add.html", adusrname=username)
        return redirect('/admin_login')
    if request.method == "POST":
        vname = request.form["ven_name"]
        vloc = request.form["ven_loc"]
        vcap = request.form["ven_cap"]
        vplace = request.form["ven_place"]
        vimg = request.files['ven_img']
        username = session['usr']
        v_creator = Admin.query.filter_by(admin_username=username).first()
        v_creator_id = v_creator.admin_id
        file_name = secure_filename(vimg.filename)
        if file_name != '':
            file_ext = os.path.splitext(file_name)[1]
            rfile_name=vplace+"_"+vloc+file_ext
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            vimg.save(os.path.join(app.config['UPLOAD_PATH'], rfile_name))
        venue = Venue(venue_name=vname, venue_loc=vloc, venue_capa=vcap,
                      venue_place=vplace, venue_creator_id=v_creator_id, venue_img=rfile_name)
        db.session.add(venue)
        db.session.commit()
        flash("Venue created successfully!","dashboard_success")
        return redirect("/admin_dashboard")





###################################### Creating Shows inside Venue #############################################

@app.route("/admin_dashboard/<venue_id>/create_show", methods=["POST", "GET"])
def create_show(venue_id):
    if request.method == "GET":
        if session['logged_in']:
            username = session['usr']
            return render_template('add_show.html', admin_username=username, venue_id=venue_id)
        return redirect('/admin_login')
    if request.method == "POST":
        show_admin_id=Venue.query.filter_by(venue_id=venue_id).first().venue_creator_id
        s_name = request.form["s_name"]
        rating = request.form["rating"]
        time = request.form["time"]
        tag = request.form["tag"]
        price = request.form["price"]
        show_img = request.files['show_img']
        show_date = request.form['show_date']
        if not date_validation(show_date):
            flash("Date must be after today","date_error")
            return redirect("/admin_dashboard/"+venue_id+"/create_show")
        
        ven_cap=Venue.query.filter_by(venue_id=venue_id).first().venue_capa
        show_cap=ven_cap
        file_name = secure_filename(show_img.filename)
        if file_name != '':
            file_ext = os.path.splitext(file_name)[1]
            rfile_name=s_name+"_"+venue_id+file_ext
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            show_img.save(os.path.join(app.config['UPLOAD_PATH'], rfile_name))
        show_data = Shows(show_name=s_name, show_rating=rating, show_time=time,
                          show_tag=tag, show_price=price, show_venue_id=venue_id, show_img=rfile_name, show_date=show_date,show_cap=show_cap, show_admin_id=show_admin_id, show_revenue=0)
        db.session.add(show_data)
        db.session.commit()
        flash("Show created successfully!","dashboard_success")
        return redirect("/admin_dashboard/"+venue_id+"/shows")



############################# Listing Available Shows #########################################

@app.route("/admin_dashboard/<venue_id>/shows", methods=["POST", "GET"])
def shows(venue_id):
    if request.method == "GET":
        if session['logged_in']:
            username = session['usr']
            shows = Shows.query.filter_by(show_venue_id=venue_id).all()
            return render_template("shows.html", admin_username=username, venue_id=venue_id, show_detls=shows)
        else:
            return redirect('/admin_login')




###################################### Update Venue  #############################################

@app.route("/admin_dashboard/<venue_id>/update", methods=["GET", "POST"])
def update_venue(venue_id):
    if request.method == "GET":
        if session['logged_in']:
            username = session['usr']
            venue_details = Venue.query.filter_by(venue_id=venue_id).first()
            return render_template("update_venue.html", ven_det=venue_details, admin_username=username)
        else:
            return redirect('/admin_login')
    if request.method == "POST":
        venue_details = Venue.query.filter_by(venue_id=venue_id).first()
        ven_name = request.form["ven_name"]
        ven_image=request.files["ven_img"]
        venue_details.venue_name = ven_name
        if ven_image:
            file_name=secure_filename(ven_image.filename)
            if file_name!="":
                file_ext=os.path.splitext(file_name)[1]
                rfile_name=venue_details.venue_place+"_"+venue_details.venue_loc+file_ext
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                ven_image.save(os.path.join(app.config['UPLOAD_PATH'], rfile_name))
            venue_details.venue_image=rfile_name
        db.session.commit()
        flash("Venue details updated successfully!", "dashboard_success")
        return redirect("/admin_dashboard")







###################################### Deleting Venue #############################################

@app.route("/admin_dashboard/<ven_id>/delete", methods=["GET", "POST"])
def delete_ven(ven_id):
    if request.method == 'GET':
        if session['logged_in']:
            username = session['usr']
            return render_template("delete_venue.html", admin_username=username, ven_id=ven_id)
        else:
            return redirect('/admin_login')




#############################################################  Confirming Delete Venue ##############################################################

@app.route("/admin_dashboard/<ven_id>/delete_venue", methods=["GET", "POST"])
def delete_venue(ven_id):
    venue = Venue.query.filter_by(venue_id=ven_id).first()
    show = Shows.query.filter_by(show_venue_id=ven_id).all()
    booking = Bookings.query.filter_by(booking_venue_id=ven_id).all()
    rating = Ratings.query.filter_by(rvenue_id=ven_id).all()
    if request.method == "GET":
        if session['logged_in']:
            filename = os.path.join(app.config["UPLOAD_PATH"], venue.venue_img)
            if os.path.exists(filename):
                os.remove(filename)
            db.session.delete(venue)
            for s in show:
                filename = os.path.join(app.config["UPLOAD_PATH"], s.show_img)
                if os.path.exists(filename):
                    os.remove(filename)
                db.session.delete(s)
            if len(booking)>0:
                for b in booking:
                    db.session.delete(b)
            if len(rating)>0:
                for r in rating:
                    db.session.delete(r)
            db.session.commit()
        return redirect('/admin_dashboard')
    return redirect("/admin_dashboard")





###################################### Update Show #############################################

@app.route("/admin_dashboard/<venue_id>/<show_id>/update", methods=["GET", "POST"])
def update_show(venue_id, show_id):
    if request.method == "GET":
        if 'logged_in' in session.keys():
            username = session['usr']
            show_detail = Shows.query.filter_by(show_id=show_id).first()
            return render_template("update_show.html", show_detail=show_detail, admin_username=username, venue_id=venue_id)
        else:
            abort(401, 'you are not authorised to view')
            # return redirect('/admin_login')
    if request.method == "POST":
        show_details = Shows.query.filter_by(show_id=show_id).first()
        show_rating = request.form["rating"]
        show_time = request.form["time"]
        show_pric = request.form["price"]
        show_details.show_rating = show_rating
        show_details.show_time = show_time
        show_details.show_price = show_pric
        show_date = request.form['show_date']
        if not date_validation(show_date):
            flash("Date must be after today","date_error")
            return redirect("/admin_dashboard/"+venue_id+"/"+show_id+"/update")
        show_details.show_date = show_date
        show_image=request.files["show_img"]
        if show_image:
            file_name=secure_filename(show_image.filename)
            if file_name!="":
                file_ext=os.path.splitext(file_name)[1]
                rfile_name=venue_id+"_"+show_details.show_name+file_ext
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                show_image.save(os.path.join(app.config['UPLOAD_PATH'], rfile_name))
            show_details.show_img=rfile_name
        db.session.commit()
        flash("Show details updated successfully!","dashboard_success")
        return redirect("/admin_dashboard/"+venue_id+"/"+"shows")





###################################### Deleting Shows #############################################

@app.route("/admin_dashboard/<ven_id>/<show_id>/delete", methods=["GET", "POST"])
def delete_sho(ven_id, show_id):
    if session['logged_in']:
        username = session['usr']
        return render_template("delete_show.html", admin_username=username, ven_id=ven_id, show_id=show_id)
    return redirect('/admin_login')





######################################################### Confirming Delete Show #################################################################

@app.route("/admin_dashboard/<ven_id>/<show_id>/delete_show", methods=["GET", "POST"])
def delete_show(ven_id, show_id):
    show = Shows.query.filter_by(show_id=show_id).first()
    booking = Bookings.query.filter_by(booking_show_id=show_id).all()
    rating = Ratings.query.filter_by(rshow_id=show_id).all()
    if request.method == "GET":
        if session['logged_in']:
            filename = os.path.join(app.config["UPLOAD_PATH"], show.show_img)
            if os.path.exists(filename):
                os.remove(filename)
            db.session.delete(show)
            if len(booking)>0:
                for b in booking:
                    db.session.delete(b)
            if len(rating)>0:
                for r in rating:
                    db.session.delete(r)
            db.session.commit()
        return redirect("/admin_dashboard/"+ven_id+"/"+"shows")
    return redirect('/admin_login')




############################################################### User Dashboard #############################################################

@app.route("/user_dashboard", methods=['GET', 'POST'])
def user_dashboard():
    if request.method == "GET":
        if session['user_logged_in']:
            username = session['user']
            user = Users.query.filter_by(user_username=username).first()
            venues= Venue.query.filter(Venue.venue_place.ilike(user.user_location)).all()
            shows=Shows.query.all()
            return render_template('user_dashboard.html', user_username=username, venues=venues, shows=shows)
        return redirect('/user_login')
            





###########################################################  Seat Booking ############################################################

@app.route('/user_dashboard/book/<show_id>', methods=['GET','POST'])
def bookings(show_id):
    if request.method=='GET':
        if session['user_logged_in']:
            username=session['user']
            show_det=Shows.query.filter_by(show_id=show_id).first()
            venue_det=Venue.query.filter_by(venue_id=show_det.show_venue_id).first()
            if int(show_det.show_cap)==0:
                flash("Show is Housefull. Please try in other venues.", "housefull")
                return redirect("/user_dashboard")
            return render_template('booking_show.html', show_details=show_det, venue_details=venue_det, user_username=username)
        return redirect('/user_login')   
    if request.method=='POST':
        no_of_seats=request.form['no_of_seats']
        if type(no_of_seats)==str or type(no_of_seats)==int:
            try:
                session["seats"]=int(no_of_seats)
            except ValueError:
                flash("Enter a positive integer", "int_error")
                return redirect("/user_dashboard/book/"+show_id)
        show_det=Shows.query.filter_by(show_id=show_id).first()
        if int(no_of_seats)>int(show_det.show_cap):
            flash(" Show is Housefull ! Please enter less seats than available.","low_seat_count")
            return redirect("/user_dashboard/book/"+show_id)
        return redirect('/user_dashboard/booking/'+show_id)
    



######################################### Confirming to Book Show ###########################################

@app.route("/user_dashboard/booking/<show_id>", methods=["GET", "POST"])
def booking_total(show_id):
    if request.method=="GET":
        if session["user_logged_in"]:
            username=session["user"]
            show_det=Shows.query.filter_by(show_id=show_id).first()
            no_of_seats=session["seats"]
            total_price=no_of_seats*int(show_det.show_price)
            show_det.show_revenue+=total_price
            db.session.commit()
            return render_template("bookings_total.html", user_username=username,show_det=show_det, no_of_seats=no_of_seats, total_price=total_price)
        return redirect("/")
    if request.method=="POST":
        if request.form["surity"]=="confirm":
            now=datetime.now()
            username=session["user"]
            buser_id=Users.query.filter_by(user_username=username).first().user_id
            bshow_id=show_id
            show_det=Shows.query.filter_by(show_id=show_id).first()
            bvenue_id=show_det.show_venue_id
            booked=Bookings(booking_date_time=now, booking_user_id=buser_id, booking_show_id=bshow_id, booking_venue_id=bvenue_id)
            db.session.add(booked)
            show_det.show_cap=int(show_det.show_cap)-int(session["seats"])
            db.session.commit()
            flash("Booked successfully", "dashboard_success")
            return redirect("/user_dashboard")
        if request.form["surity"]=="no":
            flash("Booking Cancelled", "error")
            return redirect("/user_dashboard")
        
        



######################################################### User Profile ##############################################################

@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if session['user_logged_in']:
        username = session['user']
        user_profile = Users.query.filter_by(user_username=username).first()
        return render_template('user_profile.html', user_det=user_profile)
    return redirect("/user_login")



################################################################# User Bookings ###########################################################

@app.route("/my_bookings",methods=["GET"])
def my_bookings():
    if request.method=="GET":
        if session["user_logged_in"]:
            username=session["user"]
            user_id=Users.query.filter_by(user_username=username).first().user_id
            booking_det=Bookings.query.filter_by(booking_user_id=user_id).order_by(Bookings.booking_date_time.desc()).all()
            return render_template("bookings.html", bookings=booking_det, Venues=Venue, Shows=Shows, user_username=username)
        return redirect("/user_login") 




################################################################ Searching Venues by names, Shows by names/tags/genre ####################################################

@app.route("/search", methods=["GET", "POST"])
def search():
    if session["user_logged_in"]:
        username=session["user"]
        myquery=request.args.get("my_query")
        my_query="%{}%".format(myquery)
        searched_venues=Venue.query.filter(or_(Venue.venue_name.ilike(my_query), Venue.venue_loc.ilike(my_query), Venue.venue_place.ilike(my_query))).all()
        searched_shows=Shows.query.filter(or_(Shows.show_name.ilike(my_query),Shows.show_rating.ilike(my_query), Shows.show_tag.ilike(my_query))).all()
        return render_template("searched_results.html", venues=searched_venues, shows=searched_shows, user_username=username)
    return redirect("/User_Login")



####################################################  Show Rating ###############################################################

@app.route("/rating/<show_id>", methods=["GET", "POST"])
def rateshow(show_id):
    if request.method=="GET":
        if session["user_logged_in"]:
            username=session["user"]
            user_id=Users.query.filter_by(user_username=username).first().user_id
            show=Shows.query.filter_by(show_id=show_id).first()
            return render_template("Ratings.html", show_det=show)
        return redirect("/User_Login")
    if request.method=="POST":
        show=Shows.query.filter_by(show_id=show_id).first()
        username=session["user"]
        user_id=Users.query.filter_by(user_username=username).first().user_id
        rated_user_id_per_show=Ratings.query.filter_by(rshow_id=show_id)
        ruser_id_list_per_show=[rating.ruser_id for rating in rated_user_id_per_show]
        if user_id in ruser_id_list_per_show:
            flash("You have already rated", category="error")
            return redirect("/my_bookings")
        rating_value=request.form.get("rating")
        rating=Ratings(ratings=rating_value, ruser_id=user_id, rshow_id=show.show_id, rvenue_id=show.show_venue_id)
        db.session.add(rating)
        db.session.commit()
        ratings_per_show=Ratings.query.filter_by(rshow_id=show_id).all()
        rating_list=[int(rating.ratings) for rating in ratings_per_show]
        avg_rating=sum(rating_list)/len(rating_list)
        show_det=Shows.query.filter_by(show_id=show_id).first()
        show_det.show_rating=avg_rating
        db.session.commit()
        flash("Show Rated successfully", category="dashboard_success")
        return redirect("/my_bookings")





################################### VENUE DETAILS #########################################
@app.route("/venue_details/<ven_id>", methods=["GET"])
def show_venue(ven_id):
    if request.method=="GET":
        if session["user_logged_in"]:
            username=session["user"]
            venue_det=Venue.query.filter_by(venue_id=ven_id).first()
            show_det=Shows.query.filter_by(show_venue_id=venue_det.venue_id).all()
            return render_template("venue_details.html", venue=venue_det, shows=show_det, user_username=username)
        return redirect("/user_login")




################################### SHOW DETAILS ############################################
@app.route("/show/<show_id>", methods=["GET"])
def show_details(show_id):
    if request.method=="GET":
        if session["user_logged_in"]:
            username=session["user"]
            show_det=Shows.query.filter_by(show_id=show_id).first()
            return render_template("show_details.html", show=show_det, user_username=username)
        return redirect("/user_login")




################################################################# Summary for Admin #############################################################

@app.route("/summary", methods=["GET"])
def summary():
    if request.method=="GET":
        if session["logged_in"]:
            username=session["usr"]
            aduser_id=Admin.query.filter_by(admin_username=username).first().admin_id
            booking_det=Bookings.query.all()
            show_det=Shows.query.filter_by(show_admin_id=aduser_id).all()
            sid_list=[s.show_id for s in show_det]
            bsid_list=[bs.booking_show_id for bs in booking_det]
            b_sid_aid=[]
            for sid in sid_list:
                if sid in bsid_list:
                    b_sid_aid.append(sid)
            genre_revenue={}
            for sid in b_sid_aid:
                show_det=Shows.query.filter_by(show_id=sid).first()
                if show_det.show_tag not in genre_revenue:
                    genre_revenue[show_det.show_tag]=show_det.show_revenue
                else:
                    genre_revenue[show_det.show_tag]+=show_det.show_revenue
            if len(b_sid_aid)!=0:
                with app.app_context():
                    sns.barplot(x=list(genre_revenue.keys()), y=list(genre_revenue.values()))
                    plt.xlabel("Genre")
                    plt.ylabel("Revenue")
                    plt.title("Revenue by Genre")
                    plt.savefig(os.path.join(app.config['UPLOAD_PATH'], "revenue.jpg"))
            genre_revenue={}
            return render_template("summary.html", b_sid_aid=b_sid_aid)
        return redirect("/")


@app.route('/delete_all_venue', methods=['GET', 'POST'])
def delete():
    venue=Venue.query.all()
    show=Shows.query.all()
    book=Bookings.query.all()
    rate=Ratings.query.all()
    for i in venue:
        filename = os.path.join(app.config["UPLOAD_PATH"], i.venue_img)
        if os.path.exists(filename):
            os.remove(filename)
        db.session.delete(i)
        for s in show:
            filename = os.path.join(app.config["UPLOAD_PATH"], s.show_img)
            if os.path.exists(filename):
                os.remove(filename)
            db.session.delete(s)
        if len(book)>0:
            for b in book:
                db.session.delete(b)
        if len(rate)>0:
            for r in rate:
                db.session.delete(r)
        db.session.commit()
    return redirect('/admin_dashboard')
        








#Running the app

if __name__ == "__main__":
    app.debug = True
    app.run()








