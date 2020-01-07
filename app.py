#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Venue, Artist, Show, Location
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
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  locations = Location.query.order_by(Location.city.desc())

  for location in locations:
    if len(location.venues) > 0:
      data.append({
        "city": location.city,
        "state": location.state,
        "venues": location.venues
      })
      
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(venues),
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows = venue.shows
  past_shows = []
  upcoming_shows = []

  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    else:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.Location.city,
    "state": venue.Location.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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

  venue = {}
  venue['name'] = request.form['name'].strip()
  venue['city'] = request.form['city'].title().strip()
  venue['state'] = request.form['state'].strip()
  venue['address'] = request.form['address'].strip()
  venue['phone'] = request.form['phone'].strip()
  venue['genres'] = request.form.getlist('genres')
  venue['facebook_link'] = request.form['facebook_link'].strip()
  venue['image_link'] = request.form['image_link'].strip()

  error = False
  location = {}
  try:
    city = venue['city']
    location = Location.query.filter_by(city=city).first()

    if location is None:
      new_location = Location(
          city=venue['city'],
          state=venue['state']
        )
      db.session.add(new_location)
      db.session.commit()
    
    existing_location = Location.query.filter_by(city=city).first()

    new_venue = Venue(
      name = venue['name'],
      address = venue['address'],
      phone = venue['phone'],
      genres = venue['genres'],
      facebook_link = venue['facebook_link'],
      image_link = venue['image_link'],
      location_id = existing_location.id
    )
    
    db.session.add(new_venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    if error:
      return render_template('forms/new_venue.html', form=VenueForm())
    else:
      return redirect(url_for('venues'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.order_by(Artist.id.asc())

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
      
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(artists),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  past_shows = []
  upcoming_shows = []

  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.Venue.name,
        "venue_image_link": show.Venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    else:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.Venue.name,
        "venue_image_link": show.Venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
  
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artists = Artist.query.get(artist_id)

  form.name.process_data(artists.name)
  form.city.process_data(artists.city)
  form.state.process_data(artists.state)
  form.phone.process_data(artists.phone)
  form.facebook_link.process_data(artists.facebook_link)
  form.image_link.process_data(artists.image_link)

  artist={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = {}
  artist['name'] = request.form['name'].strip()
  artist['city'] = request.form['city'].title().strip()
  artist['state'] = request.form['state'].strip()
  artist['phone'] = request.form['phone'].strip()
  artist['genres'] = request.form.getlist('genres')
  artist['facebook_link'] = request.form['facebook_link'].strip()
  artist['image_link'] = request.form['image_link'].strip()

  error = False
  try:
    edit_artist = Artist.query.get(artist_id)

    edit_artist.name = artist['name']
    edit_artist.city = artist['city']
    edit_artist.state = artist['state']
    edit_artist.phone = artist['phone']
    edit_artist.genres = artist['genres']
    edit_artist.facebook_link = artist['facebook_link']
    edit_artist.image_link = artist['image_link']

    db.session.commit()
    flash('Artist ' + artist['name'] + ' was successfully updated!')

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + artist['name'] + ' could not be updated.')
  finally:
    db.session.close()
    if error:
      return render_template('forms/new_artist.html', form=ArtistForm())
    else:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venues = Venue.query.get(venue_id)

  form.name.process_data(venues.name)
  form.address.process_data(venues.address)
  form.city.process_data(venues.Location.city)
  form.state.process_data(venues.Location.state)
  form.genres.process_data(venues.genres)
  form.phone.process_data(venues.phone)
  form.facebook_link.process_data(venues.facebook_link)
  form.image_link.process_data(venues.image_link)

  venue={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.Location.city,
    "state": venues.Location.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = {}
  venue['name'] = request.form['name'].strip()
  venue['city'] = request.form['city'].title().strip()
  venue['state'] = request.form['state'].strip()
  venue['address'] = request.form['address'].strip()
  venue['phone'] = request.form['phone'].strip()
  venue['genres'] = request.form.getlist('genres')
  venue['facebook_link'] = request.form['facebook_link'].strip()
  venue['image_link'] = request.form['image_link'].strip()

  error = False
  location = {}
  try:
    city = venue['city']
    location = Location.query.filter_by(city=city).first()

    edit_venue = Venue.query.get(venue_id)

    edit_venue.name = venue['name']
    edit_venue.city = location.id
    edit_venue.address = venue['address']
    edit_venue.phone = venue['phone']
    edit_venue.genres = venue['genres']
    edit_venue.facebook_link = venue['facebook_link']
    edit_venue.image_link = venue['image_link']

    db.session.commit()
    flash('Venue ' + venue['name'] + ' was successfully updated!')

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue['name'] + ' could not be updated.')
  finally:
    db.session.close()
    if error:
      return render_template('forms/new_venue.html', form=VenueForm())
    else:
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  artist = {}
  artist['name'] = request.form['name'].strip()
  artist['city'] = request.form['city'].title().strip()
  artist['state'] = request.form['state'].strip()
  artist['phone'] = request.form['phone'].strip()
  artist['genres'] = request.form.getlist('genres')
  artist['facebook_link'] = request.form['facebook_link'].strip()
  artist['image_link'] = request.form['image_link'].strip()

  error = False

  try:
    new_artist = Artist(
        name = artist['name'],
        city = artist['city'],
        state = artist['state'],
        phone = artist['phone'],
        genres = artist['genres'],
        facebook_link = artist['facebook_link'],
        image_link = artist['image_link']
      )

    db.session.add(new_artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    if error:
      return render_template('forms/new_artist.html', form=ArtistForm())
    else:
      return redirect(url_for('artists'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.order_by(Show.start_time).filter(Show.start_time >= datetime.now())
  data = []
  
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  show = {}
  show['artist_id'] = request.form['artist_id'].strip()
  show['venue_id'] = request.form['venue_id'].strip()
  show['start_time'] = request.form['start_time'].strip()

  error = False

  try:
    new_show = Show(
        artist_id = show['artist_id'],
        venue_id = show['venue_id'],
        start_time = show['start_time']
      )

    db.session.add(new_show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    if error:
      return render_template('forms/new_show.html', form=ShowForm())
    else:
      return redirect(url_for('shows'))

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
