from extensions import db
from datetime import datetime


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    visit_type = db.Column(db.String(50))  # outpatient, inpatient, emergency

    # SOAP Notes
    soap_subjective = db.Column(db.Text)   # What patient says
    soap_objective = db.Column(db.Text)    # What doctor observes
    soap_assessment = db.Column(db.Text)   # Diagnosis
    soap_plan = db.Column(db.Text)         # Treatment plan

    # Clinical Info
    chief_complaint = db.Column(db.Text)
    history_of_illness = db.Column(db.Text)
    physical_examination = db.Column(db.Text)
    treatment_notes = db.Column(db.Text)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    is_confidential = db.Column(db.Boolean, default=False)

    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    diagnoses = db.relationship('Diagnosis', backref='record', lazy=True)
    prescriptions = db.relationship('Prescription', backref='record', lazy=True)

    def __repr__(self):
        return f'<MedicalRecord {self.id} - Patient {self.patient_id}>'


class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    icd10_code = db.Column(db.String(20))
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))    # primary, secondary
    status = db.Column(db.String(50))  # active, resolved
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Diagnosis {self.icd10_code} - {self.name}>'


class VitalSigns(db.Model):
    __tablename__ = 'vital_signs'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blood_pressure = db.Column(db.String(20))   # e.g. 120/80
    heart_rate = db.Column(db.Integer)           # bpm
    temperature = db.Column(db.Float)            # celsius
    weight = db.Column(db.Float)                 # kg
    height = db.Column(db.Float)                 # cm
    spo2 = db.Column(db.Integer)                 # oxygen %
    respiratory_rate = db.Column(db.Integer)
    blood_glucose = db.Column(db.Float)
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def bmi(self):
        if self.weight and self.height:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None

    def __repr__(self):
        return f'<VitalSigns Patient {self.patient_id}>'


class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medication_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    route = db.Column(db.String(50))    # oral, IV, topical
    instructions = db.Column(db.Text)
    status = db.Column(db.String(30), default='active')
    signed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prescription {self.medication_name}>'