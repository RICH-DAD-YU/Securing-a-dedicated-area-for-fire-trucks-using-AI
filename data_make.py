import sqlite3

conn = sqlite3.connect("apart.db", isolation_level=None) #자동으로 커밋(실제로 DB에 반영)

curs = conn.cursor()

curs.execute( 'CREATE TABLE IF NOT EXISTS apartment \
    (name text , car_plate text PRIMARY KEY, phone_num text)')

make_tuple = (
    ("김현숙", '32가5481' ,'010-3295-9842'),
    ("김종국", '23나3152' ,'010-3267-1321'),
    ("박서준", '12바5471' ,'010-1238-3211'),
    ('박하준', '18소1252' ,'010-3620-9987'),
    ('최도윤', '83조8991' ,'010-7632-8763'),
    ('김시우', '127나9812','010-4693-2357'),
    ('이은우', '52무0728' ,'010-4472-0649'),
    ('박지호', '69아6054' ,'010-9178-1193'),
    ('김민준', '70더5145' ,'010-0821-4326'),
    ('하유준', '94구2412' ,'010-9076-4487'),
    ('차승원', '52주3108', '010-2341-4862'),
)
curs.executemany("INSERT INTO apartment(name, car_plate, phone_num) VALUES(?, ?, ?)", make_tuple)
