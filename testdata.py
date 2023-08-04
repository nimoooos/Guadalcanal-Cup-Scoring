from models import db, Team, Event, Placement
from application import app

app.app_context()

# Create all tables
db.drop_all()
db.create_all()

# adding unit information, sample

db.session.add(Team(name="2-35 IN"))
db.session.add(Team(name="HHBN"))
db.session.add(Team(name="325 BSB"))
db.session.add(Team(name="2-25 AVN"))
db.session.add(Team(name="1-27 IN"))
db.session.commit()

# adding all event information, sample
db.session.add(Event(name="Softball Tournament", weight="6"))
db.session.add(Event(name="Ultimate Frisbee", weight="7"))
db.session.add(Event(name="Flag Football", weight="15"))
db.session.commit()

# adding all placement information
db.session.add(Placement(teams_id=1, events_id=1, place=1))
db.session.add(Placement(teams_id=2, events_id=1, place=2))
db.session.add(Placement(teams_id=3, events_id=1, place=3))
db.session.add(Placement(teams_id=4, events_id=1, place=4))
db.session.add(Placement(teams_id=5, events_id=1, place=5))

db.session.add(Placement(teams_id=1, events_id=2, place=5))
db.session.add(Placement(teams_id=2, events_id=2, place=4))
db.session.add(Placement(teams_id=3, events_id=2, place=3))
db.session.add(Placement(teams_id=4, events_id=2, place=2))
db.session.add(Placement(teams_id=5, events_id=2, place=1))

db.session.add(Placement(teams_id=1, events_id=3, place=2))
db.session.add(Placement(teams_id=2, events_id=3, place=4))
db.session.add(Placement(teams_id=3, events_id=3, place=3))
db.session.add(Placement(teams_id=4, events_id=3, place=1))
db.session.add(Placement(teams_id=5, events_id=3, place=5))
db.session.commit()

# result = Placement.query.filter_by(teams_id=1).all()
# print(result)

# for r in result:
#     print(r)
#     print(Team.query.filter_by(id=r.teams_id).first().name)  # print team name
#     print(Event.query.filter_by(id=r.events_id).first().name)  # print event name
#     print(r.place)

result = Team.query.all()

for r in result:
    team = Team.query.filter_by(id=r.id).first()
    team.update_score()
    print("--------------------")
db.session.commit()
