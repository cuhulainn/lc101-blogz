from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog")
def index():
  # when the GET request comes without a query param:
  if not request.args.get('id'):
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build-a-blog", blogs=blogs)
  
  # when the GET request comes from /newpost with a query param, use the ID to get the relevant Blog object to pass to the entryview template :
  else:
    blog_id = request.args.get('id')
    blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('entryview.html', blog=blog)

@app.route("/newpost", methods=["GET","POST"])
def new_post():
  # For POST requests:
  if request.method == "POST":

    # Collect user inputs:
    blog_title = request.form['blog_title']
    blog_body = request.form['blog_body']

    # Set up falsy default error variables:
    title_blank = ""
    body_blank = ""
    
    #Check for blank forms:
    if not blog_title:
      title_blank = "Please tell us the subject of your ramblings!"

    if not blog_body:
      body_blank = "Just a title?!  If you don't have anything to say, why are you blogging?  (Please enter text for your blog entry!)"
    
    # If no errors, post entry and redirect to blog page with query param:
    if not title_blank and not body_blank:
      new_entry = Blog(blog_title, blog_body)
      db.session.add(new_entry)
      db.session.commit()

      # Now the newly created entry has an ID, so pass it to the redirect:
      return redirect('/blog?id=' + str(new_entry.id))
    
    # else redisplay form with errors:
    else:
      return render_template('newpost.html',title="Add a new blog entry", title_blank=title_blank, body_blank=body_blank, blog_title=blog_title, blog_body=blog_body)

  return render_template('newpost.html',title="Add a new blog entry")

if __name__ == '__main__':
    app.run()