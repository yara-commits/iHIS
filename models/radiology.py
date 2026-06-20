from extensions import db
from datetime import datetime


class RadiologyOrder(db.Model):
    __tablename__ = 'radiology_orders'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    imaging_type = db.Column(db.String(100), nullable=False)
    # X-Ray, CT, MRI, Ultrasound, Mammography, PET, Echo
    body_part = db.Column(db.String(100))
    urgency = db.Column(db.String(20), default='routine')
    # routine, urgent, stat
    clinical_info = db.Column(db.Text)
    status = db.Column(db.String(30), default='pending')
    # pending, scheduled, completed, cancelled
    scheduled_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Relationships
    reports = db.relationship('RadiologyReport', backref='order', lazy=True)

    def __repr__(self):
        return f'<RadiologyOrder {self.imaging_type} - Patient {self.patient_id}>'


class RadiologyReport(db.Model):
    __tablename__ = 'radiology_reports'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('radiology_orders.id'),
                         nullable=False)
    radiologist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                               nullable=False)
    findings = db.Column(db.Text)
    impression = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    is_critical = db.Column(db.Boolean, default=False)
    image_links = db.Column(db.Text)  # JSON string of image paths
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    signed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RadiologyReport {self.id} - Order {self.order_id}>'


class ImagingType(db.Model):
    __tablename__ = 'imaging_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50))
    description = db.Column(db.Text)
    preparation = db.Column(db.Text)
    duration = db.Column(db.String(50))
    price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ImagingType {self.name}>'