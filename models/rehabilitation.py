from extensions import db
from datetime import datetime


class PhysicalTherapist(db.Model):
    __tablename__ = 'physical_therapists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, unique=True)
    specialty = db.Column(db.String(100))
    # Physical Therapy, Sports, Neurological,
    # Orthopedic, Pediatric, Cardiac, Pulmonary,
    # Occupational, Speech, Pain Management
    license_no = db.Column(db.String(100))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PhysicalTherapist user_id={self.user_id}>'


class TherapyAssessment(db.Model):
    __tablename__ = 'therapy_assessments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'),
                           nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                             nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Assessment scores
    pain_score = db.Column(db.Integer)       # 0-10
    mobility_score = db.Column(db.Integer)   # 0-10
    strength_score = db.Column(db.Integer)   # 0-10
    balance_score = db.Column(db.Integer)    # 0-10
    functional_score = db.Column(db.Integer) # 0-10

    # Detailed assessments
    functional_assessment = db.Column(db.Text)
    mobility_assessment = db.Column(db.Text)
    muscle_strength = db.Column(db.Text)
    range_of_motion = db.Column(db.Text)
    posture_evaluation = db.Column(db.Text)
    gait_analysis = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    plans = db.relationship('TherapyPlan', backref='assessment', lazy=True)

    def __repr__(self):
        return f'<TherapyAssessment Patient {self.patient_id}>'


class TherapyPlan(db.Model):
    __tablename__ = 'therapy_plans'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer,
                              db.ForeignKey('therapy_assessments.id'),
                              nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'),
                           nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                             nullable=False)
    goals = db.Column(db.Text)
    modalities = db.Column(db.Text)
    # Manual therapy, Exercise, Electrotherapy,
    # Ultrasound, Hydrotherapy
    frequency = db.Column(db.String(100))
    duration_weeks = db.Column(db.Integer)
    status = db.Column(db.String(30), default='active')
    # active, completed, discontinued
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Relationships
    sessions = db.relationship('TherapySession', backref='plan', lazy=True)
    progress = db.relationship('RehabProgress', backref='plan', lazy=True)

    def __repr__(self):
        return f'<TherapyPlan Patient {self.patient_id}>'


class TherapySession(db.Model):
    __tablename__ = 'therapy_sessions'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('therapy_plans.id'),
                        nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                             nullable=False)
    session_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer, default=60)
    pain_before = db.Column(db.Integer)   # 0-10
    pain_after = db.Column(db.Integer)    # 0-10
    exercises_done = db.Column(db.Text)   # JSON string
    techniques_used = db.Column(db.Text)
    patient_response = db.Column(db.Text)
    home_program = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TherapySession {self.id} - Plan {self.plan_id}>'


class ExerciseLibrary(db.Model):
    __tablename__ = 'exercise_library'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    # Strengthening, Stretching, Balance,
    # Cardio, Neurological, Breathing
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    image_url = db.Column(db.String(300))
    video_url = db.Column(db.String(300))
    difficulty = db.Column(db.String(20))
    # beginner, intermediate, advanced
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Exercise {self.name}>'


class RehabProgress(db.Model):
    __tablename__ = 'rehabilitation_progress'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('therapy_plans.id'),
                        nullable=False)
    measurement_type = db.Column(db.String(100))
    # pain, mobility, strength, balance, ROM
    value = db.Column(db.Float)
    unit = db.Column(db.String(50))
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RehabProgress {self.measurement_type} - Plan {self.plan_id}>'


class FunctionalOutcome(db.Model):
    __tablename__ = 'functional_outcomes'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('therapy_plans.id'),
                        nullable=False)
    outcome_scale = db.Column(db.String(100))
    # Barthel Index, FIM, DASH, KOOS etc
    score = db.Column(db.Float)
    max_score = db.Column(db.Float)
    interpretation = db.Column(db.Text)
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FunctionalOutcome {self.outcome_scale} - Plan {self.plan_id}>'