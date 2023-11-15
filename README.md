# Guadalcanal-Cup-Scoring

This Flask based web app keeps scores for different events,
and displays tabulated scoreboard to all users.

## How To Set Up
This app is written for Python version 3.11.4. Ensure your
environment has both Python 3.11.4 and the dependencies
listed in [requirements.txt](requirements.txt).

In addition, make sure to populate the [env.py](env.py)
file. It should include:
* DB_URI: Uniform Resource Identifier for the database.
It might look like: ```postgresql://username:password@hostname/databasename```
* GMAP_KEY: API Key for the Google Maps API. It should be
a long string of case-sensitive alphanumeric characters.
* FLASK_SECRETKEY: key used by Flask to generate session
cookies. It should be a long string.
* DEBUG: This variable is used to distinguish between
a development environment and a production environment.
set as ``True`` in dev, and set as ``False`` in prod.

After all setup, run [app.py](app.py). This will
automatically allow ``waitress`` to serve the application.

## Main Features
### Scoreboard
Upon loading the scoreboard for the first time, a snapshot
of the scoreboard is taken and stored in ``scoreboard_global``,
as a 2D array. This is then displayed to all users accessing
the scoreboard. It is also updated whenever an event owner
updates the scores, or whenever an admin force updates the
scoreboard. This minimizes the number of times the application
needs to access the database, *which is the bottleneck for the
application.*

### Welcome
Upon accessing the root directory of the website, users will
be directed to a fullscreen logo of Lightning Labs for 0.5
seconds, then be redirected to the info page. This functionality
is dependent on javascript. Clicking the logo also redirects
users to the info page. This page does not inherit from the
[base.html](templates/base.html) template.

### Base
The frontend uses Bootstrap version 4. The base imports necessary
Bootstrap dependencies in the header.
Navbar contains four buttons. It is not recommended to add more
buttons, because the layout changes to two lines on mobile.
Following that are the flash messages. This uses the Bootstrap
alerts, and it can be called with ``flask.flash(message, alertlevel)``.
See the documentation [here](https://getbootstrap.com/docs/4.0/components/alerts/).

### Info
Info page is fully hard coded with HTML and some JavaScript.
It also makes use of Bootstrap for certain div styling.

## Maintenance and Operation
### Database
Score is kept inside a database. The database is accessed
through ``Flask-SQLAlchemy``, which provides a way to interact
with the database without using SQL queries. Database queries
are made in the following instances:
* Seeding database
* Updating scoreboard
* Taking a snapshot of the scoreboard

Database connection is most likely to be the bottleneck, so
ensure that the number of SQL queries are minimized.

### Admin Account
Admin account is created using a [seed file](seed2023.py). Ensure
a new User object is created, and an associated Access with ``event_id=0``
is created as well. Admin accounts can also create new accounts,
and give and take away access from existing accounts. If new codes
need to be generated, it can be done by logging in and clicking
on the Admin button.

Admins can also back up the database and force scoreboard update.


### User Account/Updating Scoreboard
Based on the seed file or live generation, user account can be
created. Based on the Access, users can update score for events.
Users can select the teams that placed in the top 4, and the
score submission sets ``placement`` as ``5`` for all other teams.
When ``placement == 0``, it displays as ``N/A`` on scoreboard,
and when ``placement == 5``, it displays as ``0`` on scoreboard.
