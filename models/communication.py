from extensions import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))
    # info, warning, success, danger, critical
    category = db.Column(db.String(50))
    # appointment, lab, radiology, pharmacy,
    # system, message, alert
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    link = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.title} - User {self.user_id}>'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            nullable=False)
    subject = db.Column(db.String(200))
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('messages.id'),
                          nullable=True)
    # for reply threads
    deleted_by_sender = db.Column(db.Boolean, default=False)
    deleted_by_receiver = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    replies = db.relationship('Message', backref=db.backref('parent',
                              remote_side=[id]), lazy=True)

    def __repr__(self):
        return f'<Message {self.subject} - From {self.sender_id}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    # LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW, EXPORT
    resource_type = db.Column(db.String(100))
    # Patient, MedicalRecord, Prescription etc
    resource_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(300))
    status = db.Column(db.String(20), default='success')
    # success, failed, warning
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.action} - User {self.user_id}>'


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SystemSetting {self.key}>'


class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'),
                           nullable=False)
    module = db.Column(db.String(100))
    # clinical, lab, radiology, rehab, dental
    recommendation = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float)
    accepted = db.Column(db.Boolean, nullable=True)
    accepted_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                            nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AIRecommendation {self.module} - Patient {self.patient_id}>'