from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def place_to_score(place):
    if place == 1: return 10
    if place == 2: return 7
    if place == 3: return 5
    if place == 4: return 3
    else: return 0


def connect_db(app):
    """Wraps logic into a function connecting app to database"""
    db.app = app
    db.init_app(app)
    return app


def backup_table(table_class):
    from proj_util import write_to_csv
    from os import path

    directory = path.join("backup", "database")
    filename = "{}.csv".format(table_class.__tablename__)

    query = table_class.query.all()
    array_2d = [[]]  # store the query into an array

    for column in table_class.__table__.columns:  # create header with column names
        array_2d[0].append(column.name)

    for row in query:
        to_append = []
        for column in array_2d[0]:
            to_append.append((vars(row)[column]))
        array_2d.append(to_append)  # add new row into array

    print("Creating {}...".format(filename))
    print(array_2d)

    write_to_csv(directory, filename, array_2d)


class Team(db.Model):
    """Database model for competing teams (units, not individuals)"""
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer)

    def __str__(self):
        return f"<{self.__tablename__}: id={self.id}, name={self.name}, score={self.score}>"

    def __repr__(self):
        return self.__str__()

    def update_score(self):
        """Updates, sets, and returns the total score for each team based on the team's places in different events"""
        results = Placement.query.filter_by(teams_id=self.id).all()
        total_score = 0
        print("\nUpdating total score for {}...".format(self.name))
        for r in results:
            event = Event.query.filter_by(id=r.events_id).first().name
            place = Placement.query.filter_by(place=r.place).first().place
            weight = Event.query.filter_by(id=r.events_id).first().weight
            points = place_to_score(place)
            weighted = weight * points

            print("{event}: {place}th place, {points} raw, {weighted} weighted"
                  .format(event=event, place=place, points=points, weighted=weighted))

            total_score += weighted

        print("Total score: {}".format(total_score))
        self.score = total_score
        return total_score


class Event(db.Model):
    """Database model for different events (i.e., Basketball, Frisbee)"""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f"<{self.__tablename__}: id={self.id}, name={self.name}, weight={self.weight}>"

    def __repr__(self):
        return self.__str__()


class Placement(db.Model):
    """Linker between teams and events to show what team won what event"""
    __tablename__ = 'placements'

    teams_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    events_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    place = db.Column(db.Integer, nullable=True)

    def __str__(self):
        return f"<{self.__tablename__}: teams_id={self.teams_id}, events_id={self.events_id}, place={self.place}>"

    def __repr__(self):
        return self.__str__()


class User(db.Model):
    """Stores user login information. Each code can access one event"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Text, nullable=False)
    # TODO: create log of who is editing what and when
        # Each user account is a randomly generated code, no username/password combo (avoid PII storage)


class Access(db.Model):
    """Stores info of what access user has"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
