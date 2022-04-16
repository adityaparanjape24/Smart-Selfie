import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDesktopWidget,QLineEdit, QCheckBox
from PyQt5.QtGui import QImage , QPixmap, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtCore
import cv2
import time 
import datetime
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import re


class MainWindow(QWidget):

    def __init__(self):

        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()
        self.setWindowTitle("Smart Selfie")
        self.move(self.center())
        self.message = QLabel("Smile please to capture photos")
        self.message.setStyleSheet("color: green;")
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.message.setFont(QFont('Arial', 11))
        self.VBL.addWidget(self.message)
        self.FeedLabel = QLabel()
        self.FeedBox = QHBoxLayout()
        self.FeedBox.addStretch()
        self.FeedBox.addWidget(self.FeedLabel)
        self.FeedBox.addStretch()
        self.VBL.addLayout(self.FeedBox)
        self.e_label = QLabel("Enter your email to receive your photos !")
        self.e_label.setStyleSheet("color: blue;")
        self.e_label.setFont(QFont('Arial', 10))
        self.email = QLineEdit()
        self.email.resize(200, 30)
    
        self.email.returnPressed.connect(self.Share)
        self.VBL.addWidget(self.e_label)
        self.VBL.addWidget(self.email)
        self.e_status = QLabel()
        self.VBL.addWidget(self.e_status)
        
        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.resize(120,20)
        self.CancelBTN.clicked.connect(self.CancelFeed)
        
        self.ShareBTN = QPushButton("Share")
        self.filedata = []
        
        self.ShareBTN.clicked.connect(self.Share)
        self.ShareBTN.resize(120,20)

        self.ImageBox = QHBoxLayout()
        self.VBL.addLayout(self.ImageBox)

        self.ActionBox = QHBoxLayout()
        self.ActionBox.addStretch()
        self.VBL.addLayout(self.ActionBox)
        self.ActionBox.addWidget(self.CancelBTN)
        self.ActionBox.addWidget(self.ShareBTN)
        self.ActionBox.addStretch()

        self.Worker1 = Worker1()
        self.Email_worker = Email_worker()
        self.Email_worker.email_status.connect(self.EmailStatus)
        
        self.Worker1.start()

        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.capturedImage.connect(self.capturedImageSlot)
        self.Worker1.filename.connect(self.filecapture)
        
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
        
    def filecapture(self,file_name):
        self.filedata.append(file_name)


    def CancelFeed(self):
        self.Worker1.stop()
        self.close()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.Worker1.stop()
            self.close()

    def EmailStatus(self,status):
        self.e_status.setText(status)
        self.e_status.setStyleSheet("color: green;")
        
    
    def Share(self):
        regex = '^[a-z0-9-A-Z]+[\._]?[a-z0-9-A-Z]+[@]\w+[.]\w{2,3}$'
        if (re.fullmatch(regex , self.email.text())):
            self.e_status.setText("Valid email address")
            self.email.text()
            print(self.email.text())
            print(self.filedata)

            self.Email_worker.email_value = self.email.text()
            self.Email_worker.photos = self.filedata
            self.e_status.setText("Sending...")
            self.e_status.setStyleSheet("color: blue;")
            self.Email_worker.start()

        else:
            self.e_status.setText("Invalid email address")
            self.e_status.setStyleSheet("color: red;")

        

class Email_worker(QThread):
    email_value = ""
    photos = []
    email_status = pyqtSignal(str)
    def run(self):
        
        # create message object instance
        msg = MIMEMultipart()
        # setup the parameters of the message
        password = "johkjngfpfienmwj"
        msg['From'] ="smartselfie24@gmail.com"
        msg['To'] = self.email_value
        msg['Subject'] = "Selfie Photos"

        body = "Glimpse of your great memories :) , Have a look !!"
        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))
        
        self.size = len(self.photos)
        print(len(self.photos))

        for data in self.photos:
            #print(self.filedata[data])
            print(data)
            filename = data
            with open(filename,"rb") as attachment:
        
                # instance of MIMEBase and named as p
                p = MIMEBase('application', 'octet-stream')
                
                # To change the payload into encoded form
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                
                p.add_header('Content-Disposition', "attachment; filename= selfi_image.png")
                
                # attach the instance 'p' to instance 'msg'
                msg.attach(p)
                    
                # create server
        server = smtplib.SMTP('smtp.gmail.com: 587')
        
        server.starttls()
        
        # Login Credentials for sending the mail
        server.login(msg['From'], password)
        
        
        # send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        
        server.quit()
        
        status = f"successfully sent email to {msg['To']}"
        print("successfully sent email to %s:" % (msg['To']))
        self.email_status.emit(status)

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    capturedImage = pyqtSignal(QImage)
    filename = pyqtSignal(str)
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
                       
                       if file_counter <=5:
                         cv2.imwrite(file_name, original_image)
                         self.filename.emit(file_name)
                         original_image = cv2.cvtColor(original_image,cv2.COLOR_BGR2RGB)
                         formatted_img = QImage(original_image.data, original_image.shape[1], original_image.shape[0], QImage.Format_RGB888)
                         captured_Image_frame = formatted_img.scaled(64, 64, Qt.KeepAspectRatio)
                         self.capturedImage.emit(captured_Image_frame)

                frame = cv2.flip(frame, 1)  
                frame= cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                Convert_To_Qt_Format = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                Pic = Convert_To_Qt_Format.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)


    def stop(self):
        self.ThreadActive = False
        self.quit()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

