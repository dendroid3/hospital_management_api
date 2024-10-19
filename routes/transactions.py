from flask import Blueprint, request, jsonify, current_app
from db import db 
import requests
from models import Transaction  
from models import Bill  
import base64
from datetime import datetime
import logging

transactions_bp = Blueprint('transactions', __name__)
logger = logging.getLogger(__name__)

@transactions_bp.route('/', methods=['POST'])
def add_transaction():
    data = request.get_json()
    
    # Create a new transaction object
    new_transaction = Transaction(
        checkout_request_id=data['checkout_request_id'],
        bill_id=data['bill_id'],
        status=data['status'],
        amount=data['amount'],
        paying_phone_number=data['paying_phone_number'],
        receipt_number=data['receipt_number'],
        transaction_date=data['transaction_date']
    )

    # Add the transaction to the session and commit
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({"message": "Transaction added", "transaction_id": new_transaction.id}), 201

@transactions_bp.route('/', methods=['GET'])
def get_all_transactions():
    try:
        # Query all transactions from the database
        transactions = Transaction.query.all()

        # Prepare the transactions list in JSON format
        transactions_list = [
            {
                "id": transaction.id,
                "checkout_request_id": transaction.checkout_request_id,
                "bill_id": transaction.bill_id,
                "status": transaction.status,
                "amount": transaction.amount,
                "paying_phone_number": transaction.paying_phone_number,
                "receipt_number": transaction.receipt_number,
                "transaction_date": transaction.transaction_date
            }
            for transaction in transactions
        ]

        return jsonify(transactions_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Function to get OAuth token
def get_mpesa_access_token(consumer_key, consumer_secret):
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_url, auth=(consumer_key, consumer_secret))
    json_response = r.json()
    access_token = json_response['access_token']
    return access_token

# Function to initiate STK push
def stk_push_request(phone_number, amount, checkout_request_id, description):
    # Safaricom API details
    access_token = get_mpesa_access_token(current_app.config['MPESA_CONSUMER_KEY'], current_app.config['MPESA_CONSUMER_SECRET'])
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {"Authorization": f"Bearer {access_token}"}

    # Business shortcode, Passkey, Timestamp, and Password
    shortcode = current_app.config['MPESA_SHORTCODE']
    # passkey = current_app.config['MPESA_PASSKEY']
    # timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # password = base64.b64encode(f"{'174379'}{'c9ad901de83c496e631b8f3f6bbda12924ee956eb4684a00c2da50946d63c143'}{timestamp}".encode()).decode('utf-8')
   
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    data_to_encode = '174379' + passkey + timestamp
    password = base64.b64encode(data_to_encode.encode('utf-8')).decode('utf-8')

    # STK Push payload
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # The phone number initiating the transaction
        "PartyB": shortcode,     # Business shortcode receiving the payment
        "PhoneNumber": phone_number,
        "CallBackURL": 'https://geographical-euphemia-wazo-tank-f4308d3f.koyeb.app/transactions/callback',
        "AccountReference": checkout_request_id,  # This can be an invoice number or description
        "TransactionDesc": description
    }

    logger.info("Payload Data: %s", payload)

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


@transactions_bp.route('/deposit', methods=['POST'])
def initiate_mpesa_payment():

    logger.info("Received payload: %s", request.json)

    data = request.get_json()

    bill_id = data['bill_id']
    bill = Bill.query.get(bill_id)

    # Extract the details from the request
    phone_number = data['phone_number']
    amount = bill.amount
    description = data.get('description', 'Payment')  # Optional description

    # Call the STK Push function
    stk_response = stk_push_request(phone_number, amount, bill_id, description)

    # return stk_response
    # Check if the STK Push was successful
    if stk_response.get('ResponseCode') == '0':
        checkout_request_id = stk_response.get('CheckoutRequestID')

        transaction = Transaction(
            checkout_request_id=checkout_request_id,
            bill_id=bill_id,
            status="Pending",
            amount=amount,
            paying_phone_number=phone_number,
            transaction_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "STK Push initiated successfully", "transaction_id": transaction.id}), 200
    else:
        # Handle errors from the STK push request
        return jsonify({"message": "Failed to initiate STK Push", "error": stk_response.get('errorMessage')}), 400
    
@transactions_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    # logger.info("Received payload: %s", request.json)
    # logger.info("M-Pesa Callback Received")
    # logger.info("Content Type: %s", request.content_type)
    # logger.info("Request Method: %s", request.method)
    # logger.info("Request URL: %s", request.url)
    # logger.info("Request Headers: %s", request.headers)
    # logger.info("Request Body: %s", request.get_data(as_text=True))

    # Process the callback data
    data = request.get_json()
    if data:
        logger.info("Callback Data: %s", data)
    try:
        data = request.get_json()
        
        # Extract relevant data from the callback payload
        checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']
        result_code = data['Body']['stkCallback']['ResultCode']
        logger.info("checkout_request_id: %s", checkout_request_id)

        # Find the first transaction with the same checkout_request_id
        transaction = Transaction.query.filter_by(checkout_request_id=checkout_request_id).first()

        if transaction:
            if result_code == 0:  # Payment was successful (MPesa returns 0 for success)
                # Update the transaction status to "Paid"
                transaction.status = "Paid"

                # Find the related bill and update its status to "Paid"
                bill = Bill.query.filter_by(id=transaction.bill_id).first()
                if bill:
                    bill.status = "Paid"

                # Commit the changes to the database
                db.session.commit()
                return jsonify({"message": "Transaction and Bill updated successfully"}), 200
            else:
                # If payment was not successful, do nothing and return
                return jsonify({"message": "Payment not successful, no updates made"}), 200
        else:
            return jsonify({"error": "Transaction not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
