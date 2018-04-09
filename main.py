from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogging@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    # stuck here -- having trouble figure out how to query
    # individual parts of the blog entry. want to display
    # title and body in an html template but am not sure what
    # else to write out other than blog.query.all()
    entries = Blog.query.all()
    return render_template('blog.html', title = "Blog", entries = entries)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']
        new_entry = Blog(blog_title, blog_content)
        db.session.add(new_entry)
        db.session.commit()
        return redirect('/')
    
    return render_template('new_post.html', title = "New Blog Entry")

if __name__ == "__main__":
    app.run()