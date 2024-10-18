from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_role(self, role):
        if 1 <= role <= 3:
            self.role = role
        else:
            raise ValueError("Role must be between 1 and 3")
        
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.String(10))
    specialization = db.Column(db.String(50))
    phone_number_country_code = db.Column(db.String(5))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    years_of_experience = db.Column(db.Integer)
    qualifications = db.Column(db.Text)  # Store as JSON string
    start_of_employment = db.Column(db.String(10))
    emergency_contact = db.Column(db.String(15))
    emergency_contact_country_code = db.Column(db.String(5))


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    doctor_id = db.Column(db.Integer)  # Foreign key to doctors table
    emergency_contact_phone_number = db.Column(db.String(15))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    cost = db.Column(db.Integer)
    appointment_date = db.Column(db.String(10))  # Use appropriate date format
    status = db.Column(db.String(20))  # e.g., 'scheduled', 'completed', 'canceled'
    reason_for_visit = db.Column(db.String(200))
    notes = db.Column(db.Text, nullable=True)  # Make notes nullable
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)  
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp()) 
    record = db.Column(db.Text, nullable=False)  

    def __repr__(self):
        return f"<Record {self.subject} for Patient {self.patient_id}>"

class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default="Pending")  # Example statuses: "Paid", "Pending", etc.
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp()) 
    amount = db.Column(db.Float, nullable=False)
    patient = db.relationship('Patient', backref=db.backref('bills', lazy=True))
