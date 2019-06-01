# connects to the loclahost db
import psycopg2


# initialize connection
conn = psycopg2.connect(user='guido', dbname='socratica')

if (conn):
    print('connection successful')
    conn.close()
