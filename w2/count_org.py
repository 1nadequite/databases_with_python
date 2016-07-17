import sqlite3

db = sqlite3.connect('count_org.sqlite')
cur_db = db.cursor()

# delete table Counts if they exists
cur_db.execute('''
DROP TABLE IF EXISTS Counts
''')

# create table Counts
cur_db.execute('''
CREATE TABLE Counts (org TEXT, count INTEGER)
''')

filename = raw_input('Enter file name: ')
if ( len(filename) < 1 ):
    filename = 'mbox.txt'
data = open(filename)
for line in data:
    if not line.startswith('From: '):
        continue
    pieces = line.split()
    email = pieces[1]
    org = email.split('@')[1]
    # check if this org is in the table
    cur_db.execute('SELECT count FROM Counts WHERE org = ? ', (org, ))
    row = cur_db.fetchone()
    if row is None:
        cur_db.execute('''INSERT INTO Counts (org, count)
                VALUES ( ?, 1 )''', ( org, ) )
    else:
        cur_db.execute('UPDATE Counts SET count = count + 1 WHERE org = ?',
            (org, ))
    db.commit()

# take first 10 org, with max count
sqlstr = 'SELECT org, count FROM Counts ORDER BY count DESC LIMIT 10'

print
print "Counts:"
for row in cur_db.execute(sqlstr) :
    print str(row[0]), row[1]

cur_db.close()
