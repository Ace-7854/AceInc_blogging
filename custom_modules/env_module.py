from dotenv import load_dotenv
from os import environ

def get_sql_config() -> dict:
    load_dotenv()

    config = {
        'host' : environ['sql_host'],
        'user' : environ['sql_user'],
        'password' : environ['sql_password'],
        'database' : environ['sql_database']
    }

    return config

def get_email():
    load_dotenv()
    return environ['google_email']

def get_pwrd():
    load_dotenv()
    return environ['google_app_pwrd']