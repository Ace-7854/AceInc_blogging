"""THIS FILE IS FOR RUNNING BACKEND COMMANDS FOR THE SERVER 
AND ENSURING FUNCTIONALITY OF FUNCTIONS ASWELL AS TESTING"""
from custom_modules.mysql_module import MySQLManager

def main():
    db = MySQLManager()
    db.connect()

    db.disconnect()

if __name__ == "__main__":
    main()