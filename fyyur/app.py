#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

# Already set in comfig.py.

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary='shows', backref=db.backref('venue', lazy=True))
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.website} {self.facebook_link} {self.genres} {self.seeking_talent} {self.seeking_description}>'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.image_link} {self.website} {self.facebook_link} {self.genres} {self.seeking_venue} {self.seeking_description}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
      return f'<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>'


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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  cities_states = db.session.query(Venue.city, Venue.state).group_by('city', 'state').all()
  data = []
  for city_state in cities_states:
    s_data = {}
    venues = []
    city = city_state[0]
    state = city_state[1]
    in_venues = db.session.query(Venue.id, Venue.name).filter(Venue.city==city, Venue.state==state).all()
    for in_venue in in_venues:
      ven = {}
      ven['id'] = in_venue[0]
      ven['name'] = in_venue[1]
      venues.append(ven)
    s_data['city'] = city
    s_data['state'] = state
    s_data['venues'] = venues
    data.append(s_data)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = '%' + request.form['search_term'] + '%'
  search_venues = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike(search_term)).all()
  count = len(search_venues)
  response = {}
  data = []
  for search_venue in search_venues:
    dat = {}
    dat['id'] = search_venue[0]
    dat['name'] = search_venue[1]
    data.append(dat)
  response['count'] = count
  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venues = db.session.query(Venue).all()
  datas = []
  for venue in venues:
    ven = {}
    ven['id'] = venue.id
    ven['name'] = venue.name
    ven["genres"] = venue.genres.split(',')
    ven["city"] = venue.city
    ven["state"] = venue.state
    ven['address'] = venue.address
    ven["phone"] = venue.phone
    ven["website"] = venue.website
    ven["facebook_link"] = venue.facebook_link
    ven["seeking_talent"] = venue.seeking_talent
    ven["seeking_description"] = venue.seeking_description
    ven["image_link"] = venue.image_link
    show_venue = db.session.query(Show).filter(Show.venue_id==venue.id).all()
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    if show_venue != []:
      for show in show_venue:
        if show.start_time < datetime.datetime.now():
          past_show = {}
          past_show['artist_id'] = show.artist_id
          query_artist_name = db.session.query(Artist.name).filter(Artist.id==show.artist_id).one()
          past_show['artist_name'] = query_artist_name[0]
          query_artist_image_link = db.session.query(Artist.image_link).filter(Artist.id==show.artist_id).one()
          past_show['artist_image_link'] = query_artist_image_link[0]
          past_show['start_time'] = str(show.start_time)
          past_shows_count += 1
          past_shows.append(past_show)
        else:
          upcoming_show = {}
          upcoming_show['artist_id'] = show.artist_id
          query_artist_name = db.session.query(Artist.name).filter(Artist.id==show.artist_id).one()
          upcoming_show['artist_name'] = query_artist_name[0]
          query_artist_image_link = db.session.query(Artist.image_link).filter(Artist.id==show.artist_id).one()
          upcoming_show['artist_image_link'] = query_artist_image_link[0]
          upcoming_show['start_time'] = str(show.start_time)
          upcoming_shows_count += 1
          upcoming_shows.append(upcoming_show)   
    ven['past_shows'] = past_shows
    ven['upcoming_shows'] = upcoming_shows
    ven['past_shows_count'] = past_shows_count
    ven['upcoming_shows_count'] = upcoming_shows_count
    datas.append(ven)
  data = list(filter(lambda d: d['id'] == venue_id, datas))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = ','.join(request.form.getlist('genres'))
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = request.form['seeking_talent'] == str(True)
    seeking_description = request.form['seeking_description']    
    new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, website=website, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    db.session.query(Venue).filter(Venue.id==venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Venue was successfully deleted!')
  else:
    flash('An error occurred. Venue could not be deleted.')
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  in_artists = db.session.query(Artist.id, Artist.name).all()
  data = []
  for in_artist in in_artists:
    art = {}
    art['id'] = in_artist[0]
    art['name'] = in_artist[1]
    data.append(art)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = '%' + request.form['search_term'] + '%'
  search_artists = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(search_term)).all()
  count = len(search_artists)
  response = {}
  data = []
  for search_artist in search_artists:
    dat = {}
    dat['id'] = search_artist[0]
    dat['name'] = search_artist[1]
    data.append(dat)
  response['count'] = count
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artists = db.session.query(Artist).all()
  datas = []
  for artist in artists:
    art = {}
    art['id'] = artist.id
    art['name'] = artist.name
    art["genres"] = artist.genres.split(',')
    art["city"] = artist.city
    art["state"] = artist.state
    art["phone"] = artist.phone
    art["website"] = artist.website
    art["facebook_link"] = artist.facebook_link
    art["seeking_venue"] = artist.seeking_venue
    art["seeking_description"] = artist.seeking_description
    art["image_link"] = artist.image_link
    show_artist = db.session.query(Show).filter(Show.artist_id==artist.id).all()
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    if show_artist != []:
      for show in show_artist:
        if show.start_time < datetime.datetime.now():
          past_show = {}
          past_show['venue_id'] = show.venue_id
          query_venue_name = db.session.query(Venue.name).filter(Venue.id==show.venue_id).one()
          past_show['venue_name'] = query_venue_name[0]
          query_venue_image_link = db.session.query(Venue.image_link).filter(Venue.id==show.venue_id).one()
          past_show['venue_image_link'] = query_venue_image_link[0]
          past_show['start_time'] = str(show.start_time)
          past_shows_count += 1
          past_shows.append(past_show)
        else:
          upcoming_show = {}
          upcoming_show['venue_id'] = show.venue_id
          query_venue_name = db.session.query(Venue.name).filter(Venue.id==show.venue_id).one()
          upcoming_show['venue_name'] = query_venue_name[0]
          query_venue_image_link = db.session.query(Venue.image_link).filter(Venue.id==show.venue_id).one()
          upcoming_show['venue_image_link'] = query_venue_image_link[0]
          upcoming_show['start_time'] = str(show.start_time)
          upcoming_shows_count += 1
          upcoming_shows.append(upcoming_show) 
    art['past_shows'] = past_shows
    art['upcoming_shows'] = upcoming_shows
    art['past_shows_count'] = past_shows_count
    art['upcoming_shows_count'] = upcoming_shows_count
    datas.append(art)
  data = list(filter(lambda d: d['id'] == artist_id, datas))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = Edit_ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  query = db.session.query(Artist).filter(Artist.id == artist_id).all()
  artist = query[0]
  form.state.data = artist.state
  form.genres.data = artist.genres
  form.name.data = artist.name
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = str(artist.seeking_venue)
  form.seeking_description.data = artist.seeking_description    
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  query = db.session.query(Artist).filter(Artist.id == artist_id).all()
  artist = query[0]
  try:
    name = request.form['name']
    if name != '':
      artist.name = name
    city = request.form['city']
    if city != '':
      artist.city = city
    state = request.form['state']
    if state != '':
      artist.state = state
    phone = request.form['phone']
    if phone != '':
      artist.phone = phone
    genres = ','.join(request.form.getlist('genres'))
    if genres != '':
      artist.genres = genres
    image_link = request.form['image_link']
    if image_link != '':
      artist.image_link = image_link
    website = request.form['website']
    if website != '':
      artist.website = website
    facebook_link = request.form['facebook_link']
    if facebook_link != '':
      artist.facebook_link = facebook_link
    seeking_venue = request.form['seeking_venue'] == str(True)
    if seeking_venue != '':
      artist.seeking_venue = seeking_venue
    seeking_description = request.form['seeking_description']
    artist.seeking_description = seeking_description    
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = Edit_VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  query = db.session.query(Venue).filter(Venue.id == venue_id).all()
  venue = query[0]
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.name.data = venue.name
  form.city.data = venue.city
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = str(venue.seeking_talent)
  form.seeking_description.data = venue.seeking_description    
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  query = db.session.query(Venue).filter(Venue.id == venue_id).all()
  venue = query[0]
  try:
    name = request.form['name']
    if name != '':
      venue.name = name
    city = request.form['city']
    if city != '':
      venue.city = city
    state = request.form['state']
    if state != '':
      venue.state = state
    address = request.form['address']
    if address != '':
      venue.address = address
    phone = request.form['phone']
    if phone != '':
      venue.phone = phone
    genres = ','.join(request.form.getlist('genres'))
    if genres != '':
      venue.genres = genres
    image_link = request.form['image_link']
    if image_link != '':
      venue.image_link = image_link
    website = request.form['website']
    if website != '':
      venue.website = website
    facebook_link = request.form['facebook_link']
    if facebook_link != '':
      venue.facebook_link = facebook_link
    seeking_talent = request.form['seeking_talent'] == str(True)
    if seeking_talent != '':
      venue.seeking_talent = seeking_talent
    seeking_description = request.form['seeking_description']
    venue.seeking_description = seeking_description    
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = ','.join(request.form.getlist('genres'))
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = request.form['seeking_venue'] == str(True)
    seeking_description = request.form['seeking_description']    
    new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, website=website, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
  error = False
  try:
    db.session.query(Artist).filter(Artist.id==artist_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('Artist was successfully deleted!')
  else:
    flash('An error occurred. Aritst could not be deleted.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = db.session.query(Show).all()
  for show in shows:
    dat = {}
    query_venue = db.session.query(Venue).filter(Venue.id==show.venue_id).all()
    query_artist = db.session.query(Artist).filter(Artist.id==show.artist_id).all()
    dat['venue_id'] = show.venue_id
    dat['venue_name'] = query_venue[0].name
    dat['artist_id'] = show.artist_id
    dat['artist_name'] = query_artist[0].name
    dat['artist_image_link'] = query_artist[0].image_link
    dat['start_time'] = str(show.start_time)
    data.append(dat)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Show could not be listed.')
  return render_template('pages/home.html')

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
