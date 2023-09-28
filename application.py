import flask
from flask import url_for  # DO NOT REMOVE: imported for use in frontend
from flask_debugtoolbar import DebugToolbarExtension

import env
import models
from proj_util import random_user_code, pivot_table, write_to_csv, zip_folder, backup_table_all

import datetime
import os

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = env.DB_URI
app.config["SECRET_KEY"] = env.FLASK_SECRETKEY
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
# TODO: set session option auto flush to false to fix SSL issue -- solved?
debug = DebugToolbarExtension(app)

models.connect_db(app)
app.app_context().push()
models.db.create_all()

# these lists hold the data for scoreboard to reduce database access
scoreboard_global: list[list] = []
scoreboard_global_pivot: list[list] = []
scoreboard_update_time: datetime.datetime = datetime.datetime(year=1970, month=1, day=1)  # using 1970 to align with unix time 0


def update_scoreboard() -> None:
    """
    Update scoreboard_global which is stored in RAM. This prevents excessive database access.
    """
    teams = models.Team.query.all()  # list of teams, ordered by score (desc)
    events = models.Event.query.order_by(models.Event.id).all()  # list of all events, ordered by id
    events.pop(0)  # remove admin from events

    for team in teams:
        team.update_score()

    # create header for scoreboard table
    header: list[str] = ["Teams"]
    for event in events:
        header.append(event.name)
    header.append("Total Score")
    scoreboard = [header]  # create scoreboard table with header row

    for team in teams:  # each loop generates a new row with team name and scores from each event
        row = [team.name]  # generate a row with team name as first item

        # query with all the team's placements, ordered by event id
        placements = models.Placement.query.filter_by(teams_id=team.id).order_by(models.Placement.events_id)
        for placement in placements:
            if placement.place == 0:
                row.append("N/A")
            else:
                raw_score = models.place_to_score(placement.place)
                score_weight = models.Event.query.filter_by(id=placement.events_id).first().weight
                row.append(raw_score*score_weight)

        row.append(team.score)  # total score for each team at the end of row
        scoreboard.append(row)  # add the created row to scoreboard

    global scoreboard_global
    scoreboard[0][0] = ""
    scoreboard_global = scoreboard

    global scoreboard_global_pivot
    scoreboard_global_pivot = pivot_table(scoreboard_global)

    # update scoreboard_update_time with the current time in HST
    global scoreboard_update_time
    hst_adjustment = datetime.timedelta(hours=-10)
    scoreboard_update_time = datetime.datetime.now(datetime.timezone.utc) + hst_adjustment
    update_time_string = scoreboard_update_time.strftime("%B %d, %H:%M HST")
    flask.flash("Scoreboard is current as of {}".format(update_time_string), "info")

    return None


@app.route('/')
def welcome():
    """
    Called by default. Flashes Lightning Labs logo then redirects to info page.
    """
    print("Loading welcome page...")
    flask.flash("This website was created by Lightning Labs!", "info")
    return flask.render_template('Welcome.html')


@app.route('/scores', methods=['POST', 'GET'])
def scores():
    """
    This page displays scoreboard.
    """
    scoreboard_is_initialized = scoreboard_update_time.year == 1970
    if scoreboard_is_initialized:
        print("Updating Scoreboard...")
        update_scoreboard()  # update scoreboard if it hasn't been updated

    scoreboard_render: list[list] = scoreboard_global  # import scoreboard_global to be rendered
    scoreboard_render_pivot: list[list] = scoreboard_global_pivot
    show_scoreboard: bool = True
    show_leaderboard: bool = True

    teams: list[dict] = []
    for row in scoreboard_render:
        row_element = {"name": row[0], "score": row[-1]}
        teams.append(row_element)

    # remove title row
    if len(teams) > 0:
        teams.pop(0)

    # Sort teams list by score, descending
    teams = sorted(teams, key=lambda x: -x["score"])

    # make list of events
    events: list = []
    if len(scoreboard_render) > 0:
        events = scoreboard_render[0]

    scoreboard_mini: dict = {}
    if flask.request.method == 'POST':  # if unit or event is selected
        def req_code_parser(req_code) -> str:
            """
            Takes request code and converts it to unit or event name
            """
            return req_code.split("_")[1].replace("+", " ")

        def make_scoreboard_mini(scoreboard):
            table_name = req_code_parser(flask.request.form['request_code'])

            # search for event or team name in scoreboard and insert info in to that row
            req_info = [scoreboard[0]]
            for scoreboard_row in scoreboard:
                if scoreboard_row[0] == table_name:
                    req_info.append(scoreboard_row)
                    break

            for index in range(len(req_info[0])):
                scoreboard_mini[req_info[0][index]] = req_info[1][index]

        if flask.request.form['request_code'].startswith("TEAM_"):
            make_scoreboard_mini(scoreboard=scoreboard_render)
            show_leaderboard = False
            show_scoreboard = False

        if flask.request.form['request_code'].startswith("EVENT_"):
            make_scoreboard_mini(scoreboard=scoreboard_render_pivot)
            show_leaderboard = False
            show_scoreboard = False

    scoreboard_update_time_string = scoreboard_update_time.strftime("%B %d, %H:%M HST")
    flask.flash("Scoreboard is current as of {}".format(scoreboard_update_time_string), "info")
    return flask.render_template(
        'scores.html',
        teams=teams,
        scoreboard=scoreboard_render_pivot,
        events=events,
        requested_info=scoreboard_mini,
        show_scoreboard=show_scoreboard,
        show_leaderboard=show_leaderboard)


@app.route('/info', methods=['POST', 'GET'])
def info():
    """
    This page displays static images in directory listed in folder_path
    """

    file_list: list = []
    folder_path = os.path.join('static', 'TLW PPT Slides')
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_list.append(os.path.join(root, file))

    return flask.render_template('info.html', files=file_list)


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

        else:  # match found, send to account()
            flask.session['user_code'] = password
            flask.flash("Login successful!", "success")
            return flask.redirect(url_for('account'))

    else:
        flask.flash("Warning! Access code is required to view the scoreboard.", "warning")

    return flask.render_template('login.html')


@app.route('/account', methods=['POST', 'GET'])
def account():
    """
    Account menu. Shows different options available to users.
    """

    if flask.request.method == 'POST':  # called when a form submit is clicked
        event_id: str = flask.request.form['event_id']

        logout_code = "-1"
        admin_code = "0"

        if event_id == logout_code:
            flask.flash("Logged Out", "warning")
            flask.session.pop('user_code', None)
            return flask.redirect('scores')

        if event_id == admin_code:
            return flask.redirect('admin')

        else:
            flask.session['event_id'] = event_id
            return flask.redirect('edit')

    # see what access the user has and only display relevant buttons
    events_access = {}
    events = models.Event.query.order_by(models.Event.id)
    user_code = flask.session['user_code']
    user_id = models.User.query.filter_by(code=user_code).first().id
    access_list = models.Access.query.filter_by(user_id=user_id)
    for access in access_list:
        events_access.update({access.event_id: True})

    return flask.render_template('account.html',
                                 user_code=user_code,
                                 events_access=events_access,
                                 events=events)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    """
    Admin menu. Shows special actions available only to admin account holders.
    """

    # initialize user_dict
    user_list = models.User.query.all()
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
            backup_scoreboard = os.path.join("backup", "scoreboard.csv")
            return flask.send_file(backup_scoreboard, as_attachment=True)

        if request_code == "BACKUP_DATABASE":
            models.backup_tables_all()
            backup_zip = zip_folder(os.path.join("backup", "database"))
            return flask.send_file(backup_zip, as_attachment=True)

        if request_code.startswith("VIEWUSER_"):
            view_object = models.User.query.filter_by(id=request_code.split("_")[1]).first()  # grab the User with the correct id

            # load user info into sessions then call viewuser()
            view_user = {"id": view_object.id, "code": view_object.code}
            flask.session['view_user'] = view_user
            return flask.redirect(url_for('viewuser'))

    flask.flash("This project cannot store PII such as Rank and Name. Contact Lightning Labs for more information.", 'danger')

    return flask.render_template('admin.html',
                                 user_code=flask.session['user_code'],
                                 user_list=user_dict)


@app.route('/admin/viewuser', methods=['POST', 'GET'])
def viewuser():
    """
    From admin, view a user account and modify details
    """
    view_user = flask.session['view_user']  # grab user's id and login code

    if flask.request.method == 'POST':
        request_code = flask.request.form['request_code']

        if request_code.startswith("ADD_"):  # create new access row
            event_id = request_code.split("_")[1]
            user_id = view_user["id"]

            models.db.session.add(models.Access(event_id=event_id, user_id=user_id))
            models.db.session.commit()
            return flask.redirect(url_for('viewuser'))

        if request_code.startswith("REMOVE_"):  # find the existing row and remove it
            event_id = request_code.split("_")[1]
            user_id = view_user["id"]
            row = models.Access.query.filter_by(event_id=event_id, user_id=user_id).first()

            models.db.session.remove(row)
            models.db.session.commit()
            return flask.redirect(url_for('viewuser'))

    permissions = models.User.query.filter_by(id=view_user["id"]).first().permissions
    all_events = models.Event.query.all()

    # create a dictionary of all events.
    event_dict = {}
    for event in all_events:
        event_dict[event.id] = {"event_name": event.name, "permission": False}

    # set certain permissions to True
    for access in permissions:
        event_dict[access.event_id]["permission"] = True

    return flask.render_template('viewuser.html',
                                 view_user=view_user,
                                 event_dict=event_dict)


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

    team_placements = {}  # keeps track of what team scored how much
    event_placements = models.Placement.query.filter_by(events_id=event_id).order_by(models.Placement.teams_id)
    for event_placement in event_placements:
        team_placements[event_placement.teams_id] = event_placement.place

    def num_to_ordinal(number):
        """
        Convert number to their ordinal value for placement purposes.
        Functions improperly if number>100, and will return "101th", "102th", etc.
        """
        last_digit = number % 10
        if number == 1: return str("🥇")
        if number == 2: return str("🥈")
        if number == 3: return str("🥉")

        if number <= 20: return str(number) + "th"

        if last_digit == 1: return str(number) + "st"
        if last_digit == 2: return str(number) + "nd"
        if last_digit == 3:
            return str(number) + "rd"
        else:
            return str(number) + "th"

    # generate dropdown menu options for placement
    dropdown_options = []
    for i in range(teams.count()):
        dropdown_options.append((i + 1, num_to_ordinal(i + 1)))  # option value is i+1, displayed value is ordinal

    return flask.render_template('edit.html',
                                 user_code=user_code,
                                 event=event,
                                 teams=teams,
                                 placements=dropdown_options,
                                 team_placements=team_placements)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    """
    Confirms that data has been entered.
    """
    if flask.request.method == 'POST':
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
        flask.flash("Unknown error encountered. No data submission received.", "danger")

    return flask.render_template('submit.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
