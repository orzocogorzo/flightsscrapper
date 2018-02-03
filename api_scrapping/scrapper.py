from pymongo import MongoClient
from api_scrapping.flights_api import ApiHandler
import time

bounds = [47.92, 29.77, -28.22, 2.68]
data_keys = {
    "adshex": [
        "flight_id",
        "lat",
        "lng",
        "track",
        "alt",
        "speed",
        "squawk",
        "radar",
        "type",
        "registration",
        "timestamp",
        "s_airport",
        "t_airport",
        "IATA",
        "unknown1",
        "unknown2",
        "OACI",
        "unknown3",
    ]
}

client = MongoClient()
db = client.flights_db
flights_cl = db.flights

api = ApiHandler()

response = api.get_request(bounds)
del response['full_count']
del response['version']

while True:
    bulk = []
    for k, v in response.items():
        data = {
            "adshex": k
        }

        key_val = {}
        i = 0
        for d in v:
            key_val[data_keys["adshex"][i]] = d
            i = i + 1

        data.update(key_val)

        bulk.append(data)

    bulked = flights_cl.insert_many(bulk)
    print("inserted " + str(len(bulked.inserted_ids)) + " items to db")

    time.sleep(60)
