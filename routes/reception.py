from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.patient import Patient
from models.appointment import Appointment, DoctorProfile
from models.user import User
from datetime import datetime, date

reception = Blueprint('reception', __name__)


def reception_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['receptionist', 'admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@reception.route('/')
@login_required
@reception_required
def index():
    today = date.today()
    todays_appointments = Appointment.query.filter(
        db.func.date(Appointment.scheduled_at) == today,
        Appointment.deleted_at == None
    ).order_by(Appointment.scheduled_at.asc()).all()

    waiting = Appointment.query.filter(
        db.func.date(Appointment.scheduled_at) == today,
        Appointment.status == 'confirmed'
    ).count()

    total_patients = Patient.query.filter_by(
        deleted_at=None
    ).count()

    new_today = Patient.query.filter(
        db.func.date(Patient.created_at) == today
    ).count()

    return render_template('dashboard/reception.html',
                           todays_appointments=todays_appointments,
                           waiting=waiting,
                           total_patients=total_patients,
                           new_today=new_today)


@reception.route('/checkin/<int:appointment_id>', methods=['POST'])
@login_required
@reception_required
def checkin(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Patient checked in successfully!', 'success')
    return redirect(url_for('reception.index'))


@reception.route('/queue')
@login_required
@reception_required
def queue():
    today = date.today()
    queue = Appointment.query.filter(
        db.func.date(Appointment.scheduled_at) == today,
        Appointment.status.in_(['pending', 'confirmed']),
        Appointment.deleted_at == None
    ).order_by(Appointment.scheduled_at.asc()).all()
    return render_template('dashboard/queue.html', queue=queue)


@reception.route('/register-patient', methods=['GET', 'POST'])
@login_required
@reception_required
def register_patient():
    if request.method == 'POST':
        import uuid
        mrn = f'MRN-{str(uuid.uuid4())[:8].upper()}'
        p = Patient(
            mrn=mrn,
            full_name=request.form.get('full_name'),
            date_of_birth=request.form.get('date_of_birth'),
            gender=request.form.get('gender'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            emergency_contact_name=request.form.get('emergency_contact_name'),
            emergency_contact_phone=request.form.get('emergency_contact_phone'),
            registered_by=current_user.id
        )
        db.session.add(p)
        db.session.commit()
        flash(f'Patient registered! MRN: {mrn}', 'success')
        return redirect(url_for('reception.index'))

    return render_template('patients/new.html')


@reception.route('/schedule-appointment', methods=['GET', 'POST'])
@login_required
@reception_required
def schedule_appointment():
    if request.method == 'POST':
        scheduled_at = datetime.strptime(
            request.form.get('scheduled_at'),
            '%Y-%m-%dT%H:%M'
        )
        appt = Appointment(
            patient_id=request.form.get('patient_id'),
            doctor_id=request.form.get('doctor_id'),
            scheduled_at=scheduled_at,
            duration=request.form.get('duration', 30),
            reason=request.form.get('reason'),
            appointment_type=request.form.get('appointment_type'),
            status='pending',
            created_by=current_user.id
        )
        db.session.add(appt)
        db.session.commit()
        flash('Appointment scheduled!', 'success')
        return redirect(url_for('reception.index'))

    patients = Patient.query.filter_by(deleted_at=None).all()
    doctors = User.query.all()
    return render_template('appointments/new.html',
                           patients=patients,
                           doctors=doctors)