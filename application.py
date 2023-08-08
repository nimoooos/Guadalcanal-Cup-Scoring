import flask
from flask import session
from flask_debugtoolbar import DebugToolbarExtension

import env
import models

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = env.DB_URI
app.config["SECRET_KEY"] = env.FLASK_SECRETKEY
debug = DebugToolbarExtension(app)

models.connect_db(app)
app.app_context().push()
models.db.create_all()


@app.route('/')
def home():
    teams = models.Team.query.all()  # create a list of teams participating
    print("\nUpdating team scores...")
    for t in teams:
        t.update_score()
    print("\nUpdating team scores complete.")

    teams = models.Team.query.order_by(-models.Team.score).all()  # list of teams, ordered by score (desc)
    events = models.Event.query.order_by(models.Event.id).all()  # list of all events, ordered by id

    print("\nBeginning to create scoreboard table...")
    # create header for scoreboard table
    header = ["Teams"]
    for e in events:
        header.append(e.name)
    header.append("Total Score")
    print("Creating header complete.")

    scoreboard = [header]  # create scoreboard table with header row

    for team in teams:
        print("Creating row for {}...".format(team.name))
        # loop generates a row with team name and scores from each event
        row = [team.name]  # generate a row with team name as first item

        # query with all the team's placements, ordered by event id
        placements = models.Placement.query.filter_by(teams_id=team.id).order_by(models.Placement.events_id)
        for placement in placements:
            print(placement)
            row.append(models.place_to_score(placement.place) *  # raw score from placement
                       models.Event.query.filter_by(id=placement.events_id).first().weight)  # weight from event

        row.append(team.score)
        scoreboard.append(row)

    print("Creating table complete.")
    print("Rendering template...")
    return flask.render_template('index.html', teams=teams, scoreboard=scoreboard)


if __name__ == '__main__':
    app.run(debug=True)
