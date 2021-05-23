#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request
from flask import Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(240), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))
    upcoming_shows = db.Column(db.Integer)

    def __repr__(self):
        return f'<Venue {self.id} name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))

    def __repr__(self):
        return f'<Artist {self.id} name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False,
        default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),
        nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),
        nullable=False)
    artist = db.relationship(Artist,
        backref=db.backref('shows', cascade='all, delete'))
    venue = db.relationship(Venue,
        backref=db.backref('shows', cascade='all, delete'))

    def __repr__(self):
        return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    else:
        date = value
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()
    # Use set so there are no duplicate venues
    locations = set()

    for venue in venues:
        # add city/state tuples
      locations.add((venue.city, venue.state))

    # for each unique city/state, add venues
    for location in locations:
      data.append({
          "city": location[0],
          "state": location[1],
          "venues": []
      })

    for venue in venues:
      num_upcoming_shows = 0

      shows = Show.query.filter_by(venue_id=venue.id).all()

      # get current date to filter num_upcoming_shows
      current_date = datetime.now()

      for show in shows:
        if show.start_time > current_date:
            num_upcoming_shows += 1

      for venue_location in data:
        if venue.state == venue_location['state'] and venue.city == venue_location['city']:
          venue_location['venues'].append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": num_upcoming_shows
          })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['GET', 'POST'])
def search_venues():

    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    venue_list = []
    now = datetime.now()
    for venue in venues:
        venue_list.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Venue.query.join(Show).filter(Show.start_time > datetime.utcnow(), Show.venue_id == venue.id).all())
        })
        print(venue_list)

    response = {
        "count": len(venues),
        "data": venue_list
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
    venue = Venue.query.filter_by(id=venue_id).first()
    data = None
    shows = db.session.query(Show).filter(Show.venue_id == venue.id).all()
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

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm()
    
    try:
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
              phone=form.phone.data, image_link=form.image_link.data,genres=form.genres.data,
              facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,
              website_link=form.website_link.data, seeking_talent=form.seeking_talent.data)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
        error = True
        print(e)
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        abort(500)
    finally:
        db.session.close()
    return redirect(url_for('venues'))

    #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['GET', 'POST'])
def delete_venue(venue_id):

    error = False
    try:
        venue = Venue.query.filter_by(id=venue_id).first_or_404()
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        error = True
        print(f'Error ==> {e}')
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash(f'An error occurred. Venue {venue_id} could not be deleted.')
            return redirect(url_for('venues'))
        else: flash(f'Venue {venue_id} was successfully deleted.')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists', methods=['GET'])
def artists():

    all_artist = []
    try:
        all_artist = Artist.query.all()
    except Exception as e:
        db.session.rollback()
        db.session.close()
    data = []
    if all_artist:
        for artist in all_artist:
            data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=all_artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get("search_term", "")
    search_response = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for artist in search_response:
        data.append({
            "artist_id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(Artist.query.join(Show).filter(Show.start_time > datetime.now(), Show.artist_id == artist.id).all())
        })

    response = {
        "count": len(search_response),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    shows = db.session.query(Show).filter(Show.artist_id == artist_id).all()   
    venue_past_shows = []
    venue_up_shows = []
    artist = Artist.query.filter_by(id=artist_id).first()
    data = None

    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        start_time = format_datetime(str(show.start_time))

        venue_show = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(start_time)
        }
        if show.start_time >= datetime.utcnow():
            venue_up_shows.append(venue_show)
        elif show.start_time < datetime.utcnow():
            venue_past_shows.append(venue_show)

    data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "facebook_link": artist.facebook_link,
            "website_link": artist.website_link,
            "image_link": artist.image_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "upcoming_shows_count": len(venue_up_shows),
            "upcoming_shows":  venue_up_shows,
            "past_shows": venue_past_shows,
            "past_shows_count": len(venue_past_shows),
        }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    try:
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website_link
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

        db.session.add(artist)
        db.session.commit()  
        flash('Artist was successfully updated!')
    except ValueError as e: 
        error = True
        db.session.rollback()
        print(e)
        flash("An error occurred. Artist " +
              request.form['name'] + " could not be changed.")
    finally: 
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
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
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

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
    venue.image_link = form.image_link.data

    db.session.add(venue)
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm()

    try:
        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
              phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
              facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,
              website_link=form.website_link.data, seeking_venue=form.seeking_venue.data)
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form['name'] + " was successfully listed!")
    except ValueError as e:
        error = True
        print(e)
        db.session.rollback()
        flash("An error occurred. Artist " +
              request.form['name'] + " could not be listed.")
    finally:
        db.session.close()
    return redirect(url_for('artists'))
    #return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['GET', 'POST'])
def delete_artist(artist_id):
    
    error = False
    try:
        artist = Artist.query.filter_by(id=artist_id).first_or_404()
        db.session.delete(artist)
        db.session.commit()
    except Exception as e:
        error = True
        print(f'Error ==> {e}')
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash(f'An error occurred. Artist {artist_id} could not be deleted.')
            return redirect(url_for('artists'))
        else: flash(f'Artist {artist_id} was successfully deleted.')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_shows = []
    try:
        venues_all = Venue.query.join(Artist, Venue.state == Artist.state).all()
        data = db.session.query(Show).all()
        for show in data:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            venue = Venue.query.filter_by(id=show.venue_id).first()
            all_shows.append({
                        "venue_id": show.id,
                        "venue_name": venue.name,
                        "artist_id": artist.id,
                        "artist_name":artist.name,
                        "artist_image_link": artist.image_link,
                        "start_time": show.start_time
                    })
    except Exception as e:
        print(e)
        pass
    return render_template('pages/shows.html', shows=all_shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm()

    try:
        show = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data,
              start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    except ValueError as e:
        error = True
        print(e)
        db.session.rollback()
        flash("An error occurred. Show could not be listed.")
    finally:
        db.session.close()
    return redirect(url_for('shows'))
    #return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
