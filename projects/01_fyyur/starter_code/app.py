#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from sqlalchemy.dialects.postgresql import ARRAY
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
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

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    phone = db.Column(db.String(120), nullable=False, unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), unique=True)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String(120)))
    #    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), unique=True)
    website= db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer,primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        return f'<Venue {self.start_time}>'


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
  venue_groups = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []
  for venue_group in venue_groups:
    city_name = venue_group[0]
    city_state = venue_group[1]
    filtered = db.session.query(Venue).filter(Venue.city == city_name, Venue.state == city_state)
    group = {
        "city": city_name,
        "state": city_state,
        "venues": []
    }
    venues = filtered.all()
    # List venues in the city/state group
    for venue in venues:
        group['venues'].append({
            "id": venue.id,
            "name": venue.name,
            # "num_shows_upcoming": len(venue.shows)
        })
    data.append(group)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term")
  venues_names = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%'))
  count = []
  for name in venues_names:
    count.append(name.name)
    response={
    "count": len(count),
    "data": venues_names,
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  now = datetime.utcnow()
  venue.upcoming_shows = (
    db.session.query(Show)
    .join(Venue, Show.venue_id == Venue.id)
    .filter(Show.venue_id == venue_id, Show.start_time > now)
    .all()
   )
  venue.upcoming_shows_count = len(venue.upcoming_shows)
  venue.past_shows = (
    db.session.query(Show)
    .join(Venue, Show.venue_id == Venue.id)
    .filter(Show.venue_id == venue_id, Show.start_time < now)
    .all()
  )
  venue.past_shows_count = len(venue.past_shows)
  return render_template("pages/show_venue.html", venue=venue)


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
  x=request.form.get('seeking_talent')
  if x:
    xx=True
  try:
    venue = Venue(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    address=request.form['address'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'),
    facebook_link=request.form['facebook_link'],
    image_link=request.form['image_link'],
    website=request.form['website'],
    seeking_talent=xx,
    seeking_description=request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e :
    print(e)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: [COMPLETED] Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash(f'An error occurred. Venue {venue_id} could not be deleted.')
      abort(400)
    else : flash(f'Venue {venue_id} was successfully deleted.')
  # TODO: [COMPLETED] BONUS CHALLENGE:  Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #data=[{
    #"id": 4,
    #"name": "Guns N Petals",
  #}, {
    #"id": 5,
    #"name": "Matt Quevedo",
  #}, {
    #"id": 6,
    #"name": "The Wild Sax Band",
  #}]
  data = Artist.query.order_by(Artist.name).all()

  return render_template('pages/artists.html', artists=data)
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term")
  artists_names = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%'))
  count = []
  for name in artists_names:
    count.append(name.name)
    response={
    "count": len(count),
    "data": artists_names,
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    now = datetime.utcnow()
    artist.upcoming_shows = (
        db.session.query(Show)
        .join(Artist, Show.artist_id == artist_id)
        .filter(Show.artist_id == artist_id, Show.start_time > now)
        .all()
    )
    if len(artist.upcoming_shows):
        artist.upcoming_shows_count = len(artist.upcoming_shows)
    artist.past_shows = (
        db.session.query(Show)
        .join(Artist, Show.artist_id == Artist.id)
        .filter(Show.artist_id == artist_id, Show.start_time < now)
        .all()
    )
    if len(artist.past_shows):
        artist.past_shows_count = len(artist.past_shows)

    print(artist.genres)

    return render_template("pages/show_artist.html", artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= db.session.query(Artist).filter(Artist.id == artist.id).all()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= db.session.query(Venue).filter(Venue.id == venue.id).all()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
# called upon submitting the new artist listing form
# DONE: insert form data as a new Venue record in the db, instead
# DONE: modify data to be the data object returned from db insertion
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    response = {}
    error = False
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        image_link = request.form.get("image_link")
        website = request.form.get("website")
        seeking_description = request.form.get("seeking_description")
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_description=seeking_description,
        )
        response["name"] = artist.name
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        flash("An error occurred. Artist " + name + " could not be listed.")
        db.session.rollback()
    finally:
        db.session.close()
        if error == False:
            flash("Artist " + response["name"] + " was successfully listed!")

    return render_template("pages/home.html")

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #x=request.form.get('seeking_venue')
  #if x:
    #xx=True
  #try:
    #artist = Artist(
    #name=request.form['name'],
    #city=request.form['city'],
    #state=request.form['state'],
    #address=request.form['address'],
    #phone=request.form['phone'],
    #genres=request.form.getlist('genres'),
    #facebook_link=request.form['facebook_link'],
    #website=request.form['website'],
    #image_link=request.form['image_link'],
    #seeking_venue=xx,
    #seeking_description=request.form['seeking_description']
    #)
    #db.session.add(artist)
    #db.session.commit()
  # on successful db insert, flash success
    #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #except Exception as e :
    #print(e)
    #flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed')
    #db.session.rollback()
  #finally:
    #db.session.close()
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = Show.query.order_by(Show.start_time.desc()).all()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
        artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
        data.extend([{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
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
  try:
    venue_id = request.form.get("venue_id")
    artist_id = request.form.get("artist_id")
    start_time = request.form.get("start_time")

    show = Show(
      venue_id=venue_id,
      artist_id=artist_id,
      start_time=start_time,
    )
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
