import requests
from pymongo import MongoClient
from bson.json_util import dumps
import time


class ApiHandler:
    def __init__(self):
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Host": "data-live.flightradar24.com",
            "Origin": "https://www.flightradar24.com",
            "Referer": "https://www.flightradar24.com/40.34,-12.77/5",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
        }

        self.client = MongoClient()
        # template_bounds = ["y1","y2","x1","x2"]
        self.bounds = [47.92, 29.77, -28.22, 2.68]
        self.data_keys = {
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

        self.run()

    def build_params(self):
        params = {
            "adsb": 1,
            "bounds": self.build_bounds(),
            "estimated": 1,
            "faa": 1,
            "flarm": 1,
            "gliders": 1,
            "maxage": 14400,
            "mlat": 1,
            "stats": 1,
            "vehicles": 1
        }
        return params



    def build_bounds(self):
        return ','.join([str(d) for d in self.bounds])


    def get_request(self):
        base_url = "https://data-live.flightradar24.com"
        api_route = "/zones/fcgi/feed.js"
        query_params = self.build_params()

        r = requests.get(''.join([base_url, api_route]), params=query_params, headers=self.headers)

        if len(r.text):
            return r.json()
        else:
            return {"code": 400}

    def run(self):

        db = self.client.flights_db
        flights_cl = db.flights

        while True:
            response = self.get_request()
            del response['full_count']
            del response['version']

            bulk = []
            for k, v in response.items():
                data = {
                    "adshex": k
                }

                key_val = {}
                i = 0
                for d in v:
                    key_val[self.data_keys["adshex"][i]] = d
                    i = i + 1

                data.update(key_val)

                bulk.append(data)

            bulked = flights_cl.insert_many(bulk)
            print("inserted " + str(len(bulked.inserted_ids)) + " items to db")

            time.sleep(60)

    def get(self, env, start_res):
        db = self.client.flights_db
        flights_cl = db.flights

        data = [x for x in flights_cl.find()]
        sdata = dumps(data).encode()
        start_res("200 OK", [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(sdata)))
        ])

        return iter([sdata])


api = ApiHandler()
run_api = api.get
