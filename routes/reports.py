from flask import Blueprint, render_template, make_response, request
from flask_login import login_required, current_user
from extensions import db
from models.patient import Patient
from models.clinical import MedicalRecord, Prescription
from models.laboratory import LabOrder, LabResult
from models.radiology import RadiologyOrder, RadiologyReport
from models.appointment import Appointment
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

reports = Blueprint('reports', __name__)


def generate_pdf_header(story, styles, title, subtitle=''):
    """Add standard header to PDF"""
    story.append(Paragraph('iHIS - Intelligent Health Information System', 
                           styles['Title']))
    story.append(Paragraph(title, styles['Heading1']))
    if subtitle:
        story.append(Paragraph(subtitle, styles['Normal']))
    story.append(Paragraph(
        f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}',
        styles['Normal']
    ))
    story.append(Spacer(1, 20))


@reports.route('/patient/<int:patient_id>/pdf')
@login_required
def patient_report(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient_id).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header
    generate_pdf_header(story, styles,
                        f'Patient Report: {patient.full_name}',
                        f'MRN: {patient.mrn}')

    # Patient Info
    story.append(Paragraph('Patient Information', styles['Heading2']))
    patient_data = [
        ['Full Name', patient.full_name],
        ['MRN', patient.mrn],
        ['Date of Birth', str(patient.date_of_birth)],
        ['Gender', patient.gender],
        ['Blood Type', patient.blood_type or 'Unknown'],
        ['Phone', patient.phone or 'N/A'],
        ['Email', patient.email or 'N/A'],
        ['Allergies', patient.allergies or 'None'],
        ['Chronic Diseases', patient.chronic_diseases or 'None'],
    ]
    table = Table(patient_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Medical Records
    if records:
        story.append(Paragraph('Medical Records', styles['Heading2']))
        for record in records:
            story.append(Paragraph(
                f'Visit: {record.visit_date.strftime("%Y-%m-%d")} - {record.visit_type}',
                styles['Heading3']
            ))
            if record.chief_complaint:
                story.append(Paragraph(
                    f'Chief Complaint: {record.chief_complaint}',
                    styles['Normal']
                ))
            if record.soap_assessment:
                story.append(Paragraph(
                    f'Assessment: {record.soap_assessment}',
                    styles['Normal']
                ))
            if record.soap_plan:
                story.append(Paragraph(
                    f'Plan: {record.soap_plan}',
                    styles['Normal']
                ))
            story.append(Spacer(1, 10))

    # Prescriptions
    if prescriptions:
        story.append(Paragraph('Prescriptions', styles['Heading2']))
        rx_data = [['Medication', 'Dosage', 'Frequency', 'Duration', 'Status']]
        for rx in prescriptions:
            rx_data.append([
                rx.medication_name,
                rx.dosage or 'N/A',
                rx.frequency or 'N/A',
                rx.duration or 'N/A',
                rx.status
            ])
        rx_table = Table(rx_data, colWidths=[2*inch, 1*inch, 1.2*inch, 1*inch, 0.8*inch])
        rx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(rx_table)

    doc.build(story)
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'attachment; filename=patient_{patient.mrn}_report.pdf'
    return response


@reports.route('/lab/<int:order_id>/pdf')
@login_required
def lab_report(order_id):
    order = LabOrder.query.get_or_404(order_id)
    results = LabResult.query.filter_by(order_id=order_id).all()
    patient = Patient.query.get_or_404(order.patient_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    generate_pdf_header(story, styles,
                        'Laboratory Report',
                        f'Patient: {patient.full_name} | MRN: {patient.mrn}')

    # Order Info
    order_data = [
        ['Order ID', str(order.id)],
        ['Order Date', order.order_date.strftime('%Y-%m-%d %H:%M')],
        ['Priority', order.priority.upper()],
        ['Status', order.status.upper()],
        ['Clinical Info', order.clinical_info or 'N/A'],
    ]
    table = Table(order_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Results
    if results:
        story.append(Paragraph('Test Results', styles['Heading2']))
        results_data = [['Test Name', 'Result', 'Unit',
                          'Reference Range', 'Status']]
        for result in results:
            status = 'CRITICAL' if result.is_critical else \
                     'ABNORMAL' if result.is_abnormal else 'Normal'
            results_data.append([
                result.test_name,
                result.result_value or 'Pending',
                result.unit or '',
                result.reference_range or 'N/A',
                status
            ])
        results_table = Table(results_data,
                              colWidths=[2*inch, 1.2*inch, 0.8*inch,
                                         1.5*inch, 1*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(results_table)

    doc.build(story)
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'attachment; filename=lab_report_{order_id}.pdf'
    return response


@reports.route('/appointment/pdf')
@login_required
def appointment_report():
    appointments = Appointment.query.order_by(
        Appointment.scheduled_at.desc()
    ).limit(50).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    generate_pdf_header(story, styles, 'Appointments Report')

    data = [['ID', 'Patient', 'Doctor', 'Date & Time', 'Type', 'Status']]
    for appt in appointments:
        data.append([
            str(appt.id),
            str(appt.patient_id),
            str(appt.doctor_id),
            appt.scheduled_at.strftime('%Y-%m-%d %H:%M'),
            appt.appointment_type or 'N/A',
            appt.status.upper()
        ])

    table = Table(data, colWidths=[0.5*inch, 1*inch, 1*inch,
                                    1.8*inch, 1.2*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'attachment; filename=appointments_report.pdf'
    return response