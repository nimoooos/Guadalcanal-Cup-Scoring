import flask
from flask import url_for  # imported for use in frontend
from flask_debugtoolbar import DebugToolbarExtension

from env import DB_URI, FLASK_SECRETKEY
import models
from proj_util import num_to_ordinal, random_user_code
import datetime

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config["SECRET_KEY"] = FLASK_SECRETKEY
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
# TODO: set session option autoflush to false to fix SSL issue -- solved?
debug = DebugToolbarExtension(app)

models.connect_db(app)
app.app_context().push()
models.db.create_all()

scoreboard_global = []
scoreboard_update_time = "Not Initialized"
print("Warning: Scoreboard is not yet initialized!")

def update_scoreboard():
    """Update scoreboard_global which is stored in RAM"""
    teams = models.Team.query.all()  # list of teams, ordered by score (desc)
    events = models.Event.query.order_by(models.Event.id).all()  # list of all events, ordered by id
    events.pop(0)  # remove admin from events

    for t in teams:
        t.update_score()

    # create header for scoreboard table
    header = ["Teams"]
    for e in events:
        header.append(e.name)
    header.append("Total Score")

    scoreboard = [header]  # create scoreboard table with header row
    for team in teams:
        # loop generates a row with team name and scores from each event
        row = [team.name]  # generate a row with team name as first item

        # query with all the team's placements, ordered by event id
        placements = models.Placement.query.filter_by(teams_id=team.id).order_by(models.Placement.events_id)
        for placement in placements:
            if placement.place == 0:
                row.append("N/A")
            else:
                row.append(models.place_to_score(placement.place) *  # raw score from placement
                           models.Event.query.filter_by(id=placement.events_id).first().weight)  # weight from event

        row.append(team.score)  # total score for each team at the end of row
        scoreboard.append(row)  # add the created row to scoreboard

    global scoreboard_global
    scoreboard_global = scoreboard
    global scoreboard_update_time
    scoreboard_update_time = str(datetime.datetime.now().strftime("%B %d, %H:%M %Z"))
    print(scoreboard_update_time)
    flask.flash("Scoreboard last updated: {}".format(scoreboard_update_time), "info")


@app.route('/')
def welcome():
    print("Loading welcome page...")
    # Automatically goes to home() after 0.5 seconds
    flask.flash("This website was created by Lightning Labs!", "info")
    return flask.render_template('Welcome.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    scoreboard_render = scoreboard_global

    flask.flash("Scoreboard last updated: {}".format(scoreboard_update_time), "info")

    teams = models.Team.query.order_by(-models.Team.score).all()  # list of teams, ordered by score (desc)

    return flask.render_template('index.html', teams=teams, scoreboard=scoreboard_render)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if flask.request.method == 'POST':  # called when login button redirects to login()
        password = flask.request.form['password'].upper()
        query = models.User.query.filter_by(code=password)

        if query.count() == 0:  # no match found, send back to login()
            flask.flash("Error! Incorrect code presented.", "danger")
            return flask.redirect(flask.url_for('login'))

        else:  # match found, send to edit()
            flask.session['user_code'] = password
            flask.flash("Login successful!", "success")
            return flask.redirect(flask.url_for('account'))

    return flask.render_template('login.html')


@app.route('/account', methods=['POST', 'GET'])
def account():
    if flask.request.method == 'POST':  # called when a form submit is clicked
        event_id = flask.request.form['event_id']
        if event_id == "-1":  # logout code
            flask.flash("Logged Out", "warning")
            flask.session.pop('user_code', None)
            return flask.redirect('home')

        if event_id == "0":  # admin code
            return flask.redirect('admin')
        else:
            flask.session['event_id'] = event_id
            return flask.redirect('edit')

    events_access = {}  # dictionary of events, and whether the user has access
    events = models.Event.query.order_by(models.Event.id)
    user_code = flask.session['user_code']
    user_id = models.User.query.filter_by(code=user_code).first().id
    access_list = models.Access.query.filter_by(user_id=user_id)

    for access in access_list:
        events_access.update({access.event_id: True})
        # add all access to dictionary

    return flask.render_template('account.html', user_code=user_code, events_access=events_access, events=events)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    user_list = models.User.query.all()  # initialize user_list
    user_dict = {}
    for user in user_list:
        user_dict[user] = []

    if flask.request.method == 'POST':  # called when a form submit is clicked
        request_code = flask.request.form['request_code']

        if request_code == "UPDATE_SCOREBOARD":
            update_scoreboard()
            flask.flash("Scoreboard is updated!", "info")
            return flask.redirect('admin')

        if request_code == "CREATE_NEW_USER":
            new_user_code = random_user_code()
            models.db.session.add(models.User(code=new_user_code))
            models.db.session.commit()
            flask.flash("New login code generated: {}".format(new_user_code), "success")
            return flask.redirect('admin')

        if request_code.startswith("VIEW_"):
            flask.flash("Under construction: request {} received".format(request_code), "info")
            return flask.redirect('admin')

    # TODO: admin should be able to view all users, create new users, and give different access to different users
    flask.flash("Admin page under construction.\nAdmin features will include: view all users, create new users, control permissions for users",'info')
    flask.flash("This project cannot store PII such as Rank and Name. Contact Lightning Labs for more information.","danger")
    return flask.render_template('admin.html', user_code=flask.session['user_code'], user_list=user_dict)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    # TODO: pre-select placement for each team based on previous data entry
    user_code = flask.session['user_code']
    event_id = flask.session['event_id']
    event = models.Event.query.filter_by(id=event_id).first()
    teams = models.Team.query.order_by(models.Team.id)
    placements = []
    for i in range(teams.count()):
        placements.append((i + 1, num_to_ordinal(i + 1)))
    return flask.render_template('edit.html', user_code=user_code, event=event, teams=teams, placements=placements)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if flask.request.method == 'POST':
        db_submit = {}  # list to be stored in session
        for item in flask.request.form:
            key = convert_to_id(item)  # receiving team id as integer
            value = convert_to_id(flask.request.form[item])  # receiving team placement as integer
            db_submit[key] = value
        flask.session['db_submit'] = db_submit  # loaded into submit for future feature (confirmation page)

        # this loops through all the submission and updates record
        event_id = flask.session['event_id']
        for team_id in db_submit:
            placement = models.Placement.query.get((team_id, event_id))
            placement.place = db_submit[team_id]
            models.db.session.commit()

        update_scoreboard()  # update score upon successful submission
        flask.flash("Submit successful!", "success")
    else:
        flask.flash("Unknown error encountered.", "danger")

    return flask.render_template('submit.html')


def convert_to_id(string):
    if string.startswith("teamid_"):
        return int(string.split("_")[1])
    if string.isnumeric:
        return int(string)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
