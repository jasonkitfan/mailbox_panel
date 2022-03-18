import cv2 as cv

capture = cv.VideoCapture(0, cv.CAP_V4L)
while True:
    isTrue, frame = capture.read()
    cv.imshow("Camera", frame)

    if cv.waitKey(20) and 0xFF == ord("d"):
        break
