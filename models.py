from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy=True)
    location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.address} {self.phone} {self.genres} {self.website} {self.image_link} {self.facebook_link} {self.seeking_venue} {self.seeking_description} {self.location_id}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.website} {self.image_link} {self.facebook_link} {self.seeking_venue} {self.seeking_description}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime())

    def __repr__(self):
        return f'<Show {self.id} {self.venue_id} {self.artist_id}>'

class Location(db.Model):
    __tablename__ = 'Location'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    venues = db.relationship('Venue', backref='Location', lazy=True)

    def add_venue(self, venue):
      new_venue = Venue(
          name=venue['name'],
          address=venue['address'],
          phone=venue['phone'],
          genres=venue['genres'],
          facebook_link=venue['facebook_link'],
          image_link=venue['image_link'],
          location_id=self.id
        )

      db.session.add(new_venue)

    def __repr__(self):
        return f'<Venue {self.id} {self.city} {self.state}>'
