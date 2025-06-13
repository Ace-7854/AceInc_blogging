"""THIS FILE IS FOR RUNNING BACKEND COMMANDS FOR THE SERVER 
AND ENSURING FUNCTIONALITY OF FUNCTIONS ASWELL AS TESTING"""

def main():
    from custom_modules.mysql_module import MySQLManager
    
    db = MySQLManager()
    db.connect()

    db.create_required_tbls()

    db.disconnect()