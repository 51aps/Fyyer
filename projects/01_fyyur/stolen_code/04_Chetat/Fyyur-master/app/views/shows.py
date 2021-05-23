# !/usr/bin/env python3
# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from models import Shows, Venue, Artist, db
from . import bp
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from datetime import datetime
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from app.forms import *


#  Shows
#  ----------------------------------------------------------------

@bp.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.(DONE)
    all_shows = []
    try:
        venues_all = Venue.query.join(Artist, Venue.state == Artist.state).all()
        data = db.session.query(Shows).all()
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

    return render_template("pages/shows.html", shows=all_shows)

@bp.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@bp.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead(DONE)
    show_form = ShowForm()

    artist_id = show_form.artist_id.data
    venue_id = show_form.venue_id.data
    start_time = show_form.start_time.data

    show = Shows.insert().values(artist_id=artist_id,
                                 venue_id=venue_id, start_time=start_time)
    try:
        db.session.execute(show)
        db.session.commit()
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    except Exception as e:
        flash("An error occurred. Show could not be listed.")
        db.session.rollback()
        db.session.flush()
        print(e)
    return render_template("pages/home.html")
