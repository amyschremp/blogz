from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

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

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')


@app.route('/blog')
def blog():
    owner = User.query.filter_by(username=session['username']).first()
    entry_id = request.args.get('id')
    if entry_id:
        blog = Blog.query.get(entry_id)
        return render_template('individual_entry.html', blog = blog)
    else:
        blog_entries = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blog.html', title = "Blogz", blog_entries = blog_entries)

@app.route('/delete', methods=['POST'])
def delete():
    to_be_deleted = request.form['id']
    Blog.query.filter_by(id=to_be_deleted).delete()
    db.session.commit()
    return redirect('/')

@app.route('/')
def index():
    '''convenience route'''
    return redirect('/blog')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist')
    return render_template('login.html', title='Login')

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
            return redirect('/')
    
    return render_template('new_post.html', title = "New Blog Entry")


if __name__ == "__main__":
    app.run()