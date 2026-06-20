from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.user import User, Role
from models.patient import Patient
from models.appointment import Appointment
from models.communication import AuditLog, SystemSetting, Notification
from datetime import datetime, date

superadmin = Blueprint('superadmin', __name__)


def superadmin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() != 'superadmin':
            flash('Access denied. Super Admin only.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@superadmin.route('/')
@login_required
@superadmin_required
def index():
    # System stats
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_patients = Patient.query.filter_by(deleted_at=None).count()
    total_appointments = Appointment.query.count()

    # Security stats
    failed_logins = AuditLog.query.filter_by(
        action='LOGIN_FAILED'
    ).count()
    recent_logs = AuditLog.query.order_by(
        AuditLog.timestamp.desc()
    ).limit(20).all()

    # System alerts
    unread_notifications = Notification.query.filter_by(
        is_read=False,
        type='danger'
    ).count()

    return render_template('admin/superadmin.html',
                           total_users=total_users,
                           active_users=active_users,
                           total_patients=total_patients,
                           total_appointments=total_appointments,
                           failed_logins=failed_logins,
                           recent_logs=recent_logs,
                           unread_notifications=unread_notifications)


@superadmin.route('/users')
@login_required
@superadmin_required
def users():
    all_users = User.query.order_by(
        User.created_at.desc()
    ).all()
    return render_template('admin/users.html', users=all_users)


@superadmin.route('/users/new', methods=['GET', 'POST'])
@login_required
@superadmin_required
def new_user():
    if request.method == 'POST':
        existing = User.query.filter_by(
            email=request.form.get('email')
        ).first()
        if existing:
            flash('Email already exists!', 'danger')
            return redirect(url_for('superadmin.new_user'))

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
        flash(f'User {user.full_name} created!', 'success')
        return redirect(url_for('superadmin.users'))

    roles = Role.query.all()
    return render_template('admin/new_user.html', roles=roles)


@superadmin.route('/roles')
@login_required
@superadmin_required
def roles():
    all_roles = Role.query.all()
    return render_template('admin/roles.html', roles=all_roles)


@superadmin.route('/roles/new', methods=['GET', 'POST'])
@login_required
@superadmin_required
def new_role():
    if request.method == 'POST':
        role = Role(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(role)
        db.session.commit()
        flash('Role created!', 'success')
        return redirect(url_for('superadmin.roles'))
    return render_template('admin/new_role.html')


@superadmin.route('/audit-logs')
@login_required
@superadmin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(
        AuditLog.timestamp.desc()
    ).paginate(page=page, per_page=50)
    return render_template('admin/audit_logs.html', logs=logs)


@superadmin.route('/settings')
@login_required
@superadmin_required
def settings():
    all_settings = SystemSetting.query.all()
    return render_template('admin/settings.html', settings=all_settings)


@superadmin.route('/settings/update', methods=['POST'])
@login_required
@superadmin_required
def update_setting():
    key = request.form.get('key')
    value = request.form.get('value')
    setting = SystemSetting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        setting.updated_by = current_user.id
    else:
        setting = SystemSetting(
            key=key,
            value=value,
            updated_by=current_user.id
        )
        db.session.add(setting)
    db.session.commit()
    flash('Setting updated!', 'success')
    return redirect(url_for('superadmin.settings'))


@superadmin.route('/security')
@login_required
@superadmin_required
def security():
    failed_logins = AuditLog.query.filter_by(
        action='LOGIN_FAILED'
    ).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return render_template('admin/security.html',
                           failed_logins=failed_logins)


@superadmin.route('/users/<int:id>/toggle', methods=['POST'])
@login_required
@superadmin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.full_name} {status}!', 'success')
    return redirect(url_for('superadmin.users'))