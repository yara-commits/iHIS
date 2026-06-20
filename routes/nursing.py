from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.patient import Patient
from models.clinical import VitalSigns, Prescription
from models.communication import Notification
from datetime import datetime

nursing = Blueprint('nursing', __name__)


def nurse_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['nurse', 'admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@nursing.route('/')
@login_required
@nurse_required
def index():
    patients = Patient.query.filter_by(
        is_active=True,
        deleted_at=None
    ).order_by(Patient.created_at.desc()).all()
    critical_count = Notification.query.filter_by(
        type='danger',
        is_read=False
    ).count()
    return render_template('dashboard/nurse.html',
                           patients=patients,
                           critical_count=critical_count)


@nursing.route('/vitals/<int:patient_id>/add', methods=['GET', 'POST'])
@login_required
@nurse_required
def add_vitals(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        vitals = VitalSigns(
            patient_id=patient_id,
            recorded_by=current_user.id,
            blood_pressure=request.form.get('blood_pressure'),
            heart_rate=request.form.get('heart_rate'),
            temperature=request.form.get('temperature'),
            weight=request.form.get('weight'),
            height=request.form.get('height'),
            spo2=request.form.get('spo2'),
            respiratory_rate=request.form.get('respiratory_rate'),
            blood_glucose=request.form.get('blood_glucose'),
            notes=request.form.get('notes')
        )
        db.session.add(vitals)

        # Alert if critical vitals
        hr = request.form.get('heart_rate')
        spo2 = request.form.get('spo2')
        if hr and (int(hr) > 120 or int(hr) < 50):
            notif = Notification(
                user_id=current_user.id,
                title='Critical Heart Rate',
                message=f'Patient {patient.full_name} has abnormal heart rate: {hr} bpm',
                type='danger',
                category='alert'
            )
            db.session.add(notif)

        if spo2 and int(spo2) < 90:
            notif = Notification(
                user_id=current_user.id,
                title='Critical SpO2',
                message=f'Patient {patient.full_name} has low oxygen: {spo2}%',
                type='danger',
                category='alert'
            )
            db.session.add(notif)

        db.session.commit()
        flash('Vital signs recorded successfully!', 'success')
        return redirect(url_for('patient.view', id=patient_id))

    return render_template('dashboard/add_vitals.html', patient=patient)


@nursing.route('/vitals/<int:patient_id>/history')
@login_required
@nurse_required
def vitals_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    vitals = VitalSigns.query.filter_by(
        patient_id=patient_id
    ).order_by(VitalSigns.recorded_at.desc()).all()
    return render_template('dashboard/vitals_history.html',
                           patient=patient,
                           vitals=vitals)


@nursing.route('/medications/schedule')
@login_required
@nurse_required
def medication_schedule():
    prescriptions = Prescription.query.filter_by(
        status='active'
    ).order_by(Prescription.created_at.desc()).all()
    return render_template('dashboard/medication_schedule.html',
                           prescriptions=prescriptions)


@nursing.route('/notes/<int:patient_id>/add', methods=['GET', 'POST'])
@login_required
@nurse_required
def add_note(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        from models.communication import AuditLog
        note = AuditLog(
            user_id=current_user.id,
            action='NURSING_NOTE',
            resource_type='Patient',
            resource_id=patient_id,
            description=request.form.get('note')
        )
        db.session.add(note)
        db.session.commit()
        flash('Nursing note added!', 'success')
        return redirect(url_for('patient.view', id=patient_id))
    return render_template('dashboard/add_note.html', patient=patient)