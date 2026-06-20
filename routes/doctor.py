from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.patient import Patient
from models.clinical import MedicalRecord, Diagnosis, VitalSigns, Prescription
from models.appointment import Appointment, DoctorProfile
from models.laboratory import LabOrder
from models.radiology import RadiologyOrder
from datetime import datetime

doctor = Blueprint('doctor', __name__)


def doctor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['doctor', 'admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@doctor.route('/')
@login_required
@doctor_required
def index():
    today = datetime.utcnow().date()
    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).filter(
        db.func.date(Appointment.scheduled_at) == today
    ).all()
    pending_labs = LabOrder.query.filter_by(
        doctor_id=current_user.id,
        status='pending'
    ).count()
    pending_radiology = RadiologyOrder.query.filter_by(
        doctor_id=current_user.id,
        status='pending'
    ).count()
    return render_template('dashboard/doctor.html',
                           appointments=appointments,
                           pending_labs=pending_labs,
                           pending_radiology=pending_radiology)


@doctor.route('/emr/<int:patient_id>/new', methods=['GET', 'POST'])
@login_required
@doctor_required
def new_record(patient_id):
    p = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=current_user.id,
            visit_type=request.form.get('visit_type'),
            chief_complaint=request.form.get('chief_complaint'),
            history_of_illness=request.form.get('history_of_illness'),
            physical_examination=request.form.get('physical_examination'),
            soap_subjective=request.form.get('soap_subjective'),
            soap_objective=request.form.get('soap_objective'),
            soap_assessment=request.form.get('soap_assessment'),
            soap_plan=request.form.get('soap_plan'),
            treatment_notes=request.form.get('treatment_notes'),
        )
        db.session.add(record)
        db.session.flush()

        # Add diagnosis
        icd_code = request.form.get('icd10_code')
        diagnosis_name = request.form.get('diagnosis_name')
        if diagnosis_name:
            diagnosis = Diagnosis(
                record_id=record.id,
                icd10_code=icd_code,
                name=diagnosis_name,
                type=request.form.get('diagnosis_type', 'primary'),
                status='active'
            )
            db.session.add(diagnosis)

        # Add prescription
        medication = request.form.get('medication_name')
        if medication:
            prescription = Prescription(
                record_id=record.id,
                doctor_id=current_user.id,
                patient_id=patient_id,
                medication_name=medication,
                dosage=request.form.get('dosage'),
                frequency=request.form.get('frequency'),
                duration=request.form.get('duration'),
                instructions=request.form.get('instructions'),
            )
            db.session.add(prescription)

        db.session.commit()
        flash('Medical record created successfully!', 'success')
        return redirect(url_for('patient.view', id=patient_id))

    return render_template('emr/new.html', patient=p)


@doctor.route('/emr/<int:record_id>')
@login_required
@doctor_required
def view_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    return render_template('emr/view.html', record=record)


@doctor.route('/lab-order/<int:patient_id>/new', methods=['GET', 'POST'])
@login_required
@doctor_required
def new_lab_order(patient_id):
    p = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        order = LabOrder(
            patient_id=patient_id,
            doctor_id=current_user.id,
            priority=request.form.get('priority', 'routine'),
            clinical_info=request.form.get('clinical_info'),
            notes=request.form.get('notes'),
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        flash('Lab order created successfully!', 'success')
        return redirect(url_for('patient.view', id=patient_id))
    return render_template('laboratory/new_order.html', patient=p)


@doctor.route('/radiology-order/<int:patient_id>/new', methods=['GET', 'POST'])
@login_required
@doctor_required
def new_radiology_order(patient_id):
    p = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        order = RadiologyOrder(
            patient_id=patient_id,
            doctor_id=current_user.id,
            imaging_type=request.form.get('imaging_type'),
            body_part=request.form.get('body_part'),
            urgency=request.form.get('urgency', 'routine'),
            clinical_info=request.form.get('clinical_info'),
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        flash('Radiology order created successfully!', 'success')
        return redirect(url_for('patient.view', id=patient_id))
    return render_template('radiology/new_order.html', patient=p)