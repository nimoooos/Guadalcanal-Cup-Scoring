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
    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
