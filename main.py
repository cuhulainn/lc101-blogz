from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:blogz@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'gz7QOJv7OFXVsdfqe4257'

class Blog(db.Model):
    
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255))
  body = db.Column(db.Text)
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  published = db.Column(db.DateTime, default=datetime.utcnow)

  def __init__(self, title, body, owner):
      self.title = title
      self.body = body
      self.owner = owner

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255))
  blogs = db.relationship('Blog', backref = 'owner')

  def __init__(self, email, password):
    self.email = email
    self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route("/login", methods=["GET","POST"])
def login():
  if request.method == "POST":
    # Collect user inputs and identify user by email entered
    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter_by(email=email).first()
    
    # if user is not found:
    if not user:
      flash("User not found, please try again or click the 'Create Account' link in the top right to sign up!", "error")

    # if user is found and password is incorrect:
    if user and user.password != password:
      flash("Account found, but the password is incorrect. Please try again.", "error")

    # If user is found and password is correct, log the user in:
    if user and user.password == password:
      session["email"] = email
      flash("Logged in!", "success")
      return redirect("/newpost")
    
  return render_template("login.html", title="Login - EpiBlog")

@app.route("/signup", methods=["GET","POST"])
def signup():
  if request.method == "POST":
    # Collect user inputs
    email = request.form["email"]
    password = request.form["password"]
    verify = request.form["verify"]

    existing_user = User.query.filter_by(email=email).first()
    
    if existing_user:
      flash("That email address has already been registered, please login!", "error")
    
    if not existing_user and not email or not password or not verify:
      flash("All fields are required.", "error")

    if not existing_user and not password == verify:
      flash("The passwords did not match.", "error")

    if not existing_user and not len(password) >= 3 or not len(email) >= 3:
      flash("All fields must be at least 3 characters long.", "error") 

    if not existing_user and password == verify and len(password) >= 3 and len(email) >= 3 :
      new_user = User(email, password)
      db.session.add(new_user)
      db.session.commit()
      session["email"] = email
      return redirect("/newpost")

  return render_template("signup.html",title="Signup - EpiBlog")

@app.route("/logout")
def logout():
  del session['email']
  return redirect('/blog')

@app.route("/")
def index():
  authors = User.query.all()
  return render_template("index.html",title="Authors - EpiBlog",authors=authors)

@app.route("/blog")
def list_blogs():
  # Handle a GET request that comes without a query param by displaying all blogs:
  if not request.args.get('id') and not request.args.get('user'):
    blogs = Blog.query.order_by(Blog.published.desc()).all()
    return render_template('blog.html',title="Home- EpiBlog", blogs=blogs)
  
  # Handle a GET request that comes with user query parameter to display a dynamic user page:
  if request.args.get('user'):
    owner_id = request.args.get('user')
    blogs = Blog.query.filter_by(owner_id=owner_id).order_by(Blog.published.desc()).all()
    return render_template("authorview.html",title="User- EpiBlog", blogs=blogs)

  # Handle a GET request that comes from /newpost with a query param, use the ID to get the relevant Blog object to pass to the entryview template :
  else:
    blog_id = request.args.get('id')
    blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('entryview.html',title="EpiBlog", blog=blog)

@app.route("/newpost", methods=["GET","POST"])
def new_post():
  # Define the owner 
  owner = User.query.filter_by(email=session['email']).first()
  
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
      new_entry = Blog(blog_title, blog_body, owner)
      db.session.add(new_entry)
      db.session.commit()

      # Now the newly created entry has an ID, so pass it to the redirect:
      return redirect('/blog?id=' + str(new_entry.id))
    
    # else redisplay form with errors:
    else:
      return render_template('newpost.html',title="Add a new blog entry", title_blank=title_blank, body_blank=body_blank, blog_title=blog_title, blog_body=blog_body)

  return render_template('newpost.html',title="New entry - EpiBlog")

if __name__ == '__main__':
    app.run()