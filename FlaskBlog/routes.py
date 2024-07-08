
from FlaskBlog import app,db,bcrypt
from flask import render_template,redirect,request,flash,url_for,abort
from FlaskBlog.form import RegistrationForm,LoginForm,updateForm,newPostForm
from FlaskBlog.models import User, Post
from flask_login import login_user, current_user,logout_user,login_required
import secrets
import os
from PIL import Image
import datetime

@app.route("/")
@app.route("/home")
def home():
    posts= Post.query.all()
    return render_template("home.html",posts=posts,)
@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
         return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw= bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user= User(username=form.username.data, email=form.email.data, password= hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("You account was successfully created,you can log in now ", 'success')
        return redirect(url_for("login"))
    return render_template("register.html",title="register", form=form)
    
@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
         return redirect(url_for("home"))
    form = LoginForm()
    next_page= request.args.get("next")  
    if form.validate_on_submit():
            user= User.query.filter_by(email= form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user,remember=form.remember.data)
                if next_page:    
                    return redirect(next_page)
                else:
                    return redirect(url_for("home"))
            else:
                flash("Log in unsuccessful check your email and password " ,'danger')
                
    return render_template("login.html",title="login", form=form)

@app.route("/logout")
def logout():
     logout_user()
     return redirect(url_for("home"))


def save_picture(form_picture):
     random_hex= secrets.token_hex(8)
     _, ext= os.path.splitext(form_picture.filename)
     profile_fn= random_hex + ext
     output_size= (125,125)
     i= Image.open(form_picture)
     i.thumbnail(output_size)
     file_path= os.path.join(app.root_path, "static/profile_pics", profile_fn)
     i.save(file_path)
     return profile_fn
     
@app.route("/account", methods=["GET","POST"])
@login_required
def account():
     form= updateForm()
     if form.validate_on_submit():
          if form.picture.data:
               previous_picture= current_user.image_file
               previous_picture_path= os.path.join(app.root_path, "static/profile_pics", previous_picture)
               current_user.image_file= save_picture(form.picture.data)
               os.remove(previous_picture_path)
               
          current_user.username= form.username.data
          current_user.email= form.email.data
          db.session.commit()
          flash("Your Profile info was successfully updated", "success")
          return redirect(url_for("account"))
     
     elif request.method=="GET":
          form.username.data= current_user.username
          form.email.data= current_user.email 
     image= url_for("static", filename=f"profile_pics/{current_user.image_file}") 
     return render_template("account.html",title="account", image= image, form= form)
    

@app.route("/post/new", methods=["GET","POST"])
@login_required
def new_post():
     form= newPostForm()
     if form.validate_on_submit():
          newPost= Post(user_id=current_user.id,title=form.title.data, content=form.content.data)
          db.session.add(newPost)
          db.session.commit()
          flash("Post was created successfully", "success")
          return redirect(url_for("home"))
     return render_template("create_post.html",title="newPost",form= form)

@app.route("/post/<int:post_id>")
def post(post_id):
     post= Post.query.get_or_404(post_id)
     return render_template("post.html",title= post.title,post=post)

@app.route("/post/<int:post_id>/update", methods=["GET","POST"])
@login_required
def update_post(post_id):
     post= Post.query.get_or_404(post_id)
     if post.author != current_user:
          abort(403)
     form= newPostForm()
     if form.validate_on_submit():
          post.title= form.title.data
          post.content= form.content.data
          db.session.commit()
          flash("You  post was successfully updated", "success")
          return redirect(url_for("post", post_id=post.id))
     elif request.method== "GET":
          form.title.data= post.title
          form.content.data= post.content
     return render_template("update_post.html", title=f"update {post.title}", form=form,post=post.id)

@app.route("/post/<int:post_id>/delete", methods=["GET","POST"])
@login_required
def delete_post(post_id):
     post= Post.query.get_or_404(post_id)
     if post.author != current_user:
          abort(403)
     db.session.delete(post)
     db.session.commit()
     flash("Post was successfully deleted","success")
     return redirect (url_for("home"))