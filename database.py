import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = os.path.join(os.getcwd(), 'test.db')

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

    ExhibitSectionID = Column(Integer, primary_key=True)
    Name = Column(String)
    Exhibits = relationship('Exhibit', backref='ExhibitSection')


class Exhibit(Base):

    __tablename__ = 'Exhibits'

    ExhibitID = Column(Integer, primary_key=True)
    Name = Column(String)
    ExhibitSectionID = Column(Integer, ForeignKey('ExhbitSections.ExhibitSectionID'))
    ViewControllerID = Column(Integer, ForeignKey('ViewControllers.ViewControllerID'))
    ViewController = relationship('ViewController')
    Text = Column(String)
    MediaPath = Column(String, nullable=True)


class ViewController(Base):

    __tablename__ = 'ViewControllers'

    ViewControllerID = Column(Integer, primary_key=True)
    Key = Column(String, unique=True)
    Name = Column(String, unique=True)
    SegueID = Column(String, unique=True)


def init_db():
    Base.metadata.create_all(bind=engine)
