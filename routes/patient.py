from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.patient import Patient
from models.clinical import MedicalRecord, VitalSigns
from models.appointment import Appointment
import uuid

patient = Blueprint('patient', __name__)


def generate_mrn():
    return f'MRN-{str(uuid.uuid4())[:8].upper()}'


@patient.route('/')
@login_required
def index():
    patients = Patient.query.filter_by(
        deleted_at=None
    ).order_by(Patient.created_at.desc()).all()
    return render_template('patients/index.html', patients=patients)


@patient.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        from extensions import db
        p = Patient(
            mrn=generate_mrn(),
            full_name=request.form.get('full_name'),
            date_of_birth=request.form.get('date_of_birth'),
            gender=request.form.get('gender'),
            blood_type=request.form.get('blood_type'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            nationality=request.form.get('nationality'),
            national_id=request.form.get('national_id'),
            emergency_contact_name=request.form.get('emergency_contact_name'),
            emergency_contact_phone=request.form.get('emergency_contact_phone'),
            emergency_contact_relation=request.form.get('emergency_contact_relation'),
            allergies=request.form.get('allergies'),
            chronic_diseases=request.form.get('chronic_diseases'),
            registered_by=current_user.id
        )
        db.session.add(p)
        db.session.commit()
        flash(f'Patient {p.full_name} registered! MRN: {p.mrn}', 'success')
        return redirect(url_for('patient.view', id=p.id))
    return render_template('patients/new.html')


@patient.route('/<int:id>')
@login_required
def view(id):
    p = Patient.query.get_or_404(id)
    records = MedicalRecord.query.filter_by(
        patient_id=id
    ).order_by(MedicalRecord.visit_date.desc()).all()
    appointments = Appointment.query.filter_by(
        patient_id=id
    ).order_by(Appointment.scheduled_at.desc()).all()
    vitals = VitalSigns.query.filter_by(
        patient_id=id
    ).order_by(VitalSigns.recorded_at.desc()).limit(5).all()
    return render_template('patients/view.html',
                           patient=p,
                           records=records,
                           appointments=appointments,
                           vitals=vitals)


@patient.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    p = Patient.query.get_or_404(id)
    if request.method == 'POST':
        from extensions import db
        p.full_name = request.form.get('full_name')
        p.phone = request.form.get('phone')
        p.email = request.form.get('email')
        p.address = request.form.get('address')
        p.allergies = request.form.get('allergies')
        p.chronic_diseases = request.form.get('chronic_diseases')
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patient.view', id=p.id))
    return render_template('patients/edit.html', patient=p)


@patient.route('/search')
@login_required
def search():
    q = request.args.get('q', '')
    patients = Patient.query.filter(
        (Patient.full_name.ilike(f'%{q}%')) |
        (Patient.mrn.ilike(f'%{q}%')) |
        (Patient.phone.ilike(f'%{q}%'))
    ).filter_by(deleted_at=None).all()
    return render_template('patients/search.html',
                           patients=patients, query=q)