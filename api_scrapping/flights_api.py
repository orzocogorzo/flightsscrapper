import requests


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

    def build_params(self, bnds):
        params = {
            "adsb": 1,
            "bounds": self.build_bounds(bnds),
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



    def build_bounds(self, bnds):
        # template_bounds = ["y1","y2","x1","x2"]
        return ','.join([str(d) for d in bnds])


    def get_request(self, bnds):
        base_url = "https://data-live.flightradar24.com"
        api_route = "/zones/fcgi/feed.js"
        query_params = self.build_params(bnds)

        r = requests.get(''.join([base_url, api_route]), params=query_params, headers=self.headers)

        if len(r.text):
            return r.json()
        else:
            return {"code": 400}
