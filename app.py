from flask import Flask, session, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwrd = request.form['password']

        from custom_modules.mysql_module import MySQLManager

        db = MySQLManager()
        db.connect()

        from custom_modules.utils import is_valid_email
        if is_valid_email(username):
            user = db.get_user_by_email(username)
            print(user)
            if user is None:
                return "Unregistered email given, please double check the email given or register"
            else:
                session['user'] = user
        else:
            user = db.get_user_by_username(username)
            if user is None:
                return "Unregistered username given, please double check the username given or register"
            else:
                session['user'] = user
        db.disconnect()

        from custom_modules.security_module import check_pass
        if check_pass(session['user']['password'], pwrd):
            session['user']['password'] = None
            print(session['user'])
            return redirect(url_for('blog_catagories'))
        else:
            return "Incorrect password given"
    return render_template(
        'login.html'
    )

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username=request.form['username']
        email=request.form['email']
        pwrd=request.form['password']
        re_pwrd=request.form['re-password']

        if pwrd != re_pwrd:
            return "Passwords do not match!"

        session['user'] = {
            'username' : username,
            'email' : email,
            'pwrd' : pwrd
        }

        
        from custom_modules.email_module import EmailManager
        mail = EmailManager()
        session['code'] = mail.send_confirmation(session['user']['email'])

        return redirect(url_for('email_confirmation'))


    return render_template(
        'register.html'
    )

@app.route('/email_confirmation', methods=['GET', 'POST'])
def email_confirmation():
    if request.method == 'POST':
        usr_code = int(request.form['code'])
        if usr_code != session['code']:
            return "INVALID CODE GIVEN"
        
        # print(f"Given code:{session['code']}\n Code retrieved:{usr_code}")

        from custom_modules.mysql_module import MySQLManager
        db = MySQLManager()
        db.connect()
        user = session['user']
        db.insert_new_user(user['username'], user['email'], user['pwrd'])
        db.disconnect()

        return "GO TO LOGIN PAGE AND LOG IN USING THE GIVEN CREDENTIALS" 

    return render_template('email_confirmation.html')

# @app.route('/blog_page/<title:str>')
# def blog_page(title, id):
#     if session['user'] not in session:
#         redirect(url_for('logout'))


#     return render_template('blog_page.html')

@app.route('/blog_catagories')
def blog_catagories():
    if 'user' not in session:
        redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()    
    cat = db.get_catagories()
    db.disconnect()

    return render_template(
        'blog_catagories.html',
        catagories = cat
    )

# @app.route('/profile_page/<username:str>')
# def profile(username:str, id:int):
#     if 'user' not in session:
#         redirect(url_for('logout'))

#     return render_template('profile_page.html')

# @app.route('/blogs/<catagory:str>')
# def blogs(catagory:str, id:int):
#     if 'user' not in session:
#         redirect(url_for('logout'))

#     return render_template('list_blogs_cat.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)