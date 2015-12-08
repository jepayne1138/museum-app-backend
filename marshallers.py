from flask.ext.restful import fields


# Helper nested marshallers
exhibit = {
    'exhibitID': fields.Integer,
    'name': fields.String,
    'exhibitSectionID': fields.Integer,
    'viewControllerID': fields.Integer,
    'text': fields.String,
    'resourceID': fields.Integer,
}
exhibit_section = {
    'exhibitSectionID': fields.Integer,
    'name': fields.String,
}
resource = {
    'resourceID': fields.Integer,
    'url': fields.String,
}
event = {
    'eventID': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'resourceID': fields.Integer,
    'startTime': fields.DateTime(dt_format='iso8601'),
    'endTime': fields.DateTime(dt_format='iso8601'),
}


# Main API return marshallers
view_controller = {
    'viewControllerID': fields.Integer,
    'name': fields.String,
    'segueID': fields.String,
    'revision': fields.Integer,
}

update = {
    'exhibits': fields.List(fields.Nested(exhibit)),
    'exhibit_sections': fields.List(fields.Nested(exhibit_section)),
    'resources': fields.List(fields.Nested(resource)),
    'events': fields.List(fields.Nested(event)),
    'revision': fields.Integer,
}
