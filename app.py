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

        

        db.disconnect()

    return render_template(
        'login.html'
    )

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('login'))

# @app.route('register')
# def register():
#     if request.method == 'POST':
#         pass

#     return render_template(
#         'register.html'
#     )


# app.route('/blog_page')
# def blog_page():
#     if session['user'] not in session:
#         redirect(url_for('logout'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)