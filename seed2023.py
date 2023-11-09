from models import db, Team, Event, Placement, User, Access
from application import app

app.app_context()

# Drop all then recreate all tables
print("Dropping all tables...")
db.drop_all()
print("Creating all tables...")
db.create_all()
db.session.commit()
print("Table initialization successful!")

# adding unit information
print("Populating table 'Team'...")

team_list = [
    {"id": 1,  "name": "2-35 IN"},
    {"id": 2,  "name": "HHBN"},
    {"id": 3,  "name": "325 BSB"},
    {"id": 4,  "name": "2-25 AVN"},
    {"id": 5,  "name": "1-27 IN"},
    {"id": 6,  "name": "65 BEB"},
    {"id": 7,  "name": "3-7 FA"},
    {"id": 8,  "name": "2-14 CAV"},
    {"id": 9,  "name": "524 CSSB"},
    {"id": 10, "name": "225 BSB"},
    {"id": 11, "name": "3-25 AVN"},
    {"id": 12, "name": "29 BEB"},
    {"id": 13, "name": "2-11 FA"},
    {"id": 14, "name": "1-21 IN"},
    {"id": 15, "name": "2-6 CAV"},
    {"id": 16, "name": "2-27 IN"},
    {"id": 17, "name": "25th STB"},
    {"id": 18, "name": "3-4 CAV"},
    {"id": 19, "name": "209th ASB"},
    {"id": 20, "name": "125th IEW"}
]
current = 0
total = len(team_list)

for team in team_list:
    db.session.add(Team(id=team["id"], name=team["name"], score=0))
    current += 1
    print("\rJob {current}/{total} staged...".format(current=current, total=total), end="")
db.session.commit()
print("\nPopulating table 'Team' successful!")

# adding all event information
print("Populating table 'Event'...")
db.session.add(Event(id=0, name="Admin", weight=0))
db.session.commit()

event_list = [
    {id:  1, "weight": 1, "name": "Softball Tournament"},
    {id:  2, "weight": 1, "name": "Ultimate Frisbee"},
    {id:  3, "weight": 1, "name": "Flag Football"},
    {id:  4, "weight": 1, "name": "Tug-O-War"},
    {id:  5, "weight": 1, "name": "Basketball"},
    {id:  6, "weight": 1, "name": "Video Game Tourney"},
    {id:  7, "weight": 1, "name": "Surf Competition"},
    {id:  8, "weight": 1, "name": "TL Got Talent"},
    {id:  9, "weight": 1, "name": "Volleyball"},
    {id: 10, "weight": 1, "name": "Bowling"},
    {id: 11, "weight": 1, "name": "10K Race"},
    {id: 12, "weight": 1, "name": "Swimming Relay"},
    {id: 13, "weight": 1, "name": "TL Cook-off"},
    {id: 14, "weight": 1, "name": "Field Feeding Cook-off"},
    {id: 15, "weight": 1, "name": "Drone Race"},
    {id: 16, "weight": 2, "name": "Weightlifting"},
    {id: 17, "weight": 2, "name": "Combatives"},
    {id: 18, "weight": 2, "name": "Stress Shoot"}
]

current = 0
total = len(event_list)

for event in event_list:
    db.session.add(Event(id=event[id], weight=event["weight"], name=event["name"]))
    current += 1
    print("\rJob {current}/{total} staged...".format(current=current, total=total), end="")
db.session.commit()
print("\nPopulating table 'Event' successful!")

# adding all blank ranking information
print("Populating table 'Placement'...")

current = 0
total = len(team_list)*len(event_list)

for team_id in range(1, len(team_list)+1):  # corresponds to every team id
    for event_id in range(1, len(event_list)+1):  # corresponds to every event id
        db.session.add(Placement(teams_id=team_id, events_id=event_id, place=0))
        current += 1
        print("\rJob {current}/{total} staged...".format(current=current, total=total), end="")
    db.session.commit()
print("\nPopulating table 'Placement' successful!")

# creating admin user
print("Populating table 'User'...")
db.session.add(User(id=0, code='WHO1ST'))
db.session.commit()
print("Populating table 'User' successful!")


print("Populating table 'Access'...")
db.session.add(Access(user_id=0, event_id=0))
db.session.add(Access(user_id=0, event_id=1))
db.session.commit()
print("Populating table 'Access' successful!")

print("Database initialization successful!")
