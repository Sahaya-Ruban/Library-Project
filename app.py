from flask import Flask,render_template,flash,session,request,redirect,url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired,Length
from werkzeug.security import generate_password_hash,check_password_hash
import re


app=Flask(__name__)

app.secret_key="Ruban@1234"

url="mongodb://localhost:27017/"

client=MongoClient(url)

db=client.Library_Project

collection=db.details
collection_signup=db.signup

def is_password_strong(Password):
    if len(Password)<8 :
        return False
    if not re.search(r"[a-z]", Password) or not re.search(r"[A-Z]", Password) or not re.search(r"\d",Password):
        return False
    if not re.search(r"[!@#$%^&*()-+{}|\"<>]?", Password):
        return False
    return True

class User:
    def __init__(self,username, password):
        self.username = username
        self.password = password

class signup_form(FlaskForm):
    username=StringField("Username:",validators=[InputRequired(),Length(min=4,max=20)])
    password=PasswordField("Password:",validators=[InputRequired(),Length(min=8,max=50)])
    submit=SubmitField("Signup")

class loginForm(FlaskForm):
    username=StringField("Username:",validators=[InputRequired(),Length(min=4,max=20)])
    password=PasswordField("Password:",validators=[InputRequired(),Length(min=8,max=50)])
    submit=SubmitField("Login")

def isloggedin():
    return "name" in session


@app.route("/signup",methods=["GET","POST"])

def signup():
    form=signup_form()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        if not is_password_strong(password):
            flash("Password should be 8 characters")
            return redirect(url_for("signup"))
        hashed_password=generate_password_hash(password)
        
        old_user=collection_signup.find_one({"Name":username})
        
        if old_user:
            flash("Username already taken")
            return render_template("signin.html",form=form)
        sign_detail=collection_signup.insert_one({"Username":username,"Password":hashed_password})
        
        print(sign_detail)
        flash("Signup successful","Success")
        return redirect(url_for("login"))
    return render_template("signin.html",form=form)

@app.route("/login",methods=["GET","POST"])

def login():
    form=loginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        login_detail=collection_signup.find_one({"Username":username})
        if login_detail and check_password_hash(login_detail["Password"],password):
            user=User(username=login_detail["Username"],password=login_detail["Password"])
            session["name"]=user.username
            return redirect(url_for("home"))
        flash("Invalid Credentials","Danger")
    return render_template("login.html",form=form)


@app.route("/")

def main():
    return render_template("main.html")

@app.route("/home")

def home():
    if isloggedin():
        username=session["name"]
        data=collection.find({"Name":username})
        return render_template("index.html",data=data)

@app.route("/insert",methods=["GET","POST"])

def insert():
    if request.method=="POST":
        Book_name=request.form["Book_name"]
        Book_id=request.form["Book_id"]
        Author_name=request.form["Author_name"]
        Status=request.form["Status"]
        
        Name=session["name"]
        
        lib_dict={"Name":Name,
                  "Book_name":Book_name,
                  "Book_id":Book_id,
                  "Author_name":Author_name,
                  "Status":Status
                  }
        
        collection.insert_one(lib_dict)
        return redirect(url_for("home"))
    
    return render_template("insert.html")  

@app.route("/edit/<string:id>",methods=["GET","POST"])

def edit(id):
    edit_dict={}
    if request.method=="POST":
        
        Book_name=request.form["Book_name"]
        Book_id=request.form["Book_id"]
        Author_name=request.form["Author_name"]
        Status=request.form["Status"]
        
        edit_dict.update({"Book_name":Book_name})
        edit_dict.update({"Book_id":Book_id})
        edit_dict.update({"Author_name":Author_name})
        edit_dict.update({"Status":Status})
        
        collection.update_one({"_id":ObjectId(id)},{"$set":{"Book_name":Book_name,"Book_id":Book_id,"Author_name":Author_name,"Status":Status}})
        return redirect(url_for("home"))
    data=collection.find_one({"_id":ObjectId(id)})
    return render_template("edit.html",data=data)

@app.route("/delete<string:id>")

def delete(id):
    collection.delete_one({"_id":ObjectId(id)})
    return redirect(url_for("home"))  

@app.route("/logout")

def logout():
    session.pop("user",None)
    flash("Loggedout Successfull","Success")
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True)  