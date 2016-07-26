import xml.etree.ElementTree as ET # XML API
import sqlite3 # for work with sqllite

conn = sqlite3.connect('trackDB.sqlite') # open a connection to the SQLite DB
cur = conn.cursor() # create cursor for work with DB

# make fresh table (remove old table, create new)
cur.executescript('''
    DROP TABLE IF EXISTS Artist;
    DROP TABLE IF EXISTS Genre;
    DROP TABLE IF EXISTS Album;
    DROP TABLE IF EXISTS Track;

    CREATE TABLE Artist (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE
    );

    CREATE TABLE Genre (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE
    );

    CREATE TABLE Album (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        artist_id INTEGER,
        title TEXT UNIQUE
    );

    CREATE TABLE Track (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        title TEXT UNIQUE,
        album_id INTEGER,
        genre_id INTEGER,
        len INTEGER,
        rating INTEGER,
        count INTEGER
    );
''')

filename = raw_input('Enter file name: ')
if (len(filename) < 1): filename = 'Library.xml'

# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>
# <key>Genre</key><string>Rock</string>

def lookup(d, key): # if tag = key, return text from this tag, else return None
    found = False
    for child in d:
        if found: return child.text
        if child.tag == 'key' and child.text == key:
            found = True
    return None

stuff = ET.parse(filename) # parse XML
all_stuff = stuff.findall('dict/dict/dict') # find all dict
print 'Dict count:', len(all_stuff)

for entry in all_stuff:
    if (lookup(entry, 'Track ID') is None): continue # if exist track id

    name = lookup(entry, 'Name') # check if exist name, artist, album, genre
    artist = lookup(entry, 'Artist')
    album = lookup(entry, 'Album')
    genre = lookup(entry, 'Genre')
    count = lookup(entry, 'Play Count')
    rating = lookup(entry, 'Rating')
    length = lookup(entry, 'Total Time');

    if name is None or artist is None or album is None or genre is None:
        continue

    cur.execute('''INSERT OR IGNORE INTO Artist (name) VALUES ( ? )''', (artist,)) # if exist ingore this, else insert new Artist name
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist,)) # take id Artist for Track and for Album
    artist_id = cur.fetchone()[0] # return Artist id

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) VALUES ( ?, ? )''', (album, artist_id)) # if exist ignore this, else insert new Album name with Artist id
    cur.execute('''INSERT OR IGNORE INTO Genre (name) VALUES ( ? )''', (genre,)) # if exist ignore this, else insert new Genre name
    cur.execute('SELECT Album.id, Genre.id FROM Album, Genre WHERE Album.title = ? AND Genre.name = ? ', (album, genre)) # take id Album and id Genre for Track
    album_id, genre_id = cur.fetchone() # return Album id and Genre id

    # create new Track, with Album id, Genre id
    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, genre_id, len, rating, count)
        VALUES ( ?, ?, ?, ?, ?, ? )''',
        (name, album_id, genre_id, length, rating, count))

    conn.commit() # this method commit the currect transaction

# sql request, take first 3 tracks
sqlstr = 'SELECT Track.title, Artist.name, Album.title, Genre.name FROM Track JOIN Genre JOIN Album JOIN Artist ON Track.genre_id = Genre.id AND Track.album_id = Album.id AND Album.artist_id = Artist.id ORDER BY Artist.name LIMIT 3'

# print Track title, Artist name, Album title, Genre name
for row in cur.execute(sqlstr):
    print str(row[0]), str(row[1]), str(row[2]), str(row[3])

cur.close() # close the DB connection

