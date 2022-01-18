import cv2
import datetime
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')
file_counter = 0
while True:
    _, frame = cap.read()
    original_frame = frame.copy()
    original_frame = cv2.flip(original_frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = face_cascade.detectMultiScale(gray, 1.3, 5)
    for x, y, w, h in face:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        face_roi = frame[y:y+h, x:x+w]
        gray_roi = gray[y:y+h, x:x+w]
        smile = smile_cascade.detectMultiScale(gray_roi, 1.3, 25)
        for x1, y1, w1, h1 in smile:
            cv2.rectangle(face_roi, (x1, y1), (x1+w1, y1+h1), (255, 0, 0), 2)
            time_stamp = datetime.datetime.now().strftime("%d-%m-%Y-%I:%M:%S %P")
            file_counter += 1
            file_name = f'selfie-{time_stamp} ({file_counter}).png'
            cv2.imwrite(file_name, original_frame)
    frame = cv2.flip(frame, 1)
    cv2.imshow('Smile Please :) ', frame)
    if file_counter ==10:
      break
    if cv2.waitKey(10) == ord('q'):
        break
    
      
    
