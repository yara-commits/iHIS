from app import app, db
from models.user import User, Role
from models.patient import Patient
from models.appointment import Appointment, Department, Specialty
from models.laboratory import LabTest
from models.pharmacy import Medication
from models.rehabilitation import ExerciseLibrary
from datetime import datetime, date, timedelta


def seed():
    with app.app_context():
        print('🌱 Creating tables...')
        db.create_all()

        print('🌱 Seeding roles...')
        roles = [
            Role(name='superadmin', description='Full system access'),
            Role(name='admin', description='Hospital administrator'),
            Role(name='doctor', description='Medical doctor'),
            Role(name='nurse', description='Nursing staff'),
            Role(name='lab_tech', description='Laboratory technician'),
            Role(name='radiologist', description='Radiology specialist'),
            Role(name='pharmacist', description='Pharmacy staff'),
            Role(name='dentist', description='Dental specialist'),
            Role(name='therapist', description='Physical therapist'),
            Role(name='receptionist', description='Reception staff'),
            Role(name='patient', description='Patient portal access'),
        ]
        for role in roles:
            existing = Role.query.filter_by(name=role.name).first()
            if not existing:
                db.session.add(role)
        db.session.commit()
        print('✅ Roles created!')

        print('🌱 Seeding users...')
        users_data = [
            {
                'username': 'superadmin',
                'email': 'superadmin@ihis.com',
                'full_name': 'Super Administrator',
                'role': 'superadmin',
                'password': 'admin123'
            },
            {
                'username': 'admin',
                'email': 'admin@ihis.com',
                'full_name': 'Hospital Administrator',
                'role': 'admin',
                'password': 'admin123'
            },
            {
                'username': 'doctor1',
                'email': 'doctor@ihis.com',
                'full_name': 'Dr. Ahmed Hassan',
                'role': 'doctor',
                'password': 'admin123'
            },
            {
                'username': 'doctor2',
                'email': 'doctor2@ihis.com',
                'full_name': 'Dr. Sara Mohamed',
                'role': 'doctor',
                'password': 'admin123'
            },
            {
                'username': 'nurse1',
                'email': 'nurse@ihis.com',
                'full_name': 'Nurse Fatima Ali',
                'role': 'nurse',
                'password': 'admin123'
            },
            {
                'username': 'lab1',
                'email': 'lab@ihis.com',
                'full_name': 'Lab Tech Omar Khalid',
                'role': 'lab_tech',
                'password': 'admin123'
            },
            {
                'username': 'radiologist1',
                'email': 'radiology@ihis.com',
                'full_name': 'Dr. Yusuf Radwan',
                'role': 'radiologist',
                'password': 'admin123'
            },
            {
                'username': 'pharmacist1',
                'email': 'pharmacy@ihis.com',
                'full_name': 'Pharmacist Layla Nour',
                'role': 'pharmacist',
                'password': 'admin123'
            },
            {
                'username': 'dentist1',
                'email': 'dental@ihis.com',
                'full_name': 'Dr. Hana Samir',
                'role': 'dentist',
                'password': 'admin123'
            },
            {
                'username': 'therapist1',
                'email': 'therapy@ihis.com',
                'full_name': 'Therapist Kareem Fawzy',
                'role': 'therapist',
                'password': 'admin123'
            },
            {
                'username': 'reception1',
                'email': 'reception@ihis.com',
                'full_name': 'Receptionist Dina Tarek',
                'role': 'receptionist',
                'password': 'admin123'
            },
        ]

        for u_data in users_data:
            existing = User.query.filter_by(
                email=u_data['email']
            ).first()
            if not existing:
                role = Role.query.filter_by(
                    name=u_data['role']
                ).first()
                user = User(
                    username=u_data['username'],
                    email=u_data['email'],
                    full_name=u_data['full_name'],
                    role_id=role.id
                )
                user.set_password(u_data['password'])
                db.session.add(user)
        db.session.commit()
        print('✅ Users created!')

        print('🌱 Seeding departments...')
        departments = [
            Department(name='Emergency', location='Ground Floor'),
            Department(name='Internal Medicine', location='Floor 1'),
            Department(name='Cardiology', location='Floor 2'),
            Department(name='Neurology', location='Floor 3'),
            Department(name='Pediatrics', location='Floor 4'),
            Department(name='Surgery', location='Floor 5'),
            Department(name='Laboratory', location='Ground Floor'),
            Department(name='Radiology', location='Ground Floor'),
            Department(name='Pharmacy', location='Ground Floor'),
            Department(name='Dental', location='Floor 1'),
            Department(name='Rehabilitation', location='Floor 2'),
        ]
        for dept in departments:
            existing = Department.query.filter_by(
                name=dept.name
            ).first()
            if not existing:
                db.session.add(dept)
        db.session.commit()
        print('✅ Departments created!')

        print('🌱 Seeding specialties...')
        specialties = [
            'Internal Medicine', 'Cardiology', 'Neurology',
            'Pediatrics', 'Orthopedics', 'Surgery', 'ENT',
            'Dermatology', 'Psychiatry', 'Ophthalmology',
            'Oncology', 'Gynecology', 'Urology', 'Endocrinology',
            'Gastroenterology', 'Pulmonology', 'Nephrology',
            'Family Medicine', 'Emergency Medicine'
        ]
        for spec_name in specialties:
            existing = Specialty.query.filter_by(
                name=spec_name
            ).first()
            if not existing:
                db.session.add(Specialty(name=spec_name))
        db.session.commit()
        print('✅ Specialties created!')

        print('🌱 Seeding patients...')
        patients_data = [
            {
                'mrn': 'MRN-00000001',
                'full_name': 'Mohammed Al-Rashid',
                'dob': date(1985, 3, 15),
                'gender': 'male',
                'blood_type': 'O+',
                'phone': '+20 100 123 4567',
                'allergies': 'Penicillin',
                'chronic_diseases': 'Hypertension, Type 2 Diabetes'
            },
            {
                'mrn': 'MRN-00000002',
                'full_name': 'Fatima Al-Zahra',
                'dob': date(1990, 7, 22),
                'gender': 'female',
                'blood_type': 'A+',
                'phone': '+20 100 234 5678',
                'allergies': 'None',
                'chronic_diseases': 'Asthma'
            },
            {
                'mrn': 'MRN-00000003',
                'full_name': 'Youssef Ibrahim',
                'dob': date(1978, 11, 8),
                'gender': 'male',
                'blood_type': 'B+',
                'phone': '+20 100 345 6789',
                'allergies': 'Sulfa drugs',
                'chronic_diseases': 'None'
            },
            {
                'mrn': 'MRN-00000004',
                'full_name': 'Aisha Mahmoud',
                'dob': date(1995, 1, 30),
                'gender': 'female',
                'blood_type': 'AB-',
                'phone': '+20 100 456 7890',
                'allergies': 'Latex',
                'chronic_diseases': 'Hypothyroidism'
            },
            {
                'mrn': 'MRN-00000005',
                'full_name': 'Karim Hassan',
                'dob': date(2000, 5, 12),
                'gender': 'male',
                'blood_type': 'O-',
                'phone': '+20 100 567 8901',
                'allergies': 'None',
                'chronic_diseases': 'None'
            },
        ]

        doctor = User.query.filter_by(email='doctor@ihis.com').first()
        for p_data in patients_data:
            existing = Patient.query.filter_by(
                mrn=p_data['mrn']
            ).first()
            if not existing:
                patient = Patient(
                    mrn=p_data['mrn'],
                    full_name=p_data['full_name'],
                    date_of_birth=p_data['dob'],
                    gender=p_data['gender'],
                    blood_type=p_data['blood_type'],
                    phone=p_data['phone'],
                    allergies=p_data['allergies'],
                    chronic_diseases=p_data['chronic_diseases'],
                    registered_by=doctor.id if doctor else None
                )
                db.session.add(patient)
        db.session.commit()
        print('✅ Patients created!')

        print('🌱 Seeding lab tests...')
        lab_tests = [
            LabTest(name='Complete Blood Count', code='CBC',
                    category='Hematology',
                    normal_range='See report', unit='Various'),
            LabTest(name='HbA1c', code='HBA1C',
                    category='Diabetes',
                    normal_range='< 5.7%', unit='%'),
            LabTest(name='Fasting Blood Glucose', code='FBG',
                    category='Diabetes',
                    normal_range='70-100', unit='mg/dL'),
            LabTest(name='Total Cholesterol', code='CHOL',
                    category='Lipid Profile',
                    normal_range='< 200', unit='mg/dL'),
            LabTest(name='TSH', code='TSH',
                    category='Thyroid',
                    normal_range='0.4-4.0', unit='mIU/L'),
            LabTest(name='Creatinine', code='CREAT',
                    category='Kidney Function',
                    normal_range='0.7-1.3', unit='mg/dL'),
            LabTest(name='ALT', code='ALT',
                    category='Liver Function',
                    normal_range='7-56', unit='U/L'),
            LabTest(name='Urine Analysis', code='UA',
                    category='Urinalysis',
                    normal_range='See report', unit='Various'),
        ]
        for test in lab_tests:
            existing = LabTest.query.filter_by(code=test.code).first()
            if not existing:
                db.session.add(test)
        db.session.commit()
        print('✅ Lab tests created!')

        print('🌱 Seeding medications...')
        medications = [
            Medication(name='Paracetamol', generic_name='Acetaminophen',
                      category='Analgesic', dosage_forms='Tablet, Syrup',
                      strength='500mg, 1000mg'),
            Medication(name='Amoxicillin', generic_name='Amoxicillin',
                      category='Antibiotic', dosage_forms='Capsule, Syrup',
                      strength='250mg, 500mg'),
            Medication(name='Metformin', generic_name='Metformin HCl',
                      category='Antidiabetic', dosage_forms='Tablet',
                      strength='500mg, 850mg, 1000mg'),
            Medication(name='Amlodipine', generic_name='Amlodipine Besylate',
                      category='Antihypertensive', dosage_forms='Tablet',
                      strength='5mg, 10mg'),
            Medication(name='Omeprazole', generic_name='Omeprazole',
                      category='Proton Pump Inhibitor',
                      dosage_forms='Capsule', strength='20mg, 40mg'),
            Medication(name='Atorvastatin', generic_name='Atorvastatin',
                      category='Statin', dosage_forms='Tablet',
                      strength='10mg, 20mg, 40mg'),
            Medication(name='Salbutamol', generic_name='Albuterol',
                      category='Bronchodilator',
                      dosage_forms='Inhaler, Tablet',
                      strength='2mg, 4mg'),
        ]
        for med in medications:
            existing = Medication.query.filter_by(
                name=med.name
            ).first()
            if not existing:
                db.session.add(med)
        db.session.commit()
        print('✅ Medications created!')

        print('🌱 Seeding exercises...')
        exercises = [
            ExerciseLibrary(
                name='Knee Flexion',
                category='Strengthening',
                description='Bend and straighten the knee',
                instructions='Lie on back, slowly bend knee to 90 degrees',
                sets=3, reps=10, difficulty='beginner'
            ),
            ExerciseLibrary(
                name='Shoulder Rotation',
                category='Stretching',
                description='Rotate shoulder joint',
                instructions='Stand straight, rotate arm in circles',
                sets=2, reps=15, difficulty='beginner'
            ),
            ExerciseLibrary(
                name='Balance Board',
                category='Balance',
                description='Stand on balance board',
                instructions='Stand on board, maintain balance 30 seconds',
                sets=3, duration_seconds=30, difficulty='intermediate'
            ),
            ExerciseLibrary(
                name='Diaphragmatic Breathing',
                category='Breathing',
                description='Deep breathing exercise',
                instructions='Breathe deeply using diaphragm',
                sets=2, reps=10, difficulty='beginner'
            ),
        ]
        for ex in exercises:
            existing = ExerciseLibrary.query.filter_by(
                name=ex.name
            ).first()
            if not existing:
                db.session.add(ex)
        db.session.commit()
        print('✅ Exercises created!')

        print('🌱 Seeding appointments...')
        patients = Patient.query.all()
        doctor = User.query.filter_by(email='doctor@ihis.com').first()
        admin = User.query.filter_by(email='admin@ihis.com').first()

        if patients and doctor:
            appts = [
                Appointment(
                    patient_id=patients[0].id,
                    doctor_id=doctor.id,
                    scheduled_at=datetime.utcnow() + timedelta(hours=1),
                    duration=30,
                    status='confirmed',
                    reason='Regular checkup',
                    appointment_type='consultation',
                    created_by=admin.id if admin else doctor.id
                ),
                Appointment(
                    patient_id=patients[1].id,
                    doctor_id=doctor.id,
                    scheduled_at=datetime.utcnow() + timedelta(hours=2),
                    duration=45,
                    status='pending',
                    reason='Follow-up diabetes',
                    appointment_type='follow-up',
                    created_by=admin.id if admin else doctor.id
                ),
                Appointment(
                    patient_id=patients[2].id,
                    doctor_id=doctor.id,
                    scheduled_at=datetime.utcnow() + timedelta(days=1),
                    duration=30,
                    status='pending',
                    reason='Chest pain evaluation',
                    appointment_type='consultation',
                    created_by=admin.id if admin else doctor.id
                ),
            ]
            for appt in appts:
                db.session.add(appt)
            db.session.commit()
        print('✅ Appointments created!')

        print('')
        print('=' * 50)
        print('✅ DATABASE SEEDED SUCCESSFULLY!')
        print('=' * 50)
        print('')
        print('🔑 Login Credentials:')
        print('  Super Admin : superadmin@ihis.com / admin123')
        print('  Admin       : admin@ihis.com / admin123')
        print('  Doctor      : doctor@ihis.com / admin123')
        print('  Nurse       : nurse@ihis.com / admin123')
        print('  Lab Tech    : lab@ihis.com / admin123')
        print('  Radiologist : radiology@ihis.com / admin123')
        print('  Pharmacist  : pharmacy@ihis.com / admin123')
        print('  Dentist     : dental@ihis.com / admin123')
        print('  Therapist   : therapy@ihis.com / admin123')
        print('  Receptionist: reception@ihis.com / admin123')
        print('')
        print('🚀 Run: python app.py')
        print('🌐 Open: http://localhost:5000')


if __name__ == '__main__':
    seed()