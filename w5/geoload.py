import urllib
import sqlite3
import json
import time
import ssl

# url google geocode
serviceurl = 'http://maps.googleapis.com/maps/api/geocode/json?'

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS Locations (
        address TEXT,
        geodata TEXT
    )
''')

filename = open('where.data')
count = 0
for line in filename:
    if count > 30: break

    address = line.strip()

    cur.execute('SELECT geodata FROM Locations WHERE address = ? ', (buffer(address),))

    try:
        data = cur.fetchone()[0]
        print 'Found in database', address
        continue
    except:
        pass

    print 'Resolving', address
    url = serviceurl + urllib.urlencode({"sensor": "false", "address": address})
    print 'Retrieving', url
    uh = urllib.urlopen(url)
    data = uh.read()
    print 'Retrieved', len(data), 'characters', data[:20].replace('\n', '')
    count += 1

    try:
        js = json.loads(str(data))
    except:
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS'):
        print '===Failure to Retrieve==='
        print data
        break

    cur.execute('''INSERT INTO Locations (address, geodata) VALUES ( ?, ? )''', (buffer(address), buffer(data)))
    conn.commit()
    time.sleep(1)

print 'Run geodump.py to read the data from the database so you can visualize it on a map.'
