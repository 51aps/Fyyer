# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from app import db
from datetime import datetime

# DONE: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

Shows = db.Table("Shows",
                 db.Column("id", db.Integer, primary_key=True),
                 db.Column("artist_id", db.Integer, db.ForeignKey("Artist.id")),
                 db.Column("venue_id", db.Integer, db.ForeignKey("Venue.id")),
                 db.Column("start_time", db.DateTime, default=datetime.utcnow()))


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120), index=True)
    state = db.Column(db.String(120), index=True)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String())
    website_link = db.Column(db.String(500))
    artists = db.relationship("Artist", secondary=Shows,
                              backref=db.backref('Venue',
                                            cascade="all,delete"), lazy=True)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(300))
    website_link = db.Column(db.String(500))

    venues = db.relationship("Venue", secondary=Shows,  backref="Artist", lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
