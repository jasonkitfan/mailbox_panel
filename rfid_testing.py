import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

reader = SimpleMFRC522()

while True:
    time.sleep(1)
    try:
        id, text = reader.read()
        print(id)
        print(text)
    except:
        print("unable to read")
    # finally:
    #     GPIO.cleanup()
