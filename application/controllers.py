from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from application.database import db
from application.models import User, Admin, ParkingLot, ParkingSpot, Booking
from application.utils import validate_username, validate_password, validate_email
from flask import current_app as app

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
    
# @app.route('/toggle_spot/<int:spot_id>', methods=['POST'])
# def toggle_spot(spot_id):
#     spot = ParkingSpot.query.get_or_404(spot_id)
#     spot.status = 'O' if spot.status == 'A' else 'A'
#     db.session.commit()
#     return redirect(url_for('admin_dashboard'))

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