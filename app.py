from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime, date
import werkzeug
import os
import random
import string
import io
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'visitor_pass_secret_key_2024'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'visitor_pass.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── MODELS ───────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone         = db.Column(db.String(20))
    role          = db.Column(db.String(20), default='visitor')   # visitor | admin
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    bookings      = db.relationship('Booking', backref='user', lazy=True)

class Package(db.Model):
    __tablename__ = 'packages'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float, nullable=False)
    duration    = db.Column(db.String(50))          # e.g. "1 Day", "3 Days"
    max_visitors= db.Column(db.Integer, default=1)
    features    = db.Column(db.Text)                # comma-separated
    is_active   = db.Column(db.Boolean, default=True)
    bookings    = db.relationship('Booking', backref='package', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id           = db.Column(db.Integer, primary_key=True)
    pass_code    = db.Column(db.String(12), unique=True, nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    package_id   = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    visit_date   = db.Column(db.Date, nullable=False)
    num_visitors = db.Column(db.Integer, default=1)
    purpose      = db.Column(db.String(200))
    host_name    = db.Column(db.String(100))
    status       = db.Column(db.String(20), default='pending')  # pending|approved|rejected|expired
    total_amount = db.Column(db.Float)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contacts'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), nullable=False)
    subject    = db.Column(db.String(200))
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read    = db.Column(db.Boolean, default=False)

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def generate_pass_code():
    return 'VP-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def seed_packages():
    if Package.query.count() == 0:
        packages = [
            Package(name='Day Pass',        price=299,  duration='1 Day',   max_visitors=1,
                    description='Perfect for single-day visits. Full access to all common areas.',
                    features='Single Entry,Common Areas,Cafeteria Access,WiFi,Locker'),
            Package(name='Family Pass',     price=799,  duration='1 Day',   max_visitors=4,
                    description='Ideal for families. Covers up to 4 visitors on the same day.',
                    features='4 Visitors,All Areas,Guided Tour,Cafeteria,Parking,WiFi'),
            Package(name='Corporate Pass',  price=1499, duration='3 Days',  max_visitors=10,
                    description='3-day corporate access for teams and delegations.',
                    features='10 Visitors,Conference Room,Dedicated Host,Parking,Meals,WiFi'),
            Package(name='VIP Annual Pass', price=4999, duration='365 Days',max_visitors=2,
                    description='Unlimited annual access with VIP perks and priority service.',
                    features='Unlimited Entry,VIP Lounge,Priority Lane,Concierge,Parking,Meals'),
        ]
        db.session.bulk_save_objects(packages)
        db.session.commit()

def seed_admin():
    if User.query.filter_by(role='admin').count() == 0:
        admin = User(
            name='Admin',
            email='admin@visitorpass.com',
            password_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stats = {
        'total_visitors': User.query.filter_by(role='visitor').count(),
        'total_bookings': Booking.query.count(),
        'approved_passes': Booking.query.filter_by(status='approved').count(),
        'packages_count': Package.query.filter_by(is_active=True).count(),
    }
    return render_template('index.html', stats=stats)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/packages')
def packages():
    pkgs = Package.query.filter_by(is_active=True).all()
    return render_template('packages.html', packages=pkgs)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        c = Contact(
            name=request.form['name'],
            email=request.form['email'],
            subject=request.form.get('subject', ''),
            message=request.form['message']
        )
        db.session.add(c)
        db.session.commit()
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user     = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id']   = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard') if user.role == 'visitor' else url_for('admin_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']
        phone    = request.form.get('phone', '')
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        user = User(name=name, email=email,
                    password_hash=generate_password_hash(password, method='pbkdf2:sha256'), phone=phone)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ── Visitor Dashboard ─────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user     = User.query.get(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    return render_template('dashboard.html', user=user, bookings=bookings)

# ── Booking ───────────────────────────────────────────────────────────────────

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user_id' not in session:
        flash('Please login to book a pass.', 'warning')
        return redirect(url_for('login'))
    pkgs = Package.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        pkg        = Package.query.get(int(request.form['package_id']))
        num        = int(request.form.get('num_visitors', 1))
        visit_date = datetime.strptime(request.form['visit_date'], '%Y-%m-%d').date()
        pass_code  = generate_pass_code()
        while Booking.query.filter_by(pass_code=pass_code).first():
            pass_code = generate_pass_code()
        b = Booking(
            pass_code    = pass_code,
            user_id      = session['user_id'],
            package_id   = pkg.id,
            visit_date   = visit_date,
            num_visitors = num,
            purpose      = request.form.get('purpose', ''),
            host_name    = request.form.get('host_name', ''),
            total_amount = pkg.price * num,
            status       = 'pending'
        )
        db.session.add(b)
        db.session.commit()
        flash(f'Booking submitted! Your Pass Code: <strong>{pass_code}</strong>', 'success')
        return redirect(url_for('dashboard'))
    preselect = request.args.get('pkg')
    return render_template('booking.html', packages=pkgs, preselect=preselect)

# ── Admin Dashboard ───────────────────────────────────────────────────────────

@app.route('/admin')
def admin_dashboard():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    stats = {
        'users':    User.query.filter_by(role='visitor').count(),
        'bookings': Booking.query.count(),
        'pending':  Booking.query.filter_by(status='pending').count(),
        'approved': Booking.query.filter_by(status='approved').count(),
        'revenue':  db.session.query(db.func.sum(Booking.total_amount)).scalar() or 0,
    }
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(20).all()
    messages = Contact.query.order_by(Contact.created_at.desc()).limit(10).all()
    return render_template('admin.html', stats=stats, bookings=bookings, messages=messages)

@app.route('/admin/booking/<int:bid>/status', methods=['POST'])
def update_booking_status(bid):
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    b        = Booking.query.get_or_404(bid)
    b.status = request.form['status']
    db.session.commit()
    flash('Booking status updated.', 'success')
    return redirect(url_for('admin_dashboard'))

# ── Download Pass PDF ─────────────────────────────────────────────────────────

@app.route('/download-pass/<int:bid>')
def download_pass(bid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    b = Booking.query.get_or_404(bid)
    # Only the owner can download, and only approved passes
    if b.user_id != session['user_id'] or b.status != 'approved':
        flash('Pass is not available for download.', 'warning')
        return redirect(url_for('dashboard'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Header background
    pdf.set_fill_color(10, 12, 16)
    pdf.rect(0, 0, 210, 60, 'F')
    pdf.set_fill_color(0, 229, 195)
    pdf.rect(0, 58, 210, 3, 'F')

    # ── Title
    pdf.set_text_color(0, 229, 195)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_xy(0, 12)
    pdf.cell(210, 12, 'VISITOR PASS', align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(180, 180, 200)
    pdf.set_xy(0, 26)
    pdf.cell(210, 8, 'GreenLand Digital Pass System', align='C')

    # ── Pass Code
    pdf.set_xy(0, 38)
    pdf.set_font('Courier', 'B', 18)
    pdf.set_text_color(255, 181, 71)
    pdf.cell(210, 12, b.pass_code, align='C')

    # ── Status badge
    pdf.set_xy(75, 68)
    pdf.set_fill_color(35, 196, 94)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(60, 10, 'APPROVED', align='C', fill=True)

    # ── Details section
    y = 90
    pdf.set_draw_color(50, 55, 75)

    details = [
        ('Visitor Name', b.user.name),
        ('Email', b.user.email),
        ('Package', b.package.name),
        ('Visit Date', b.visit_date.strftime('%d %B %Y')),
        ('Number of Visitors', str(b.num_visitors)),
        ('Purpose', b.purpose or 'General Visit'),
        ('Host', b.host_name or 'Reception'),
        ('Total Amount', f'Rs. {int(b.total_amount)}'),
        ('Booking Date', b.created_at.strftime('%d %B %Y, %I:%M %p')),
    ]

    for label, value in details:
        pdf.set_xy(20, y)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(120, 120, 140)
        pdf.cell(60, 8, label)
        pdf.set_xy(82, y)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(40, 40, 50)
        pdf.cell(110, 8, value)
        y += 12
        pdf.set_draw_color(230, 230, 235)
        pdf.line(20, y - 3, 190, y - 3)

    # ── Footer note
    y += 10
    pdf.set_xy(20, y)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(150, 150, 160)
    pdf.multi_cell(170, 5, 'This is a digitally generated visitor pass. Please present this pass at the entrance gate. '
                            'This pass is valid only for the date and number of visitors mentioned above.')

    # ── Bottom bar
    pdf.set_fill_color(10, 12, 16)
    pdf.rect(0, 280, 210, 17, 'F')
    pdf.set_xy(0, 283)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 120)
    pdf.cell(210, 6, 'GreenLand Visitor Pass System  |  www.visitorpass.in  |  +91 98765 43210', align='C')

    # ── Output
    pdf_bytes = pdf.output()
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=VisitorPass_{b.pass_code}.pdf'
    return response

# ── API: pass check ───────────────────────────────────────────────────────────

@app.route('/api/verify-pass', methods=['POST'])
def verify_pass():
    code = request.json.get('pass_code', '').strip().upper()
    b    = Booking.query.filter_by(pass_code=code).first()
    if not b:
        return jsonify({'valid': False, 'message': 'Pass not found.'})
    return jsonify({
        'valid':       True,
        'status':      b.status,
        'visitor':     b.user.name,
        'package':     b.package.name,
        'visit_date':  b.visit_date.strftime('%d %b %Y'),
        'pass_code':   b.pass_code,
    })

# ─── MAIN ─────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    seed_packages()
    seed_admin()

if __name__ == '__main__':
    app.run(debug=True)