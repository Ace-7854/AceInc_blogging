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
        try:
            db = MySQLManager()
            db.connect()
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            flash("Database connection error. Please try again later.", 'error')
            return redirect(url_for('login'))
        finally:
            if 'user' in session:
                db.disconnect()
                return redirect(url_for('logout'))

        from custom_modules.utils import is_valid_email
        if is_valid_email(username):
            try:
                user = db.get_user_by_email(username)
            except Exception as e:
                flash("Your email was not found. Please try again with a different email.", 'error')
                return redirect(url_for('login'))
            if user is None:
                # return "Unregistered email given, please double check the email given or register"
                flash('Unregistered email given, please double check the email given or register', 'error')
                return redirect(url_for('login'))
            else:
                session['user'] = user
        else:
            try:
                user = db.get_user_by_username(username)
            except Exception as e:
                flash("Your username was not found. Please try again with a different username.", 'error')
                return redirect(url_for('login'))
            if user is None:
                flash("Unregistered username given, please double check the username given or register")
            else:
                session['user'] = user
        db.disconnect()
        try:
            from custom_modules.security_module import check_pass
            if check_pass(session['user']['password'], pwrd):
                session['user']['password'] = None
                # print(session['user'])
                return redirect(url_for('blog_catagories'))
            else:
                flash("Incorrect password given")
        except Exception as e:
            print(f"Error during password check: {e}")
            flash("An error occurred while checking your password. Please try again.", 'error')
    return render_template(
        'login.html'
    )

@app.route('/logout')
def logout():
    session.pop('user', None)
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
        try:
            session['code'] = mail.send_confirmation(session['user']['email'])
        except Exception as e:
            print(f"Error sending confirmation email: {e}")
            flash("An error occurred while sending the confirmation email. Please try again.", 'error')
            return redirect(url_for('register'))

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
        try:
            db.connect()
            user = session['user']
            db.insert_new_user(user['username'], user['email'], user['pwrd'])
            db.disconnect()
        except Exception as e:
            print(f"Error inserting new user: {e}")
            flash("An error occurred while creating your account. Please try again.", 'error')
            return redirect(url_for('register'))

        flash('Account Successfully Made','success')
        return redirect(url_for('logout'))

    return render_template('email_confirmation.html')

@app.route('/new_cat', methods= ['POST', 'GET'])
def new_cat():
    if request.method == "POST":
        cat_name = request.form['cat_name']
        desc = request.form['description']

        from custom_modules.mysql_module import MySQLManager
        db = MySQLManager()
        try:
            db.connect()
            db.insert_new_catagory(cat_name, desc)
            db.disconnect()
        except Exception as e:
            print(f"Error inserting new category: {e}")
            flash("An error occurred while creating the category. Please try again.", 'error')
            return redirect(url_for('new_cat'))

    return render_template('new_cat.html')

@app.route('/new_post/<int:cat_id>', methods=['POST','GET'])
def new_post(cat_id:int):
    try:
        if 'user' not in session:
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        from custom_modules.mysql_module import MySQLManager
        db = MySQLManager()
        try:
            db.connect()
            db.insert_new_post(session['user']['user_id'], title, content)
            post = db.get_post_by_title(title)
            db.insert_link_cat_post(cat_id, post['post_id'])
            db.disconnect()
        except Exception as e:
            print(f"Error inserting new post: {e}")
            flash("An error occurred while creating the post. Please try again.", 'error')
            return redirect(url_for('new_post', cat_id=cat_id))
        return redirect(url_for('blog_catagories'))

    return render_template('new_post.html')

@app.route('/view_blog/<string:slug>')
def view_blog(slug:str):
    try:
        if 'user' not in session:
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    try:
        db.connect()
        post = db.get_post_by_slug(slug)
        comments = db.get_comments_by_post(post['post_id'])
        db.disconnect()
    except Exception as e:
        print(f"Error retrieving post or comments: {e}")
        flash("An error occurred while retrieving the blog post. Please try again later.", 'error')
        return redirect(url_for('blog_catagories'))
    return render_template(
        'view_blog.html',
        post = post,
        comments = comments
    )
@app.route('/submit_comment/<int:post_id>', methods=['POST'])
def submit_comment(post_id):
    try:
        if 'user' not in session:
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()

    # Get form data
    username = request.form.get('username') or None
    content = request.form.get('content')

    # Get post slug for redirect (even if comment fails)
    try:
        slug = db.get_post_slug_by_id(post_id)
    except Exception as e:
        print(f"Error retrieving post slug: {e}")
        flash("An error occurred while retrieving the blog post. Please try again later.", 'error')
        db.disconnect()
        return redirect(url_for('blog_catagories'))
    
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
    try:
        if 'user' not in session:
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))
    
    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()    
    cat = db.get_catagories()
    db.disconnect()

    return render_template(
        'blog_catagories.html',
        categories = cat
    )

@app.route('/profile_page', methods=['GET', 'POST'])
def profile_page():
    try:
        if 'user' not in session:
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']

        from custom_modules.mysql_module import MySQLManager
        db = MySQLManager()
        db.connect()
        db.update_user(session['user']['user_id'], new_username, new_email)
        db.disconnect()

        flash("Profile updated!", "success")


    return render_template(
        'profile_page.html',
        user = session['user'])

@app.route('/blogs/<string:slug>')
def blogs(slug:str):
    try:
        if 'user' not in session:
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    from custom_modules.utils import remove_html_tags
    db = MySQLManager()
    db.connect()
    cat = db.get_cat_by_slug(slug)
    # print(cat)
    posts = db.get_all_posts_by_cat(cat['catagory_id'])
    # print(posts)
    lst_of_psts = []
    for post in posts:
        temp_p = db.get_post_by_id(post['post_id'])
        temp_p['summary'] = remove_html_tags(temp_p['content'][:150]) + '...'
        lst_of_psts.append(temp_p)

    db.disconnect()

    return render_template(
        'list_blogs_cat.html',
        cata = cat,
        psts = lst_of_psts
    )

@app.route('/admin_dash')
def admin_dash():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    return render_template(
        'admin_dash.html'
    )

@app.route('/user_viewer')
def user_viewer():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()
    users = db.get_all_users()
    db.disconnect()

    return render_template(
        'user_viewer.html',
        users=users
    )

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id:int):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return redirect(url_for('logout'))
    except KeyError:
        return redirect(url_for('logout'))

    from custom_modules.mysql_module import MySQLManager
    db = MySQLManager()
    db.connect()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        flag = request.form['flag']

        db.update_user(id=id, username=username, email=email, role=role, flag=flag)
        flash('User updated successfully', 'success')
        return redirect(url_for('user_viewer'))

    user = db.get_user_by_id(id)
    db.disconnect()

    return render_template(
        'edit_user.html',
        user=user
    )


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run()