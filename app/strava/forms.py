from flask.ext.wtf import Form
from wtforms import IntegerField, SubmitField, StringField
from wtforms.validators import NumberRange


class CountyForm(Form):
    county_number = IntegerField('County Number', [NumberRange(min=1, max=56, message="Counties are between 1 and 56")])
    submit = SubmitField("Search")


class AddRider(Form):
    name = StringField('Name')
    submit = SubmitField('Register')
