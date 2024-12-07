from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField
from datetime import datetime as dt, timedelta

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class UploadForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    number = StringField("Number", validators=[DataRequired()])
    image = FileField("Image", validators=[DataRequired()])
    submit = SubmitField("ADD")

class CheckoutForm(FlaskForm):
    delivery_options = SelectField(
        "Delivery Date", 
        choices=[
            ('1', f"{(dt.now() + timedelta(days=1)).strftime("%B %d, %Y")}"),
            ('2', f"{(dt.now() + timedelta(days=3)).strftime("%B %d, %Y")}"),
            ('3', f"{(dt.now() + timedelta(days=5)).strftime("%B %d, %Y")}")
        ],
        validate_choice=False
    )
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("OK")

class Confirm(FlaskForm):
    feedback = CKEditorField("Feedback")
    accept = SubmitField("Accept")
    refuse = SubmitField("Refuse")

class PlaceOrder(FlaskForm):
    submit = SubmitField("Place Your Order")