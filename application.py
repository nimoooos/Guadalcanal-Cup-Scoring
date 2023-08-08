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
    for t in teams:
        t.update_score()
    teams = models.Team.query.order_by(-models.Team.score).all()  # list of teams, ordered by score (desc)
    return flask.render_template('index.html', teams=teams)


if __name__ == '__main__':
    app.run(debug=True)
