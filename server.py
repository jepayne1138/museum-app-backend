"""Note that _formhelpers.html was taken from flask documentation
http://flask.pocoo.org/docs/0.10/patterns/wtforms/
"""
import argparse
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from database import db_session, init_db, \
                     ViewController, MetadataInteger, Exhibit, ExhibitSection, \
                     MediaResource, Event
import marshallers
import forms
from flask.ext.restful import Resource, Api, marshal_with, reqparse
from sqlalchemy import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

csv_sort_order = {
    'ViewController': 1,
    'MediaResource': 1,
    'MetadataInteger': 1,
    'Event': 2,
    'ExhibitSection': 2,
    'Exhibit': 3,
}


def csv_sort(row):
    return csv_sort_order[row[0]]

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


# API -------------------------------------------------------------------------


# Setup API
api = Api(app)


class ViewControllerListAPI(Resource):

    """Returns a list of all supported ViewControllers

    Not really a necessary API call, but was simple to implement and return a
    set list of static information to test the API and database.

    Upon a get request returns
    """

    @marshal_with(marshallers.view_controller, envelope='view_controllers')
    def get(self):
        view_controllers = ViewController.query.all()
        return view_controllers


class UpdateAPI(Resource):

    """Returns a list of all exhibits that need to be updated

    Get request takes a revision number as mandatory input.
    """

    @marshal_with(marshallers.update)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('revision', type=int, required=True, help='Could not convert revision number to integer')
        args = parser.parse_args()

        # Get latest revision number
        revision = MetadataInteger.query.filter_by(key='revision').first().value

        # Get all table information
        exhibits = Exhibit.query.filter(Exhibit.revision > args.revision).all()
        exhibit_sections = ExhibitSection.query.filter(ExhibitSection.revision > args.revision).all()
        resources = MediaResource.query.filter(MediaResource.revision > args.revision).all()
        events = Event.query.filter(Event.revision > args.revision).all()
        return {
            'exhibits': exhibits,
            'exhibit_sections': exhibit_sections,
            'resources': resources,
            'events': events,
            'revision': revision
        }


# Add all resources to the api
api.add_resource(ViewControllerListAPI, '/viewcontrollers', endpoint='viewcontrollers')
api.add_resource(UpdateAPI, '/update', endpoint='update')


# Web interface ---------------------------------------------------------------


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/add-exhibit', methods=['GET', 'POST'])
def add_exhibit():
    form = forms.ExhibitForm(request.form)
    revision = MetadataInteger.query.filter_by(key='revision').first().value
    if request.method == 'POST' and form.validate():
        new_exhibit = Exhibit(
            name=form.name.data,
            exhibitSectionID=1,
            viewControllerID=1,
            text=form.text.data,
            resourceID=1,
            revision=revision,
        )
        sessionAdd(new_exhibit)
        db_session.commit()
        return redirect(url_for('index'))

    return render_template('add-exhibit.html', form=form)


# Run program -----------------------------------------------------------------

def main(args):
    # Create the database schema if it doesn't exist
    init_db()

    # Initialize the revision number
    sessionAdd(MetadataInteger(key='revision', value=0))
    db_session.commit()
    # Get the current revision number
    revision = MetadataInteger.query.filter_by(key='revision').first()

    # Populate date from csv
    if args.csv:
        revision.value += 1
        with open(args.csv, 'r') as csv_file:
            db_reader = csv.reader(csv_file)
            # Sort the input so that foreign keys will be satisfied
            sorted_list = sorted(list(db_reader), key=csv_sort)
            # Parse csv and convert to database entries (Needs more error handling)
            # Currently assumes perfect input
            for row in sorted_list:
                model_name = row[0]
                model = globals()[model_name]
                mapper = inspect(model)
                values = row[1:]
                values.append(int(revision.value))
                columns = [x.key for x in mapper.attrs if isinstance(x, ColumnProperty)]
                id_name = columns[0]
                parsed_dict = dict(zip(columns, values))
                if model_name == 'Event':
                    parsed_dict['startTime'] = datetime.strptime(parsed_dict['startTime'], '%Y-%m-%d %H:%M:%S')
                    parsed_dict['endTime'] = datetime.strptime(parsed_dict['endTime'], '%Y-%m-%d %H:%M:%S')
                if parsed_dict[id_name] == '0':
                    del parsed_dict[id_name]
                print(parsed_dict)
                sessionAdd(model(**parsed_dict))

        # Commit the changes
        db_session.commit()

    # Run the server
    app.run(host=args.address, port=args.port, debug=False)


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
    parser.add_argument(
        '-c', '--csv', type=str, default='',
        help='Populate the database from a given .csv file'
    )
    args = parser.parse_args()

    main(args)
