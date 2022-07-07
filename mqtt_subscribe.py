# pip3 install paho-mqtt

import random
import json
from paho.mqtt import client as mqtt_client
from mqtt_publish import PublishMQTT
import datetime

"""
broker 
"mqtt.fluux.io"             // flutter cannot connect this broker
'broker.emqx.io'
"test.mosquitto.org"
"""


class SubscribeMQTT:

    def __init__(self, arduino, mysql):
        self.broker = "test.mosquitto.org"
        self.port = 1883
        self.topic = "/python/mailbox_testing"
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.publisher = PublishMQTT()
        self.mysql = mysql
        self.arduino = arduino
        self.id = "raspberrypi"
        self.client = ""

    def start_subscribe(self):
        self.client = self.connect_mqtt()
        self.subscribe(self.client)
        self.client.loop_forever()

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            message = json.loads(msg.payload.decode())
            print(f"Received `{message}` from `{msg.topic}` topic")
            if message["receiver"] == self.id:
                self.take_action(message["command"], message["flat"])

        client.subscribe(self.topic)
        client.on_message = on_message

    def publish(self, message):
        result = self.client.publish(self.topic, message)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{message}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")

    def take_action(self, command, flat):

        if command == "open_mailbox":
            print(f"i am opening mailbox {flat}")
            self.arduino.write("M01L01\n".encode("utf_8"))

        elif command == "request_data":
            print(f"getting mailbox data for {flat}")
            data = self.mysql.get_mailbox_data(flat)
            data["command"] = "response_data"
            data["receiver"] = flat
            dict_to_json = json.dumps(data)
            self.publish(dict_to_json)

        elif command == "request_qr_code":
            data = {"command": "response_qr_code", "receiver": flat}
            old_qr, is_valid, create = self.mysql.check_if_still_valid("qr_code", flat)
            if is_valid:
                print(f"getting old qr code fo {flat}")
                time_change = datetime.timedelta(minutes=5)
                create = datetime.datetime.fromtimestamp(create)
                expired_at = create + time_change
                start_time = f"{create.date()} {create.strftime('%X')}"
                end_time = f"{expired_at.date()} {expired_at.strftime('%X')}"
                data["qr_code"] = old_qr
                data["valid_from"] = start_time
                data["valid_to"] = end_time
            else:
                print(f"generating new qr code for {flat}")
                valid_from, valid_to = self.get_valid_time()
                data["valid_from"] = valid_from
                data["valid_to"] = valid_to
                data["qr_code"] = self.mysql.get_qr_code(flat)

            dict_to_json = json.dumps(data)
            self.publish(dict_to_json)

        elif command == "refresh_qr_code":
            new_code = self.mysql.refresh_qr_code(flat)
            data = {"command": "response_qr_code", "receiver": flat}
            valid_from, valid_to = self.get_valid_time()
            data["valid_from"] = valid_from
            data["valid_to"] = valid_to
            data["qr_code"] = new_code
            dict_to_json = json.dumps(data)
            self.publish(dict_to_json)

        elif command == "request_pin_code":
            data = {"command": "response_pin_code", "receiver": flat}
            old_pin, is_valid, create = self.mysql.check_if_still_valid("pin", flat)
            if is_valid:
                print(f"getting old pin code fo {flat}")
                time_change = datetime.timedelta(minutes=5)
                create = datetime.datetime.fromtimestamp(create)
                expired_at = create + time_change
                start_time = f"{create.date()} {create.strftime('%X')}"
                end_time = f"{expired_at.date()} {expired_at.strftime('%X')}"
                data["pin"] = old_pin
                data["valid_from"] = start_time
                data["valid_to"] = end_time
            else:
                print(f"generating new pin code for {flat}")
                valid_from, valid_to = self.get_valid_time()
                data["valid_from"] = valid_from
                data["valid_to"] = valid_to
                data["pin"] = self.mysql.get_pin(flat)

            dict_to_json = json.dumps(data)
            self.publish(dict_to_json)

        elif command == "refresh_pin_code":
            new_code = self.mysql.refresh_pin_code(flat)
            data = {"command": "response_pin_code", "receiver": flat}
            valid_from, valid_to = self.get_valid_time()
            data["valid_from"] = valid_from
            data["valid_to"] = valid_to
            data["pin"] = new_code
            dict_to_json = json.dumps(data)
            self.publish(dict_to_json)

    def get_valid_time(self):
        now = datetime.datetime.now()
        time_change = datetime.timedelta(minutes=5)
        valid_time = now + time_change
        start_time = f"{now.date()} {now.strftime('%X')}"
        end_time = f"{valid_time.date()} {valid_time.strftime('%X')}"
        return start_time, end_time
