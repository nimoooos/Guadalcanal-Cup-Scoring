from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from ordinalize import num_to_ordinal


class TeamRankForm(FlaskForm):
    submit = SubmitField("Submit Rankings")
    team_list = []
    input_list = []

    # noinspection PyMissingConstructor
    def __init__(self, teams):
        for team in teams:  # update team_list
            self.team_list.append(team)

        # create a choice_list for every team
        num_teams = len(self.team_list)
        choice_list = []
        for i in range(num_teams):
            choice_list.append((i + 1, num_to_ordinal(i + 1)))

        # add input items into self.input_list
        for team in self.team_list:
            self.input_list.append(SelectField(team.name, choices=choice_list))
