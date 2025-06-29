"""THIS FILE IS FOR RUNNING BACKEND COMMANDS FOR THE SERVER 
AND ENSURING FUNCTIONALITY OF FUNCTIONS ASWELL AS TESTING"""
from custom_modules.mysql_module import MySQLManager

def remove_all_tbls(db:MySQLManager):
    items = db.get_db_tbl()

    for item in items:
        db.drop_tbl(item['Tables_in_db_blog'])

def make_tbls(db:MySQLManager):
    db.create_required_tbls()

def make_cats(db:MySQLManager):
    db.insert_new_catagory("Personal Projects", "This catagory is for all of my developed and finalised software with an explanation as to how and why it functions")
    db.insert_new_catagory("Life Updates", "This catagory is updates to my life like major events or changes")
    db.insert_new_catagory("The Info Abyss", "This catagory is for random things that I end up dumping on the platform")
    db.insert_new_catagory("Current Projects", "This area is for unfinished and being worked on projects")

def make_mock_posts(db:MySQLManager):
    post_one = {
        'id': 1,
        'title' : "Mock post one",
        'content': "This is a mock post"
    }

    post_two = {
        'id':1,
        'title':"Mock post two",
        'content':"This is a mock post"
    }

    lst = [post_one, post_two]

    for post in lst:
        db.insert_new_post(post['id'], post['title'], post['content'])
    
    pst_ids = []
    for post in lst:
        pst_ids.append(db.get_post_by_title(post['title']))

    print(pst_ids)

    for id in pst_ids:
        db.insert_link_cat_post(3, id['post_id'])


def main():
    db = MySQLManager()
    db.connect()

    # make_tbls(db)
    # remove_all_tbls(db)
    # make_cats(db)
    # make_mock_posts(db)

    db.disconnect()

if __name__ == "__main__":
    main()