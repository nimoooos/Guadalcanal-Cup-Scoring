import flask  # imported for type annotation
from flask_sqlalchemy import SQLAlchemy
from proj_util import timer

db = SQLAlchemy()


def place_to_score(place: int) -> int:
    """
    Converts placement (int) to score (int). Used for calculating total score.
    """
    if place == 1: return 10
    if place == 2: return 8
    if place == 3: return 6
    if place == 4: return 4
    else: return 0


def connect_db(app: flask.Flask) -> flask.Flask:
    """
    Wraps logic into a function connecting app to database
    """
    db.app = app
    db.init_app(app)
    return app


def backup_table(table_class: db.Model) -> None:
    """
    Receives table class, creates .csv file in /backup/database
    """
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


def backup_tables_all() -> None:
    backup_table(Team)
    backup_table(Event)
    backup_table(Placement)
    backup_table(User)
    backup_table(Access)


class Team(db.Model):
    """
    Database model for competing teams (units, not individuals)
    """
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer)

    def __str__(self) -> str:
        return f"<{self.__tablename__}: id={self.id}, name={self.name}, score={self.score}>"

    def __repr__(self) -> str:
        return self.__str__()

    @timer
    def update_score(self) -> None:
        """
        Updates, sets, and returns the total score for each team based on the team's places in different events
        """
        results = Placement.query.filter_by(teams_id=self.id).all()
        total_score = 0
        print("Updating total score for {team_name}...".format(team_name=self.name), end="")
        for r in results:
            place = Placement.query.filter_by(place=r.place).first().place
            weight = Event.query.filter_by(id=r.events_id).first().weight
            points = place_to_score(place)
            weighted = weight * points
            total_score += weighted

        print("\r{} score: {}".format(self.name, total_score))
        self.score = total_score
        return None

    @timer
    def update_score_v2(self) -> None:
        """
        New version of update_score, using join functionality to reduce the number of database requests
        """
        self_name = self.name
        self_id = self.id
        print("Updating total score for {team_name}...".format(team_name=self_name, end=""))

        # grab all placement rows with the associated weight
        query = db.session.query(
            Placement.place,
            Event.weight,
            Placement.teams_id
        ).join(Event, Placement.events_id == Event.id).all()

        total_score = 0
        for q in query:
            # q[0] = Placement.place, q[1] = Event.weight, q[2] = Placement.teams_id
            if q[2] == self_id:  # filtering done in python to reduce database load
                total_score += place_to_score(q[0])*q[1]
            else: pass

        print("\r{} score: {}".format(self.name, total_score))
        self.score = total_score
        return None


class Event(db.Model):
    """Database model for different events (i.e., Basketball, Frisbee)"""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    def __str__(self) -> str:
        return f"<{self.__tablename__}: id={self.id}, name={self.name}, weight={self.weight}>"

    def __repr__(self) -> str:
        return self.__str__()


class Placement(db.Model):
    """
    Linker table between teams and events to show what team won what event
    """
    __tablename__ = 'placements'

    teams_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    events_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    place = db.Column(db.Integer, nullable=True)

    def __str__(self) -> str:
        return f"<{self.__tablename__}: teams_id={self.teams_id}, events_id={self.events_id}, place={self.place}>"

    def __repr__(self) -> str:
        return self.__str__()


class User(db.Model):
    """
    Stores user login information. Each code can have different access permissions depending on Access class.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Text, nullable=False)

    permissions = db.relationship('Access', backref='User')
    # TODO: create log of who is editing what and when
    # Each user account is a randomly generated code, no username/password combo (avoid PII storage)


class Access(db.Model):
    """
    Stores info of what access a User has.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    event = db.relationship('Event', backref='Access')
