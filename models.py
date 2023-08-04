from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Wraps logic into a function connecting app to database"""
    db.app = app
    db.init_app(app)
    return app


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
        """calculate the correct score and update the score column"""
        places = False  # TODO: insert query for sum


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
