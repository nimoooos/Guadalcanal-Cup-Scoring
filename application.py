import flask
from flask import url_for  # DO NOT REMOVE: imported for use in frontend
from flask_debugtoolbar import DebugToolbarExtension

from env import DB_URI, FLASK_SECRETKEY
import models
from proj_util import num_to_ordinal, random_user_code, pivot_table, write_to_csv, zip_folder, backup_table_all
import datetime
import os

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config["SECRET_KEY"] = FLASK_SECRETKEY
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
# TODO: set session option auto flush to false to fix SSL issue -- solved?
debug = DebugToolbarExtension(app)

models.connect_db(app)
app.app_context().push()
models.db.create_all()

scoreboard_global = []
scoreboard_global_pivot = []
scoreboard_update_time = "N/A"
print("Scoreboard: ", scoreboard_update_time)


def update_scoreboard() -> None:
    """
    Update scoreboard_global which is stored in RAM. This prevents excessive database access.
    """
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
    global scoreboard_global_pivot
    scoreboard_global_pivot = pivot_table(scoreboard_global)
    global scoreboard_update_time
    scoreboard_update_time = str(datetime.datetime.now().strftime("%B %d, %H:%M %z"))

    print(scoreboard_update_time)
    flask.flash("Scoreboard last updated: {}".format(scoreboard_update_time), "info")
    return None


@app.route('/')
def welcome():
    """
    Called by default. Flashes Lightning Labs logo then redirects to info page.
    """
    print("Loading welcome page...")
    # update_scoreboard()  # DO NOT commit this line, this calls database for ~400 queries. debugging purposes only
    # Automatically goes to home() after 0.5 seconds
    flask.flash("This website was created by Lightning Labs!", "info")

    return flask.render_template('Welcome.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    """
    This page displays scoreboard.
    """
    if scoreboard_update_time == "N/A":
        update_scoreboard()  # update scoreboard if it hasn't been updated
        print("Updating Scoreboard...")

    scoreboard_render = scoreboard_global
    scoreboard_render_pivot = scoreboard_global_pivot
    show_scoreboard = True

    flask.flash("Scoreboard last updated: {}".format(scoreboard_update_time), "info")

    # extract team name and scores into an array of dictionaries
    teams = []
    for row in scoreboard_render:
        row_element = {"name": row[0], "score": row[-1]}
        teams.append(row_element)

    # remove title row
    if len(teams) > 0:
        teams.pop(0)

    teams = sorted(teams, key=lambda x: -x["score"])  # Sort teams list by score, descending

    # make list of events
    events = []
    if len(scoreboard_render) > 0:
        events = scoreboard_render[0]

    request_type = "NONE"
    requested_info = {}
    if flask.request.method == 'POST':  # if unit or event is selected
        def req_code_parser(req_code):
            return req_code.split("_")[1].replace("+", " ")  # removes header, and replaces "+" with " "

        if flask.request.form['request_code'].startswith("TEAM_"):
            show_scoreboard = False
            request_type = "UNIT"
            parsed = req_code_parser(flask.request.form['request_code'])

            req_info = [scoreboard_render[0]]  # header
            for row in scoreboard_render:
                if row[0] == parsed:  # match found
                    req_info.append(row)
                    break

            for index in range(len(req_info[0])):
                requested_info[req_info[0][index]] = req_info[1][index]

        if flask.request.form['request_code'].startswith("EVENT_"):
            show_scoreboard = False
            request_type = "EVENT"
            parsed = req_code_parser(flask.request.form['request_code'])

            req_info = [scoreboard_render_pivot[0]]  # header
            for row in scoreboard_render_pivot:
                if row[0] == parsed:  # match found
                    req_info.append(row)
                    break

            for index in range(len(req_info[0])):
                requested_info[req_info[0][index]] = req_info[1][index]

    return flask.render_template(
        'index.html',
        teams=teams,
        scoreboard=scoreboard_render_pivot,
        events=events,
        request_type=request_type,
        requested_info=requested_info,
        show_scoreboard=show_scoreboard)


@app.route('/info', methods=['POST', 'GET'])
def info():
    """
    This page displays static images in directory "static/TLW PPT Slides"
    """
    # TODO: dynamically grab the list of files and send it through render_template.
    return flask.render_template('info.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Login page.
    It's also a redirect destination for login POST request, which confirms if login info is correct.
    """
    if flask.request.method == 'POST':  # called when login button redirects to login()
        password = flask.request.form['password'].upper()
        query = models.User.query.filter_by(code=password)

        if query.count() == 0:  # no match found, send back to login()
            flask.flash("Error! Incorrect code presented.", "danger")
            return flask.redirect(url_for('login'))

        else:  # match found, send to edit()
            flask.session['user_code'] = password
            flask.flash("Login successful!", "success")
            return flask.redirect(url_for('account'))

    return flask.render_template('login.html')


@app.route('/account', methods=['POST', 'GET'])
def account():
    """
    Account menu. Shows different options available to users.
    """

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
    """
    Admin menu. Shows special actions available only to admin account holders.
    """

    user_list = models.User.query.all()  # initialize user_list
    user_dict = {}
    for user in user_list:
        user_dict[user] = []

    if flask.request.method == 'POST':  # called when a form submit is clicked
        request_code = flask.request.form['request_code']

        if request_code == "UPDATE_SCOREBOARD":
            update_scoreboard()
            flask.flash("Scoreboard is updated!", "success")
            return flask.redirect('admin')

        if request_code == "CREATE_NEW_USER":
            new_user_code = random_user_code(8)
            models.db.session.add(models.User(code=new_user_code))
            models.db.session.commit()
            flask.flash("New login code generated: {}".format(new_user_code), "success")
            return flask.redirect('admin')

        if request_code == "BACKUP_SCOREBOARD":
            write_to_csv("backup", "scoreboard.csv", scoreboard_global)
            return flask.send_file(os.path.join("backup", "scoreboard.csv"), as_attachment=True)

        if request_code == "BACKUP_DATABASE":
            backup_table_all()

            zip_directory = zip_folder(os.path.join("backup", "database"))

            flask.flash("Check backup/database folder", "success")
            return flask.send_file(zip_directory, as_attachment=True)

        if request_code.startswith("VIEWUSER_"):
            """
            call viewuser()
            """
            view_object = models.User.query.filter_by(id=request_code.split("_")[1]).first()  # grab the User with the correct id

            # load user info into sessions
            view_user = {"id": view_object.id, "code": view_object.code}
            flask.session['view_user'] = view_user
            return flask.redirect(url_for('viewuser'))

    # TODO: HIGH PRIORITY admin should be able to give and take away different access to different users
    flask.flash("Admin page under construction.\nPending admin features: control permissions for users", 'info')
    flask.flash("This project cannot store PII such as Rank and Name. Contact Lightning Labs for more information.", 'danger')
    return flask.render_template('admin.html', user_code=flask.session['user_code'], user_list=user_dict)


@app.route('/admin/viewuser', methods=['POST', 'GET'])
def viewuser():
    """
    From admin, view a user account and modify details
    """
    view_user = flask.session['view_user']
    permissions = models.User.query.filter_by(id=view_user["id"]).first().permissions
    all_events = models.Event.query.all()

    # create a dictionary of all events.
    event_dict = {}
    for event in all_events:
        event_dict[event.id] = {"event_name": event.name, "permission": False}

    # set certain permissions to True
    for access in permissions:
        event_dict[access.event_id]["permission"] = True

    print(event_dict)

    return flask.render_template('viewuser.html', view_user=view_user, event_dict=event_dict)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    """
    Score update menu.
    """
    # TODO: HIGH PRIORITY pre-select placement for each team based on previous data entry
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
    """
    Confirms that data has been entered.
    """
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


def convert_to_id(string) -> int | None:
    """
    converts string "teamid_num" into integer num
    """
    if string.startswith("teamid_"):
        return int(string.split("_")[1])
    if string.isnumeric:
        return int(string)
    else:
        return None


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
