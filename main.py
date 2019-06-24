# main.py

from config import *   # credentials and table names
import psycopg2
from datetime import datetime
import requests


# logging config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s | %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', filename='/home/guido/logs/python/cs-market/cs-market.log')
log = logging.getLogger(__name__)

# disable logging for requests
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


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

    # unpack the 3 variables
    item_id, name, color, wear = item

    r = requests.get(url.format(name, color, wear))
    result = r.json()

    # get the timestamp at runtime
    dt = datetime.now()


    # try to read the values from the API call, if one is missing
    try:
        low = result['lowest_price'][:-1].replace(',', '.')   # strip the euro sybmol and convert in the . format
    except:
        low = 0
        log.warning("Couldn't fetch lowest price for {}-{}, {}".format(name, color, wear))

    try:
        med = result['median_price'][:-1].replace(',', '.')   # strip the euro symbol and convert in the . format
    except:
        med = 0
        log.warning("Couldn't fetch median price for {}-{}, {}".format(name, color, wear))

    try:
        vol = result['volume'].replace(',', '')   # strip . 
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

log.info('Database update complete.')
