# routes/patients.py

from flask import Blueprint, request, jsonify
from models import Patient, Doctor, Bill, Record, User
from db import db

patients_bp = Blueprint('patients', __name__)

# Endpoint to create a new patient
@patients_bp.route('/', methods=['POST'])
def add_patient():
    data = request.get_json()
    email = data['email']

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=data['date_of_birth'],
        gender=data['gender'],
        phone_number=data['phone_number'],
        email=data['email'],
        address=data['address'],
        doctor_id=data['doctor_id'],
        emergency_contact_phone_number=data['emergency_contact_phone_number']
    )
    db.session.add(new_patient)

    password = data['first_name'] + "." + data['last_name']
    role = 2

    new_user = User(email=email)
    new_user.set_password(password)
    new_user.set_role(role)  

    db.session.add(new_user)

    db.session.commit()
    return jsonify({"message": "Patient added", "patient_id": new_patient.id}), 201

# Endpoint to fetch all patients
@patients_bp.route('/', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    results = []
    
    for patient in patients:
        doctor = Doctor.query.get(patient.doctor_id)  # Get the related doctor

        results.append({
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "phone_number": patient.phone_number,
            "email": patient.email,
            "address": patient.address,
            "emergency_contact_phone_number": patient.emergency_contact_phone_number,
            "doctor": {
                "id": doctor.id,
                "Name": doctor.title + " " + doctor.surname + " " + doctor.first_name + " (" + doctor.specialization + ")",
                "Phone Number": doctor.phone_number_country_code + " " + doctor.phone_number,
            } if doctor else None
        })
    
    return jsonify(results), 200

# Endpoint to update patient details
@patients_bp.route('/<int:patient_id>', methods=['PATCH'])
def update_patient(patient_id):
    data = request.get_json()
    patient = Patient.query.get_or_404(patient_id)
    
    patient.first_name = data['first_name']
    patient.last_name = data['last_name']
    patient.date_of_birth = data['date_of_birth']
    patient.gender = data['gender']
    patient.phone_number = data['phone_number']
    patient.email = data['email']
    patient.address = data['address']
    patient.doctor_id = data['doctor_id']
    patient.emergency_contact_phone_number = data['emergency_contact_phone_number']
    
    db.session.commit()
    return jsonify({"message": "Patient updated"}), 200

# Endpoint to delete a patient
@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted"}), 204

@patients_bp.route('/<int:patient_id>/bills', methods=['GET'])
def get_bills_by_patient(patient_id):
    # Query all bills where the patient_id matches
    bills = Bill.query.filter_by(patient_id=patient_id).all()

    # Check if any bills are found
    if not bills:
        return jsonify({'message': 'No bills found for this patient'}), 404

    # Prepare the results in JSON format
    results = []
    for bill in bills:
        results.append({
            "id": bill.id,
            "status": bill.status,
            "creation_date": bill.creation_date,
            "amount": bill.amount,
            "description": bill.description  # Include the description field
        })

    return jsonify(results), 200

@patients_bp.route('/<int:patient_id>/records', methods=['GET'])
def get_records_for_patient(patient_id):
    # Query all bills where the patient_id matches
    records = Record.query.filter_by(patient_id=patient_id).all()

    # Check if any bills are found
    if not records:
        return jsonify({'message': 'No records found for this patient'}), 404

    # Prepare the results in JSON format
    results = []
    for record in records:
        results.append({
            "id": record.id,
            "subject": record.subject,
            "creation_date": record.creation_date,
            "record": record.record,
        })

    return jsonify(results), 200
