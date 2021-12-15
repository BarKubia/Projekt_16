from flask import render_template, Response, request
from blog import app
from faker import Faker
from blog.models import Entry, db
from blog.forms import EntryForm

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
def create_entry():
   return edit_create_entry(function=True, entry_id=999)


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
   return edit_create_entry(function=False, entry_id=entry_id)
