from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
import os
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
    logout_user,
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
app.config["SECRET_KEY"] = os.urandom(64)


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "signin"


@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)


# Flask -> {flask_sqlalchemy } -> Database (sqlite , postgres , mysql)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Welcome to my Flask application"


list = ["Apple", "Banana", "Orange"]

students = [
    {"name": "student_1", "roll_no": 1, "Age": 22},
    {"name": "student_2", "roll_no": 2, "Age": 23},
]


# GET , POST , PUT , DELETE


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        password = request.form["user_password"]

        user = Users(name=name, password=generate_password_hash(password), email=email)
        db.session.add(user)
        db.session.commit()

        return f"Name: {name} , Email: {email}"

    return render_template("form.html")


class Signin(FlaskForm):
    email = StringField("Enter Email : ", [validators.DataRequired()])
    password = PasswordField("Enter Password : ", [validators.DataRequired()])
    submit = SubmitField("Login")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = Signin()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("protected"))

    return render_template("signin.html", form=form)


@app.route("/protected")
@login_required
def protected():
    return render_template("home.html", user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user
    return redirect(url_for("signin"))


@app.route("/users", methods=["GET"])
def users():
    users = Users.query.all()  # users is a list of user objects
    print(users)
    return render_template("users.html", users=users)


# Create , Read , Update , Delete
@app.route("/user_get/<int:user_id>", methods=["GET"])
def user_get(user_id):
    user = Users.query.get(user_id)
    return f"Name: {user.name} Age: {user.age} Email: {user.email}"


@app.route("/user_update/<int:user_id>", methods=["POST", "GET"])
def user_update(user_id):
    user = Users.query.get(user_id)
    if request.method == "POST":
        name = request.form["user_name"]
        email = request.form["user_email"]
        age = request.form["user_age"]

        user.name = name
        user.email = email
        user.age = age

        db.session.commit()
        return f"User {name} updated successfully!"
    return render_template("updateform.html", user=user)


@app.route("/user_delete/<int:user_id>", methods=["GET"])
def user_delete(user_id):
    user = Users.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return "User Deleted !"


@app.route("/index")
def index():
    return render_template("index.html", fruits=list)


@app.route("/students")
def student():
    return render_template("student.html", students=students)


@app.route("/admin")
@app.route("/admin/<name>")
def admin(name=None):
    return render_template("admin.html", variable=name)


@app.route("/user/<path:username>")
def user(username):
    return f"Hello {escape(username)}"


@app.route("/integer/<int:integer>")
def integer(integer):
    return f"The integer is {integer}"


@app.route("/image")
def image():
    return render_template("image.html")


if __name__ == "__main__":
    app.run(debug=True)
