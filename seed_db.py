from melomaniac import db, create_app
from werkzeug.security import generate_password_hash
from datetime import timedelta, datetime
import random
from faker import Faker
from melomaniac.models import *
import logging
from werkzeug.utils import secure_filename

app = create_app()
ctx = app.app_context()
ctx.push()

# Set logging level for Faker to warning to suppress unnecessary output
logging.getLogger('faker').setLevel(logging.WARNING)

fake = Faker()

# some retrieved from https://www.namesnack.com/guides/music-venue-business-names
venueNames = ["The Triffid", "The Tivoli", "Fortitude Valley Music Hall", "The Empire Hotel", "Roadie Room", "Rolling Spot", "Purple Music Hall", "Drum and Stage",
            "Velvet Venue", "Phoenix Music House", "Garage Stereo", "The Sound Garden", "The Sound Box", "Suncorp Stadium", "The Gabba", "The Zoo", "The Foundry", "The Brightside",
            "Fuzz Music Square", "Popcorn Performance", "Vuvuzela Venue", "Mic Palace", "Greaser", "Tomcat", "The Bearded Lady", "The Milk Factory", "The Junk Bar",
            "The Tramway", "The Outpost", "The Tramway", "Vinnie's Dive Bar", "The End of the World Bar", "Beyond the Pale", "Dendy Cinemas"]

def randomUser():
    user = User(name=fake.name(), email=fake.email(), password_hash=generate_password_hash(fake.password()), contact_number=fake.phone_number(), address=fake.address())
    return user

def randomVenue(name):
    venue = Venue(name=name, address=fake.address(), capacity=random.randint(30, 1000))
    return venue

def randomEvent(users, venues, image_name):
    user = random.choice(users)
    venue = random.choice(venues)

    names = [f"A night with {user.name}", f"The {user.name} Experience", f"{user.name} Live", f"{user.name} in Concert", f"{user.name} at {venue.name}",
             f"{venue.name} Festival", f"{venue.name} Concert", f"{venue.name} Live", f"{venue.name} Music Festival", f"{venue.name} Music Concert",
             f"{venue.name} Music Experience", f"{venue.name} Music Night", f"{venue.name} Music Party", f"{venue.name} Music Show", f"{venue.name} Music Fest",
             f"{user.name}'s Rhythmic Odyssey", f"{user.name} Unplugged at {venue.name}", f"Sounds of the City with {user.name}", f"{user.name}'s Musical Renaissance",
             f"The {user.name} Chronicles", f"Encore: {user.name} at {venue.name}", f"Under the Stars with {user.name}", f"{venue.name} Presents: An Evening with {user.name}",
             f"{user.name}: Beyond the Music", f"Journey Through Sound with {user.name}"]
    
    name = random.choice(names)
    
    hourDif = timedelta(hours=random.randint(1, 72))    # how long each event lasts - between 1 - 72 hours

    descriptionLines = [f"{user.name} is a {random.choice(['singer', 'musician', 'band'])} from {fake.city()}.",
                        f"For the next {hourDif} hours, {user.name} will be performing at {venue.name}.",
                        f"Come down to {venue.name} to see {user.name} perform live!",
                        f"Prepare for liftoff with {user.name}, as we proudly present our {name}, a sonic innovation promising to bend your mind with captivating melodies which will awaken parts of your brain you didn't know needed awakening.",
                        "This electrifying event promises to push boundaries and challenge the norms of what you thought was sound.",
                        "This is a night you won't want to miss!",
                        "Tickets are limited, so get in quick!",
                        f"{user.name} at the frontier of this auditory revolution brings a blend of genres that defy categorisation.",
                        f"{name} is not just a concert, it's an experience that will transport you to another dimension, where up is sound and down is not real.",
                        f"Whether you're an avid follower or simply someone craving the exhilaration of live performances, {name} promises an unforgettable night that transcends music.",
                        f"Come and see what all the fuss is about!",
                        f"Come and see what the critics are raving about!",
                        "Don't miss your chance to be a part of this!",
                        f"From humble beginnings in {fake.city()}, {user.name} has risen to the global stage, wowing audiences with their unique sound.",
                        f"Join us for an evening of talent as {user.name} brings to {venue.name} a musical journey like no other.",
                        "The sound, the lights, the energy - this event promises a show that will be remembered for ages.",
                        f"People have travelled from all over just to catch a glimpse of {user.name} in action. Now's your chance!",
                        f"Every note tells a story, dive deep into the world of {user.name} and experience the magic first hand.",
                        f"{name} is set to be the musical phenomena of the year, you don't want to miss this!",
                        "An evening where music meets passion, and dreams come alive on stage.",
                        f"Known for their groundbreaking performances, {user.name} is ready to light the stage on fire at {venue.name}.",
                        "This isn't just another music event; it's a celebration of art, life, and the undying spirit of all musicians.",
                        f"From the heartbeats of drums to the soulful tunes of the guitar, every moment at {name} will resonate with your inner rhythm."]

    start_time = fake.date_time_between(start_date='-1y', end_date='+1y')
    publish_time = min(start_time - timedelta(days=random.randint(1, 7)), datetime.now() - timedelta(days=random.randint(1, 7)))  # events are published between 1 to 7 days before they start or 1-7 days ago, whichever is earlier
    end_time = start_time + hourDif
    
    event = Event(
        name=name,
        description=' '.join(random.sample(descriptionLines, 4)),
        user_id=user.id,
        venue_id=venue.id,
        publish_date=publish_time,
        start_date=start_time,
        end_date=end_time,
        genre=random.choice(list(Genre)).value,
        image=f'/static/image/{secure_filename(image_name)}',
        ticket_price=float(random.randint(0, 100)),
        status=random.choice([status for status in EventStatus if status != EventStatus.INACTIVE]).value
    )
    
    return event

def randomComment(users, events):
    user = random.choice(users)
    event = random.choice(events)

    date = fake.date_time_between(start_date=event.publish_date, end_date=datetime.now())

    commentPool = [
        "Had a blast last time! Can't wait.",
        "The last event was amazing. Looking forward to this.",
        "I've got my tickets already!",
        "Hope it's as good as the last one.",
        "Can't wait to hear some great music 🤠",
        "Don't waste your time. It's not worth it 😴",
        "These guys are ripoffs!",
        "1 star, never again",
        "I'm so excited!",
        "I'm so disappointed.",
        "These guys stole my money and ran 🤬",
        "I'm so glad I got tickets to this!",
        "Wait, these guys are still around?",
        "Absolutely amazing performance last time. Hope for a repeat!",
        "Heard so much about this event, finally get to see it!",
        "The opening act last time was so bad lol 😫",
        "Not sure what the hype was about, felt pretty mid",
        f"Traveling all the way from {fake.city()} just to see this. It better be good!",
        "The crowd was perfect last time.",
        "If it's anything like their last show then i'm a fan!",
        "Heard mixed reviews, but I'm willing to give it a shot.",
        "Bring it on! Can't wait for round two!!",
        "Honestly, their old gigs were better. Hope they step it up this time.",
        f"I HATE {event.user.name} !!!",
        f"Really? {event.venue.name} was the best you guys could do 💀",
        "Can't wait for this event! Got my tickets the moment they went on sale. 🎶",
        f"I've seen {event.user.name} three times now, and they never disappoint! Can't wait!",
        "Anyone going from the west side? Looking for carpool options.",
        "Saw a sneak peek of their setlist. Trust me, you guys are in for a treat!",
        "This is going to be my first concert. Super excited! 🤩"
    ]
    
    comment = Comment(
        user_id=user.id,
        event_id=event.id,
        text=random.choice(commentPool),
        timestamp=date
    )
    
    return comment

def randomBooking(users, events):
    user = random.choice(users)
    event = random.choice(events)
    
    qty = random.randint(1, 5)
    
    booking = Booking(
        user_id=user.id,
        event_id=event.id,
        quantity=qty,
        total_price=qty * event.ticket_price
    )
    
    return booking

# commits need to be done after each step to ensure that the ids are generated properly
print("Seed script running...")
print("Creating users...")
users = [randomUser() for _ in range(30)]
db.session.add_all(users)
db.session.commit()

print("Creating venues...")
venues = [randomVenue(venueNames[i]) for i in range(len(venueNames))]
db.session.add_all(venues)
db.session.commit()

print("Creating events...")
events = [randomEvent(users, venues, f'image_{i}.jpg') for i in range(1, 51)]
db.session.add_all(events)
db.session.commit()

print("Creating comments...")
comments = [randomComment(users, events) for _ in range(100)]

print("Creating bookings...")
bookings = [randomBooking(users, events) for _ in range(75)]

# Add everything else to the database
db.session.add_all(comments)
db.session.add_all(bookings)
db.session.commit()