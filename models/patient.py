from extensions import db
from datetime import datetime
class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(30), unique=True, nullable=False)  # Medical Record Number
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    full_name = db.Column(db.String(150), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_type = db.Column(db.String(5))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    nationality = db.Column(db.String(50))
    national_id = db.Column(db.String(50))
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(150))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relation = db.Column(db.String(50))
    
    # Medical Info
    allergies = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    vaccination_records = db.Column(db.Text)
    
    # System fields
    registered_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    vital_signs = db.relationship('VitalSigns', backref='patient', lazy=True)

    def age(self):
        today = datetime.today()
        return today.year - self.date_of_birth.year

    def __repr__(self):
        return f'<Patient {self.mrn} - {self.full_name}>'