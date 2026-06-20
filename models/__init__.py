from .user import User, Role
from .patient import Patient
from .clinical import MedicalRecord, Diagnosis, VitalSigns, Prescription
from .appointment import Appointment, Department, Specialty, DoctorProfile
from .laboratory import LabOrder, LabResult, LabTest
from .radiology import RadiologyOrder, RadiologyReport, ImagingType
from .pharmacy import Medication, PharmacyInventory, DispensingRecord, DrugInteraction
from .dental import DentalSpecialty, Dentist, DentalRecord, DentalChart, DentalProcedure, DentalImage, OrthodonticCase
from .rehabilitation import PhysicalTherapist, TherapyAssessment, TherapyPlan, TherapySession, ExerciseLibrary, RehabProgress, FunctionalOutcome
from .communication import Notification, Message, AuditLog, SystemSetting, AIRecommendation