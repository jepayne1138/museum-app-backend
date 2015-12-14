import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = os.path.join(os.getcwd(), 'museum_backend.db')

engine = create_engine('sqlite:///{}'.format(DB_PATH), convert_unicode=True)
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)


Base = declarative_base()
Base.query = db_session.query_property()


class ExhibitSection(Base):

    __tablename__ = 'ExhbitSections'

    exhibitSectionID = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    exhibits = relationship('Exhibit', backref='exhibitSection')
    revision = Column(Integer)


class Exhibit(Base):

    __tablename__ = 'Exhibits'

    exhibitID = Column(Integer, primary_key=True)
    name = Column(String)
    exhibitSectionID = Column(Integer, ForeignKey('ExhbitSections.exhibitSectionID'))
    viewControllerID = Column(Integer, ForeignKey('ViewControllers.viewControllerID'))
    viewController = relationship('ViewController')
    text = Column(String)
    resourceID = Column(Integer, ForeignKey('Resources.resourceID'))
    resource = relationship('MediaResource')
    revision = Column(Integer)


class ViewController(Base):

    __tablename__ = 'ViewControllers'

    viewControllerID = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    segueID = Column(String, unique=True)
    revision = Column(Integer)


class Event(Base):

    __tablename__ = 'Events'

    eventID = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    resourceID = Column(Integer, ForeignKey('Resources.resourceID'))
    resource = relationship('MediaResource')
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    revision = Column(Integer)


class MediaResource(Base):

    __tablename__ = 'Resources'

    resourceID = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    revision = Column(Integer)


class MetadataInteger(Base):

    __tablename__ = 'Metadata'

    metadataIntegerID = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(Integer)


class Information(Base):

    __tablename__ = 'Information'

    informationID = Column(Integer, primary_key=True)
    information = Column(String)
    parking = Column(String)
    hours = Column(String)
    location = Column(String)
    revision = Column(Integer)


def init_db():
    Base.metadata.create_all(bind=engine)
