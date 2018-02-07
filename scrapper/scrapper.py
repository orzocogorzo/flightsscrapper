import requests
import time


class ApiHandler:

    def get_request(self):
        """
            build request with requests library and return response in json format
        :return:
        """
        base_url = "https://flights24api.herokuapp.com/"

        r = requests.get(base_url)

        if len(r.text):
            return r.json()
        else:
            return {"code": 400}

    def run(self):
        while True:
            self.get_request()
            time.sleep(300)

    def wsgi(self, env, start_res):

        data = 'hey there, I am still sending requests'
        start_res("200 OK", [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(data)))
        ])

        yield data
