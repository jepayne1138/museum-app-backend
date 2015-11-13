import argparse
from flask import Flask
from database import db_session, init_db, \
                     ViewController, MetadataInteger, Exhibit, ExhibitSection, \
                     MediaResource
from flask.ext.restful import Resource, Api, fields, marshal, reqparse
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)


# Database ORM ----------------------------------------------------------------


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def sessionAdd(obj):
    try:
        db_session.add(obj)
        db_session.flush()
    except IntegrityError:
        db_session.rollback()



# Setup database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress warning, can set to True if needed in future


# Create the database schema if it doesn't exist
init_db()

# Define database schema

# Initialize the revision number
sessionAdd(MetadataInteger(key='revision', value=0))
db_session.commit()
# Get the current revision number
revision = MetadataInteger.query.filter_by(key='revision').first().value

# Define ViewController objects
view_controllers = {
    'text': ViewController(key='text', name='ExhibitTextViewController', segueID='toExhibitTextViewController', revision=revision),
    'image': ViewController(key='image', name='ExhibitImageViewController', segueID='toExhibitImageViewController', revision=revision),
    'video': ViewController(key='video', name='ExhibitVideoViewController', segueID='toExhibitVideoViewController', revision=revision),
    'audio': ViewController(key='audio', name='ExhibitAudioViewController', segueID='toExhibitAudioViewController', revision=revision),
    'web': ViewController(key='web', name='ExhibitWebViewController', segueID='toExhibitWebViewController', revision=revision),
}


# Populate default view controllers
for name, vc in view_controllers.items():
    sessionAdd(vc)
db_session.commit()
# Update view controller dictionary - Only necessary if going to programatically add Exhibits here
# view_controllers.update({vc.Key: vc for vc in ViewController.query.all()})


# API -------------------------------------------------------------------------


# Setup API
api = Api(app)


class ViewControllerListAPI(Resource):

    """Returns a list of all supported ViewControllers

    Not really a necessary API call, but was simple to implement and return a
    set list of static information to test the API and database.

    Upon a get request returns
    """

    get_return_fields = {
        'name': fields.String,
        'segueID': fields.String,
        'revision': fields.Integer,
    }

    def get(self):
        all_vc = ViewController.query.all()
        return {
            'viewcontrollers': [
                marshal(vc.__dict__, self.get_return_fields) for vc in all_vc
            ]
        }


class UpdateAPI(Resource):

    """Returns a list of all exhibits that need to be updated

    Get request takes a revision number as mandatory input.
    """

    exhibit_return_fields = {
        'name': fields.String,
        'exhibitSectionID': fields.Integer,
        'viewControllerID': fields.Integer,
        'text': fields.String,
        'resourceID': fields.Integer,
    }
    exhibit_section_return_fields = {
        'exhibitsSectionID': fields.Integer,
        'name': fields.String,
    }
    resource_return_fields = {
        'resourceID': fields.Integer,
        'url': fields.String,
    }

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('revision', type=int, required=True, help='Could not convert revision number to integer')

        args = parser.parse_args()

        # Get latest revision number
        cur_revision = MetadataInteger.query.filter_by(key='revision').first().value

        # Get exhibit update data
        exhibits = Exhibit.query.filter(Exhibit.revision > args.revision).all()
        # Get exhibit section update data
        exhibit_sections = ExhibitSection.query.filter(ExhibitSection.revision > args.revision).all()
        # Get resource update data
        resources = MediaResource.query.filter(MediaResource.revision > args.revision).all()
        return {
            'exhibits': [marshal(exhibit.__dict__, self.exhibit_return_fields) for exhibit in exhibits],
            'exhibit_sections': [marshal(exhibit_section.__dict__, self.exhibit_section_return_fields) for exhibit_section in exhibit_sections],
            'resources': [marshal(resource.__dict__, self.resource_return_fields) for resource in resources],
            'revision': cur_revision
        }


api.add_resource(ViewControllerListAPI, '/viewcontrollers', endpoint='viewcontrollers')
api.add_resource(UpdateAPI, '/update', endpoint='update')


# Run program -----------------------------------------------------------------


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Provides the backend server and exposed API for the Museum App'
    )
    parser.add_argument(
        '-a', '--address', type=str, default='localhost',
        help='Host address for running the server'
    )
    parser.add_argument(
        '-p', '--port', type=int, default=5000,
        help='Port for running the server'
    )
    args = parser.parse_args()

    app.run(host=args.address, port=args.port, debug=False)
