from models import db, Team, Event, Placement, User, Access
from application import app

app.app_context()

# Drop all then recreate all tables
db.drop_all()
db.create_all()
db.session.commit()

# adding unit information

db.session.add(Team(id=1,  name="2-35 IN",   score=0))
db.session.add(Team(id=2,  name="HHBN",      score=0))
db.session.add(Team(id=3,  name="325 BSB",   score=0))
db.session.add(Team(id=4,  name="2-25 AVN",  score=0))
db.session.add(Team(id=5,  name="1-27 IN",   score=0))
db.session.add(Team(id=6,  name="65 BEB",    score=0))
db.session.add(Team(id=7,  name="3-7 FA",    score=0))
db.session.add(Team(id=8,  name="2/14 CAV",  score=0))
db.session.add(Team(id=9,  name="524 CSSB",  score=0))
db.session.add(Team(id=10, name="225 BSB",   score=0))
db.session.add(Team(id=11, name="3-25 AVN",  score=0))
db.session.add(Team(id=12, name="29 BEB",    score=0))
db.session.add(Team(id=13, name="2-11 FA",   score=0))
db.session.add(Team(id=14, name="1-21 IN",   score=0))
db.session.add(Team(id=15, name="2-6 CAV",   score=0))
db.session.add(Team(id=16, name="2-27 IN",   score=0))
db.session.add(Team(id=17, name="25th STB",  score=0))
db.session.add(Team(id=18, name="3/4 CAV",   score=0))
db.session.add(Team(id=19, name="209th ASB", score=0))
db.session.commit()


# adding all event information
db.session.add(Event(id=0, name="Admin", weight=0))

db.session.add(Event(id=1,  weight=1, name="Flag Football"))
db.session.add(Event(id=2,  weight=1, name="Softball"))
db.session.add(Event(id=3,  weight=2, name="Weightlifting"))
db.session.add(Event(id=4,  weight=1, name="Basketball"))
db.session.add(Event(id=5,  weight=1, name="Video Game"))
db.session.add(Event(id=6,  weight=2, name="Combatives"))
db.session.add(Event(id=7,  weight=1, name="Ultimate Frisbee"))
db.session.add(Event(id=8,  weight=1, name="Surf"))
db.session.add(Event(id=9,  weight=1, name="TL Got Talent"))
db.session.add(Event(id=10, weight=1, name="Bowling"))
db.session.add(Event(id=11, weight=1, name="Golf"))
db.session.add(Event(id=12, weight=1, name="Volleyball"))
db.session.add(Event(id=13, weight=1, name="Lightning Chef Cook Off"))
db.session.add(Event(id=14, weight=1, name="Swimming Relay"))
db.session.add(Event(id=15, weight=2, name="Best Team"))
db.session.commit()


# adding all blank ranking information
for team_id in range(19):
    for event_id in range(15):
        db.session.add(Placement(teams_id=team_id+1, events_id=event_id+1, place=0))
        # +1 is there so the loop starts at 1 instead of 0
    db.session.commit()


# creating admin user
db.session.add(User(id=0, code='WHO1ST'))
db.session.commit()

db.session.add(Access(user_id=0, event_id=0))
db.session.add(Access(user_id=0, event_id=1))
db.session.commit()
