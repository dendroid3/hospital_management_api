# config.py

import os

class Config:
    MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', 'zmDTtXkhe4diI75DwTHrfGai11MgVvkx')
    MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'onNX4p5OrApTaHRj')
    MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379')
    MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'c9ad901de83c496e631b8f3f6bbda12924ee956eb4684a00c2da50946d63c143')
    MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'https://yourdomain.com/callback')
