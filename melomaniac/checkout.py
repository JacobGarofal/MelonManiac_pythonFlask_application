from flask import Blueprint, current_app as app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from . import bookings

from .forms import CheckoutForm
from .models import Booking, Event
from .tasks import set_events_to_sold_out

from . import db

bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@bp.route('/remove/<cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    item = session['cart'][cart_id]

    session['cart'].pop(cart_id)
    session.modified = True
    app.logger.info(f"Removed {item} from cart. Cart is now {session['cart']}")
    return redirect(url_for('checkout.index'))

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CheckoutForm()
    if 'cart' not in session:
        session['cart'] = {}
    items = session['cart']
    
    if form.validate_on_submit():

        bookings = []

        # create bookings in DB
        for item in items.values():
            event = Event.query.get(item['event_id'])

            # calculate total number of bookings in cart for current event
            total_tickets_in_cart = sum(i['quantity'] for i in items.values() if i['event_id'] == event.id)

            if total_tickets_in_cart > event.available_tickets:
                flash(f'Tickets for "{event.name}" exceed availability. Please adjust your cart.', 'danger')
                return render_template('checkout.html', items=items, form=form, title='Checkout')

            booking = Booking(
                user_id=current_user.id,
                event_id=item['event_id'],
                quantity=item['quantity'],
                total_price=item['total_price']
            )
            bookings.append(booking)
        session['cart'] = {}
        session.modified = True
        db.session.add_all(bookings)
        db.session.commit()
        app.logger.info(f"Created bookings for {current_user} for events {items}")

        flash(f'Your bookings have been successful.', category='success')
        set_events_to_sold_out(db)  # run task check to set sold out event status
        return redirect(url_for('main.index'))
    
    return render_template('checkout.html', items=items, form=form, title='Checkout')

