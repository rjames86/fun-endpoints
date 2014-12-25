from flask.ext.wtf import Form
from wtforms import IntegerField, SubmitField
from wtforms.validators import Required, NumberRange


class CountyForm(Form):
    county_number = IntegerField('Country Code', [NumberRange(min=1, max=56, message="Counties are between 1 and 56")])
    submit = SubmitField("Search")
