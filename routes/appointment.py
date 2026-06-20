from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.appointment import Appointment, DoctorProfile
from models.patient import Patient
from models.user import User
from datetime import datetime

appointment = Blueprint('appointment', __name__)


@appointment.route('/')
@login_required
def index():
    role = current_user.role.name.lower()

    if role in ['admin', 'superadmin', 'receptionist']:
        appointments = Appointment.query.filter_by(
            deleted_at=None
        ).order_by(Appointment.scheduled_at.desc()).all()

    elif role == 'doctor':
        appointments = Appointment.query.filter_by(
            doctor_id=current_user.id,
            deleted_at=None
        ).order_by(Appointment.scheduled_at.desc()).all()

    elif role == 'patient':
        patient = Patient.query.filter_by(
            user_id=current_user.id
        ).first()
        appointments = Appointment.query.filter_by(
            patient_id=patient.id if patient else 0,
            deleted_at=None
        ).order_by(Appointment.scheduled_at.desc()).all()

    else:
        appointments = []

    return render_template('appointments/index.html',
                           appointments=appointments)


@appointment.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        # Check for conflicts
        doctor_id = request.form.get('doctor_id')
        scheduled_at = datetime.strptime(
            request.form.get('scheduled_at'),
            '%Y-%m-%dT%H:%M'
        )

        conflict = Appointment.query.filter_by(
            doctor_id=doctor_id,
            scheduled_at=scheduled_at,
            deleted_at=None
        ).filter(
            Appointment.status.in_(['pending', 'confirmed'])
        ).first()

        if conflict:
            flash('Doctor already has an appointment at this time!', 'danger')
            return redirect(url_for('appointment.new'))

        appt = Appointment(
            patient_id=request.form.get('patient_id'),
            doctor_id=doctor_id,
            scheduled_at=scheduled_at,
            duration=request.form.get('duration', 30),
            reason=request.form.get('reason'),
            appointment_type=request.form.get('appointment_type'),
            notes=request.form.get('notes'),
            status='pending',
            created_by=current_user.id
        )
        db.session.add(appt)
        db.session.commit()
        flash('Appointment scheduled successfully!', 'success')
        return redirect(url_for('appointment.index'))

    patients = Patient.query.filter_by(deleted_at=None).all()
    doctors = User.query.join(User.role).filter(
        db.text("roles.name = 'doctor'")
    ).all()
    return render_template('appointments/new.html',
                           patients=patients,
                           doctors=doctors)


@appointment.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    appt = Appointment.query.get_or_404(id)
    new_status = request.form.get('status')
    appt.status = new_status
    appt.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Appointment status updated to {new_status}!', 'success')
    return redirect(url_for('appointment.index'))


@appointment.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    appt = Appointment.query.get_or_404(id)
    appt.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled.', 'warning')
    return redirect(url_for('appointment.index'))


@appointment.route('/calendar')
@login_required
def calendar():
    return render_template('appointments/calendar.html')


@appointment.route('/api/events')
@login_required
def api_events():
    appointments = Appointment.query.filter_by(
        deleted_at=None
    ).all()
    events = []
    for appt in appointments:
        events.append({
            'id': appt.id,
            'title': f'Patient {appt.patient_id}',
            'start': appt.scheduled_at.isoformat(),
            'status': appt.status
        })
    return jsonify(events)