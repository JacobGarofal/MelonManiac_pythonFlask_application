from flask import Blueprint, flash, render_template, request, url_for, redirect, session
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User
from .forms import LoginForm,RegisterForm
from flask_login import login_user, login_required,logout_user
from . import db

#create a blueprint
bp = Blueprint('auth', __name__)

# This is the registration function to allow users to sign in
@bp.route('/register', methods=['GET', 'POST'])
def register():
    register = RegisterForm()
    #the validation of form is fine, HTTP request is POST
    if (register.validate_on_submit()==True):
            #get username, password and email from the form
            uname = register.user_name.data
            pwd = register.password.data
            email = register.email.data
            contact_number = register.contact_number.data
            address = register.address.data
            #check if a user exists
            user = db.session.scalar(db.select(User).where(User.name==uname))
            if user:#this returns true when user is not None
                flash('Username already exists, please try another', category='warning')
                return redirect(url_for('auth.register'))
            # don't store the password in plaintext!
            pwd_hash = generate_password_hash(pwd)
            #create a new User model object
            new_user = User(name=uname, password_hash=pwd_hash, email=email, contact_number=contact_number, address=address)
            db.session.add(new_user)
            db.session.commit()
            #commit to the database and redirect to HTML page
            return redirect(url_for('main.index'))
    #the else is called when the HTTP request calling this page is a GET
    else:
        return render_template('user.html', form=register, heading='Register', title="Register")

# This is the login function which allows users to sign in to their account
@bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_name = login_form.user_name.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.name == user_name))

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('main.index'))
        else:
            flash('Incorrect username or password', category='warning')

    return render_template('user.html', form=login_form, heading='Login', title="Login")

# this is the logout function which allows users to sign out from their
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", category='success')
    return redirect(url_for('main.index'))