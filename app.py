# pip install opencv-contrib-python==4.5.5.62
# pip install eel

import eel
import cv2 as cv
from camera import VideoCamera
import base64
import serial
from multiprocessing import Process
import time
from mfrc522 import SimpleMFRC522
from mariadb import MySQL
from mqtt_subscribe import SubscribeMQTT
from api_to_server import APIToServer

# destroy all the chrome windows for lanuching in full screen mode
# import os
# os.system("taskkill /im chrome.exe /f")

temp_flat = "1A"
mega2560_id = "M01"
lock_no = "L01"
valid_pin = "123456"
valid_qr = "{{fuma5xeo87tvsnn}}"

"""
data_qr = {
    "{{abc}}": 
        {
        "mega_id": "M01",
        "lock_no": "L01",
        "flat": "1A",
        "valid_time": "01012000",
        }
    "{{def}}": 
        {
        "mega_id": "M01",
        "lock_no": "L02",
        "flat": "1B",
        "valid_time": "01012005",
        }
    "{{ghi}}": 
        {
        "mega_id": "M01",
        "lock_no": "L03",
        "flat": "1C",
        "valid_time": "01012010",
        }
}
"""


arduino_serial = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.1)
subscriber = SubscribeMQTT(arduino_serial)
db = MySQL("mailbox")
api = APIToServer()


def serial_read():
    global arduino_serial
    arduino_serial.flush()
    while True:
        time.sleep(0.01)
        if arduino_serial.in_waiting > 0:
            try:
                mydata = arduino_serial.readline().decode("utf-8").rstrip()
                print(mydata)
            except:
                print("something cannot decode")


def send_serial(board, lock, f):
    global arduino_serial
    data = f"{board}{lock}\n"
    arduino_serial.write(data.encode("utf_8"))
    eel.showValid(f"Mailbox {f} is Opening", "green")
    print("data sent to arduino")


haar_cascade = cv.CascadeClassifier('haar_face.xml')
face_recognizer = cv.face.LBPHFaceRecognizer_create()
face_recognizer.read('face_trained.yml')
people = ['ckf']

isFacial, isQr, isPin, current_num = False, False, False, -1


def facial_activate(capture):
    global isFacial
    while isFacial:
        eel.sleep(0.001)
        is_true, frame = capture.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces_rect = haar_cascade.detectMultiScale(gray, 1.1, 3)

        if len(faces_rect) > 0:
            for (x, y, w, h) in faces_rect:
                faces_roi = gray[y:y + h, x:x + w]
                label, confidence = face_recognizer.predict(faces_roi)
                print(f'Label = {people[label]} with a confidence of {confidence}')

                if confidence < 70:
                    cv.putText(frame, str(people[label]), (x, y), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0),
                               thickness=2)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
                    send_serial(mega2560_id, lock_no, temp_flat)
                    isFacial = False
                else:
                    cv.putText(frame, str("Unknown"), (x, y), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 255), thickness=2)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), thickness=2)
        print("checking facial")
        # cv.imshow("Camera", frame)
        if cv.waitKey(20) and 0xFF == ord("d"):
            break


def qr_code_checking(image):
    global isQr, db
    detector = cv.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    if data:
        print(str(data))
        is_valid, flat = db.check_qr_code(data)
        is_valid_api = api.check_qr_code(data)
        if is_valid:
            send_serial(mega2560_id, lock_no, flat)
            isQr = False
        elif is_valid_api:
            send_serial(mega2560_id, lock_no, flat)
            isQr = False
        else:
            eel.showInvalid("Invalid QR code", "red")
    if cv.waitKey(1) == ord("q"):
        pass
    print("checking qr code")


@eel.expose
def check_input(pin):
    print(pin)
    is_valid, flat = db.check_pin(pin)
    if is_valid:
        print("valid input")
        send_serial(mega2560_id, lock_no, flat)
    else:
        print("invalid input")
        eel.showInvalid("Invalid Input", "red")()


@eel.expose
def data_from_js(num):
    global isFacial, isQr, isPin, current_num
    if num == 0 and num != current_num:
        print("facial activated")
        isFacial, current_num = True, num
        capture = cv.VideoCapture(0)
        facial_activate(capture)
    elif num == 1 and num != current_num:
        print("qr code activated")
        isQr, current_num = True, num
    elif num == 2 and num != current_num:
        print("pin activated")
        isPin, current_num = True, num
    else:
        isFacial, isQr, isPin, current_num = False, False, False, num
        cv.destroyAllWindows()
        print(f"isFacial = {isFacial}, isQr = {isQr}, isPin = {isPin}")
    cv.destroyAllWindows()


def gen(camera):
    global isQr
    while isQr:
        frame = camera.get_frame()
        image = camera.get_image()
        qr_code_checking(image)
        yield frame


@eel.expose
def video_feed():
    x = VideoCamera()
    y = gen(x)
    for each in y:
        # Convert bytes to base64 encoded str, as we can only pass json to frontend
        blob = base64.b64encode(each)
        blob = blob.decode("utf-8")
        eel.updateImageSrc(blob)()
        # time.sleep(0.1)


def rfid_read():
    global db
    reader = SimpleMFRC522()
    while True:
        time.sleep(1)
        try:
            unique_id, text = reader.read()
            print(unique_id)
            print(type(unique_id))
            is_valid, flat = db.check_rfid(str(unique_id))
            print("that card is valid")
            if is_valid:
                send_serial(mega2560_id, lock_no, flat)
            # print(text)
        except:
            print("unable to read")


def main():
    arduino = Process(target=serial_read)
    arduino.start()
    rfid = Process(target=rfid_read)
    rfid.start()
    mqtt_sub = Process(target=subscriber.start_subscribe)
    mqtt_sub.start()
    eel.init("html")
    eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])


if __name__ == "__main__":
    main()
