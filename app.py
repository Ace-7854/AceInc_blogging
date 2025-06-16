from flask import Flask, session, render_template, request, redirect, url_for, flash

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
            flash('Passwords did not match', 'error')
            return redirect(url_for('register'))

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
            flash('Code was incorrect', 'error')
            return redirect(url_for('email_confirmation'))

        from custom_modules.mysql_module import MySQLManager
        db = MySQLManager()
        db.connect()
        user = session['user']
        db.insert_new_user(user['username'], user['email'], user['pwrd'])
        db.disconnect()

        flash('Account Successfully Made','success')
        return redirect(url_for('logout'))

    return render_template('email_confirmation.html')

@app.route('/view_blog/<string:slug>')
def view_blog(slug:str):
    if 'user' not in session:
        redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()
    post = db.get_post_by_slug(slug)
    comments = db.get_comments_by_post(post['post_id'])
    db.disconnect()

    return render_template(
        'view_blog.html',
        post = post,
        comments = comments
    )
@app.route('/submit_comment/<int:post_id>', methods=['POST'])
def submit_comment(post_id):
    if 'user' not in session:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()

    # Get form data
    username = request.form.get('username') or None
    content = request.form.get('content')

    # Get post slug for redirect (even if comment fails)
    slug = db.get_post_slug_by_id(post_id)

    if not content.strip():
        flash("Comment cannot be empty.", "warning")
        db.disconnect()
        return redirect(url_for('view_blog', slug=slug))

    try:
        db.insert_new_comment(post_id, session['user']['user_id'], username, content)
    except Exception as e:
        print(f"❌ Error inserting comment: {e}")
        flash("Something went wrong while posting your comment.", "danger")
    finally:
        db.disconnect()

    flash("Your comment was posted successfully!", "success")
    return redirect(url_for('view_blog', slug=slug))

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
        categories = cat
    )

# @app.route('/profile_page/<username:str>')
# def profile(username:str):
#     if 'user' not in session:
#         return redirect(url_for('logout'))

    

#     return render_template('profile_page.html')

@app.route('/blogs/<string:slug>')
def blogs(slug:str):
    if 'user' not in session:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()
    cat = db.get_cat_by_slug(slug)
    print(cat)
    posts = db.get_all_posts_by_cat(cat['catagory_id'])
    print(posts)

    lst_of_psts = []
    for post in posts:
        temp_p = db.get_post_by_id(post['post_id'])
        lst_of_psts.append(temp_p)

    db.disconnect()

    return render_template(
        'list_blogs_cat.html',
        cata = cat,
        psts = lst_of_psts
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)