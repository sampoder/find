import os    
import json
import math
from airtable import Airtable
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim

app = Flask(__name__)

@app.route('/')
def main():

  # Setup Geolocator to use Nominatim

  geolocator = Nominatim(user_agent="sampoderfindlocation")

  # Setup Airtable & Draw the Latest Record

  airtable = Airtable(os.getenv("BASE_KEY"), 'Table')

  airtable_data = airtable.get_all(view='Grid view', sort=[('Created', 'desc')], maxRecords=1)

  # Get Current Longitude & Latitude from Airtable Record

  og_longitude = float(airtable_data[0]['fields']['Longitude'])

  og_latitude = float(airtable_data[0]['fields']['Latitude'])

  # Find Geographical Info Based on Longitude & Latitude

  location = geolocator.reverse(str(og_latitude) + "," + str(og_longitude))

  if location.raw['address']['country'] == "Singapore":

    # Get Location Info for Every MRT Station in SG

    f = open('mrts.json')

    data = json.load(f)
      
    f.close()

    # Define Variables Needed to Rank Distances

    og_difference = 800

    big_diff_name = ""

    big_diff_lat = 0

    big_diff_long = 0

    # Loop Through Stations

    for list in data:

      # Define Variables Needed

      latitude = 0

      longitude = 0

      name = ""

      for (k, v) in list.items():

        if k == "Latitude":

          latitude = v

        if k == "Longitude":

          longitude = v

        if k == "STN_NAME":

          name = v

      # Set up Math Equation

      p1 = [longitude, latitude]

      p2 = [og_longitude, og_latitude]

      # Difference Equation

      diff = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

      # Make Sure Difference is Positive 

      if diff < 0:

        diff = diff*-1

      # Sort Differences

      if diff < og_difference:

        og_difference = diff

        big_diff_name = name.title().replace("Mrt", "MRT") 

        big_diff_lat = latitude

        big_diff_long = longitude

    # Generate Google Maps Link
    
    maps_link = "https://maps.google.com/?ll="+str(big_diff_lat)+","+str(big_diff_long)

    # Render Template

    return render_template('mrt.html', station_name = big_diff_name, maps_link = maps_link, country = location.raw['address']['country'])

  else:

    # Render Template

    country = location.raw['address']['country']

    wiki_link = "https://en.wikipedia.org/wiki/"+country.replace(" ", "_")

    return render_template('world.html', country = country, wiki_link = wiki_link)


if __name__ == '__main__':

   app.run(debug = True, host ="0.0.0.0")
