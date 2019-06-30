#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch the relevant information (price, volumes) from the Steam Marketplace, based on  \
        a table that serves as an index
"""

__author__ = 'Guido Minieri'
__version__ = '1.0.0'


# imports
import sys
from datetime import datetime
import requests
import psycopg2
from config import *   # credentials and table names


# logging config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s | %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', filename=LOGPATH)
log = logging.getLogger(__name__)

# disable logging for requests
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# function definition
def parse_response(str):
    """Clean the response of the api to obtain a single string"""
    str = str[:-1]
    str = str.replace(',', '.')
    str = str.replace('--', '00')
    return str


# define the url to access the steam market api
url = 'https://steamcommunity.com/market/priceoverview/?%20country=IT&currency=3&appid=730&market_hash_name={}%20%7C%20{}%20%28{}%29'

# connect to the database
conn = psycopg2.connect(user=USER, dbname=DB)

# create the cursor
c = conn.cursor()
c.execute("SELECT id, name, color, wear FROM {}".format(ITEM_DB))
records = c.fetchall()

# loop and write to db
for item in records:
    # get the timestamp at runtime
    dt = datetime.now()

    # unpack the 3 variables
    item_id, name, color, wear = item

    # send the request
    try:
        r = requests.get(url.format(name, color, wear))
    except:
        log.error('Request failed')
        sys.exit()
    result = r.json()

    # try to read the values from the API call, if one is missing
    try:
        low = parse_response(result['lowest_price'])
    except:
        low = 0
        log.warning("Couldn't fetch lowest price for {}-{}, {}".format(name, color, wear))

    try:
        med = parse_response(result['median_price'])
    except:
        med = 0
        log.warning("Couldn't fetch median price for {}-{}, {}".format(name, color, wear))

    try:
        vol = result['volume'].replace(',', '')   # strip , and replace with comma
    except:
        vol = 0
        log.warning("Couldn't fetch volume for {}-{}, {}".format(name, color, wear))
        
    # write into the db
    c.execute("INSERT INTO market(executed_on, item_id, volume, lowest_price, median_price) values('{}', '{}', '{}', '{}', '{}');".format(dt, item_id, vol, low, med))

# make changes permanent
conn.commit()

# clear the cursor and close the connection
if (conn):
    c.close()
    conn.close()

# final log message
log.info('Database update complete.')
