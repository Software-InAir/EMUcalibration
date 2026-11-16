import sys
from datetime import datetime

import pyvisa
from PyQt6.QtCore import pyqtSignal, Qt, QObject, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSpacerItem, QLineEdit, QRadioButton, QSizePolicy, QDialog

import requests

USE_INSTRUMENT = False

API_URL = "http://100.125.162.5:8000/readings"


class FlukeCalibration(QDialog):
    def __init__(self):
        super().__init__()

        if USE_INSTRUMENT:
            rm = pyvisa.ResourceManager()

            my_instrument = rm.open_resource('GPIB0::1::INSTR')
            dmm = my_instrument.query('*IDN?')

        self.serial = ""
        self.param1 = ""
        self.param2 = ""
        self.param3 = ""

        self.setWindowTitle("Fluke 8840A")
        self.setFixedSize(1280, 635)

        self.on = 0

        self.flukeLayout = QVBoxLayout()

        self.upperSpacer = QSpacerItem(0, 50)
        self.flukeLayout.addItem(self.upperSpacer)

        self.contentLayout = QVBoxLayout()
        self.flukeLayout.addLayout(self.contentLayout)

        self.titleLayout = QVBoxLayout()
        self.contentLayout.addLayout(self.titleLayout)

        self.titleLayout.addStretch(1)

        self.unitLabel = QLabel("Fluke 8840A")
        self.unitLabel.setStyleSheet("""
                                    font-size: 24px
                                    """)
        self.unitLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLayout.addWidget(self.unitLabel)

        self.procedureLabel = QLabel("Calibration Procedures")
        self.procedureLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLayout.addWidget(self.procedureLabel)

        self.titleSpacer = QSpacerItem(0, 50)
        self.titleLayout.addItem(self.titleSpacer)

        self.procedureLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.procedureLayout)
        self.procedureLayout.addStretch(1)

        self.procedureSelectionLabel = QLabel("Select Procedure:")
        self.procedureSelectionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.procedureLayout.addWidget(self.procedureSelectionLabel)

        self.procedureButtonsLayout = QVBoxLayout()
        self.procedureLayout.addLayout(self.procedureButtonsLayout)

        self.allTests = QRadioButton("Run All Calibration Procedures")
        self.allTests.setChecked(True)
        self.procedureButtonsLayout.addWidget(self.allTests)

        self.initialization = QRadioButton("Initialization")
        self.initialization.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.initialization)

        self.procedureLayout.addStretch(1)

        self.buttonSpacer = QSpacerItem(0, 100)
        self.contentLayout.addItem(self.buttonSpacer)

        self.confirmbutton = QPushButton("Begin")
        self.confirmbutton.setFixedWidth(100)
        self.confirmbutton.setFixedHeight(100)
        self.confirmbutton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.confirmbutton.clicked.connect(self.confirmButtonClicked)

        self.contentLayout.addWidget(self.confirmbutton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bottomSpacer = QSpacerItem(0, 100)
        self.flukeLayout.addItem(self.bottomSpacer)

        self.setLayout(self.flukeLayout)

    def confirmButtonClicked(self):
        try:

            if self.allTests.isChecked():
                self.allTests = True
                self.frontJacks = FrontJacks()
                self.frontJacks.show()

            if self.initialization.isChecked():
                self.frontJacks = FrontJacks()
                self.frontJacks.show()

        except Exception as e:
            print(f"Error: {e}")

    def PostCalibration(self, serial, a, b, c, date):
        payload = {
            # Design payload for updated calibration where necessary.
            # Create SQL table
            # Create API endpoint
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


class FrontJacks(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Front Jack Selection"
        self.setFixedSize(400, 300)

        self.contentLayout = QVBoxLayout()

        self.promptLabel = QLabel("Ensure that all input jacks remain disconnected from external sources.")
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.actionLabel = QLabel("Set unit to use front jacks by depressing the Front switch on the Fluke 8840A.")
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = FlukePerformance()
    window.show()
    sys.exit(app.exec())