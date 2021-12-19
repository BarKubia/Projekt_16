from flask import render_template, Response, request, session, flash, redirect, url_for
from blog import app
from faker import Faker
from blog.models import Entry, db
from blog.forms import EntryForm
from blog.forms import LoginForm
import functools


def edit_create_entry(function, entry_id):
   errors = None
   if function:
      form = EntryForm()
      entry = Entry(
         title=form.title.data,
         body=form.body.data,
         is_published=form.is_published.data
         )
            
   else:
      entry = Entry.query.filter_by(id=entry_id).first_or_404()
      form = EntryForm(obj=entry)
   
   if request.method == 'POST':
      if form.validate_on_submit():
         if function:
            db.session.add(entry)
         else:
            form.populate_obj(entry)

         db.session.commit()
      else:
         errors = form.errors
   return render_template("entry_form.html", form=form, errors=errors)


def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
       if session.get('logged_in'):
           return view_func(*args, **kwargs)
       return redirect(url_for('login', next=request.path))
   return check_permissions




@app.route("/")
def index():
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())

   return render_template("homepage.html", all_posts=all_posts)

@app.route("/Faker")
def generate_entries(how_many=10):
   fake = Faker()

   for i in range(how_many):
       post = Entry(
           title=fake.sentence(),
           body='\n'.join(fake.paragraphs(15)),
           is_published=True
       )
       db.session.add(post)
   db.session.commit()
   return Response(status=200)

@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
   return edit_create_entry(function=True, entry_id=None)


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
   return edit_create_entry(function=False, entry_id=entry_id)

@app.route("/delete/<int:entry_id>", methods=["GET", "POST"])
@login_required
def delete_entry(entry_id):
   errors=None
   entry = Entry.query.filter_by(id=entry_id).first_or_404()
   form = EntryForm(obj=entry)

   if request.method == 'POST':
      if form.validate_on_submit():
         db.session.delete(entry)
         db.session.commit()
 
      else:
         errors = form.errors
      return index()
   return render_template("delete.html", form=form, errors=errors)

@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
       if form.validate_on_submit():
           session['logged_in'] = True
           session.permanent = True  # Use cookie to store session.
           flash('You are now logged in.', 'success')
           return redirect(next_url or url_for('index'))
       else:
           errors = form.errors
           
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'POST':
       session.clear()
       flash('You are now logged out.', 'success')
   return redirect(url_for('index'))

# blog/routes.py



@app.route("/drafts/", methods=['GET'])
@login_required
def list_drafts():
   drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
   return render_template("drafts.html", drafts=drafts)