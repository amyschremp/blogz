from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:6Igb7BIYuxeMEWEt@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)
app.secret_key = '4Dm585aTpt'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, owner_id, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner_id
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['blog', 'index', 'login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog')
def blog():
    entry_id = request.args.get('id')
    user_id = request.args.get('user')
    if session:
        current_user = session['username']
   
    # are they trying to view an individual post?
    if entry_id:
        blog = Blog.query.filter_by(id = entry_id).first()
        user_id = blog.owner_id
        user = User.query.get(user_id)
        return render_template('individual_entry.html', blog=blog, user=user, User=User)
    # are they trying to view a specific user's page?
    elif user_id:
        user = User.query.filter_by(id = user_id).first()
        blog_entries = Blog.query.filter_by(owner=user).order_by(Blog.id.desc()).all()
        return render_template('user.html', title = "{0}'s Blogz".format(user.username), blog_entries=blog_entries, user=user, User=User)
    # if not, show them all the posts by the current_user.
    else:
        blog_entries = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blog.html', title = "All Blogz", blog_entries=blog_entries, User = User)


@app.route('/delete', methods=['POST'])
def delete():
    to_be_deleted = request.form['id']
    Blog.query.filter_by(id=to_be_deleted).delete()
    db.session.commit()
    return redirect('/blog')


@app.route('/')
def index():
    authors = User.query.order_by(User.id.desc()).all()
    return render_template('index.html', authors=authors, title="All Authors", User=User)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if not username or not password:
            flash('Please enter a username and password.')
        elif not existing_user:
            flash('Username does not exist.')
        elif not password == existing_user.password:
            flash('Password is incorrect.')
        elif existing_user and existing_user.password == password:
            session['username'] = username
            return redirect('/newpost')
    return render_template('login.html', title='Login', User=User)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        entry_title = request.form['blog_title']
        entry_body = request.form['blog_content']
        if not entry_title or not entry_body:
            flash('Please enter both a title and a body.')
        elif len(entry_title) > 120:
            flash('Please enter a title of 120 characters or less.')
        elif len(entry_body) > 2000:
            flash('Please enter a body of 2000 characters or less.')
        else:
            new_blog = Blog(entry_title, entry_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            return redirect('/blog?id={}'.format(new_blog_id))
    
    return render_template('new_post.html', title = "New Blog Entry", User=User)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify_password']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if not username:
                flash('Please enter a username.')
            elif not password:
                flash('Please enter a password.')
            elif not verify:
                flash('Please verify your password.')
            elif not password == verify:
                flash('Passwords do not match.')
            elif len(username) > 30 or len(username) < 3:
                flash('Please enter a username between 3 and 30 characters.')
            elif len(password) > 30 or len(password) < 3:
                flash('Please enter a password between 3 and 30 characters.')
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
        else:
            flash("Username already exists.")
    return render_template('signup.html', title = "Sign Up for Blogz", User=User)


if __name__ == "__main__":
    app.run()