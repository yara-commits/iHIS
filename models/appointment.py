from extensions import db
from datetime import datetime


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=30)  # minutes
    status = db.Column(db.String(30), default='pending')
    # pending, confirmed, cancelled, completed, no_show
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    appointment_type = db.Column(db.String(50))
    # in-person, online, follow-up, urgent
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id}>'


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Department {self.name}>'


class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctors = db.relationship('DoctorProfile', backref='specialty', lazy=True)

    def __repr__(self):
        return f'<Specialty {self.name}>'


class DoctorProfile(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, unique=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    license_no = db.Column(db.String(100))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    bio = db.Column(db.Text)
    consultation_fee = db.Column(db.Float)
    available_days = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DoctorProfile user_id={self.user_id}>'