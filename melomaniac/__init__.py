#from package import Class
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import logging
from flask_wtf.csrf import CSRFProtect

db=SQLAlchemy()

#create a function that creates a web application
# a web server will run this web application
def create_app():
  
    app=Flask(__name__)  # this is the name of the module/package that is calling this app
    app.secret_key='somesecretgoeshere'
    #set the app configuration data 
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.sqlite'
    #initialise db with flask app
    db.init_app(app)

    csrf = CSRFProtect(app)
    bootstrap = Bootstrap5(app)

    #this is a much safer way to store passwords
    Bcrypt(app)

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    
    # TODO: RE: Flask-Login
    #initialize the login manager
    login_manager = LoginManager()
    
    #set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    #create a user loader function takes userid and returns User
    from .models import User  # importing here to avoid circular references
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    #importing views module here to avoid circular references
    # a common practice.
    from . import views
    app.register_blueprint(views.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import events
    app.register_blueprint(events.bp)

    from . import api
    app.register_blueprint(api.api_bp)

    from . import checkout
    app.register_blueprint(checkout.bp)

    from . import bookings
    app.register_blueprint(bookings.bp)

    #function to handle 
    @app.errorhandler(404) 
    @app.errorhandler(500)
    @app.errorhandler(400)  
    @app.errorhandler(401)
    # inbuilt function which takes error as parameter 
    def not_found(e): 
      return render_template("error.html", error=e, title="Error"), e.code
    
    return app
