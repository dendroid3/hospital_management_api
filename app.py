# app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes.auth import auth_bp
from routes.doctors import doctors_bp
from routes.patients import patients_bp
from routes.appointments import appointments_bp 
from routes.bills import bills_bp
from routes.records import records_bp
from routes.transactions import transactions_bp

from config import Config

from db import db

app = Flask(__name__)
app.config.from_object(Config)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# JWT Setup
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(doctors_bp, url_prefix='/doctors')
app.register_blueprint(patients_bp, url_prefix='/patients')
app.register_blueprint(appointments_bp, url_prefix='/appointments') 
app.register_blueprint(records_bp, url_prefix='/records')
app.register_blueprint(bills_bp, url_prefix='/bills')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return "Welcome to the Hospital Management System API"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
