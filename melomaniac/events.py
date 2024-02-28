from datetime import datetime
import uuid
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for, flash, current_app as app
from sqlalchemy import func
from flask_wtf.file import FileRequired

from melomaniac import api
from .models import Booking, Event, EventStatus, Genre, Comment, Venue
from .forms import CommentForm, EventForm, GetTicketForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask import jsonify
#additional import:
from flask_login import login_required, current_user
from .utils import utils

# create a blueprint for the 'event' routes
bp = Blueprint('event', __name__, url_prefix='/events')

# Define a custom Jinja2 template filter for natural time display 
@bp.app_template_filter('naturaltime')
def naturaltime_filter(dt):
    return utils.humanize(dt)

# Helper function to add an item to the shopping cart in the session 
def add_to_cart(event_id, quantity, total_price):
    # init cart in session if it doesn't already exist
    if 'cart' not in session:
        session['cart'] = {}
    
    item = {
        'event_id': event_id,
        'event_name': Event.query.get(event_id).name,   # used for showing event name on checkout page
        'quantity': quantity,
        'total_price': total_price
    }

    # add item to cart (gives it a random ID)
    session['cart'][uuid.uuid4().hex] = item
    session.modified = True
    flash("Successfully added to cart.", category='success')
    app.logger.info(f"Added {item} to cart. Cart is now {session['cart']}")

    return jsonify(status='success', cart_length=len(session['cart']))

# Helper function to check and handle file uploads 
def check_upload_file(form):
  #get file data from form  
  fp = form.image.data
  filename = fp.filename
  #get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  #upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH, 'static/image', secure_filename(filename))
  #store relative path in DB as image location in HTML is relative
  db_upload_path = '/static/image/' + secure_filename(filename)
  #save the file and return the db upload path
  fp.save(upload_path)
  app.logger.info(f"Image '{filename}' has been uploaded.")
  return db_upload_path

@bp.route('/my/page/<int:page>')
@bp.route('/my')
@login_required
def my_events(page=1):
    events_query = db.session.query(Event).filter(Event.user_id == current_user.id)
    events_query = events_query.order_by(Event.start_date.asc())
    pagination = events_query.paginate(page=page, per_page=9, error_out=False)
    events = pagination.items
    return render_template('events/my_events.html', my_events=events, title='My Events', EventStatus=EventStatus, Genre=Genre, pagination=pagination)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    form.image.validators += [FileRequired(message='Image cannot be empty')]
    venues = Venue.query.all()  # Retrieve all venues from the database


    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        user_id = current_user.id if current_user else None

        venue_id = int(request.form.get('venue'))  # Get the selected venue ID from the form

        # Retrieve the selected venue object
        venue = Venue.query.get(venue_id)

        # If no venue is selected, create a new venue based on the form input
        if not venue:
            venue = Venue(
                name=form.venue_name.data,
                address=form.venue_address.data,
                capacity=form.venue_capacity.data
            )
            db.session.add(venue)
            db.session.commit()
            
        event = Event(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            ticket_price=form.ticket_price.data,
            venue=venue,  # Assign the venue instance
            image=db_file_path,
            user_id=user_id,
            genre=form.genre.data
        )

        if 'create_event' in request.form:
            db.session.add(event)
            db.session.commit()

            flash('Successfully created a new event', category='success')
            return redirect(url_for('event.create'))
    
    return render_template('events/create.html', form=form, title='Create Event', venues=venues)

# Edit route for modifying the details of a selected event
@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    event = Event.query.get(event_id)
    venues = Venue.query.all()

    if event is None:
        flash('Event not found', category='danger')
        return redirect(url_for('main.index'))

    if event.user_id != current_user.id:
        flash("You don't have permission to edit this event", category='danger')
        return redirect(url_for('main.index'))
    
    if event.status == EventStatus.CANCELLED.value:
        flash("You cannot edit a cancelled event", category='danger')
        return redirect(url_for('main.index'))

    form = EventForm(obj=event)
    if event.image is not None:
       # remove the FileRequired validator
       form.image.validators = [v for v in form.image.validators if not isinstance(v, FileRequired)]

    if request.method == 'POST':
        if 'cancel_event' in request.form:
            event.status = EventStatus.CANCELLED.value
            db.session.commit()
            flash('Event canceled', category='success')
            return redirect(url_for('main.index'))

        if 'Edit_Details' in request.form:
            if 'eventBanner' in request.files:
                db_file_path = check_upload_file(form)
                event.image = db_file_path

            event.name = form.name.data
            event.description = form.description.data
            event.start_date = form.start_date.data
            event.end_date = form.end_date.data
            event.genre = form.genre.data

            if request.form.get('freeEventCheck') == 'on':
                event.ticket_price = 0.0
            else:
                event.ticket_price = form.ticket_price.data

            venue_id = request.form.get('venue_id')

            if venue_id:
                venue_id = int(venue_id)
                venue = Venue.query.get(venue_id)
            else:
                venue = event.venue

            event.venue = venue

            db.session.commit()
            flash('Event details updated', category='success')
            return redirect(url_for('event.edit', event_id=event_id))

    return render_template('events/edit_details.html', form=form, event=event, title='Edit Event', venues=venues)
    
# create route for viewing event details
@bp.route('/<int:event_id>', methods=['GET', 'POST'])
def get_event(event_id):
  event = Event.query.get_or_404(event_id)
  comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.timestamp.desc()).all()

  form = GetTicketForm()
  comment_form = CommentForm()
  form.event_id.data = event.id
  comment_form.event_id.data = event.id
  if request.method == 'POST':
    if 'submit_comment' in request.form and current_user.is_authenticated:
      if comment_form.validate_on_submit():
        comment = Comment(
            user_id=current_user.id,
            event_id=event_id,
            text=comment_form.text.data
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted.', 'success')
        return redirect(url_for('event.get_event', event_id=event_id))
      else:
        flash('Failed to post comment.', 'danger')
    else:
        if form.validate_on_submit():
          id = form.event_id.data
          quantity = form.quantity.data
          add_to_cart(id, quantity, event.ticket_price * quantity)
          return redirect(url_for('event.get_event', event_id=event.id))
        else:
          app.logger.warning(f'Failed to add booking for event {event.id} to cart')
          flash('Failed to add booking to cart', 'danger')

  return render_template('events/view.html', event=event, title=event.name, genres=Genre, comments=comments, status=EventStatus, form=form, comment_form=comment_form)
