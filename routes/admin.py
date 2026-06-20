from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.user import User, Role
from models.patient import Patient
from models.appointment import Appointment, Department, Specialty
from models.communication import AuditLog, Notification
from datetime import datetime, date

admin = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/')
@login_required
@admin_required
def index():
    today = date.today()
    total_patients = Patient.query.filter_by(deleted_at=None).count()
    total_staff = User.query.filter_by(is_active=True).count()
    todays_appointments = Appointment.query.filter(
        db.func.date(Appointment.scheduled_at) == today
    ).count()
    new_patients_today = Patient.query.filter(
        db.func.date(Patient.created_at) == today
    ).count()

    # Appointments by status
    pending = Appointment.query.filter_by(status='pending').count()
    confirmed = Appointment.query.filter_by(status='confirmed').count()
    completed = Appointment.query.filter_by(status='completed').count()
    cancelled = Appointment.query.filter_by(status='cancelled').count()

    # Recent activity
    recent_logs = AuditLog.query.order_by(
        AuditLog.timestamp.desc()
    ).limit(10).all()

    return render_template('admin/index.html',
                           total_patients=total_patients,
                           total_staff=total_staff,
                           todays_appointments=todays_appointments,
                           new_patients_today=new_patients_today,
                           pending=pending,
                           confirmed=confirmed,
                           completed=completed,
                           cancelled=cancelled,
                           recent_logs=recent_logs)


@admin.route('/staff')
@login_required
@admin_required
def staff():
    users = User.query.filter_by(
        is_active=True
    ).order_by(User.created_at.desc()).all()
    return render_template('admin/staff.html', users=users)


@admin.route('/staff/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_staff():
    if request.method == 'POST':
        # Check if email exists
        existing = User.query.filter_by(
            email=request.form.get('email')
        ).first()
        if existing:
            flash('Email already exists!', 'danger')
            return redirect(url_for('admin.new_staff'))

        user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            full_name=request.form.get('full_name'),
            phone=request.form.get('phone'),
            role_id=request.form.get('role_id')
        )
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        flash(f'Staff member {user.full_name} created!', 'success')
        return redirect(url_for('admin.staff'))

    roles = Role.query.all()
    return render_template('admin/new_staff.html', roles=roles)


@admin.route('/staff/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_staff(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.role_id = request.form.get('role_id')
        user.is_active = request.form.get('is_active') == 'on'
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        db.session.commit()
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('admin.staff'))

    roles = Role.query.all()
    return render_template('admin/edit_staff.html',
                           user=user, roles=roles)


@admin.route('/staff/<int:id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_staff(id):
    user = User.query.get_or_404(id)
    user.is_active = False
    db.session.commit()
    flash(f'{user.full_name} deactivated!', 'warning')
    return redirect(url_for('admin.staff'))


@admin.route('/departments')
@login_required
@admin_required
def departments():
    departments = Department.query.all()
    return render_template('admin/departments.html',
                           departments=departments)


@admin.route('/departments/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_department():
    if request.method == 'POST':
        dept = Department(
            name=request.form.get('name'),
            description=request.form.get('description'),
            location=request.form.get('location'),
            phone=request.form.get('phone')
        )
        db.session.add(dept)
        db.session.commit()
        flash('Department created!', 'success')
        return redirect(url_for('admin.departments'))
    return render_template('admin/new_department.html')


@admin.route('/reports')
@login_required
@admin_required
def reports():
    today = date.today()
    total_patients = Patient.query.filter_by(deleted_at=None).count()
    total_appointments = Appointment.query.count()
    completed_appointments = Appointment.query.filter_by(
        status='completed'
    ).count()
    return render_template('admin/reports.html',
                           total_patients=total_patients,
                           total_appointments=total_appointments,
                           completed_appointments=completed_appointments)