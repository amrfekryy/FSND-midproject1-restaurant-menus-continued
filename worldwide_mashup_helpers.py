# this is a mashup program that uses different published APIs 
# to search for restaurants around a specific address that
# serve a specific meal.

# general
import requests
import datetime
import json

# get required API sercrets
secrets = json.loads(open('worldwide_mashup_secrets.json','r').read())
HERE_APP_ID = secrets.get('HERE_APP_ID')
HERE_APP_CODE = secrets.get('HERE_APP_CODE')
FS_CLIENT_ID = secrets.get('FS_CLIENT_ID')
FS_CLIENT_SECRET = secrets.get('FS_CLIENT_SECRET')
GGL_API_KEY = secrets.get('GGL_API_KEY')


def HERE_geocode(address):
	"""
	uses HERE API to get geocode location based on address
	https://developer.here.com/documentation/geocoder/topics/quick-start-geocode.html
	"""
	r = requests.get(
			url='https://geocoder.api.here.com/6.2/geocode.json',
			params={
			'app_id': HERE_APP_ID,
			'app_code': HERE_APP_CODE,
			'searchtext': address
			})
	# print(r.content) # explore response body
	# parse response to get lat, lng dict
	ll = r.json()['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']
	return str(ll['Latitude']), str(ll['Longitude'])


def GOOGLE_geocode(address):
	"""
	uses GOOGLE API to get geocode location based on address
	https://developers.google.com/maps/documentation/geocoding/start
	"""
	r = requests.get(
			url='https://maps.googleapis.com/maps/api/geocode/json',
			params={
			'key': GGL_API_KEY,
			'address': address
			})
	# print(r.content) # explore response body
	# parse response to get lat, lng dict
	ll = r.json()['results'][0]['geometry']['Location']
	return str(ll['lat']), str(ll['lng'])

# print(HERE_geocode('tokyo, japan'))


def get_restaurant_photos(venue_id, dimensions):
	"""
	uses FOURSQUARE API to get pictures of a restaurant
	https://developer.foursquare.com/docs/api/venues/search
	args:
	  venue_id: venue id extracted from FOURSQUARE venue search.
	  dimensions: string representing size of picture: 
	  	'XxY', X and Y can only be 36, 100, 300, or 500.
	returns:
	  if request is successful: 1, list of urls or 'No Photos'
	  else: 0, 'Unsuccessful request' 
	"""
	# make request
	r = requests.get(
		url=f'https://api.foursquare.com/v2/venues/{venue_id}/photos',
		params={
			'client_id': FS_CLIENT_ID,
			'client_secret': FS_CLIENT_SECRET,
			'v': datetime.date.today().strftime('%Y%m%d'), #YYYYMMDD
			'group': 'venue'
			# 'limit': 100, # no. of results up to 200
			# 'offset': 100 # to page through results
		})
	# print(r.content) # explore response body
	
	# print response
	if r.status_code == 200:
		photos = r.json().get('response').get('photos')
		if photos.get('count'):
			photo_url_list = []
			for item in photos.get('items'):
				photo_url = item.get('prefix') + dimensions + item.get('suffix')
				photo_url_list.append(photo_url)
			return 1, photo_url_list
		return 1, []
	return 0, "Unsuccessful request"


def find_restaurant(address, radius, meal):
	"""
	uses FOURSQUARE API to get info about restaurants around an address that serve a specific meal
	args:
	  address: string address to be used as the center location.
	  radius: integer representing the search range around the address.
	  meal: string to limit results of restaurants based on a meal.
	returns:
	  a list of dicts, each contains restaurant name, address, photos feedback 
	"""
	# geocode address
	ll = HERE_geocode(address)
	
	# make request
	r = requests.get(
		url="https://api.foursquare.com/v2/venues/search", 
		params={
			'client_id': FS_CLIENT_ID,
			'client_secret': FS_CLIENT_SECRET,
			'v': datetime.date.today().strftime('%Y%m%d'), #YYYYMMDD
			'categoryId': '4d4b7105d754a06374d81259', # food venues (restaurants)
			'intent': 'browse', # search within an area
			'll': ','.join(ll), # 'lat,lng'
			'radius': radius, # in meters
			'query': meal, # search venue names
			# 'limit': 1 # no. of results up to 50
		})
	# print(r.content) # explore response body

	# print and return restaurants information
	if r.status_code == 200:
		
		# print('Results: \n')
		results = []
		for venue in r.json().get('response').get('venues'):
			
			# RETAURANT NAME
			restuarant_name = venue.get('name')
			if not restuarant_name:
				restuarant_name = "Couldn't get name for this restaurant"
			
			# RESTAURANT ADDRESS
			restuarant_address = ''
			venue_address = venue.get('location').get('address')
			venue_cross_street = venue.get('location').get('crossStreet')
			if venue_address:
				if venue_cross_street:
					restuarant_address = f"{venue_address}, {venue_cross_street}"
				else:
					restuarant_address = venue_address	
			else:
				restuarant_address = "Couldn't get address for this restaurant"
			
			# RESTAURANT PHOTOS
			restaurant_photos = ''
			success, photos = get_restaurant_photos(venue.get('id'), '300x300')
			if success:
				if photos:
					restaurant_photos = photos
				else:
					restaurant_photos = ["There are no photos for this restaurant"]
			else:
				restaurant_photos = ["Couldn't get photos for this restaurant"]

			# wrap up results
			results.append({
				'restuarant_name': restuarant_name,
				'restuarant_address': restuarant_address,
				'restaurant_photos': restaurant_photos
				})

		# print and return results
		print_restaurants_info(results)
		return results

	else:
		# print and return error message
		print("Restaurant search request was unsuccessful!")
		return "Restaurant search request was unsuccessful!"


def print_restaurants_info(results):
	"""Prints information inside results to Terminal in a readable way for testing"""
	print('Results: \n')
	for restarant in results:
		print(f"Retaurant Name: {restarant['restuarant_name']}")
		print(f"Retaurant Address: {restarant['restuarant_address']}")
		print("Retaurant Photos:")
		for photo in restarant['restaurant_photos']:
			print(f"  - {photo}")
		print('____________________')

