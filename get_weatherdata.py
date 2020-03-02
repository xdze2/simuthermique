# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: py3-projects
#     language: python
#     name: py3-projects
# ---

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from darksky import forecast
from pvlib.location import Location

# ## Get weather data and solar flux

# +
coords = (46.15, 4.4565)  # lat, lon degree
altitude = 550  # meter
timezone = 'Europe/Paris'

days = pd.date_range(start = '2019-08-01',
                     end =   '2019-08-11',
                     freq='1d',
                     tz=timezone)

# +
# Load the API key for darksky
with open('darksky_key.txt') as f:
    KEY = f.read()

EXCLUDE = ['currently', 'minutely', 'daily', 'flags']  # from the query

def query_hourly_data(date, coords, api_key=KEY, verbose=True):
    #time = int(date.timestamp())
    time = date.isoformat()
    if verbose:
        print('query', time, end='\r')
    data = forecast(api_key, *coords,
                    units='si', lang='fr',
                    time=time, exclude=EXCLUDE)

    data_tz = data.timezone

    hourly_data = [d for d in data['hourly']['data']]

    weatherdata = pd.DataFrame.from_records(hourly_data, index='time')

    weatherdata.index = pd.to_datetime(weatherdata.index, unit='s')
    weatherdata.index = weatherdata.index.tz_localize('UTC').tz_convert(data_tz)
    return weatherdata


# +
# test
#hourlydata = query_hourly_data(d, coords, KEY)
# -

# Query weather data
hourlydata = [query_hourly_data(d, coords, KEY) for d in days]
weatherdata = pd.concat(hourlydata, sort=True)
print('done', weatherdata.shape, ' '*35)

# Interpolate
weatherdata_15min = weatherdata.resample('15min').interpolate('linear')

# ## Sun data

# +
loc = Location(*coords, timezone, altitude, 'loc')

times = weatherdata_15min.index

solar_position = loc.get_solarposition(times,
                                       #pressure=weatherdata_15min['pressure'],
                                       temperature=weatherdata_15min['temperature'])

cs = loc.get_clearsky(times,
                      solar_position=solar_position)  # ineichen with climatology table by default

# merge flux & solar position
cs = pd.concat([cs, solar_position], axis=1)

# +
#from pvlib import atmosphere
#weatherdata_15min['pressure'] # mbar
#atmosphere.alt2pres(altitude)  # Pascals
#atmosphere.pres2alt(1035.700 *1e-3*1e5)

# +
# Merge weather data and solar info
weatherdata = pd.concat([weatherdata_15min, cs], axis=1)

print('Columns:')
print(', '.join(list(weatherdata.columns)))
# -

# Graph
plt.figure( figsize=(14, 7) )
n = 6
plt.subplot( n, 1, 1 )
plt.plot(weatherdata['temperature'], 'darkred');
plt.ylabel('temperature');
plt.subplot( n, 1, 2 )
plt.plot(weatherdata['cloudCover'] , 'black'); plt.ylabel('cloud cover'); 
plt.subplot( n, 1, 3 )
plt.plot(weatherdata['precipIntensity'] , 'blue'); plt.ylabel('precipIntensity'); 
plt.subplot( n, 1, 4 )
plt.plot(weatherdata['humidity'] , 'lightblue'); plt.ylabel('humidity');
plt.subplot( n, 1, 5 )
plt.plot(weatherdata['dni'], 'orange'); plt.ylabel('solar'); 
plt.plot(weatherdata['dhi'], 'purple'); plt.ylabel('solar');
plt.plot(weatherdata['ghi'], 'black'); plt.ylabel('solar');
plt.subplot( n, 1, 6 )
plt.plot(weatherdata['elevation'], 'orange'); plt.ylabel('solar'); 

# ### Save

# +
# #!mkdir data

# +
td = weatherdata.index[-1] - weatherdata.index[0]
start = weatherdata.index[-1]

filename = f'weatherdata_{start.date().isoformat()}_{td.days}days.pck'

data_dir = './data'
path = os.path.join(data_dir, filename)
print(path)

weatherdata.to_pickle( path )
# -




