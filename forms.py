from wtforms import Form
from wtforms.fields import TextField, TextAreaField, FileField
from wtforms.validators import Length


class ExhibitForm(Form):
    name = TextField('Exhibit Name', [Length(min=1)])
    text = TextAreaField('Text')

class Resource(Form):
    upload = FileField('Resource File', [Length(min=1)])
