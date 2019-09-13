import sqlite3

def init_db(path):
    conn = sqlite3.connect(path)  # You can create a new database by changing the name within the quotes
    c = conn.cursor() # The database will be saved in the location where your 'py' file is saved
    c.execute('''CREATE TABLE IF NOT EXISTS "Cities" (
                "CityId"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "LocationId"	TEXT NOT NULL,
                "Lat"	NUMERIC NOT NULL,
                "Lon"	NUMERIC NOT NULL
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS "UsernamesCities" (
                "UserId"	INTEGER NOT NULL,
                "CityId"	TEXT NOT NULL,
                FOREIGN KEY("UserId") REFERENCES "Users"("UserId"),
                FOREIGN KEY("CityId") REFERENCES "Cities"("CityId")
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS "Users" (
                "UserId"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "Username"	TEXT NOT NULL
            )''')
                                
    conn.commit()