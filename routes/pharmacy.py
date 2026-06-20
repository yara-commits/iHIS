from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.pharmacy import Medication, PharmacyInventory, DispensingRecord, DrugInteraction
from models.clinical import Prescription
from models.patient import Patient
from models.communication import Notification
from datetime import datetime, date

pharmacy = Blueprint('pharmacy', __name__)


def pharmacy_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['pharmacist', 'admin', 'superadmin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@pharmacy.route('/')
@login_required
@pharmacy_required
def index():
    pending = Prescription.query.filter_by(status='active').count()
    low_stock = PharmacyInventory.query.filter(
        PharmacyInventory.quantity <= PharmacyInventory.reorder_level
    ).count()
    expired = PharmacyInventory.query.filter(
        PharmacyInventory.expiry_date < date.today()
    ).count()
    dispensed_today = DispensingRecord.query.filter(
        db.func.date(DispensingRecord.dispensed_at) == date.today()
    ).count()
    recent_prescriptions = Prescription.query.order_by(
        Prescription.created_at.desc()
    ).limit(10).all()
    return render_template('pharmacy/index.html',
                           pending=pending,
                           low_stock=low_stock,
                           expired=expired,
                           dispensed_today=dispensed_today,
                           recent_prescriptions=recent_prescriptions)


@pharmacy.route('/prescriptions')
@login_required
@pharmacy_required
def prescriptions():
    status = request.args.get('status', 'active')
    prescriptions = Prescription.query.filter_by(
        status=status
    ).order_by(Prescription.created_at.desc()).all()
    return render_template('pharmacy/prescriptions.html',
                           prescriptions=prescriptions,
                           status=status)


@pharmacy.route('/prescriptions/<int:id>/dispense', methods=['GET', 'POST'])
@login_required
@pharmacy_required
def dispense(id):
    prescription = Prescription.query.get_or_404(id)
    if request.method == 'POST':
        medication_id = request.form.get('medication_id')
        quantity = int(request.form.get('quantity', 0))

        # Check inventory
        inventory = PharmacyInventory.query.filter_by(
            medication_id=medication_id
        ).first()

        if not inventory or inventory.quantity < quantity:
            flash('Insufficient stock!', 'danger')
            return redirect(url_for('pharmacy.dispense', id=id))

        # Create dispensing record
        record = DispensingRecord(
            prescription_id=id,
            pharmacist_id=current_user.id,
            patient_id=prescription.patient_id,
            medication_id=medication_id,
            quantity_dispensed=quantity,
            dispensing_notes=request.form.get('notes')
        )
        db.session.add(record)

        # Update inventory
        inventory.quantity -= quantity

        # Check if low stock after dispensing
        if inventory.is_low_stock():
            notif = Notification(
                user_id=current_user.id,
                title='Low Stock Alert',
                message=f'Medication stock is running low!',
                type='warning',
                category='pharmacy'
            )
            db.session.add(notif)

        # Update prescription status
        prescription.status = 'dispensed'
        db.session.commit()
        flash('Medication dispensed successfully!', 'success')
        return redirect(url_for('pharmacy.prescriptions'))

    medications = Medication.query.filter_by(is_active=True).all()
    return render_template('pharmacy/dispense.html',
                           prescription=prescription,
                           medications=medications)


@pharmacy.route('/inventory')
@login_required
@pharmacy_required
def inventory():
    items = PharmacyInventory.query.order_by(
        PharmacyInventory.expiry_date.asc()
    ).all()
    return render_template('pharmacy/inventory.html', items=items)


@pharmacy.route('/inventory/add', methods=['GET', 'POST'])
@login_required
@pharmacy_required
def add_inventory():
    if request.method == 'POST':
        item = PharmacyInventory(
            medication_id=request.form.get('medication_id'),
            batch_number=request.form.get('batch_number'),
            quantity=int(request.form.get('quantity', 0)),
            unit=request.form.get('unit'),
            purchase_price=float(request.form.get('purchase_price', 0)),
            selling_price=float(request.form.get('selling_price', 0)),
            expiry_date=datetime.strptime(
                request.form.get('expiry_date'), '%Y-%m-%d'
            ).date(),
            reorder_level=int(request.form.get('reorder_level', 10)),
            location=request.form.get('location')
        )
        db.session.add(item)
        db.session.commit()
        flash('Inventory item added successfully!', 'success')
        return redirect(url_for('pharmacy.inventory'))

    medications = Medication.query.filter_by(is_active=True).all()
    return render_template('pharmacy/add_inventory.html',
                           medications=medications)


@pharmacy.route('/medications')
@login_required
@pharmacy_required
def medications():
    meds = Medication.query.filter_by(
        is_active=True
    ).order_by(Medication.name).all()
    return render_template('pharmacy/medications.html', medications=meds)