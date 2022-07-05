"""
api documentation:
https://documenter.getpostman.com/view/12218052/UzJFxJzH
"""

import json
import requests


class APIToServer:

    def __init__(self):
        self.url = "http://54.251.29.106/"
        self.status_url = "locker/updateLockerStatus"
        self.check_qr_url = "locker/verifyQRcode"

    def update_locker_status(self):
        response = requests.post(f"{self.url}{self.status_url}")
        print(response.status_code)

    def check_qr_code(self, qr):
        convert = json.loads(qr)
        responses = requests.post(f"{self.url}{self.check_qr_url}", json=convert)
        data = responses.json()
        print(data)
        if data["success"] == "True":
            return True
        else:
            return False

