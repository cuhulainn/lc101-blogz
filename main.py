from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

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
      flash("User not found, please try again, or click the link at right to sign up!", "error")

    # if user is found and password is incorrect:
    if user and user.password != password:
      flash("Account found, but the password is incorrect. Please try again.", "error")

    # If user is found and password is correct, log the user in:
    if user and user.password == password:
      session["email"] = email
      flash("Logged in!", "success")
      return redirect("/newpost")
    
  return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
  if request.method == "POST":
    # Collect user inputs
    email = request.form["email"]
    password = request.form["password"]
    verify = request.form["verify"]

    existing_user = User.query.filter_by(email=email).first()
    
    if not email or not password or not verify:
      flash("You didn't complete the form, please try again!", "error")

    if not password == verify:
      flash("The passwords did not match, please try again!", "error")

    if existing_user:
      flash("That email address has already been registered, please login!", "error")

    if not 3 <= len(password) <= 20 or 3 <= len(email) <= 20:
      flash("The fields must be between 3 and 20 characters, please try again!", "error") 

    if not existing_user and password == verify :
      new_user = User(email, password)
      db.session.add(new_user)
      db.session.commit()
      session["email"] = email
      return redirect("/newpost")

  return render_template("signup.html")

@app.route("/logout")
def logout():
  del session['email']
  return redirect('/blog')

@app.route("/blog")
def list_blogs():
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

  return render_template('newpost.html',title="Add a new blog entry")

if __name__ == '__main__':
    app.run()