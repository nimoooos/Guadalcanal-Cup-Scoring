import flask
from flask import url_for  # DO NOT REMOVE: imported for use in frontend
from flask import flash
from flask_debugtoolbar import DebugToolbarExtension
import werkzeug.exceptions

import env
import lightning_labs as LL
import models
import proj_util

import datetime
import os
import logging
import json

if env.DEBUG:
    logging.basicConfig(level=logging.DEBUG, format='{time} - %(levelname)s: %(message)s'.format(time=proj_util.now_hst("string")), filename="log.log", filemode='a')
else:
    logging.basicConfig(level=logging.INFO, format='{time} - %(levelname)s: %(message)s'.format(time=proj_util.now_hst("string")), filename="log.log", filemode='a')

logging.info("Application started!")

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = env.DB_URI
app.config["SECRET_KEY"] = env.FLASK_SECRETKEY
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
debug = DebugToolbarExtension(app)

models.connect_db(app)
app.app_context().push()
models.db.create_all()

# these lists hold the data for scoreboard to reduce database access
scoreboard_global: list[list] = []
scoreboard_global_pivot: list[list] = []
scoreboard_update_time: datetime.datetime = datetime.datetime(year=1970, month=1, day=1)  # using 1970 to align with unix time 0


@proj_util.timer
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
    scoreboard_global_pivot = proj_util.pivot_table(scoreboard_global)

    # update scoreboard_update_time with the current time in HST
    global scoreboard_update_time
    scoreboard_update_time = proj_util.now_hst()
    # update_time_string = scoreboard_update_time.strftime("%B %d, %H:%M HST")
    # flask.flash("Scoreboard is current as of {time}".format(time=update_time_string), "info")

    return None


def check_401(event_name="HAS_ACCOUNT") -> bool:
    """
    Check if login info exists, or if user is authorized
    Returns true if error should be thrown, returns false if authorized
    """
    if 'user_code' not in flask.session.keys():
        return True

    if not proj_util.authorized(login_code=flask.session['user_code'], event_name=event_name):
        print("Authorized!")
        return True

    return False


@app.errorhandler(werkzeug.exceptions.NotFound)
def error_handle_not_found(e):
    logging.info("Error 404")
    return flask.render_template('error.html', code=404, msg="Page not found")


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def error_handle_internal_server_error(e):
    logging.info("Error 500")
    return flask.render_template('error.html', code=500, msg="Internal server error")


@app.errorhandler(werkzeug.exceptions.HTTPException)
def error_handle_http_exception(e):
    """
    Catch-all error handler for other issues
    """
    print(e)
    print(e.get_response)
    return flask.render_template('error.html', code="", msg="Unknown error")


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
    # if check_401("Admin"): return flask.render_template("error.html", code=401, msg="Unauthorized")
    # TODO: reimplement authorization check

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
    flask.flash("Scoreboard is current as of {time}. Scores not final until Closing Ceremony.".format(time=scoreboard_update_time_string), "info")

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
    # flash("Weather Call 29NOV: Softball poised for 1500 restart.", 'warning')
    flash("Surfing rescheduled to Thurs! 0830@Pua'ena Point", 'warning')
    # flash("INFO:Field Feeding and Drone Race events are BDE-only competitions", 'warning')
    return flask.render_template('info2.html', GMAP=env.GMAP_KEY)

    panels: list[dict] = []

    # add all .png file directories into file_list
    file_list: list = []
    folder_path = os.path.join('static', 'display')  # TODO: update file location
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".png"):
                file_list.append(os.path.join(root, file))

    # look for associated .json files with .png
    for file in file_list:
        json_directory = file.replace(".png", ".json")
        with open(json_directory) as json_file:
            json_data = json.load(json_file)

        panel: dict = {"order": json_data['order'], "title": json_data['title'], "filepath": file, "content": json_data['content']}
        panels.append(panel)

    # sort panels by order set
    sorted_panels = sorted(panels, key=lambda x: x['order'])

    return flask.render_template('info.html', panels=sorted_panels)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Login page.
    It's also a redirect destination for login POST request, which confirms if login info is correct.
    """
    if not check_401():
        return flask.redirect(url_for('account'))

    if flask.request.method == 'POST':  # called when login button redirects to login()
        password = flask.request.form['password'].upper()

        if proj_util.authorized(password):
            flask.session['user_code'] = password
            flask.flash("Login successful!", "success")
            return flask.redirect(url_for('account'))

        else:  # match found, send to account()
            flask.flash("Error! Incorrect code presented.", "danger")
            return flask.redirect(url_for('login'))

    else:
        pass

    return flask.render_template('login.html')


@app.route('/account', methods=['POST', 'GET'])
def account():
    """
    Account menu. Shows different options available to users.
    """
    if check_401(): return flask.render_template("error.html", code=401, msg="Unauthorized")
    if 'event_id' in flask.session.keys(): flask.session.pop('event_id', None)

    if flask.request.method == 'POST':  # called when a form submit is clicked
        event_id: str = flask.request.form['event_id']

        logout_code = "-1"
        admin_code = "0"

        if event_id == logout_code:
            flask.flash("Logged Out", "warning")
            flask.session.pop('user_code', None)
            return flask.redirect('login')

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
    if check_401("Admin"): return flask.render_template("error.html", code=401, msg="Unauthorized")

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
            new_user_code = proj_util.random_code(8)
            models.db.session.add(models.User(code=new_user_code))
            models.db.session.commit()
            flask.flash("New login code generated: {new_code}".format(new_code=new_user_code), "success")
            return flask.redirect('admin')

        if request_code == "BACKUP_SCOREBOARD":
            if not scoreboard_global:
                update_scoreboard()
                flask.flash("Scoreboard is updated!", "success")
            proj_util.write_to_csv("backup", "scoreboard.csv", scoreboard_global)
            backup_scoreboard = os.path.join("backup", "scoreboard.csv")
            return flask.send_file(backup_scoreboard, as_attachment=True)

        if request_code == "BACKUP_DATABASE":
            models.backup_tables_all()
            backup_zip = proj_util.zip_folder(os.path.join("backup", "database"))
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
    if check_401("Admin"): return flask.render_template("error.html", code=401, msg="Unauthorized")
    view_user = flask.session['view_user']  # grab user's id and login code

    if flask.request.method == 'POST':
        request_code = flask.request.form['request_code']

        if request_code.startswith("ADD_"):  # create new access row
            event_id = request_code.split("_")[1]
            user_id = view_user["id"]
            row = models.Access(event_id=event_id, user_id=user_id)

            models.db.session.add(row)
            models.db.session.commit()

            event_name = row.event.name
            flask.flash("Access to {event_name} successfully added".format(event_name=event_name), "success")
            return flask.redirect(url_for('viewuser'))

        if request_code.startswith("REMOVE_"):  # find the existing row and remove it
            event_id = request_code.split("_")[1]
            user_id = view_user["id"]
            row = models.Access.query.filter_by(event_id=event_id, user_id=user_id).first()

            event_name = row.event.name
            models.db.session.delete(row)
            models.db.session.commit()

            flask.flash("Access to {event_name} successfully removed".format(event_name=event_name), "warning")
            return flask.redirect(url_for('viewuser'))

        if request_code.startswith("DROPUSER_"):  # remove user account
            user_id = request_code.split("_")[1]
            permissions = models.Access.query.filter_by(user_id=user_id).all()
            for permission in permissions:
                models.db.session.delete(permission)
            models.db.session.commit()

            user = models.User.query.filter_by(id=user_id).first()
            user_code = user.code
            models.db.session.delete(user)
            models.db.session.commit()

            flask.flash("{user_code} was successfully deleted.".format(user_code=user_code), "success")
            return flask.redirect(url_for('admin'))

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
    Score update menu, version 2
    Score update is only for 1-4th place
    0th place is N/A, 5th place is eliminated
    """
    # check authorization
    if check_401(): return flask.render_template("error.html", code=401, msg="Unauthorized")
    if 'event_id' not in flask.session.keys(): return flask.redirect(url_for('account'))

    event_id = flask.session['event_id']
    event = models.Event.query.filter_by(id=event_id).first()
    teams = models.Team.query.order_by(models.Team.id).all()

    if check_401(event.name): return flask.render_template("error.html", code=401, msg="Unauthorized")

    # initialize page
    display_mode = "EDIT"
    placements_scored = {1: 0,
                         2: 0,
                         3: 0,
                         4: 0}
    for place in placements_scored:
        team = models.Placement.query.filter_by(events_id=event_id, place=place).first()
        if team is None: break
        else: placements_scored[place] = team.teams_id

    dropdown_options = {0: "None"}
    for team in teams:
        dropdown_options[team.id] = team.name

    # handle POST request
    if flask.request.method == 'POST':
        request_code = flask.request.form['request_code']

        if request_code == 'CONFIRM':
            display_mode = 'CONFIRM'
            placements_scored = {1: flask.request.form['place1'],
                                 2: flask.request.form['place2'],
                                 3: flask.request.form['place3'],
                                 4: flask.request.form['place4']}

            dropdown_options = {1: "None",
                                2: "None",
                                3: "None",
                                4: "None"}
            for place in dropdown_options:
                if not placements_scored[place] == "0":
                    dropdown_options[place] = models.Team.query.filter_by(id=placements_scored[place]).first().name
                else: pass

        if request_code == 'SUBMIT':
            flask.flash("Scores submitted!", "success")
            display_mode = 'SUBMIT'
            placements_scored = {1: flask.request.form['place1'],
                                 2: flask.request.form['place2'],
                                 3: flask.request.form['place3'],
                                 4: flask.request.form['place4']}

            placements = models.Placement.query.filter_by(events_id=event_id).all()
            for placement in placements:
                if placement.teams_id == int(placements_scored[1]):
                    placement.place = 1
                elif placement.teams_id == int(placements_scored[2]):
                    placement.place = 2
                elif placement.teams_id == int(placements_scored[3]):
                    placement.place = 3
                elif placement.teams_id == int(placements_scored[4]):
                    placement.place = 4
                else:
                    placement.place = 5
                models.db.session.commit()
            update_scoreboard()

    return flask.render_template("edit.html",
                                 event=event,
                                 mode=display_mode,
                                 placements=placements_scored,
                                 dropdown=dropdown_options)


@app.route('/labs', methods=['POST', 'GET'])
def labs():
    flash("HIRING NOW! MOS, RANK Immaterial!", 'danger')
    return flask.render_template("labs.html")

@app.route('/bracket/<event_id>')
def bracket(event_id):
    
    return flask.render_template('bracket/{event_id}.html'.format(event_id=event_id))

@app.route('/medalhonor/<hero>')
def medalhonor(hero):
    
    return flask.render_template('medalhonor/{hero}.html'.format(hero=hero))



if __name__ == '__main__':
    LL.print_logo()
    if env.DEBUG: print("Running on localhost: http://127.0.0.1:5000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    # app.run(host="0.0.0.0", debug=env.DEBUG)
