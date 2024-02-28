from flask import Blueprint, current_app as app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from melomaniac.models import Booking, Event, EventStatus, Genre
from melomaniac.tasks import deactivate_old_events

from . import db

bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bp.route('/page/<int:page>')
@bp.route('/')
@login_required
def index(page=1):
    show_past = request.args.get('showPast', default=False, type=bool)
    deactivate_old_events(db)

    bookings_query = db.session.query(Booking).filter(Booking.user_id == current_user.id).join(Event, Booking.event_id == Event.id)

    if show_past:
        bookings_query = bookings_query.filter(Event.status == EventStatus.INACTIVE.value)\
                                       .order_by(Event.start_date.desc())
    else:
        bookings_query = bookings_query.filter(Event.status != EventStatus.INACTIVE.value)\
                                       .order_by(Event.start_date.asc())

    pagination = bookings_query.paginate(page=page, per_page=9, error_out=False)
    bookings = pagination.items

    return render_template('bookings.html', bookings=bookings, title='Bookings', pagination=pagination, show_past=show_past, EventStatus=EventStatus, Genre=Genre)