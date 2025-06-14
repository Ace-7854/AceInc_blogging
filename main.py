"""THIS FILE IS FOR RUNNING BACKEND COMMANDS FOR THE SERVER 
AND ENSURING FUNCTIONALITY OF FUNCTIONS ASWELL AS TESTING"""
from custom_modules.mysql_module import MySQLManager

def remove_all_tbls(db:MySQLManager):
    items = db.get_db_tbl()

    for item in items:
        db.drop_tbl(item['Tables_in_db_blog'])

def make_tbls(db:MySQLManager):
    db.create_required_tbls()


def main():
    db = MySQLManager()
    db.connect()

    make_tbls(db)
    # remove_all_tbls(db)

    db.disconnect()

if __name__ == "__main__":
    main()