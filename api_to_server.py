"""
api documentation:
https://documenter.getpostman.com/view/12218052/UzJFxJzH
"""

import json
import requests
import datetime


class APIToServer:

    def __init__(self):
        self.url = "http://54.251.29.106/"
        self.status_url = "locker/updateLockerStatus"
        self.check_qr_url = "locker/verifyQRcode"
        self.id = "raspberrypi"

    def update_locker_status(self, flat, status):
        time = int(datetime.datetime.now().timestamp())
        data = {
            "pi_id": self.id,
            "flat": flat,
            "action": status,
            "actionTime": time
        }
        print(data)
        response = requests.post(f"{self.url}{self.status_url}", json=data)
        print(response.status_code)

    def check_qr_code(self, qr):
        convert = json.loads(qr)
        responses = requests.post(f"{self.url}{self.check_qr_url}", json=convert)
        data = responses.json()
        print(data)
        print(data["success"], type(data["success"]))
        if data["success"]:
            print("successful qr checking from api server")
            return True
        else:
            print("invalid qr code checked from api server")
            return False

