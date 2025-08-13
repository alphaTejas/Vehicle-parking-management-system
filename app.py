from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask import flash
import os, re
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(current_dir, 'database_project.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db= SQLAlchemy()
# Initialize the database with the Flask app
db.init_app(app)
app.app_context().push()
#create the database tables if they don't exist
if not os.path.exists(os.path.join(current_dir, 'database_project.sqlite3')):
    db.create_all()

# Flask application setup
app.secret_key = '24F2003755'  # Needed for session management

# In-memory storage for demonstration


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    full_name = db.Column(db.String(120))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    location_name = db.Column(db.String(255))
    vehicle_number = db.Column(db.String(20))

class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    ad_username = db.Column(db.String(80), unique=True, nullable=False)
    ad_password_hash = db.Column(db.String(128), nullable=False)
    ad_email = db.Column(db.String(120), unique=True, nullable=False)
    ad_full_name = db.Column(db.String(120))
    all_lots = db.relationship('ParkingLot', backref='admin', lazy=True)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    name= db.Column(db.String(120), nullable=False)  # Added name field
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    pin_code = db.Column(db.String(10), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    #some many to one
    occupied_spots = db.Column(db.Integer, default=0, nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # 'A' for available, 'O' for occupied
    spot_number = db.Column(db.String(20))

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost_per_unit = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vehicle_number = db.Column(db.String(20), nullable=False)  # <-- Add this line

    spot = db.relationship('ParkingSpot', backref='bookings')
    user = db.relationship('User', backref='bookings')


def validate_username(username):
    if not username or len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

def validate_password(password):
    if not password or len(password) < 6 or len(password) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9@#$%^&+=]+$', password):
        return False
    return True

def validate_email(email):
    if not email or len(email) > 120:
        return False
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return False
    return True 


# Flask application routes
#---------------------------homepage---------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'admin':
            return redirect(url_for('admin_login'))
        elif user_type == 'user':
            return redirect(url_for('user_login'))
        # Handle unexpected or missing user_type
        # Option 1: Re-render the page with an error message
        return render_template('index.html', error="Please select a valid user type.")

#---------------------------user login---------------------------------------------------------------
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    elif request.method == 'POST':
        uname = request.form['username']
        pssd = request.form['passwrd']
        # Validate username and password format
        if not validate_username(uname):
            flash("Invalid username", "uname_error")
            return render_template("user_login.html", username=uname)
        query_user = User.query.filter_by(username=uname).all()

        if len(query_user) == 0:
            flash("Username does not exist", "uname_error")
            return redirect(url_for('user_login'))
        
        if len(query_user) > 0:
            db_username = User.query.filter_by(username=uname).first()
            session['username'] = db_username.username
            session['is_admin'] = False # Set admin status to False for regular users
            pssd_hash = db_username.password_hash
            if validate_password(pssd):
                if pssd != pssd_hash:
                    flash("Wrong Password", "error")
                    return render_template("user_login.html")
            if pssd == pssd_hash:
                    return redirect(url_for('user_dashboard')) 
            flash("Wrong password!", "error")
            return render_template("user_login.html")
        # if 3<len(query_user)<20:
        #     db_username = User.query.filter_by(username=uname).first()
        #     session['username'] = db_username.username
        #     session['is_admin'] = False  # Set admin status to False for regular users
        #     pssd_hash = db_username.password_hash
        #     if validate_password(pssd):
        #         if pssd == pssd_hash:
        #             return redirect(url_for('admin_dashboard'))
        #         else:
        #             flash("Invalid password", "pswd_error")
        #             return render_template("user_login.html", username=uname)
                
                
# --------------------new user registration--------------------------------------------------------
@app.route('/register_user', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('user_register.html')
    elif request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        phone = request.form['phone']
        address = request.form.get('location_name')
        vehicle_number = request.form['vehicle_number']
        # Validate username, password, and email format
        if not validate_email(email):
            flash("Invalid email format", "email_error")
            return redirect(url_for('register'))
        usr_username=request.form['username']
        if not validate_username(usr_username):
            flash("Length of username should be in betwwen 3 to 20 alphanumeric characters", "uname_error")
            return redirect(url_for('register'))
        usr_password=request.form['password']
        if not validate_password(usr_password):
            flash("Length of password should be in betwwen 6 to 20 alphanumeric characters", "pswd_error")
            return redirect(url_for('register'))
        # Check if the username or email already exists
        existing_user = User.query.filter((User.username == usr_username) | (User.email == email)).all()
        if existing_user:
            flash("Username or email already exists", "user_exists_error")
            return redirect(url_for('register'))
        # Create a new user instance
        new_user = User(
            username=usr_username,
            password_hash=usr_password,  # In a real application, hash the password
            email=email,
            full_name=full_name,
            phone=phone,
            location_name=address,
            vehicle_number=vehicle_number
        )
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('user_login')) 

#------user logout--------------------(to be called later remember)-------------------------------------------------
@app.route('/user_logout')
def user_logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('index'))   

#--------------------admin login--------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    elif request.method == 'POST':
        ad_username = request.form['adusername'] #this ad_username is different from the one which is defined in class Admin
        ad_password = request.form['adpassword']
        # Validate admin username and password format
        if not validate_username(ad_username):
            flash("Invalid admin username", "uname_error")
            return render_template("admin_login.html", ad_username=ad_username)
        query_admin = Admin.query.filter_by(ad_username=ad_username).all()
        if len(query_admin) == 0:
            flash("Admin username does not exist", "uname_error")
            return redirect(url_for('admin_login'))
        if len(query_admin) > 0:
            db_ad_username = Admin.query.filter_by(ad_username=ad_username).first()
            session['ad_username'] = db_ad_username.ad_username
            session['is_admin'] = True  # Set admin status to True for admin users
            ad_password_hash = db_ad_username.ad_password_hash
            if validate_password(ad_password):
                if ad_password != ad_password_hash:
                    flash("Wrong Admin Password", "error")
                    return render_template("admin_login.html")
            if ad_password == ad_password_hash:
                return redirect(url_for('admin_dashboard'))
            flash("Wrong admin password!", "error")
            return render_template("admin_login.html")

# -------------admin registration-----------
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'GET':
        return render_template('register_admin.html')
    elif request.method == 'POST':
        ad_email = request.form['ad_email']
        ad_full_name = request.form['ad_full_name']
        # Validate admin username, password, and email format
        ad_username = request.form['ad_username']
        if not validate_username(ad_username):
            flash("Invalid admin username format", "uname_error")
            return redirect(url_for('register_admin'))
        ad_password = request.form['ad_password']
        if not validate_password(ad_password):
            flash("Invalid admin password format", "pswd_error")
            return redirect(url_for('register_admin'))
        if not validate_email(ad_email):
            flash("Invalid admin email format", "email_error")
            return redirect(url_for('register_admin'))
        # Check if the admin username or email already exists
        existing_admin = Admin.query.filter((Admin.ad_username == ad_username) | (Admin.ad_email == ad_email)).all()
        if existing_admin:
            flash("Admin username or email already exists", "admin_exists_error")
            return redirect(url_for('register_admin'))
        # Create a new admin instance
        new_admin = Admin(
            ad_username=ad_username,
            ad_password_hash=ad_password,  # In a real application, hash the password
            ad_email=ad_email,
            ad_full_name=ad_full_name
        )
        # Add the new admin to the database
        db.session.add(new_admin)
        db.session.commit()
        flash("Admin registration successful! You can now log in.", "success")
        return redirect(url_for('admin_login'))

# -------------------------------------my second Half -------------------------------------------------------------------
# ----------------admin_dashboard--------------------


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'is_admin' in session and session.get('is_admin'):
        admin_username = session.get('ad_username')
        admin = Admin.query.filter_by(ad_username=admin_username).first()
        if admin:
            lots = ParkingLot.query.filter_by(admin_id=admin.id).all()
            return render_template('admin_dashboard.html', parking_lots=lots, ad_username=admin_username)
        else:
            flash("Admin not found.", "error")
            return redirect(url_for('admin_login'))
    else:
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect(url_for('admin_login'))

#------------------addlot dashboard--------------------
@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if request.method == 'GET':
        return render_template('add_lot.html')
    
    elif request.method == 'POST':
        # Safely fetch form data
        name = request.form.get('adname')
        prime_location_name = request.form.get('prime_location_name')
        price = request.form.get('price')

        pin_code = request.form.get('pincode')
        max_spots = request.form.get('max_spots')
        
        

        # Validate required fields
        

        # Get admin_id from session
        admin_username = session.get('ad_username')
        admin = Admin.query.filter_by(ad_username=admin_username).first()
        admin_id = admin.id if admin else None

        # Create new parking lot
        new_lot = ParkingLot(
            name=name,
            prime_location_name=prime_location_name,
            price=price,

            pin_code=pin_code,
            maximum_number_of_spots=max_spots,
            occupied_spots=0,
            admin_id=admin_id
        )
        db.session.add(new_lot)
        db.session.flush()  # Get new_lot.id before commit

        # Add parking spots linked to the new lot
        for i in range(1, int(max_spots) + 1):
            spot = ParkingSpot(
                lot_id=new_lot.id,
                status='A',  # Default to available
                spot_number=str(i)
            )
            db.session.add(spot)

        db.session.commit()

        flash("Parking lot added successfully!", "success")
        return redirect(url_for('admin_dashboard', lot_id=new_lot.id))


#------------------addlot dashboard--------------------
@app.route('/admin_dashboard/<int:lot_id>', methods=['GET','POST'])
def admin_dashboard_lot(lot_id):
    if request.method=='GET':
        return render_template('admin_dashboard.html')
    
#------------toggle spot status--------------------------------------
    
@app.route('/toggle_spot/<int:spot_id>', methods=['POST'])
def toggle_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    spot.status = 'O' if spot.status == 'A' else 'A'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

#--------------edit lot------------------------------------
@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form.get('prime_location_name')

        lot.pin_code = request.form.get('pin_code')
        lot.price = request.form.get('price')
        new_max_spots = int(request.form.get('maximum_number_of_spots'))
        old_max_spots = lot.maximum_number_of_spots
        lot.maximum_number_of_spots = new_max_spots

        db.session.commit()  # Commit lot changes first

        # Synchronize ParkingSpot records
        current_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        current_count = len(current_spots)

        if new_max_spots > current_count:
            # Add new spots
            for i in range(current_count + 1, new_max_spots + 1):
                new_spot = ParkingSpot(
                    lot_id=lot.id,
                    status='A',
                    spot_number=str(i)
                )
                db.session.add(new_spot)
        elif new_max_spots < current_count:
            # Remove extra spots
            spots_to_remove = ParkingSpot.query.filter(
                ParkingSpot.lot_id == lot.id,
                ParkingSpot.spot_number.in_([str(i) for i in range(new_max_spots + 1, current_count + 1)])
            ).all()
            for spot in spots_to_remove:
                db.session.delete(spot)

        db.session.commit()  # Commit spot changes

        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_lot.html', lot=lot)


#-------------user dashboard-----------------------
@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    lots = None
    searchType = ''
    searchValue = ''
    user = User.query.filter_by(username=session.get('username')).first()
    bookings = []
    if user:
        bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.parking_timestamp.desc()).all()
    if request.method == 'POST':
        searchType = request.form.get('searchType')
        searchValue = request.form.get('searchValue', '').strip()
        if searchType == 'pincode' and searchValue:
            lots = ParkingLot.query.filter_by(pin_code=searchValue).all()
        elif searchType == 'location' and searchValue:
            lots = ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{searchValue}%")).all()
        else:
            lots = []
    return render_template('user_dashboard.html', lots=lots, searchType=searchType, searchValue=searchValue, bookings=bookings)
    
#-----------------book lot--------------------------
@app.route('/book_spot/<int:spot_id>/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(spot_id, lot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    lot = ParkingLot.query.get_or_404(lot_id)
    user = User.query.filter_by(username=session.get('username')).first()
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        spot.status = 'O'
        booking = Booking(
            spot_id=spot.id,
            user_id=user.id,
            parking_timestamp=datetime.utcnow(),
            parking_cost_per_unit=lot.price,
            vehicle_number=vehicle_number,  # If you want to store it, add this column to your Booking model
            total_cost=None  # Will be calculated on release
        )
        db.session.add(booking)
        db.session.commit()
        flash("Spot reserved successfully!", "success")
        return redirect(url_for('user_dashboard'))
    return render_template('book_spot.html', spot=spot, lot=lot, user=user)
    
#---------------------release spot--------------------------
from datetime import datetime

@app.route('/release_spot/<int:booking_id>', methods=['GET', 'POST'])
def release_spot(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    spot = ParkingSpot.query.get_or_404(booking.spot_id)
    estimated_cost = None
    if not booking.leaving_timestamp:
        # Estimate cost using current time
        now = datetime.utcnow()
        duration_hours = (now - booking.parking_timestamp).total_seconds() / 3600
        duration_hours = max(duration_hours, 1)  # Minimum 1 hour charge
        estimated_cost = round(duration_hours * booking.parking_cost_per_unit, 2)
    if request.method == 'POST':
        booking.leaving_timestamp = datetime.utcnow()
        spot.status = 'A'
        duration_hours = (booking.leaving_timestamp - booking.parking_timestamp).total_seconds() / 3600
        duration_hours = max(duration_hours, 1)
        booking.total_cost = round(duration_hours * booking.parking_cost_per_unit, 2)
        db.session.commit()
        flash(f"Spot released successfully! Total cost: {booking.total_cost}", "success")
        return redirect(url_for('user_dashboard'))
    return render_template('release_spot.html', booking=booking, spot=spot, estimated_cost=estimated_cost, datetime=datetime)
    
#---------------------delete spot--------------------------
@app.route('/delete_spot/<int:spot_id>', methods=['POST'])
def delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    # Only allow delete if spot is available
    if spot.status == 'A':
        db.session.delete(spot)
        db.session.commit()
        flash("Spot deleted successfully!", "success")
    else:
        flash("Cannot delete an occupied spot.", "danger")
    return redirect(request.referrer or url_for('admin_dashboard')) 

#---------------------delete lot--------------------------
@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    # Check if any spot in the lot is occupied
    occupied_spots = [spot for spot in lot.spots if spot.status == 'O']
    if occupied_spots:
        flash("Cannot delete lot: Some spots are occupied.", "danger")
        return redirect(url_for('admin_dashboard'))
    # Delete all spots first (if cascade is not set)
    for spot in lot.spots:
        db.session.delete(spot)
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

#---------------------users in admin dashboard--------------------------
@app.route('/admin/users')
def admin_users():
    if 'is_admin' in session and session.get('is_admin'):
        admin_username = session.get('ad_username')
        admin = Admin.query.filter_by(ad_username=admin_username).first()
        if not admin:
            flash("Admin not found.", "error")
            return redirect(url_for('admin_login'))

        # Getting all lot ids owned by this admin
        lot_ids = [lot.id for lot in ParkingLot.query.filter_by(admin_id=admin.id).all()]

        # Getting all bookings for these lots
        spot_ids = [spot.id for spot in ParkingSpot.query.filter(ParkingSpot.lot_id.in_(lot_ids)).all()]
        bookings = Booking.query.filter(Booking.spot_id.in_(spot_ids)).all()

        # Getting unique user ids from these bookings
        user_ids = set(booking.user_id for booking in bookings)
        users = User.query.filter(User.id.in_(user_ids)).all()

        return render_template('admin_users.html', users=users, active_tab='users')
    else:
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect(url_for('admin_login'))

#---------------------registerd users for admin dashboard--------------------------
@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    lots = []
    searchType = ''
    searchValue = ''
    if 'is_admin' in session and session.get('is_admin'):
        admin_username = session.get('ad_username')
        admin = Admin.query.filter_by(ad_username=admin_username).first()
        if not admin:
            flash("Admin not found.", "error")
            return redirect(url_for('admin_login'))
        if request.method == 'POST':
            searchType = request.form.get('searchType')
            searchValue = request.form.get('searchValue', '').strip()
            if searchType == 'user_id' and searchValue:
                user = User.query.filter_by(id=searchValue).first()
                if user:
                    booking_spot_ids = [b.spot_id for b in user.bookings]
                    lots = ParkingLot.query.join(ParkingSpot).filter(
                        ParkingSpot.id.in_(booking_spot_ids),
                        ParkingLot.admin_id == admin.id
                    ).distinct().all()
            elif searchType == 'location' and searchValue:
                lots = ParkingLot.query.filter(
                    ParkingLot.prime_location_name.ilike(f"%{searchValue}%"),
                    ParkingLot.admin_id == admin.id
                ).all()
            elif searchType == 'spot_id' and searchValue:
                spot = ParkingSpot.query.filter_by(id=searchValue).first()
                lots = [spot.lot] if spot and spot.lot.admin_id == admin.id else []
        return render_template('admin_search.html', lots=lots, searchType=searchType, searchValue=searchValue, active_tab='search')
    else:
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect(url_for('admin_login'))
    
#---------------------edit profile of admin--------------------------
@app.route('/edit_admin_profile', methods=['GET', 'POST'])
def edit_admin_profile():
    if 'is_admin' in session and session.get('is_admin'):
        admin_username = session.get('ad_username')
        admin = Admin.query.filter_by(ad_username=admin_username).first()
        if not admin:
            flash("Admin not found.", "error")
            return redirect(url_for('admin_login'))
        if request.method == 'POST':
            admin.ad_full_name = request.form.get('ad_full_name')
            admin.ad_email = request.form.get('ad_email')
            # Optionally allow password change
            new_password = request.form.get('ad_password')
            if new_password and validate_password(new_password):
                admin.ad_password_hash = new_password
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_admin_profile.html', admin=admin)
    else:
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect(url_for('admin_login'))

# #---------------------user summary--------------------------
# import io
# import base64
# import matplotlib.pyplot as plt

# @app.route('/user/summary')
# def user_summary():
#     if 'username' not in session:
#         flash("Please login first.", "unauthorised")
#         return redirect(url_for('user_login'))
#     user = User.query.filter_by(username=session['username']).first()
#     bookings = Booking.query.filter_by(user_id=user.id).all()
#     # Count usage per parking lot
#     lot_usage = {}
#     for booking in bookings:
#         lot_name = booking.spot.lot.name
#         lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1

#     # Prepare data for chart
#     labels = list(lot_usage.keys())
#     values = list(lot_usage.values())

#     # Generate matplotlib bar chart
#     fig, ax = plt.subplots(figsize=(5, 3))
#     ax.bar(labels, values, color=['#7ed6df', '#70a1ff', '#ff7979', '#badc58', '#f9ca24'])
#     ax.set_ylabel('Number of times used')
#     ax.set_title('Summary on already used parking spots')
#     plt.tight_layout()

#     # Convert plot to PNG image and encode as base64
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     chart_url = base64.b64encode(img.getvalue()).decode()
#     plt.close(fig)

#     return render_template('user_summary.html', chart_url=chart_url, user=user)

#---------------------logout--------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)



