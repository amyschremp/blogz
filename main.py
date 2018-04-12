from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogging@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)
app.secret_key = '4Dm585aTpt'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    '''convenience route'''
    return redirect('/blog')

@app.route('/blog')
def blog():
    entry_id = request.args.get('id')
    if entry_id:
        blog = Blog.query.get(entry_id)
        return render_template('individual_entry.html', blog = blog)
    else:
        blog_entries = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blog.html', title = "Build-A-Blog", blog_entries = blog_entries)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
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
            new_blog = Blog(entry_title, entry_body)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            return redirect('/')
    
    return render_template('new_post.html', title = "New Blog Entry")

@app.route('/delete', methods=['POST'])
def delete():
    to_be_deleted = request.form['id']
    Blog.query.filter_by(id=to_be_deleted).delete()
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run()