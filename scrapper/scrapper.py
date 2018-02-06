import requests
from pymongo import MongoClient
from bson.json_util import dumps
from simplejson import dump
from threading import Thread
import time
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, COMMASPACE
import gzip
from os import environ


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

        self.db_connection()

        # template_bounds = ["y1","y2","x1","x2"]
        self.bounds = [60.24, 46.30, -24.75, 6.15]
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

        self.dump_path = 'dumps/dump.gz'

        self.run_background()

    def db_connection(self):
        """
            setup db connection
        :return:
        """
        MONGODB_URI = environ.get('MONGODB_URI')
        if not MONGODB_URI:
            MONGODB_URI = "mongodb://localhost:27017/"
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client.get_database('flights_db')
            return

        self.client = MongoClient(MONGODB_URI)
        self.db = self.client.get_database('flights_db')

    def build_params(self):
        """
            return the api formated params
        :return:
        """
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
        """
            format bounds with the api endpoint requirements
        :return:
        """
        return ','.join([str(d) for d in self.bounds])

    def get_request(self):
        """
            build request with requests library and return response in json format
        :return:
        """
        base_url = "https://data-live.flightradar24.com"
        api_route = "/zones/fcgi/feed.js"
        query_params = self.build_params()

        r = requests.get(''.join([base_url, api_route]), params=query_params, headers=self.headers)

        if len(r.text):
            return r.json()
        else:
            return {"code": 400}

    def run(self):
        """
            infinit loop handling the data scapping
        :return:
        """
        flights_cl = self.db['flight_points']

        while True:
            count = flights_cl.count()
            # try:
            #     count = flights_cl.count()
            # except ValueError:
            #     print('count = ' + str(count))

            if count >= 100000:
                self.mongodump()
            else:
                print("collection has {} documents".format(count))

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

    def get_db(self, env, start_res):
        """
            response to get wsgi requests
        :param env:
        :param start_res:
        :return:
        """
        flights_cl = self.db['flight_points']

        data = [x for x in flights_cl.find()]
        sdata = dumps(data).encode()
        start_res("200 OK", [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(sdata)))
        ])

        return iter([sdata])

    def compress_dump(self, data):
        """
            get data as input params and generate a file on dumps folder with de compressed data
        :param data:
        :return:
        """
        with gzip.open(self.dump_path, 'wt') as f:
            dump(data, f)

    def mongodump(self):
        """
            dump data from the db and send an email with de compressed result
        :return:
        """
        db = self.client.flights_db
        flights_cl = db.flights

        data = dumps([x for x in flights_cl.find()])
        self.compress_dump(data)

        self.send_email()
        flights_cl.delete_many({})

    def run_background(self):
        """
            run infinit loop on the background to allow response to get requests
        :return:
        """
        print('start running on background function {}'.format(self.run.__name__))
        b = Thread(name="background", target=self.run)
        b.start()

    def send_email(self):
        """
            When db is full, dump data and send it to my email
        :return:
        """
        print("\n\nSENDING EMAIL TO: lucasgarciabaro@gmail.com\n\n")
        msg = MIMEMultipart()

        msg["From"] = "lucasgarciabaro@gmail.com"
        msg["To"] = COMMASPACE.join(["lucasgarciabaro@gmail.com"])
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = "flights_db dump"

        msg.attach(MIMEText("new dump of flights_db from pythonanywhere"))

        name = "{}.gz".format(time.strftime("%m/%d-%H:%M"))

        with open(self.dump_path, 'rb') as f:
            part = MIMEApplication(
                f.read(),
                Name=name
            )
            part["Content-Disposition"] = "attachment; filename='%s'" % name
            msg.attach(part)

        smtp = smtplib.SMTP("smtp.gmail.com:587")
        smtp.starttls()

        user = environ.get('email_user')
        password = environ.get('email_password')
        smtp.login(user, password)

        smtp.sendmail(
            "lucasgarciabaro@gmail.com",
            ["lucasgarciabaro@gmail.com"],
            msg.as_string()
        )

        smtp.quit()


api = ApiHandler()
api_service = api.get_db
