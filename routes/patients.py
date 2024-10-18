# routes/patients.py

from flask import Blueprint, request, jsonify
from models import Patient, Doctor
from db import db

patients_bp = Blueprint('patients', __name__)

# Endpoint to create a new patient
@patients_bp.route('/', methods=['POST'])
def add_patient():
    data = request.get_json()
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
