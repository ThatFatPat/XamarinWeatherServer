import sqlite3
import logging
import os
from http import HTTPStatus
from decimal import Decimal

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(THIS_FOLDER, "./xamarinweatherdb.db")

class dbResponse:
    def __init__(self, data, resp_code):
        self.resp_code = resp_code
        self.data = data

# Return (True, result) on success, (False, e) on error
def _query(q, params):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(q, params)
        conn.commit()
        return (True, c.fetchall())
    except sqlite3.Error as e:
        logging.error(str(e))
        return (False, e)
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)  # You can create a new database by changing the name within the quotes
    c = conn.cursor() # The database will be saved in the location where your 'py' file is saved
    c.execute('''CREATE TABLE IF NOT EXISTS "Cities" (
                "CityId"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "LocationId"	TEXT NOT NULL UNIQUE,
                "CityName"  TEXT NOT NULL,
                "CountryName" TEXT NOT NULL,
                "Lon"	NUMERIC NOT NULL,
                "Lat"	NUMERIC NOT NULL
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS "Users" (
                "UserId"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "Username"	TEXT NOT NULL UNIQUE,
                "Password"  TEXT NOT NULL
            )''')                    
    c.execute('''CREATE TABLE IF NOT EXISTS "UsernamesCities" (
                "UserId"	INTEGER NOT NULL,
                "CityId"	TEXT NOT NULL,
                FOREIGN KEY("UserId") REFERENCES "Users"("UserId"),
                FOREIGN KEY("CityId") REFERENCES "Cities"("CityId"),
                UNIQUE (UserId, CityId)
            )''')
    conn.commit()
    conn.close()

# Returns dbResponse(UserId, HTTPStatus.OK) on success, dbResponse({"exists": False}, HTTPStatus.UNAUTHORIZED) if user does not exist, dbResponse('', HTTPStatus.INTERNAL_SERVER_ERROR) on error
def _getUserId(user, password):
    inputParams = (user, password,)
    query = "SELECT UserId from Users WHERE Username = ? AND Password = ?"
    ret = _query(query, inputParams)
    if ret[0]:
        if len(ret[1]) > 0:
            return dbResponse(ret[1][0][0], HTTPStatus.OK) # Get UserId from nested hell
        else:
            return dbResponse({"exists": False}, HTTPStatus.UNAUTHORIZED)
    else:
        return dbResponse('', HTTPStatus. INTERNAL_SERVER_ERROR)

# Returns dbResponse({"exists": True/False}, HTTPStatus.OK/HTTPStatus.UNAUTHORIZED) based on _getUserId return code. Carries _getUserId response on error.
def checkCredentials(user, password):
    ret = _getUserId(user, password)
    if ret.resp_code == HTTPStatus.OK:
         return dbResponse({"exists": True}, HTTPStatus.OK)
    else:
        return ret

# Returns dbResponse({"exists": False/True}, HTTPStatus. CREATED/HTTPStatus.BAD_REQUEST). Carries _getUserId response on error.
def registerUser(user, password):
    inputParams = (user, password)
    query = "INSERT INTO Users (Username, Password) VALUES (?, ?)"
    ret = _query(query, inputParams)
    if ret[0]:
        return dbResponse({"exists": False}, HTTPStatus.CREATED) # Account Created
    else:
        if "UNIQUE" in str(ret[1]):
            return dbResponse({"exists": True}, HTTPStatus.BAD_REQUEST) # Username exists
        else:
            return dbResponse('', HTTPStatus.INTERNAL_SERVER_ERROR)

# Returns dbResponse({"exists": True, "cities": cities}) on success. On failed auth returns response from _getUserId
def getCitiesForUser(user, password):
    resp = _getUserId(user, password)
    if resp.resp_code == HTTPStatus.OK:
        # Authorization successful
        inputParams = (resp.data,)
        query = "SELECT Cities.CityId, LocationId, CityName, CountryName, Lon, Lat FROM UsernamesCities LEFT JOIN Cities ON UsernamesCities.CityId=Cities.CityId WHERE UserId = ?"
        ret = _query(query, inputParams)
        if ret[0]:
            cities = [_rowToCityExternal(row) for row in ret[1]]
            return dbResponse({"exists": True, "cities": cities}, HTTPStatus.OK)
        else:
            return dbResponse('', HTTPStatus.INTERNAL_SERVER_ERROR)
    return resp # Return _getUserId response

# Exclude internal CityId
def _rowToCityExternal(row):
    return {"Id": row[1], "CityName": row[2], "CountryName": row[3], "CoordData":{"lon": row[4], "lat": row[5]}} 

# Include internal CityId and structure
def _rowToCityInternal(row):
    return {"CityId": row[0], "LocationId": row[1], "CityName": row[2], "CountryName": row[3], "Lon": row[4], "Lat": row[5]}

def _cityInternalToExternal(city):
    return {"Id": city["LocationId"], "CityName": city["CityName"], "CountryName": city["CountryName"], "CoordData":{"lon": city["Lon"], "lat": city["Lat"]}} 

def _verifyCity(cityExternal):
    try:
        assert str(cityExternal["Id"]) is not None
        assert str(cityExternal["CityName"]) is not None
        assert str(cityExternal["CountryName"]) is not None
        assert float(cityExternal["CoordData"]["lon"]) is not None
        assert float(cityExternal["CoordData"]["lat"]) is not None
        return True
    except:
        return False


# No cityId column   
def _cityExternalToRow(cityExternal):
    row = [None] * 5
    row[0] = str(cityExternal["Id"])
    row[1] = str(cityExternal["CityName"])
    row[2] = str(cityExternal["CountryName"])
    row[3] = float(cityExternal["CoordData"]["lon"])
    row[4] = float(cityExternal["CoordData"]["lat"])
    return tuple(row)

# TODO: City lookup in table, add city for user

def _lookupCity(locationId):
    inputParams = (locationId,)
    query = "SELECT * FROM Cities WHERE LocationId = ?"
    ret = _query(query, inputParams)
    if ret[0]:
        if len(ret[1]) > 0:
            return dbResponse(_rowToCityInternal(ret[1][0]), HTTPStatus.OK)
        else:
            return dbResponse({"exists": False}, HTTPStatus.NOT_FOUND)
    else:
        return dbResponse({"exists": False}, HTTPStatus.BAD_REQUEST)

def _addCity(cityExternal):
    if not (_verifyCity(cityExternal)):
        return dbResponse({"exists": False}, HTTPStatus.BAD_REQUEST)
    inputParams = _cityExternalToRow(cityExternal)
    query = "INSERT INTO Cities VALUES (NULL, ?, ?, ?, ?, ?)"
    ret = _query(query, inputParams)
    if ret[0]:
        return dbResponse(_lookupCity(inputParams[0]).data, HTTPStatus.OK)
    else:
        if "UNIQUE" in ret[1]:
           return dbResponse({"exists": True}, HTTPStatus.BAD_REQUEST)
        else:
           return dbResponse({"exists": False}, HTTPStatus.INTERNAL_SERVER_ERROR)


def addCityForUser(user, password, city):
    resp = _getUserId(user, password)
    if resp.resp_code != HTTPStatus.OK:
        return resp
    userId = resp.data
    resp = _lookupCity(city["Id"])
    if resp.resp_code == HTTPStatus.OK:
        cityId = resp.data["CityId"]
    elif resp.resp_code == HTTPStatus.BAD_REQUEST:
        return resp
    else:
        resp = _addCity(city)
        if resp.resp_code != HTTPStatus.OK:
            return resp
        cityId = resp.data["CityId"]
    inputParams = (userId, cityId)
    query = "INSERT INTO UsernamesCities (UserId, CityId) VALUES (?, ?)"
    ret = _query(query, inputParams)
    if ret[0]:
        return dbResponse({"exists": False}, HTTPStatus.OK)
    else:
        if "UNIQUE" in str(ret[1]):
            return dbResponse({"exists": True}, HTTPStatus.BAD_REQUEST) # City User combination exists
        else:
            return dbResponse('', HTTPStatus.INTERNAL_SERVER_ERROR)

def removeCityForUser(user, password, city):
    resp = _getUserId(user, password)
    if resp.resp_code != HTTPStatus.OK:
        return resp
    userId = resp.data
    resp = _lookupCity(city["Id"])
    if resp.resp_code == HTTPStatus.OK:
        cityId = resp.data["CityId"]
    elif resp.resp_code == HTTPStatus.BAD_REQUEST or resp.resp_code == HTTPStatus.NOT_FOUND:
        resp.resp_code = HTTPStatus.BAD_REQUEST
        return resp
    inputParams = (userId, cityId)
    query = "DELETE FROM UsernamesCities WHERE UserId = ? AND CityId = ?"
    ret = _query(query, inputParams)
    if ret[0]:
        return dbResponse({"exists": False}, HTTPStatus.OK)
    else:
        return dbResponse('', HTTPStatus.INTERNAL_SERVER_ERROR)