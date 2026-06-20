from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.laboratory import LabOrder, LabResult, LabTest
from models.patient import Patient
from models.communication import Notification
from datetime import datetime

laboratory = Blueprint('laboratory', __name__)


def lab_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['lab_tech', 'admin', 'superadmin', 'doctor']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@laboratory.route('/')
@login_required
@lab_required
def index():
    pending = LabOrder.query.filter_by(status='pending').count()
    processing = LabOrder.query.filter_by(status='processing').count()
    completed_today = LabOrder.query.filter_by(
        status='completed'
    ).filter(
        db.func.date(LabOrder.updated_at) == datetime.utcnow().date()
    ).count()
    critical = LabResult.query.filter_by(is_critical=True).count()
    recent_orders = LabOrder.query.order_by(
        LabOrder.created_at.desc()
    ).limit(10).all()
    return render_template('laboratory/index.html',
                           pending=pending,
                           processing=processing,
                           completed_today=completed_today,
                           critical=critical,
                           recent_orders=recent_orders)


@laboratory.route('/orders')
@login_required
@lab_required
def orders():
    status = request.args.get('status', 'all')
    if status == 'all':
        orders = LabOrder.query.order_by(
            LabOrder.created_at.desc()
        ).all()
    else:
        orders = LabOrder.query.filter_by(
            status=status
        ).order_by(LabOrder.created_at.desc()).all()
    return render_template('laboratory/orders.html',
                           orders=orders, status=status)


@laboratory.route('/orders/<int:id>')
@login_required
@lab_required
def view_order(id):
    order = LabOrder.query.get_or_404(id)
    results = LabResult.query.filter_by(order_id=id).all()
    return render_template('laboratory/view_order.html',
                           order=order, results=results)


@laboratory.route('/orders/<int:id>/results/add', methods=['GET', 'POST'])
@login_required
@lab_required
def add_result(id):
    order = LabOrder.query.get_or_404(id)
    if request.method == 'POST':
        test_names = request.form.getlist('test_name')
        result_values = request.form.getlist('result_value')
        units = request.form.getlist('unit')
        reference_ranges = request.form.getlist('reference_range')
        is_abnormals = request.form.getlist('is_abnormal')

        for i in range(len(test_names)):
            if test_names[i]:
                is_abnormal = str(i) in is_abnormals
                result = LabResult(
                    order_id=id,
                    technician_id=current_user.id,
                    test_name=test_names[i],
                    result_value=result_values[i] if i < len(result_values) else '',
                    unit=units[i] if i < len(units) else '',
                    reference_range=reference_ranges[i] if i < len(reference_ranges) else '',
                    is_abnormal=is_abnormal,
                    is_critical=is_abnormal
                )
                db.session.add(result)

                # Send notification if critical
                if is_abnormal:
                    notif = Notification(
                        user_id=order.doctor_id,
                        title='Critical Lab Result',
                        message=f'Critical value for {test_names[i]} - Patient {order.patient_id}',
                        type='danger',
                        category='lab'
                    )
                    db.session.add(notif)

        order.status = 'completed'
        db.session.commit()
        flash('Lab results added successfully!', 'success')
        return redirect(url_for('laboratory.view_order', id=id))

    tests = LabTest.query.filter_by(is_active=True).all()
    return render_template('laboratory/add_result.html',
                           order=order, tests=tests)


@laboratory.route('/results/<int:id>/validate', methods=['POST'])
@login_required
@lab_required
def validate_result(id):
    result = LabResult.query.get_or_404(id)
    result.validated_by = current_user.id
    result.validated_at = datetime.utcnow()
    db.session.commit()
    flash('Result validated!', 'success')
    return redirect(url_for('laboratory.view_order', id=result.order_id))