"""Note that _formhelpers.html was taken from flask documentation
http://flask.pocoo.org/docs/0.10/patterns/wtforms/
"""
import os
import argparse
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, \
                  send_from_directory
from database import db_session, init_db, \
                     ViewController, MetadataInteger, Exhibit, ExhibitSection, \
                     MediaResource, Event, Information
import marshallers
import forms
from flask.ext.restful import Resource, Api, marshal_with, reqparse
from werkzeug import secure_filename
from sqlalchemy import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.exc import IntegrityError


UPLOAD_PATH = os.path.join(os.getcwd(), 'static', 'resources')

app = Flask(__name__)

csv_sort_order = {
    'Information': 1,
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
        db_session.merge(obj)
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
        information = Information.query.filter(Information.revision > args.revision).all()
        view_controllers = ViewController.query.filter(ViewController.revision > args.revision).all()
        exhibits = Exhibit.query.filter(Exhibit.revision > args.revision).all()
        exhibit_sections = ExhibitSection.query.filter(ExhibitSection.revision > args.revision).all()
        resources = MediaResource.query.filter(MediaResource.revision > args.revision).all()
        events = Event.query.filter(Event.revision > args.revision).all()
        return {
            'information': information,
            'view_controllers': view_controllers,
            'exhibits': exhibits,
            'exhibit_sections': exhibit_sections,
            'resources': resources,
            'events': events,
            'revision': revision
        }


# Add all resources to the api
api.add_resource(ViewControllerListAPI, '/viewcontrollers', endpoint='viewcontrollers')
api.add_resource(UpdateAPI, '/update', endpoint='update')


# File upload handlers --------------------------------------------------------


ALLOWED_EXTENSIONS = forms.ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_PATH


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Web interface ---------------------------------------------------------------


@app.route('/')
@app.route('/index')
def index():
    print('index')
    return render_template('index.html')


@app.route('/resources/<path:path>')
def resoruce(path):
    return send_from_directory(UPLOAD_PATH, path)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = forms.ResourceForm(request.form)
    if request.method == 'POST' and request.files[form.upload.name].filename:
        raw_filename = request.files[form.upload.name].filename
        if allowed_file(raw_filename):
            filename = secure_filename(raw_filename)
            upload_file = request.files[form.upload.name]
            upload_path = os.path.join(UPLOAD_PATH, filename)
            upload_file.save(upload_path)
            # Save to database
            revision = MetadataInteger.query.filter_by(key='revision').first()
            revision.value += 1
            new_resource = MediaResource(
                url=filename,
                revision=revision.value,
            )
            sessionAdd(new_resource)
            db_session.commit()

        else:
            # Put some kind of error page here
            print('Failed to upload file')
        return redirect(url_for('index'))
    return render_template('add-resource.html', form=form)


@app.route('/add-exhibit', methods=['GET', 'POST'])
def add_exhibit():
    form = forms.ExhibitForm(request.form)
    if request.method == 'POST' and form.validate():
        revision = MetadataInteger.query.filter_by(key='revision').first()
        revision.value += 1
        new_exhibit = Exhibit(
            name=form.name.data,
            exhibitSectionID=form.exhibit_section.data.exhibitSectionID,
            viewControllerID=form.view_controller.data.viewControllerID,
            text=form.text.data,
            resourceID=form.resource.data.resourceID,
            revision=revision.value,
        )
        sessionAdd(new_exhibit)
        db_session.commit()
        return redirect(url_for('index'))

    return render_template('add-exhibit.html', form=form)


@app.route('/add-exhibit-section', methods=['GET', 'POST'])
def add_exhibit_section():
    form = forms.ExhibitSectionForm(request.form)
    if request.method == 'POST' and form.validate():
        revision = MetadataInteger.query.filter_by(key='revision').first()
        revision.value += 1
        new_exhibit_section = ExhibitSection(
            name=form.name.data,
            revision=revision.value,
        )
        sessionAdd(new_exhibit_section)
        db_session.commit()
        return redirect(url_for('index'))

    return render_template('add-exhibit-section.html', form=form)


@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    form = forms.EventForm(request.form)
    if request.method == 'POST' and form.validate():
        revision = MetadataInteger.query.filter_by(key='revision').first()
        revision.value += 1
        new_event = Event(
            name=form.name.data,
            description=form.description.data,
            resourceID=1,
            startTime=form.startTime.data,
            endTime=form.endTime.data,
            revision=revision.value,
        )
        sessionAdd(new_event)
        db_session.commit()
        return redirect(url_for('index'))

    return render_template('add-event.html', form=form)


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
