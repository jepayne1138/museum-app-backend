from wtforms import Form
from wtforms.fields import TextField, TextAreaField
from wtforms.validators import Length


class ExhibitForm(Form):
    name = TextField('Exhibit Name', [Length(min=1)])
    text = TextAreaField('Text')
