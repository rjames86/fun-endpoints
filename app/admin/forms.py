from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required


class TokenForm(Form):
    name = StringField("Name of user:", validators=[Required()])
    token = PasswordField('Token', validators=[Required()])
    submit = SubmitField("Submit")

