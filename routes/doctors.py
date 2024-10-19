from flask import Blueprint, jsonify, request
from db import db  # Import the db instance
from models import Doctor, User, Patient, Record, Bill
import json
from sqlalchemy import desc

# Create a Blueprint for the doctors
doctors_bp = Blueprint('doctors', __name__)

# Route to add a new doctor (POST method)
@doctors_bp.route('/', methods=['POST'])
def add_doctor():
    data = request.get_json()
    email = data['email']

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_doctor = Doctor(
        title=data['title'],
        first_name=data['first_name'],
        surname=data['surname'],
        gender=data['gender'],
        date_of_birth=data['date_of_birth'],
        specialization=data['specialization'],
        phone_number_country_code=data['phone_number_country_code'],
        phone_number=data['phone_number'],
        email=data['email'],
        address=data['address'],
        years_of_experience=data['years_of_experience'],
        qualifications=json.dumps(data['qualifications']),
        start_of_employment=data['start_of_employment'],
        emergency_contact=data['emergency_contact'],
        emergency_contact_country_code=data['emergency_contact_country_code']
    )
    db.session.add(new_doctor)
    db.session.commit()

    password = data['first_name'] + "." + data['surname']
    role = 2

    new_user = User(email=email)
    new_user.set_password(password)
    new_user.set_doctor_id(new_doctor.id)
    new_user.set_role(role)  

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Doctor added successfully!'}), 200

# Route to fetch all doctors (GET method)
@doctors_bp.route('/', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    output = []
    for doctor in doctors:
        output.append({
            'id': doctor.id,
            'title': doctor.title,
            'first_name': doctor.first_name,
            'surname': doctor.surname,
            'gender': doctor.gender,
            'date_of_birth': doctor.date_of_birth,
            'specialization': doctor.specialization,
            'phone_number_country_code': doctor.phone_number_country_code,
            'phone_number': doctor.phone_number,
            'email': doctor.email,
            'address': doctor.address,
            'years_of_experience': doctor.years_of_experience,
            'qualifications': json.loads(doctor.qualifications),  # Convert JSON string back to list
            'start_of_employment': doctor.start_of_employment,
            'emergency_contact': doctor.emergency_contact,
            'emergency_contact_country_code': doctor.emergency_contact_country_code
        })
    return jsonify(output), 200

# Route to edit an existing doctor by ID (PATCH method)
@doctors_bp.route('/<int:id>', methods=['PATCH'])
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    data = request.get_json()

    # Update all the fields from the incoming data
    doctor.title = data['title']
    doctor.first_name = data['first_name']
    doctor.surname = data['surname']
    doctor.gender = data['gender']
    doctor.date_of_birth = data['date_of_birth']
    doctor.specialization = data['specialization']
    doctor.phone_number_country_code = data['phone_number_country_code']
    doctor.phone_number = data['phone_number']
    doctor.email = data['email']
    doctor.address = data['address']
    doctor.years_of_experience = data['years_of_experience']
    doctor.qualifications = json.dumps(data['qualifications'])
    doctor.start_of_employment = data['start_of_employment']
    doctor.emergency_contact = data['emergency_contact']
    doctor.emergency_contact_country_code = data['emergency_contact_country_code']

    db.session.commit()
    return jsonify({'message': 'Doctor details updated successfully!'}), 200

# Endpoint to fetch doctors by specialization
@doctors_bp.route('/specialization', methods=['GET'])
def get_doctors_by_specialization():
    specialization = request.args.get('specialization')
    if not specialization:
        return jsonify({"error": "Specialization parameter is required"}), 400

    doctors = Doctor.query.filter_by(specialization=specialization).all()
    return jsonify([{
        "id": doctor.id,
        "title": doctor.title,
        "first_name": doctor.first_name,
        "surname": doctor.surname,
        "specialization": doctor.specialization
    } for doctor in doctors])

# Route to delete a doctor by ID (DELETE method)
@doctors_bp.route('/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor deleted successfully!'}), 200

# Route to get all patients by doctor ID
@doctors_bp.route('/patients/<int:doctor_id>', methods=['GET'])
def get_patients_by_doctor(doctor_id):
    # Query all patients where the doctor_id matches
    patients = Patient.query.filter_by(doctor_id=doctor_id).all()

    # Check if any patients are found
    if not patients:
        return jsonify({'message': 'No patients found for this doctor'}), 404

    # Prepare the results in JSON format
    results = []
    for patient in patients:
        records = Record.query.filter_by(patient_id=patient.id).order_by(desc(Record.creation_date)).all()
        records_list = [
            {
                "id": record.id,
                "subject": record.subject,
                "creation_date": record.creation_date,
                "record": record.record
            }
            for record in records
        ]

        # Fetch bills for the patient, ordered by creation_date
        bills = Bill.query.filter_by(patient_id=patient.id).order_by(desc(Bill.creation_date)).all()
        bills_list = [
            {
                "id": bill.id,
                "status": bill.status,
                "amount": bill.amount,
                "description": bill.description,
                "creation_date": bill.creation_date
            }
            for bill in bills
        ]

        results.append({
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "gender": patient.gender,
            "emergency_contact_phone_number": patient.emergency_contact_phone_number,
            "date_of_birth": patient.date_of_birth,
            "email": patient.email,
            "phone_number": patient.phone_number,
            "address": patient.address,
            "records": records_list,
            "bills": bills_list
        })

    return jsonify(results), 200
