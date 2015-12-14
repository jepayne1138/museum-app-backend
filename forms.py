from wtforms import Form
from wtforms.fields import TextField, TextAreaField, FileField, DateTimeField, \
                           SelectField, FieldList
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length
from wtforms.widgets import HTMLString, html_params
from database import MediaResource, ExhibitSection, ViewController


ALLOWED_EXTENSIONS = set(['mp3', 'png', 'jpg', 'mp4'])


class DateTimePickerWidget(object):

    """Date Time picker from Eonasdan GitHub
    https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/fieldwidgets.py#L5
    """

    data_template = (
        '<div class="input-group date appbuilder_datetime" id="datetimepicker">'
            '<span class="input-group-addon"><i class="fa fa-calendar cursor-hand"></i>'
            '</span>'
            '<input class="form-control" data-format="yyyy-MM-dd hh:mm:ss" %(text)s/>'
        '</div>'
    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        if not field.data:
            field.data = ""
        template = self.data_template

        a = HTMLString(
            template % {'text': html_params(type='text', value=field.data, **kwargs)}
        )
        print(a)
        return a


class ExhibitForm(Form):
    view_controller = QuerySelectField('View Controller Type',
        query_factory=ViewController.query.all,
        get_pk=lambda a: a.viewControllerID,
        get_label=lambda a: a.name
    )
    name = TextField('Exhibit Name', [Length(min=1)])
    text = TextAreaField('Text')
    exhibit_section = QuerySelectField('Exhibit Seciton',
        query_factory=ExhibitSection.query.all,
        get_pk=lambda a: a.exhibitSectionID,
        get_label=lambda a: a.name
    )
    resource = QuerySelectField('Resource',
        query_factory=MediaResource.query.all,
        get_pk=lambda a: a.resourceID,
        get_label=lambda a: a.url
    )


class ResourceForm(Form):
    upload = FileField('Resource File')


class EventForm(Form):
    name = TextField('Event Name', [Length(min=1)])
    description = TextAreaField('Description')
    # resource
    startTime = DateTimeField('Start Time', widget=DateTimePickerWidget())
    endTime = DateTimeField('End Time', widget=DateTimePickerWidget())


class ExhibitSectionForm(Form):
    name = TextField('Exhibit Section Name', [Length(min=1)])
