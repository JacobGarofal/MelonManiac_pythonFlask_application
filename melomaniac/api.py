from flask import Blueprint, flash, jsonify, render_template, url_for, redirect, request, session, current_app as app, url_for
from .models import Event, Venue
from . import db
from datetime import datetime
import os
from .forms import EventForm
from werkzeug.utils import secure_filename
import uuid
#additional import:
from flask_login import current_user
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/venues')
def venues():
    venues = db.session.scalars(db.select(Venue)).all()
    return jsonify([venue.to_dict() for venue in venues])


@api_bp.route('/venues', methods=['POST'])
def create_venue():
    data = request.get_json()
    venue = Venue(name=data['name'], address=data['address'], capacity=data['capacity'])
    db.session.add(venue)
    db.session.commit()
    return jsonify(venue.to_dict())


@api_bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            # Save the image file to a specific location (e.g., '/static/image')
            image_path = os.path.join(app.static_folder, 'image', secure_filename(image_file.filename))
            image_file.save(image_path)
            return jsonify({'message': 'Image uploaded successfully', 'image_path': '/static/image/' + secure_filename(image_file.filename)})

    return jsonify({'error': 'Image not uploaded'})


@api_bp.route('/events')
def events():
    events = db.session.scalars(db.select(Event)).all()
    return jsonify([event.to_dicts() for event in events])


@api_bp.route('/events', methods=['POST'])
def create_event():
    
    data = request.get_json()

    user = current_user  # Access the current logged-in user
    user_id = user.id if user else None
    
    venue_id = data.get('venue_id', None)  # Get the venue_id from the form

    try:
        # Parse date and time strings into datetime objects
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S')

    except ValueError as e:
        return jsonify({'error': 'Error parsing date and time strings', 'message': str(e)})
    
     # Update the 'image' field to include the complete path
    image_path = data.get('image')
    if not image_path.startswith('/static/image/'):
        image_path = f'/static/image/{image_path}'


    event = Event(
        name=data['name'],
        description=data['description'],
        start_date=start_date,
        end_date=end_date,
        image=image_path,
        ticket_price=data['ticket_price'],
        genre=data['genre'],
        user_id=user_id,
        venue_id=venue_id

    )

    db.session.add(event)
    db.session.commit()
    flash('Successfully created a new event', category='success')
    return redirect(url_for('event.create'))

@api_bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    session.modified = True
    return redirect(request.referrer or url_for('main.index'))
