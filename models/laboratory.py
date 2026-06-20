from extensions import db
from datetime import datetime


class LabOrder(db.Model):
    __tablename__ = 'lab_orders'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(20), default='routine')
    # routine, urgent, stat
    status = db.Column(db.String(30), default='pending')
    # pending, collected, processing, completed, cancelled
    clinical_info = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Relationships
    results = db.relationship('LabResult', backref='order', lazy=True)

    def __repr__(self):
        return f'<LabOrder {self.id} - Patient {self.patient_id}>'


class LabResult(db.Model):
    __tablename__ = 'lab_results'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('lab_orders.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_name = db.Column(db.String(200), nullable=False)
    test_category = db.Column(db.String(100))
    # CBC, LFT, KFT, Lipid, Thyroid etc
    result_value = db.Column(db.String(200))
    unit = db.Column(db.String(50))
    reference_range = db.Column(db.String(100))
    is_abnormal = db.Column(db.Boolean, default=False)
    is_critical = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    validated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    validated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LabResult {self.test_name} - Order {self.order_id}>'


class LabTest(db.Model):
    __tablename__ = 'lab_tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    normal_range = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    price = db.Column(db.Float)
    turnaround_time = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LabTest {self.name}>'