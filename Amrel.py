import sys
from datetime import datetime

import pyvisa
from PyQt6.QtCore import pyqtSignal, Qt, QObject, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSpacerItem, QLineEdit

import requests

API_URL = "http://100.125.162.5:8000/readings"


class PPS(QMainWindow):
    def __init__(self):
        super().__init__()

        rm = pyvisa.ResourceManager()

        my_instrument = rm.open_resource('GPIB0::6::INSTR')
        ps = my_instrument.query('*IDN?')

        self.currentCalibration = ""
        self.serial = ""
        self.param1 = ""
        self.param2 = ""
        self.param3 = ""


        self.setWindowTitle("Amrel PPS-35-2D")
        self.setFixedSize(1280, 635)

        self.on = 0

        self.amrel = QWidget()
        self.setCentralWidget(self.amrel)

        self.amrelLayout = QVBoxLayout()

        self.testLabel = QLabel("Amrel Power Supply Calibration Page")
        self.amrelLayout.addWidget(self.testLabel)

        self.amrelLayout.addStretch(1)

        self.amrel.setLayout(self.amrelLayout)

    def PostCalibration(self, serial, a, b, c, date):
        payload = {
            #Design payload for updated calibration where necessary.
            #Create SQL table
            #Create API endpoint
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            response.raise_for_status()
            print("Calibration upload successfully!")
            return True

        except requests.RequestException as e:
            print(f"Calubration upload failed: {e}")
            return False

    def WriteCalibrationData(self):
        try:
            lines = []
            self.Calibrations = []
            today = datetime.today()

            with open("Calibrations", 'a') as outfile:
                outfile.write(
                    f"S/N,{self.serial},Parameter 1,{self.param1},Parameter 2,{self.param2},Parameter 3,{self.param3},Date,{today}\n"
                    # Design this based on the *IDN? returns for device
                    )
                outfile.close()

            with open("Calibrations", 'r') as file:
                for line in file:
                    line.strip("")
                    current = line.split(',')
                    lines.append(line)

                for line in lines:
                    sweetbabyjesus = line.split(",")
                    print(sweetbabyjesus[1])
                    if self.serial in sweetbabyjesus[1]:
                        print(sweetbabyjesus[9])
                        self.Calibrations.append(sweetbabyjesus[9])
                print(self.Calibrations)
                self.currentCalibration = max(self.Calibrations)
                print(f"The most recent calibration date is: {self.currentCalibration}")
                print("Fingers crossed.")
                file.close()

            with open("TestStandParameters/VoltageCalibrations", 'r') as file:
                for line in file:
                    thankyoulord = line.split(",")
                    if self.currentCalibration in thankyoulord[9]:
                        self.calibratedparam1 = thankyoulord[3]
                        self.calibratedparam2 = thankyoulord[5]
                        self.calibratedparam3 = thankyoulord[7]
                file.close()

            self.PostCalibration(self.serial, self.calibratedparam1, self.calibratedparam2, self.calibratedparam3,
                                 today)

            print(self.calibratedparam1)
            print(self.calibratedparam2)
            print(self.calibratedparam3)
            print("Amen.")

        except Exception as e:
            print(f"error: {e}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PPS()
    window.show()
    sys.exit(app.exec())