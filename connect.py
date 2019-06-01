# connects to the loclahost db with the reference index
import psycopg2


# connect to the database
conn = psycopg2.connect(user='guido', dbname='cs_market')

# create the cursor
c = conn.cursor()

# retrieve all records that have been acquired
c.execute("SELECT name, color, wear FROM reference")
records = c.fetchall()


# test and extract records
for i in records:
    print(i)

# clear the cursor and close the connection
if (conn):
    c.close()
    conn.close()
    print('='*34)
    print('CLOSED CONNECTION')
