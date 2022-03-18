import cv2 as cv
import numpy

haar_cascade = cv.CascadeClassifier('haar_face.xml')

people = ['ckf']
# features = np.load('features.npy', allow_pickle=True)
# labels = np.load('labels.npy')

face_recognizer = cv.face.LBPHFaceRecognizer_create()
face_recognizer.read('face_trained.yml')

capture = cv.VideoCapture(0)
while True:

    isTrue, frame = capture.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    faces_rect = haar_cascade.detectMultiScale(gray, 1.1, 3)

    if len(faces_rect) > 0:
        for (x, y, w, h) in faces_rect:
            faces_roi = gray[y:y + h, x:x + w]
            label, confidence = face_recognizer.predict(faces_roi)
            print(f'Label = {people[label]} with a confidence of {confidence}')

            if confidence < 60:
                cv.putText(frame, str(people[label]), (x, y), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), thickness=2)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
            else:
                cv.putText(frame, str("Unknown"), (x, y), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 255), thickness=2)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), thickness=2)

            cv.imshow("Pi Camera", frame)
            # cv.imshow("Videos", frame_resized)
    else:
        cv.imshow("Pi Camera", frame)

    if cv.waitKey(20) and 0xFF == ord("d"):
        break

capture.release()
cv.destroyAllWindows()
