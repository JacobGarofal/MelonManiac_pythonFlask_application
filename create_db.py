from melomaniac import db, create_app
from melomaniac.models import *
app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()

# seed scripts run here


quit()