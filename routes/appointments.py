# routes/appointments.py

from flask import Blueprint, request, jsonify
from models import Appointment  
from models import Patient  
from db import db

appointments_bp = Blueprint('appointments', __name__)

# Endpoint to create an appointment
@appointments_bp.route('/', methods=['POST'])
def create_appointment():
    data = request.get_json()
    
    new_appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        appointment_date=data['appointment_date'],
        status=data.get('status', 'scheduled (Unpaid)'),
        reason_for_visit=data.get('reason_for_visit', ''),
        notes=data.get('notes', ''),
        cost=data.get('cost', '1000')
    )
    
    db.session.add(new_appointment)
    db.session.commit()
    
    return jsonify({"message": "Appointment created successfully", "appointment_id": new_appointment.id}), 201

# Endpoint to fetch all appointments for a specific doctor
@appointments_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_appointments_by_doctor(doctor_id):
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    results = []
    
    for appointment in appointments:
        # Assuming you have a Patient model and can get the patient using patient_id
        patient = Patient.query.get(appointment.patient_id)

        results.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "appointment_date": appointment.appointment_date,
            "cost": appointment.cost,
            "status": appointment.status,
            "reason_for_visit": appointment.reason_for_visit,
            "notes": appointment.notes,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
            "patient": {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "email": patient.email,
                "phone_number": patient.phone_number,
                "emergency_contact_phone_number": patient.emergency_contact_phone_number,
            } if patient else None  
        })
    
    return jsonify(results), 200


# Endpoint to fetch all appointments for a specific patient
@appointments_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_appointments_by_patient(patient_id):
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    results = []
    
    for appointment in appointments:
        results.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "appointment_date": appointment.appointment_date,
            "status": appointment.status,
            "reason_for_visit": appointment.reason_for_visit,
            "notes": appointment.notes,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at
        })
    
    return jsonify(results), 200

# Endpoint to update the status of an appointment
@appointments_bp.route('/<int:appointment_id>', methods=['PATCH'])
def update_appointment_status(appointment_id):
    data = request.get_json()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Update the status field
    appointment.notes = data.get('notes', appointment.notes)
    appointment.status = data.get('status', appointment.status)
    db.session.commit()
    
    return jsonify({"message": "Appointment status updated successfully"}), 200
