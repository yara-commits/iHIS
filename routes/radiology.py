from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.radiology import RadiologyOrder, RadiologyReport, ImagingType
from models.patient import Patient
from models.communication import Notification
from datetime import datetime
import os

radiology = Blueprint('radiology', __name__)


def radiology_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role.name.lower() not in ['radiologist', 'admin', 'superadmin', 'doctor']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated


@radiology.route('/')
@login_required
@radiology_required
def index():
    pending = RadiologyOrder.query.filter_by(status='pending').count()
    scheduled = RadiologyOrder.query.filter_by(status='scheduled').count()
    completed_today = RadiologyOrder.query.filter_by(
        status='completed'
    ).filter(
        db.func.date(RadiologyOrder.updated_at) == datetime.utcnow().date()
    ).count()
    critical = RadiologyReport.query.filter_by(is_critical=True).count()
    recent_orders = RadiologyOrder.query.order_by(
        RadiologyOrder.created_at.desc()
    ).limit(10).all()
    return render_template('radiology/index.html',
                           pending=pending,
                           scheduled=scheduled,
                           completed_today=completed_today,
                           critical=critical,
                           recent_orders=recent_orders)


@radiology.route('/orders')
@login_required
@radiology_required
def orders():
    status = request.args.get('status', 'all')
    if status == 'all':
        orders = RadiologyOrder.query.order_by(
            RadiologyOrder.created_at.desc()
        ).all()
    else:
        orders = RadiologyOrder.query.filter_by(
            status=status
        ).order_by(RadiologyOrder.created_at.desc()).all()
    return render_template('radiology/orders.html',
                           orders=orders, status=status)


@radiology.route('/orders/<int:id>')
@login_required
@radiology_required
def view_order(id):
    order = RadiologyOrder.query.get_or_404(id)
    reports = RadiologyReport.query.filter_by(order_id=id).all()
    return render_template('radiology/view_order.html',
                           order=order, reports=reports)


@radiology.route('/orders/<int:id>/schedule', methods=['POST'])
@login_required
@radiology_required
def schedule_order(id):
    order = RadiologyOrder.query.get_or_404(id)
    scheduled_at = request.form.get('scheduled_at')
    order.scheduled_at = datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M')
    order.status = 'scheduled'
    db.session.commit()
    flash('Imaging scheduled successfully!', 'success')
    return redirect(url_for('radiology.view_order', id=id))


@radiology.route('/orders/<int:id>/report/add', methods=['GET', 'POST'])
@login_required
@radiology_required
def add_report(id):
    order = RadiologyOrder.query.get_or_404(id)
    if request.method == 'POST':
        is_critical = request.form.get('is_critical') == 'on'

        report = RadiologyReport(
            order_id=id,
            radiologist_id=current_user.id,
            findings=request.form.get('findings'),
            impression=request.form.get('impression'),
            recommendation=request.form.get('recommendation'),
            is_critical=is_critical,
            signed_at=datetime.utcnow()
        )

        # Handle image upload
        if 'images' in request.files:
            images = request.files.getlist('images')
            image_paths = []
            for image in images:
                if image.filename:
                    filename = f"radiology_{id}_{image.filename}"
                    path = os.path.join('static/uploads', filename)
                    image.save(path)
                    image_paths.append(filename)
            report.image_links = ','.join(image_paths)

        db.session.add(report)

        # Send critical notification
        if is_critical:
            notif = Notification(
                user_id=order.doctor_id,
                title='Critical Radiology Finding',
                message=f'Critical finding in {order.imaging_type} - Patient {order.patient_id}',
                type='danger',
                category='radiology'
            )
            db.session.add(notif)

        order.status = 'completed'
        db.session.commit()
        flash('Radiology report added successfully!', 'success')
        return redirect(url_for('radiology.view_order', id=id))

    return render_template('radiology/add_report.html', order=order)