from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Shift
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roster.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return redirect(url_for('roster'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('roster'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/roster')
@login_required
def roster():
    # Get month and year from request or default to current
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    view_type = request.args.get('view', 'weekly') # 'weekly' or 'monthly'
    
    if view_type == 'monthly':
        import calendar
        # Get number of days in month
        num_days = calendar.monthrange(year, month)[1]
        dates = [datetime(year, month, day).date() for day in range(1, num_days + 1)]
    else:
        # Weekly view (default)
        target_date = datetime.now().date()
        # If a specific month/year is requested but view is weekly, start from first of that month
        if 'month' in request.args or 'year' in request.args:
            target_date = datetime(year, month, 1).date()
            
        start_of_week = target_date - timedelta(days=target_date.weekday())
        dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    users = User.query.filter(User.role != 'Admin').all()
    shifts = Shift.query.filter(Shift.shift_date >= dates[0], Shift.shift_date <= dates[-1]).all()
    
    # Organize shifts into a dictionary for easy access: {user_id: {date: shift_type}}
    roster_data = {user.id: {date: None for date in dates} for user in users}
    for shift in shifts:
        if shift.user_id in roster_data and shift.shift_date in roster_data[shift.user_id]:
            roster_data[shift.user_id][shift.shift_date] = shift.shift_type
            
    return render_template('roster.html', dates=dates, users=users, roster_data=roster_data, 
                           current_month=month, current_year=year, view_type=view_type, datetime=datetime)


@app.route('/assign_shift', methods=['POST'])
@login_required
def assign_shift():
    if current_user.role != 'Admin':
        flash('Only admins can assign shifts')
        return redirect(url_for('roster'))
    
    user_id = request.form.get('user_id')
    date_str = request.form.get('date')
    shift_type = request.form.get('shift_type')
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    existing_shift = Shift.query.filter_by(user_id=user_id, shift_date=date_obj).first()
    if existing_shift:
        existing_shift.shift_type = shift_type
    else:
        new_shift = Shift(user_id=user_id, shift_date=date_obj, shift_type=shift_type)
        db.session.add(new_shift)
    
    db.session.commit()
    return redirect(url_for('roster'))

@app.route('/team')
@login_required
def team():
    if current_user.role != 'Admin':
        flash('Only admins can manage team')
        return redirect(url_for('roster'))
    users = User.query.all()
    return render_template('team.html', users=users)

@app.route('/add_member', methods=['POST'])
@login_required
def add_member():
    if current_user.role != 'Admin':
        flash('Only admins can add members')
        return redirect(url_for('team'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'Member')
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists')
    else:
        new_user = User(username=username, password_hash=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Member added successfully')
    
    return redirect(url_for('team'))

@app.route('/edit_member/<int:user_id>', methods=['POST'])

@login_required
def edit_member(user_id):
    if current_user.role != 'Admin':
        flash('Only admins can edit members')
        return redirect(url_for('team'))
    
    user = User.query.get_or_404(user_id)
    user.username = request.form.get('username')
    user.role = request.form.get('role')
    password = request.form.get('password')
    if password:
        user.password_hash = generate_password_hash(password)
    
    db.session.commit()
    flash('Member updated successfully')
    return redirect(url_for('team'))

@app.route('/delete_member/<int:user_id>', methods=['POST'])
@login_required
def delete_member(user_id):
    if current_user.role != 'Admin':
        flash('Only admins can delete members')
        return redirect(url_for('team'))
    
    if user_id == current_user.id:
        flash('You cannot delete yourself')
        return redirect(url_for('team'))
        
    user = User.query.get_or_404(user_id)
    # Delete associated shifts first
    Shift.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('Member and their shifts deleted successfully')
    return redirect(url_for('team'))


def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='Admin')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
