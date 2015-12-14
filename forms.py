from wtforms import Form
from wtforms.fields import TextField, TextAreaField, FileField
from wtforms.validators import Length


ALLOWED_EXTENSIONS = set(['mp3', 'png', 'jpg', 'mp4'])


class ExhibitForm(Form):
    name = TextField('Exhibit Name', [Length(min=1)])
    text = TextAreaField('Text')


class ResourceForm(Form):
    upload = FileField('Resource File')
