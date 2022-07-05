# pip3 install paho-mqtt

#
import random
import json

from paho.mqtt import client as mqtt_client
from mqtt_publish import PublishMQTT
from mariadb import MySQL


class SubscribeMQTT():

    def __init__(self, arduino):
        self.broker = 'broker.emqx.io'
        self.port = 1883
        self.topic = "/python/mailbox_testing"
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.publisher = PublishMQTT()
        self.mysql = MySQL()
        self.arduino = arduino
        self.command = [
            "open_mailbox",
            "get_qr_code",
            "get_pin"
        ]

    def start_subscribe(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_forever()

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
            print(message["command"])
            if message["command"] in self.command:
                self.take_action(message["command"], message["flat"])

        client.subscribe(self.topic)
        client.on_message = on_message

    def take_action(self, command, flat):

        if command == "open_mailbox":
            print(f"i am opening mailbox {flat}")
            self.arduino.write("M01L01\n".encode("utf_8"))
