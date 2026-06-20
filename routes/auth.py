from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

auth = Blueprint('auth', __name__)


def log_action(action, description='', status='success'):
    try:
        from extensions import db
        from models.communication import AuditLog
        log = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status=status
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass


@auth.route('/login', methods=['GET', 'POST'])
def login():
    from models.user import User

    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is deactivated. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)
            from extensions import db
            user.last_login = datetime.utcnow()
            db.session.commit()

            log_action('LOGIN', f'User {user.email} logged in')
            flash(f'Welcome back, {user.full_name}!', 'success')

            return redirect(url_for('auth.dashboard'))
        else:
            log_action('LOGIN_FAILED', f'Failed login for {email}', 'failed')
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    log_action('LOGOUT', f'User {current_user.email} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/dashboard')
@login_required
def dashboard():
    role = current_user.role.name.lower()

    if role == 'superadmin':
        return redirect(url_for('superadmin.index'))
    elif role == 'admin':
        return redirect(url_for('admin.index'))
    elif role == 'doctor':
        return redirect(url_for('doctor.index'))
    elif role == 'nurse':
        return redirect(url_for('nursing.index'))
    elif role == 'lab_tech':
        return redirect(url_for('laboratory.index'))
    elif role == 'radiologist':
        return redirect(url_for('radiology.index'))
    elif role == 'pharmacist':
        return redirect(url_for('pharmacy.index'))
    elif role == 'dentist':
        return redirect(url_for('dental.index'))
    elif role == 'therapist':
        return redirect(url_for('rehabilitation.index'))
    elif role == 'receptionist':
        return redirect(url_for('reception.index'))
    elif role == 'patient':
        return redirect(url_for('patient.index'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        from extensions import db
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('auth.change_password'))

        if len(new_password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(new_password)
        db.session.commit()
        log_action('CHANGE_PASSWORD', 'User changed password')
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html')