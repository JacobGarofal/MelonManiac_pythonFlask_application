from enum import Enum
from flask import Blueprint, render_template, request
from sqlalchemy import or_
from .models import Event, EventStatus, Genre
from . import db
from .tasks import deactivate_old_events

bp = Blueprint('main', __name__)

sort_options = {
    'az-up': Event.name.asc(),
    'az-down': Event.name.desc(),
    'date-up': Event.start_date.asc(),
    'date-down': Event.start_date.desc(),
    'price-up': Event.ticket_price.asc(),
    'price-down': Event.ticket_price.desc()
}

@bp.route('/')
@bp.route('/page/<int:page>')
def index(page=1):
    deactivate_old_events(db)
    query_term = request.args.get('query')
    genre_filter = request.args.get('genre')
    status_filter = request.args.get('status')
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')
    min_price = request.args.get('minPrice')
    max_price = request.args.get('maxPrice')
    sort = request.args.get('sort')
    show_ended_events = request.args.get('showEndedEvents')
    
    if sort not in sort_options:
        sort = 'date-up'
    
    query = db.session.query(Event)

    if query_term:
        # Text search
        like = f"%{query_term}%";
        
        query = query.filter(
        or_(
            Event.description.like(like),
            Event.name.like(like)
        )
    )
    
    if not show_ended_events:
        query = query.filter(Event.status != EventStatus.INACTIVE.value)

    if genre_filter:
        genre_filter = Genre[genre_filter.upper()].value
        query = query.filter_by(genre=genre_filter)

    if status_filter:
        status_filter = EventStatus[status_filter.upper()].value
        query = query.filter_by(status=status_filter)

    if from_date:
        query = query.filter(Event.start_date >= from_date)

    if to_date:
        query = query.filter(Event.start_date <= to_date)

    if min_price:
        query = query.filter(Event.ticket_price >= min_price)

    if max_price:
        query = query.filter(Event.ticket_price <= max_price)

    # Sorting
    query = query.order_by(sort_options[sort])

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    events = pagination.items

    filter_args = {
        'query': query_term,
        'genre': genre_filter,
        'status': status_filter,
        'fromDate': from_date,
        'toDate': to_date,
        'minPrice': min_price,
        'maxPrice': max_price,
        'sort': sort,
        'showEndedEvents': show_ended_events
    }

    return render_template('index.html', title="Search Results", events=events, pagination=pagination, EventStatus=EventStatus, Genre=Genre, filter_args=filter_args)
