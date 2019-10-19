#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
"""
Creating the three models(Venue, Artist, Show) for Fyyur APP.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

class Venue(db.Model):
  """
  Create all needed columns of venues and return them all.
  Establish relationship with Artist Model.
  """
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  artists = db.relationship('Artist', secondary='shows', backref=db.backref('venue', lazy=True))
    
  def __repr__(self):
    return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.website} {self.facebook_link} {self.genres} {self.seeking_talent} {self.seeking_description}>'

class Artist(db.Model):
  """
  Create Artist Model and return all columns.
  
  """
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))

  def __repr__(self):
    return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.image_link} {self.website} {self.facebook_link} {self.genres} {self.seeking_venue} {self.seeking_description}>'

class Show(db.Model):
  """
  Create Show Model and return all columns.
  Set foreignkeys.
  """
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  
  def __repr__(self):
    return f'<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>'

