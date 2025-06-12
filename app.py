from flask import Flask, session, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if request.method == 'POST':
        pass

    return render_template(
        'login.html'
    )

@app.route('register')
def register():
    if request.method == 'POST':
        pass

    return render_template(
        'register.html'
    )


app.route('/blog_page')
def blog_page():
    if session['user'] not in session:
        redirect(url_for('logout'))


    