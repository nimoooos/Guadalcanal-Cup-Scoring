from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Wraps logic into a function connecting app to database"""
    db.app = app
    db.init_app(app)


class Team(db.Model):
    """Model for competing teams (units, not individuals)"""
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer)

    def __repr__(self):
        return f"<{self.__tablename__}: id={self.id}, name={self.name}, score={self.score}>"

class Event(db.Model):
    """Model for different events (i.e., Basketball, Frisbee)"""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<{self.__tablename__}: id={self.id}, name={self.name}, weight={self.weight}>"


class Placement(db.Model):
    """Linker between teams and events to show what team won what event"""
    __tablename__ = 'placements'

    teams_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    events_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    placement = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<{self.__tablename__}: teams_id={self.teams_id}, events_id={self.events_id}, placement={self.placement}>"

