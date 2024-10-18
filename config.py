# config.py

import os

class Config:
    MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', 'jGloGi3Wa7wAlLPauhQcooYKVEDLP1WOA2KOcXVWsHlGlbzn')
    MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'ZedLeNlNBN0G3LzxAgvJG0L9ErpsG3sYR8efEUUt9UVSnLNUTCeCkANjR0074Rla')
    MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '4115361')
    MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'c9ad901de83c496e631b8f3f6bbda12924ee956eb4684a00c2da50946d63c143')
    MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'https://hospital-management-api-1-8u27.onrender.com/transactions/callback')
