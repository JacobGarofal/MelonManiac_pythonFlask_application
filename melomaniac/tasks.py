from .models import Event, EventStatus
from flask import current_app as app

def deactivate_old_events(db):
    app.logger.info("Task started: deactivating old events")
    events = Event.query.filter(Event.end_date < db.func.current_timestamp()).filter(Event.status != EventStatus.INACTIVE.value).all()
    for event in events:
        event.status = EventStatus.INACTIVE.value
    db.session.commit()
    app.logger.info(f"{len(events)} events were deactivated")
    app.logger.info("Task completed: deactivating old events")

def set_events_to_sold_out(db):
    app.logger.info("Task started: setting events to sold out")
    events = Event.query.filter(Event.status == EventStatus.OPEN.value).all()
    for event in events:
        if event.available_tickets <= 0:
            event.status = EventStatus.SOLDOUT.value
    db.session.commit()
    app.logger.info(f"{len(events)} events were set to sold out")
    app.logger.info("Task completed: setting events to sold out")