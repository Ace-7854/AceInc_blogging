from flask import Flask, session, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login')
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
            return redirect(url_for('blog_page'))
        else:
            return "Incorrect password given"

               

    return render_template(
        'login.html'
    )

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('login'))

@app.route('/register')
def register():
    if request.method == 'POST':
        username=request.form['username']
        email=request.form['email']
        pwrd=request.form['password']
        re_pwrd=request.form['re-password']

        if pwrd != re_pwrd:
            return "Passwords do not match!"


    return render_template(
        'register.html'
    )

# @app.route('/blog_page/<title:str>')
# def blog_page(title, id):
#     if session['user'] not in session:
#         redirect(url_for('logout'))


#     return render_template('blog_page.html')

# @app.route('/blog_catagories')
# def blog_cat():
#     if session['user'] not in session:
#         redirect(url_for('logout'))

#     return render_template('blog_catagories.html')

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