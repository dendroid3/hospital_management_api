from flask import Blueprint, request, jsonify
from db import db
from models import Bill

bills_bp = Blueprint('bills', __name__)

@bills_bp.route('/', methods=['POST'])
def create_bill():
    data = request.get_json()
    
    # Check for required fields
    if 'patient_id' not in data or 'status' not in data or 'amount' not in data:
        return jsonify({"message": "Missing required fields"}), 400
    
    # Create the bill
    new_bill = Bill(
        status=data['status'],
        patient_id=data['patient_id'],
        description=data['description'],
        amount=data['amount']
    )

    db.session.add(new_bill)
    db.session.commit()

    return jsonify({"message": "Bill created successfully"}), 200
