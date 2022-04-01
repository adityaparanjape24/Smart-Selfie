import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDesktopWidget,QLineEdit
from PyQt5.QtGui import QImage , QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt 
import cv2
import time 
import datetime

class MainWindow(QWidget):

    def __init__(self):

        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        self.setWindowTitle("Smart Selfie")

        self.move(self.center())
        self.FeedLabel = QLabel()

        self.FeedBox = QHBoxLayout()

        self.FeedBox.addStretch()

        self.FeedBox.addWidget(self.FeedLabel)

        self.FeedBox.addStretch()

        self.VBL.addLayout(self.FeedBox)

        self.CancelBTN = QPushButton("Cancel")

        self.CancelBTN.resize(120,20)

        self.CancelBTN.clicked.connect(self.CancelFeed)

        self.ShareBTN = QPushButton("Share")

        self.ShareBTN.resize(120,20)

        #self.ShareBTN.move(self.center())



        self.ImageBox = QHBoxLayout()

        self.VBL.addLayout(self.ImageBox)

        self.ActionBox = QHBoxLayout()

        self.ActionBox.addStretch()

        self.VBL.addLayout(self.ActionBox)

        self.ActionBox.addWidget(self.CancelBTN)

        self.ActionBox.addWidget(self.ShareBTN)

        self.ActionBox.addStretch()

        self.Worker1 = Worker1()

        self.Worker1.start()

        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.Worker1.capturedImage.connect(self.capturedImageSlot)
        self.setLayout(self.VBL)

        
    def center(self):

        qr = self.frameGeometry()

        cp = QDesktopWidget().availableGeometry().center()

        qr.moveCenter(cp)

        return qr.topLeft()



    def ImageUpdateSlot(self, Image):

        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))



    def capturedImageSlot(self,Image):

        self.label = QLabel(self)

        self.label.setPixmap(QPixmap.fromImage(Image))
        self.ImageBox.addWidget(self.label)

    def CancelFeed(self):

        self.Worker1.stop()

        self.close()

        



class Worker1(QThread):

    ImageUpdate = pyqtSignal(QImage)

    capturedImage = pyqtSignal(QImage)

    def run(self):

        self.ThreadActive = True

        Cap = cv2.VideoCapture(0)

        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

        file_counter = 0

        while self.ThreadActive:

            ret, frame = Cap.read()

            if ret:

                original_image = frame.copy()

                original_image = cv2.flip(original_image, 1)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                face = face_cascade.detectMultiScale(gray, 1.3 ,5)

                for x, y, w, h in face:

                   cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

                   face_roi = frame[y:y+h, x:x+w]

                   gray_roi = gray[y:y+h, x:x+w]

                   smile = smile_cascade.detectMultiScale(gray_roi, 1.4, 40)

                   for x1, y1, w1, h1 in smile:

                       cv2.rectangle(face_roi, (x1, y1), (x1+w1, y1+h1), (0, 0, 255), 2)

                       time_stamp = datetime.datetime.now().strftime("%d-%m-%Y-%I:%M:%S %P")

                       file_counter += 1

                       file_name = f'selfie-{time_stamp} ({file_counter}).png'

                       if file_counter < 5:

                         cv2.imwrite(file_name, original_image)

                         convert_to_qt = QImage(frame.original_image, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

                         captured_Image_frame = ConvertToQtFormat.scaled(64, 64, Qt.KeepAspectRatio)

                         self.capturedImage.emit(captured_Image_frame)



                frame = cv2.flip(frame, 1)  

                frame= cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

                ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

                self.ImageUpdate.emit(Pic)

                if file_counter == 5:

                  self.close()



    def stop(self):

        self.ThreadActive = False

        self.quit()



if __name__ == "__main__":

    App = QApplication(sys.argv)

    Root = MainWindow()

    Root.show()

    sys.exit(App.exec())

