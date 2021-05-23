# !/usr/bin/env python3
# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from models import Shows, Venue, Artist, db
from . import bp
import dateutil.parser
from flask import render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_migrate import Migrate
from app.forms import VenueForm
from app import format_datetime


@bp.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------
@bp.route("/venues")
def venues():
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    try:
        venues = Venue.query.distinct(Venue.city, Venue.state).all()
        if venues:
            for venue in venues:
                upcoming_shows = len(Venue.query.join(Shows)
                                     .filter(Shows.c.start_time > datetime.utcnow(),
                                             Shows.c.venue_id == venue.id).all())
                data.append({
                        "city": venue.city,
                        "state": venue.state,
                        "venues": [{
                            "id": v.id,
                            "name": v.name,
                            "num_upcoming_shows": upcoming_shows
                                   }for v in Venue.query.filter_by(city=venue.city, state=venue.state).all()]
                        })
    except Exception as e:
        print(e)
        pass
    return render_template("pages/venues.html", areas=data)


@bp.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on Venues //artists// with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    search_response = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = []
    for venue in search_response:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Venue.query.join(Shows).filter(Shows.c.start_time > datetime.utcnow(), Shows.c.venue_id == venue.id).all())
        })
        print(data)

    response = {
        "count": len(search_response),
        "data": data
    }
    return render_template("pages/search_venues.html", results=response,
                           search_term=request.form.get("search_term", ""))


@bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter_by(id=venue_id).first()
    data = None
    shows = db.session.query(Shows).filter(Shows.c.venue_id == venue.id).all()
    artist_up_show = []
    artist_past_show = []
    for show in shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        start_time = format_datetime(str(show.start_time))
        artist_show = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": start_time
        }
        if show.start_time >= datetime.utcnow():
            artist_up_show.append(artist_show)
        elif show.start_time < datetime.utcnow():
            artist_past_show.append(artist_show)
    data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "upcoming_shows": artist_up_show,
            "upcoming_shows_count": len(artist_up_show),
            "past_shows": artist_past_show,
            "past_shows_count": len(artist_past_show),

            }
    return render_template("pages/show_venue.html", venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@bp.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@bp.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm()
    # venue_form.validate()
    name = venue_form.name.data
    phone = venue_form.phone.data
    address = venue_form.address.data
    city = venue_form.city.data
    image_url = venue_form.image_link.data
    facebook_url = venue_form.facebook_link.data
    state = venue_form.state.data
    genres = venue_form.genres.data
    seeking_talent = venue_form.seeking_talent.data
    seeking_description = venue_form.seeking_description.data
    website = venue_form.website_link.data

    # DONE: insert form data as a new Venue record in the db, instead
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_url,
                            facebook_link=facebook_url, genres=genres,
                    website_link=website,seeking_talent=seeking_talent,
                        seeking_description=seeking_description)
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash("Venue " + name + " was successfully listed!")
        # Done: modify data to be the data object returned from db insertion
    except Exception as e:
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash("An error occurred. Venue " + data.name + " could not be listed.")
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash("An error occurred. Venue " +
              name + " could not be listed.")
        db.session.flush()
        print(e)
    return render_template("pages/home.html")


@bp.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("bp.index"))


@bp.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()

    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.address = form.address.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data

    db.session.add(venue)
    db.session.commit()
    return redirect(url_for('bp.show_venue', venue_id=venue_id))


@bp.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()

    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link

    # DONE: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)
