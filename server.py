import argparse
from flask import Flask
from database import db_session, init_db, ViewController
from flask.ext.restful import Resource, Api, fields, marshal
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)


# Database ORM ----------------------------------------------------------------


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Setup database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress warning, can set to True if needed in future


# Create the database schema if it doesn't exist
init_db()

# Define database schema

# Define ViewController objects
view_controllers = {
    'text': ViewController(Key='text', Name='ExhibitTextViewController', SegueID='toExhibitTextViewController'),
    'image': ViewController(Key='image', Name='ExhibitImageViewController', SegueID='toExhibitImageViewController'),
    'video': ViewController(Key='video', Name='ExhibitVideoViewController', SegueID='toExhibitVideoViewController'),
    'audio': ViewController(Key='audio', Name='ExhibitAudioViewController', SegueID='toExhibitAudioViewController'),
    'web': ViewController(Key='web', Name='ExhibitWebViewController', SegueID='toExhibitWebViewController'),
}


# Populate default view controllers
for name, vc in view_controllers.items():
    try:
        db_session.add(vc)
        db_session.flush()
    except IntegrityError:
        db_session.rollback()
db_session.commit()
# Update view controller dictionary - Only necessary if going to programatically add Exhibits here
# view_controllers.update({vc.Key: vc for vc in ViewController.query.all()})


# API -------------------------------------------------------------------------


# Setup API
api = Api(app)


class ViewcontrollerListAPI(Resource):

    """Returns a list of all supported ViewControllers

    Not really a necessary API call, but was simple to implement and return a
    set list of static information to test the API and database.

    Upon a get request returns
    """

    get_return_fields = {
        'name': fields.String,
        'segueID': fields.String,
    }

    def get(self):
        all_vc = ViewController.query.all()
        vc_list = [
            {'name': vc.Name, 'segueID': vc.SegueID}
            for vc in all_vc
        ]
        return {
            'viewcontrollers': [
                marshal(vc_dict, self.get_return_fields) for vc_dict in vc_list
            ]
        }

api.add_resource(ViewcontrollerListAPI, '/viewcontrollers', endpoint='viewcontrollers')


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
