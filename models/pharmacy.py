from extensions import db
from datetime import datetime


class Medication(db.Model):
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    generic_name = db.Column(db.String(200))
    category = db.Column(db.String(100))
    dosage_forms = db.Column(db.String(200))
    # tablet, capsule, syrup, injection
    strength = db.Column(db.String(100))
    manufacturer = db.Column(db.String(200))
    description = db.Column(db.Text)
    warnings = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inventory = db.relationship('PharmacyInventory', backref='medication',
                                lazy=True)

    def __repr__(self):
        return f'<Medication {self.name}>'


class PharmacyInventory(db.Model):
    __tablename__ = 'pharmacy_inventory'

    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'),
                              nullable=False)
    batch_number = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(50))
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    expiry_date = db.Column(db.Date, nullable=False)
    reorder_level = db.Column(db.Integer, default=10)
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    def is_expired(self):
        from datetime import date
        return self.expiry_date < date.today()

    def __repr__(self):
        return f'<Inventory {self.medication_id} - Qty {self.quantity}>'


class DispensingRecord(db.Model):
    __tablename__ = 'dispensing_records'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'),
                                nullable=False)
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                              nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'),
                           nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'),
                              nullable=False)
    quantity_dispensed = db.Column(db.Integer, nullable=False)
    dispensing_notes = db.Column(db.Text)
    dispensed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Dispensing {self.id} - Patient {self.patient_id}>'


class DrugInteraction(db.Model):
    __tablename__ = 'drug_interactions'

    id = db.Column(db.Integer, primary_key=True)
    medication_id_1 = db.Column(db.Integer, db.ForeignKey('medications.id'),
                                nullable=False)
    medication_id_2 = db.Column(db.Integer, db.ForeignKey('medications.id'),
                                nullable=False)
    severity = db.Column(db.String(20))
    # mild, moderate, severe
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DrugInteraction {self.medication_id_1} x {self.medication_id_2}>'