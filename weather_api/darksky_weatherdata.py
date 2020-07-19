# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from darksky import forecast

# +
#pip install darkskylib
# -

# ## Download weather data using Darksy API

# +
# Load the API key for darksky
with open('darksky_key.txt') as f:
    KEY = f.read().strip()

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


# -

# test
boston = forecast(KEY, 42.3601, -71.0589)
print(boston['hourly']['data'][0])

# +
coords = (43.302204, 5.390193) # lat, lon degree
loc_name = 'mars'
timezone = 'Europe/Paris'

days = pd.date_range(start = '2020-03-17',
                     end =   '2020-07-17',
                     freq='1d',
                     tz=timezone)
# -

# Query weather data
hourlydata = [query_hourly_data(d, coords, KEY) for d in days]
weatherdata = pd.concat(hourlydata, sort=True)
print('done', weatherdata.shape, ' '*35)

# +
start_date = weatherdata.index[0].strftime('%Y-%m-%d')
filename = f'{loc_name}_{start_date}_{len(weatherdata)}days'
print(filename)

# save
weatherdata.to_csv(os.path.join('./data/', filename + '.csv'))
weatherdata.to_pickle(os.path.join('./data/', filename + '.pickle'))
# -


