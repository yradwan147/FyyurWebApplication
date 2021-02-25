#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from flask_migrate import Migrate
import csv
import re
import phonenumbers
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

def validURL(inp):
  pattern = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"
  return re.search(pattern, inp)

def validate_phone(num):
    if len(num) != 12:
        return False
    # try:
    #     input_number = phonenumbers.parse(num)
    #     if not (phonenumbers.is_valid_number(input_number)):
    #         return False
    # except:
    #     input_number = phonenumbers.parse("+1"+ num)
    #     if not (phonenumbers.is_valid_number(input_number)):
    #         return False
    return True
reference = {}

with open('reference.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
      items = row['City|State short|State full|County|City alias'].split('|')
      #print(items[1])
      if (len(items) > 1):
        if (items[0] not in reference.keys()):
          reference[items[0]] = items[1]

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

  # Fetch all cities and states
  places = Venue.query.with_entities(Venue.city, Venue.state).all()
  # Remove duplicates
  places_nodup = list( dict.fromkeys(places) )
  data = []

  for i in places_nodup:
    venues_obj = Venue.query.filter_by(city=i[0]).all()
    venues = []
    for q in venues_obj:
      venues.append({"id" : q.id, "name" : q.name, "num_upcoming_shows" : 0})
    data.append({"city" : i[0], "state" : i[1], "venues" : venues})

  # TODO: num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  stmt = text("Select * FROM venues WHERE name  ILIKE '%" + search_term + "%';")
  venues_obj = db.engine.execute(stmt)
  #venues_obj = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  venues = []
  for q in venues_obj:
      venues.append({"id" : q.id, "name" : q.name, "num_upcoming_shows" : 0})
  response = {"count" : len(venues), "data" : venues}
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  stmt = text("SELECT * FROM shows WHERE venue_id = " + str(venue_id) + " AND schedule < '" + str(datetime.now()) + "'")
  past_shows_obj = db.engine.execute(stmt)
  past_shows = []
  upcoming_shows = []
  for show in past_shows_obj:
    stmt = text("SELECT * FROM artists JOIN shows ON artists.id = shows.artist_id WHERE artists.id = " + str(show.artist_id) +" LIMIT 1")
    artist_obj = db.engine.execute(stmt)
    artist = artist_obj.fetchone()
    past_shows.append({"artist_id" : artist.id, "artist_name" : artist.name, "artist_image_link" : artist.image_link, "start_time" : str(show.schedule)})
  db.session.close()
  stmt = text("SELECT * FROM shows WHERE venue_id = " + str(venue_id) + " AND schedule > '" + str(datetime.now()) + "'")
  upcoming_shows_obj = db.engine.execute(stmt)
  for show in upcoming_shows_obj:
    stmt = text("SELECT * FROM artists JOIN shows ON artists.id = shows.artist_id WHERE artists.id = " + str(show.artist_id) +" LIMIT 1")
    artist_obj = db.engine.execute(stmt)
    artist = artist_obj.fetchone()
    upcoming_shows.append({"artist_id" : artist.id, "artist_name" : artist.name, "artist_image_link" : artist.image_link, "start_time" : str(show.schedule)})
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres[1:-1].split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
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
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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
  #try:
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  try:
    seeking_talent = request.form['seeking_talent']
  except:
    seeking_talent = False
  if(seeking_talent=='y'):
    seeking_talent = True
  else:
    seeking_talent = False
  seeking_description = request.form['seeking_description']
  print(name, city, state, address, phone, genres, image_link, facebook_link, website, seeking_talent, seeking_description)
  if (not validURL(facebook_link)):
    error = True
    raise Exception('Facebook Link Invalid')
  if (not validURL(image_link)):
    error = True
    raise Exception('Image Link Invalid')
  if (not validURL(website)):
    error = True
    raise Exception('Website Invalid')
  if (not validURL(facebook_link)):
    error = True
    raise Exception('Facebook Link Invalid')
  if (city in reference.keys()):
    if (state == reference[city]):
      pass
    else:
      error = True
      raise Exception("State is invalid")
  else:
    error = True
    raise Exception("City is invalid")
  if (not validate_phone(phone)):
    error = True
    raise Exception("Phone is invalid")
  if (len(genres) < 1):
    error = True
    raise Exception("Genres Invalid")
  #new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link = image_link,
  #facebook_link=facebook_link, website = website, seeking_talent = seeking_talent, seeking_description = seeking_description)
  stmt = text("INSERT INTO venues (name, city, state, address, phone, genres, image_link, facebook_link, website, seeking_talent, seeking_description)" +
      " VALUES ('"+name+"','"+city+"','"+state+"','"+address+"','"+phone+"','"+str(genres).replace("'", "")+"','"+image_link+"','"+facebook_link+"','"+website+"',"+str(seeking_talent)+",'"+seeking_description+"')")
  db.engine.execute(stmt)
  db.session.commit()
  # except:
  #   error = True
  #   db.session.rollback()
  #   print(sys.exc_info())
  # finally:
  #     db.session.close()
  
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  elif error:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.get(venue_id)
      shows = Show.query.filter_by(venue_id = venue_id).all()
      print(venue, shows)
      for show in shows:
        print(show, Show.query.filter_by(venue_id = show.venue_id).first())
        db.session.delete(Show.query.filter_by(venue_id = show.venue_id).first())
      db.session.commit()
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return redirect(url_for('venues'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for i in artists:
    data.append({"id" : i.id, "name" : i.name})
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  stmt = text("Select * FROM artists WHERE name  ILIKE '%" + search_term + "%';")
  artists_obj = db.engine.execute(stmt)
  artists = []
  for q in artists_obj:
      artists.append({"id" : q.id, "name" : q.name, "num_upcoming_shows" : 0})
  response = {"count" : len(artists), "data" : artists}
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.filter_by(id=artist_id).first()
  past_shows = []
  upcoming_shows = []
  stmt = text("SELECT * FROM shows WHERE artist_id = " + str(artist_id) + " AND schedule > '" + str(datetime.now()) + "'")
  shows_obj = db.engine.execute(stmt)
  #print(upcoming_shows_obj[0].schedule > datetime.now())
  for show in shows_obj:
    stmt = text("SELECT * FROM venues JOIN shows ON venues.id = shows.venue_id WHERE venues.id = " + str(show.venue_id) +" LIMIT 1")
    venue_obj = db.engine.execute(stmt)
    venue = venue_obj.fetchone()
    #print(show.schedule)
    upcoming_shows.append({"venue_id" : venue[0], "venue_name" : venue[1], "venue_image_link" : venue[6], "start_time" : str(show.schedule)})
  print(past_shows)
  db.session.close()
  stmt = text("SELECT * FROM shows WHERE artist_id = " + str(artist_id) + " AND schedule < '" + str(datetime.now()) + "'")
  shows_obj = db.engine.execute(stmt)
  for show in shows_obj:
    print(show.schedule)
    stmt = text("SELECT * FROM venues JOIN shows ON venues.id = shows.venue_id WHERE venues.id = " + str(show.venue_id) +" LIMIT 1")
    venue1_obj = db.engine.execute(stmt)
    venue1 = venue1_obj.fetchone()
    temp = {"venue_id" : venue1[0], "venue_name" : venue1[1], "venue_image_link" : venue1[6], "start_time" : str(show.schedule)}
    print(temp)
    past_shows.append(temp)
  print(past_shows)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres[1:-1].split(','),
    "city": artist.city,
    "state": artist.city,
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
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  artist = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres[1:-1].split(','),
    "city": artist.city,
    "state": artist.city,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
 } 
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      try:
        seeking_venue = request.form['seeking_venue']
      except:
        seeking_venue = False
      if(seeking_venue=='y'):
        seeking_venue = True
      else:
        seeking_venue = False
      seeking_description = request.form['seeking_description']
      print(name, city, state, genres, image_link, facebook_link, website, seeking_venue, seeking_description)
      if (not validURL(facebook_link)):
        error = True
        raise Exception('Facebook Link Invalid')
      if (not validURL(image_link)):
        error = True
        raise Exception('Image Link Invalid')
      if (not validURL(website)):
        error = True
        raise Exception('Website Invalid')
      if (city in reference.keys()):
        if (state == reference[city]):
          pass
        else:
          error = True
          raise Exception("State is invalid")
      else:
        error = True
        raise Exception("City is invalid")
      if (not validate_phone(phone)):
        error = True
        raise Exception("Phone is invalid")
      if (len(genres) < 1):
        error = True
        raise Exception("Genres Invalid")
      existing_artist = Artist.query.filter_by(id=artist_id).first()
      existing_artist.name = name
      existing_artist.city = city
      existing_artist.state = state
      existing_artist.phone = phone
      existing_artist.genres = genres
      existing_artist.facebook_link = facebook_link
      existing_artist.image_link = image_link
      existing_artist.website = website
      existing_artist.seeking_venue = seeking_venue
      existing_artist.seeking_description = seeking_description
      db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully edited')
  elif error:
    flash('An error occurred')

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.filter_by(id=venue_id).first()
  venue = {
    "id": venue_data.id,
    "name": venue_data.name,
    "genres": venue_data.genres[1:-1].split(','),
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.city,
    "phone": venue_data.phone,
    "website": venue_data.website,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link,
 } 
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      seeking_talent = request.form['seeking_talent']
      if(seeking_talent=='y'):
        seeking_talent = True
      else:
        seeking_talent = False
      seeking_description = request.form['seeking_description']
      print(name, city, state, address, phone, genres, image_link, facebook_link, website, seeking_talent, seeking_description)
      if (not validURL(facebook_link)):
        error = True
        raise Exception('Facebook Link Invalid')
      if (not validURL(image_link)):
        error = True
        raise Exception('Image Link Invalid')
      if (not validURL(website)):
        error = True
        raise Exception('Website Invalid')
      if (not validURL(facebook_link)):
        error = True
        raise Exception('Facebook Link Invalid')
      if (city in reference.keys()):
        if (state == reference[city]):
          pass
        else:
          error = True
          raise Exception("State is invalid")
      else:
        error = True
        raise Exception("City is invalid")
      if (not validate_phone(phone)):
        error = True
        raise Exception("Phone is invalid")
      if (len(genres) < 1):
        error = True
        raise Exception("Genres Invalid")
      existing_venue = Venue.query.filter_by(id=venue_id).first()
      existing_venue.name = name
      existing_venue.city = city
      existing_venue.state = state
      existing_venue.phone = phone
      existing_venue.genres = genres
      existing_venue.facebook_link = facebook_link
      existing_venue.image_link = image_link
      existing_venue.website = website
      existing_venue.seeking_talent = seeking_talent
      existing_venue.seeking_description = seeking_description
      existing_venue.address = address
      db.session.commit()
  except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
        db.session.close()
  
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully edited')
  elif error:
    flash('An error occurred')
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website']
      seeking_venue = request.form['seeking_venue']
      if(seeking_venue=='y'):
        seeking_venue = True
      else:
        seeking_venue = False
      seeking_description = request.form['seeking_description']
      print(name, city, state, genres, image_link, facebook_link, website, seeking_venue, seeking_description)
      if (not validURL(facebook_link)):
        error = True
        raise Exception('Facebook Link Invalid')
      if (not validURL(image_link)):
        error = True
        raise Exception('Image Link Invalid')
      if (not validURL(website)):
        error = True
        raise Exception('Website Invalid')
      if (city in reference.keys()):
        if (state == reference[city]):
          pass
        else:
          error = True
          raise Exception("State is invalid")
      else:
        error = True
        raise Exception("City is invalid")
      if (not validate_phone(phone)):
        error = True
        raise Exception("Phone is invalid")
      if (len(genres) < 1):
        error = True
        raise Exception("Genres Invalid")
      stmt = text("INSERT INTO artists (name, city, state, phone, genres, image_link, facebook_link, website, seeking_venue, seeking_description)" +
      " VALUES ('"+name+"','"+city+"','"+state+"','"+phone+"','"+str(genres).replace("'", "")+"','"+image_link+"','"+facebook_link+"','"+website+"',"+str(seeking_venue)+",'"+seeking_description+"')")
      # new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link = image_link, 
      # facebook_link=facebook_link, website = website, seeking_venue = seeking_venue, seeking_description = seeking_description)
      print(stmt)
      db.engine.execute(stmt)
      #db.session.add(new_artist)
      db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  elif error:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.filter(Show.schedule > datetime.now()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).all()
    artist = Artist.query.filter_by(id=show.artist_id).all()
    print(str(show.schedule))
    data.append({"venue_id" : venue[0].id, "venue_name" : venue[0].name, "artist.id" : artist[0].id, "artist_name" : artist[0].name, 
    "artist_image_link" : artist[0].image_link, "start_time" : str(show.schedule)})
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
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
      try:
        time_new = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
      except:
        error = True
        raise Exception("Invalid Time")
      print(artist_id, venue_id,start_time)
      new_show = Show(artist_id=artist_id, venue_id=venue_id, schedule=start_time)
      db.session.add(new_show)
      db.session.commit()
      print(new_show.schedule)
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if not error:
    flash('Show was successfully listed!')
  elif error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  
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
