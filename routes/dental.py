from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.dental import (DentalRecord, DentalChart, DentalProcedure,
                           DentalImage, OrthodonticCase, Dentist)
from models.patient import Patient
from datetime import datetime
import os

dental = Blueprint('dental', __name__)


def dental_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['dentist', 'admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@dental.route('/')
@login_required
@dental_required
def index():
    today = datetime.utcnow().date()
    todays_appointments = DentalProcedure.query.filter(
        db.func.date(DentalProcedure.performed_at) == today
    ).count()
    active_ortho = OrthodonticCase.query.filter_by(
        status='active'
    ).count()
    pending_procedures = DentalProcedure.query.filter_by(
        status='planned'
    ).count()
    recent_records = DentalRecord.query.order_by(
        DentalRecord.created_at.desc()
    ).limit(10).all()
    return render_template('dental/index.html',
                           todays_appointments=todays_appointments,
                           active_ortho=active_ortho,
                           pending_procedures=pending_procedures,
                           recent_records=recent_records)


@dental.route('/records/<int:patient_id>')
@login_required
@dental_required
def patient_record(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    record = DentalRecord.query.filter_by(
        patient_id=patient_id
    ).first()
    return render_template('dental/record.html',
                           patient=patient,
                           record=record)


@dental.route('/records/<int:patient_id>/new', methods=['GET', 'POST'])
@login_required
@dental_required
def new_record(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        record = DentalRecord(
            patient_id=patient_id,
            dentist_id=current_user.id,
            dental_history=request.form.get('dental_history'),
            dental_allergies=request.form.get('dental_allergies'),
            previous_procedures=request.form.get('previous_procedures'),
            notes=request.form.get('notes')
        )
        db.session.add(record)
        db.session.flush()

        # Create initial chart
        chart = DentalChart(
            record_id=record.id,
            numbering_system=request.form.get('numbering_system', 'universal'),
            teeth_data='{}',
            chart_date=datetime.utcnow()
        )
        db.session.add(chart)
        db.session.commit()
        flash('Dental record created!', 'success')
        return redirect(url_for('dental.patient_record', patient_id=patient_id))

    return render_template('dental/new_record.html', patient=patient)


@dental.route('/chart/<int:record_id>/update', methods=['POST'])
@login_required
@dental_required
def update_chart(record_id):
    chart = DentalChart.query.filter_by(
        record_id=record_id
    ).first_or_404()
    chart.teeth_data = request.form.get('teeth_data', '{}')
    chart.periodontal_data = request.form.get('periodontal_data', '{}')
    chart.notes = request.form.get('notes')
    db.session.commit()
    flash('Dental chart updated!', 'success')
    return redirect(url_for('dental.patient_record',
                            patient_id=chart.record.patient_id))


@dental.route('/procedures/<int:record_id>/add', methods=['GET', 'POST'])
@login_required
@dental_required
def add_procedure(record_id):
    record = DentalRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        procedure = DentalProcedure(
            record_id=record_id,
            dentist_id=current_user.id,
            procedure_type=request.form.get('procedure_type'),
            tooth_number=request.form.get('tooth_number'),
            description=request.form.get('description'),
            cost=float(request.form.get('cost', 0)),
            status=request.form.get('status', 'planned'),
            notes=request.form.get('notes')
        )
        if procedure.status == 'completed':
            procedure.performed_at = datetime.utcnow()
        db.session.add(procedure)
        db.session.commit()
        flash('Procedure added!', 'success')
        return redirect(url_for('dental.patient_record',
                                patient_id=record.patient_id))

    return render_template('dental/add_procedure.html', record=record)


@dental.route('/images/<int:record_id>/upload', methods=['GET', 'POST'])
@login_required
@dental_required
def upload_image(record_id):
    record = DentalRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                filename = f"dental_{record_id}_{image.filename}"
                path = os.path.join('static/uploads', filename)
                image.save(path)
                dental_image = DentalImage(
                    record_id=record_id,
                    image_type=request.form.get('image_type'),
                    file_path=filename,
                    description=request.form.get('description')
                )
                db.session.add(dental_image)
                db.session.commit()
                flash('Image uploaded!', 'success')
        return redirect(url_for('dental.patient_record',
                                patient_id=record.patient_id))

    return render_template('dental/upload_image.html', record=record)


@dental.route('/ortho/<int:patient_id>/new', methods=['GET', 'POST'])
@login_required
@dental_required
def new_ortho_case(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        case = OrthodonticCase(
            patient_id=patient_id,
            dentist_id=current_user.id,
            case_type=request.form.get('case_type'),
            treatment_plan=request.form.get('treatment_plan'),
            start_date=datetime.strptime(
                request.form.get('start_date'), '%Y-%m-%d'
            ).date() if request.form.get('start_date') else None,
            status='active',
            notes=request.form.get('notes')
        )
        db.session.add(case)
        db.session.commit()
        flash('Orthodontic case created!', 'success')
        return redirect(url_for('dental.patient_record',
                                patient_id=patient_id))

    return render_template('dental/new_ortho.html', patient=patient)