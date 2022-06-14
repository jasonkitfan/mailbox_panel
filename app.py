# pip install opencv-contrib-python==4.5.5.62
# pip install eel

import eel
import cv2 as cv
from camera import VideoCamera
import base64
import serial
from multiprocessing import Process
import time

# destroy all the chrome windows for lanuching in full screen mode
# import os
# os.system("taskkill /im chrome.exe /f")

flat = "1A"
mega2560_id = "M01"
lock_no = "L01"
valid_pin = "123456"
valid_qr = "{{fuma5xeo87tvsnn}}"

arduino_serial = serial.Serial("/dev/ttyUSB0", 9600, timeout=1.0)


def serial_read():
    global arduino_serial
    while True:
        time.sleep(0.01)
        if arduino_serial.in_waiting > 0:
            mydata = arduino_serial.readline().decode("utf-8").rstrip()
            print(mydata)
        time.sleep(1)


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
                    cv.putText(frame, str(people[label]), (x, y), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), thickness=2)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
                    send_serial(mega2560_id, lock_no, flat)
                else:
                    cv.putText(frame, str("Unknown"), (x, y), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 255), thickness=2)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), thickness=2)
        print("checking facial")
        # cv.imshow("Camera", frame)
        if cv.waitKey(20) and 0xFF == ord("d"):
            break


def qr_code_checking(image):
    detector = cv.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    if data:
        print(str(data))
        if data == valid_qr:
            send_serial(mega2560_id, lock_no, flat)
        else:
            eel.showInvalid("Invalid QR code", "red")
    if cv.waitKey(1) == ord("q"):
        pass
    print("checking qr code")


@eel.expose
def check_input(pin):
    print(pin)
    if pin == valid_pin:
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


def main():
    arduino = Process(target=serial_read)
    arduino.start()
    eel.init("html")
    eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])


if __name__ == "__main__":
    main()
