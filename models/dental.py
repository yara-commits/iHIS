from extensions import db
from datetime import datetime


class DentalSpecialty(db.Model):
    __tablename__ = 'dental_specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # General, Orthodontics, Prosthodontics, Endodontics,
    # Periodontics, Oral Surgery, Pediatric, Cosmetic,
    # Implantology, Oral Medicine, Maxillofacial
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DentalSpecialty {self.name}>'


class Dentist(db.Model):
    __tablename__ = 'dentists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, unique=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('dental_specialties.id'))
    license_no = db.Column(db.String(100))
    qualification = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Dentist user_id={self.user_id}>'


class DentalRecord(db.Model):
    __tablename__ = 'dental_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'),
                           nullable=False)
    dentist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False)
    dental_history = db.Column(db.Text)
    dental_allergies = db.Column(db.Text)
    previous_procedures = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Relationships
    charts = db.relationship('DentalChart', backref='record', lazy=True)
    procedures = db.relationship('DentalProcedure', backref='record', lazy=True)
    images = db.relationship('DentalImage', backref='record', lazy=True)

    def __repr__(self):
        return f'<DentalRecord Patient {self.patient_id}>'


class DentalChart(db.Model):
    __tablename__ = 'dental_charts'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('dental_records.id'),
                          nullable=False)
    numbering_system = db.Column(db.String(20), default='universal')
    # universal, fdi, palmer
    teeth_data = db.Column(db.Text)  # JSON string
    # stores status of each tooth:
    # missing, caries, filling, crown,
    # bridge, implant, root_canal, extraction
    periodontal_data = db.Column(db.Text)  # JSON string
    chart_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<DentalChart {self.id} - Record {self.record_id}>'


class DentalProcedure(db.Model):
    __tablename__ = 'dental_procedures'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('dental_records.id'),
                          nullable=False)
    dentist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False)
    procedure_type = db.Column(db.String(100), nullable=False)
    # Filling, Root Canal, Extraction, Crown,
    # Bridge, Implant, Scaling, Orthodontic
    tooth_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    status = db.Column(db.String(30), default='planned')
    # planned, in_progress, completed
    performed_at = db.Column(db.DateTime, nullable=True)
    next_visit = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DentalProcedure {self.procedure_type} - Tooth {self.tooth_number}>'


class DentalImage(db.Model):
    __tablename__ = 'dental_images'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('dental_records.id'),
                          nullable=False)
    image_type = db.Column(db.String(100))
    # Periapical, Bitewing, Panoramic,
    # CBCT, Intraoral, Extraoral, 3D
    file_path = db.Column(db.String(300))
    description = db.Column(db.Text)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DentalImage {self.image_type} - Record {self.record_id}>'


class OrthodonticCase(db.Model):
    __tablename__ = 'orthodontic_cases'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'),
                           nullable=False)
    dentist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False)
    case_type = db.Column(db.String(100))
    treatment_plan = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=True)
    expected_end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='active')
    # active, completed, discontinued
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<OrthodonticCase Patient {self.patient_id}>'