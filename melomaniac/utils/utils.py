from datetime import datetime

def humanize(timestamp: datetime):
    delta = datetime.utcnow() - timestamp

    if delta.days > 365:
        y = delta.days // 365
        return f"{y} {'year' if y == 1 else 'years'} ago"
    if delta.days > 30:
        m = delta.days // 30
        return f"{m} {'month' if m == 1 else 'months'} ago"
    if delta.days > 0:
        d = delta.days
        return f"{d} {'day' if d == 1 else 'days'} ago"
    if delta.seconds > 3600:
        h = delta.seconds // 3600
        return f"{h} {'hour' if h == 1 else 'hours'} ago"
    if delta.seconds > 60:
        m = delta.seconds // 60
        return f"{m} {'minute' if m == 1 else 'minutes'} ago"
    s = delta.seconds
    if delta.seconds < 5:
        return "just now"
    return f"{s} seconds ago"
