
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateTimeField, DecimalField, IntegerField, HiddenField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Optional, DataRequired
from flask_wtf.file import FileRequired, FileField, FileAllowed
from .models import Event, Genre 
import decimal
# event form validation

ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

def validate_ticket_price(_, field):
    if field.data is None:
        raise ValidationError('Invalid date format. Please provide a valid date and time.')
    if field.data <= 0:
        raise ValidationError('Ticket price must be greater than 0.')
    
def validate_start_date(_, field):
    if field.data is None:
        raise ValidationError('Invalid date format. Please provide a valid date and time.')
    if field.data <= datetime.now():
        raise ValidationError('Date must be in the future.')
    
def validate_end_date(form, field):
    if field.data is None:
        raise ValidationError('Invalid date format. Please provide a valid date and time.')
    if field.data <= form.start_date.data:
        raise ValidationError('End date must be after start date.')
    
def validate_quantity(_, field):
    if field.data <= 0:
        raise ValidationError('Quantity must be greater than 0.')

def validate_ticket_availability(form, field):
    event = Event.query.get(form.event_id.data)

    if not event:
        raise ValidationError("Event not found.")

    if field.data > event.available_tickets:
        raise ValidationError(f"There are only {event.available_tickets} tickets available.")

#creates the form for the user to enter the event details
class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired(), Length(min=10)])
    start_date = DateTimeField("Start Date", validators=[InputRequired(), validate_start_date])
    end_date = DateTimeField("End Date", validators=[InputRequired(), validate_end_date])
    ticket_price = DecimalField("Ticket Price", validators=[Optional(), validate_ticket_price])   # not required because some events are free
    venue = StringField("Venue", validators=[InputRequired()])
    genre = SelectField("Genre", choices=[(genre.value, genre.name) for genre in Genre], coerce=int, validators=[InputRequired()])
    image = FileField('Destination Image', validators=[
        FileAllowed(ALLOWED_FILE, message='Only supports PNG, JPG, png, jpg')])
    venue_name = StringField("Venue Name")
    venue_address = StringField("Venue Address", [Optional()])
    venue_capacity = IntegerField("Venue Capacity", [Optional()])
    Edit_Details = SubmitField("Edit Event")
    submit = SubmitField("Create Event")

# authentication form validation
#creates the login information
class LoginForm(FlaskForm):
    user_name = StringField("Username", validators=[InputRequired('Enter your username')],
                            render_kw={"class": "form-control", "placeholder": "e.g., john_doe123"})
    password = PasswordField("Password", validators=[InputRequired('Enter your password')],
                             render_kw={"class": "form-control", "placeholder": "********"})
    submit = SubmitField("Log in", render_kw={"class": "btn btn-primary btn-block"})

 # this is the registration form
class RegisterForm(FlaskForm):
    user_name = StringField("Username", validators=[InputRequired()],
                            render_kw={"class": "form-control", "placeholder": "e.g., john_doe123"})
    email = StringField("Email", validators=[Email("Please enter a valid email")],
                        render_kw={"class": "form-control", "placeholder": "e.g., john.doe@example.com"})
    contact_number = StringField("Phone Number", validators=[InputRequired()],
                                 render_kw={"class": "form-control", "placeholder": "e.g., +1 234 567 8901"})
    address = StringField("Address", validators=[InputRequired()],
                          render_kw={"class": "form-control", "placeholder": "123 Main St, City, Country"})
    password = PasswordField("Password", validators=[InputRequired(), EqualTo('confirm', message="Passwords do not match")],
                             render_kw={"class": "form-control", "placeholder": "********"})
    confirm = PasswordField("Confirm Password", render_kw={"class": "form-control", "placeholder": "********"})
    submit = SubmitField("Get Started!", render_kw={"class": "btn btn-primary btn-block"})

class GetTicketForm(FlaskForm):
    event_id = HiddenField("Event ID", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[InputRequired(), validate_quantity, validate_ticket_availability])
    submit = SubmitField("Get Tickets", render_kw={"class": "btn btn-primary btn-block"})

class CheckoutForm(FlaskForm):
    submit = SubmitField("Checkout", render_kw={"class": "btn btn-primary btn-block"})

class CommentForm(FlaskForm):
    event_id = HiddenField("Event ID", validators=[DataRequired()])
    text = StringField("Comment", name="text", render_kw={"class": "form-control", "placeholder": "Leave a comment..."}, validators=[InputRequired(), Length(max=200)])
    submit = SubmitField("Post", name="submit_comment", render_kw={"class": "btn btn-outline-primary btn-block"})