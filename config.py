import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cbit_secret_key_123'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'  # నీ MySQL కి పాస్‌వర్డ్ లేకపోతే ఇలా ఖాళీగా ఉంచు
    MYSQL_DB = 'cbit_career_hub'