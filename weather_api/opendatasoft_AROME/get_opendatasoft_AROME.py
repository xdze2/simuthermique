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

import requests
import json, os
import logging
from time import sleep
from datetime import datetime
from pathlib import Path

# # data AROME from opendatasoft

# +
# ============
#  Parameters
# ============

city_lat_lon_coordinates = {
    'Marseille': (43.3, 5.4),
    'Toulouse':  (43.6, 1.45),
}

dataset = 'arome-0025-sp1_sp2'
commune = 'Toulouse'
lat_lon = city_lat_lon_coordinates[commune]

save_dir = Path('data', commune)
save_dir.mkdir(parents=True, exist_ok=True)
print('mkdir', save_dir)

wait_hours = 3
# -

logging.basicConfig(
    filename=os.path.join(save_dir, 'log.txt'),
    format='%(asctime)s - %(levelname)s  %(message)s',
    level=logging.INFO
)


logging.info('start script')


def query(commune, lat_lon):
    url = "https://public.opendatasoft.com/api/records/1.0/search/"

    lat, lon = lat_lon
    params = {
        'dataset':dataset,
        'rows':100,
        'geofilter.distance':f"{lat:.2f}, {lon:.2f}, 100",
        'sort':'forecast'
    }

    r = requests.get(url, params=params)
    
    if r.status_code != 200:
        logging.error('query error')
        print('query error')
        print(r.text)
        data = None
    else:
        data = r.json()
        
    return data


def save_data(data):
    records = data['records']
    fields = [r['fields'] for r in records]

    times = [(f['timestamp'], f['forecast']) for f in fields]
    date_of_the_run = min(times, key=lambda x:x[1])[0]

    filename = os.path.join(save_dir, f'{date_of_the_run}.json')
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

    print(' > save:', filename)
    logging.info(f'save - run:{date_of_the_run} {len(times)} points')



while True:
    data = query(commune, lat_lon)
    save_data(data)
    print(datetime.now(), "waiting...")
    sleep(wait_hours *60*60)


