from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL
from wtforms import StringField,SubmitField, PasswordField, BooleanField
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    
class CafesForm(FlaskForm):
        name = StringField("Name", validators=[DataRequired(message='Please specify a name')])
        map_url = StringField("Map Url", validators=[DataRequired(), URL(message="Please provide a working url")])
        img_url = StringField("Img Url", validators=[DataRequired(), URL(message="Please provide a working url")])
        location = StringField("Location", validators=[DataRequired(message='Please specify a location')])
        has_wifi = BooleanField("Wifi")
        has_toilet = BooleanField("Toilet")
        has_socket = BooleanField("Socket")
        can_take_calls = BooleanField("Calls")
        seats = StringField("Seats", validators=[DataRequired(message='Please specify the number of seats')])
        coffee_price = StringField("Coffee Price", validators=[DataRequired(message='Please specify the coffee price')])
        submit = SubmitField("Submit Cafe")
class RegisterForm(FlaskForm):
        email = StringField("Email", validators=[DataRequired()])
        password = PasswordField("Password", validators=[DataRequired()])
        name = StringField("Name", validators=[DataRequired()])
        submit = SubmitField("Sign Me Up!")
        
        def to_dict(self):
            return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route('/')
def home():
    all_cafes = Cafe.query.all()
    return render_template('index.html', cafes=all_cafes)
@app.route("/new-post",methods=['GET', 'POST'])
def add():
    new_post = CafesForm()
    if new_post.validate_on_submit():
        new_cafe = Cafe(
            name=new_post.name.data,
            map_url=new_post.map_url.data,
            img_url=new_post.img_url.data,
            location=new_post.location.data,
            seats=new_post.seats.data,
            has_toilet=new_post.has_toilet.data,
            has_wifi=new_post.has_wifi.data,
            has_sockets=new_post.has_socket.data, 
            can_take_calls=new_post.can_take_calls.data,
            coffee_price=new_post.coffee_price.data
        )
        
        # Tambahkan instance baru ke session dan komit
        db.session.add(new_cafe)
        db.session.commit()
        return redirect (url_for("home"))
    return render_template("cafes.html",new_post = new_post)
@app.route("/delete")
def delete():
    cafe_id = request.args.get('id')
    
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))
@app.route("/register")
def register():
    register = RegisterForm()
    if register.validate_on_submit():
        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == register.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            register.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=register.email.data,
            name=register.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=register, current_user=current_user)
if __name__ == '__main__':
    app.run(debug=True,port=5011)