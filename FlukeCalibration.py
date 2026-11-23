import sys
from datetime import datetime
import time

import pyvisa
from PyQt6.QtCore import pyqtSignal, Qt, QObject, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSpacerItem, QLineEdit, QRadioButton, QSizePolicy, QDialog

import requests

USE_INSTRUMENT = True

allTests = False
adCalibration = False
dcCalibration = False
acCalibration = False
twoWire = False
fourWire = False
dcCurrent = False
acCurrent = False

if USE_INSTRUMENT:
    rm = pyvisa.ResourceManager()

    my_instrument = rm.open_resource('GPIB0::1::INSTR')
    serial = my_instrument.query('G3')
    run = {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "serial": serial,
    }
    print(run["date"])
    print(run["serial"])

API_URL = "http://100.125.162.5:8000/readings"


class FlukeCalibration(QDialog):
    def __init__(self):
        super().__init__()



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

        self.adCalibration = QRadioButton("A/D Calibration")
        self.adCalibration.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.adCalibration)

        self.dcCalibration = QRadioButton("DC Voltage Calibration")
        self.dcCalibration.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.dcCalibration)

        self.acCalibration = QRadioButton("AC Voltage Calibration")
        self.acCalibration.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.acCalibration)

        self.twoWire = QRadioButton("Two Wire Resistance Calibration")
        self.twoWire.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.twoWire)

        self.fourWire = QRadioButton("Four Wire Resistance Calibration")
        self.fourWire.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.fourWire)

        self.dcCurrent = QRadioButton("DC Current Calibration")
        self.dcCurrent.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.dcCurrent)

        self.acCurrent = QRadioButton("AC Current Calibration")
        self.acCurrent.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.acCurrent)

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
                global allTests
                allTests = True
                self.initialization = Initialization()
                self.initialization.exec()

            if self.adCalibration.isChecked():
                global adCalibration
                adCalibration = True
                self.adCalibration = Initialization()
                self.adCalibration.exec()

            if self.dcCalibration.isChecked():
                global dcCalibration
                dcCalibration = True
                self.dcCalibration = Initialization()
                self.dcCalibration.exec()

            if self.acCalibration.isChecked():
                global acCalibration
                acCalibration = True
                self.acCalibration = Initialization()
                self.acCalibration.exec()

            if self.twoWire.isChecked():
                global twoWire
                twoWire = True
                self.twoWire = Initialization()
                self.twoWire.exec()

            if self.fourWire.isChecked():
                global fourWire
                fourWire = True
                self.fourWire = Initialization()
                self.fourWire.exec()

            if self.dcCurrent.isChecked():
                global dcCurrent
                dcCurrent = True
                self.dcCurrent = Initialization()
                self.dcCurrent.exec()

            if self.acCurrent.isChecked():
                global acCurrent
                acCurrent = True
                self.acCurrent = Initialization()
                self.acCurrent.exec()




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


class Initialization(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Initialize Calibration"
        self.setFixedSize(400, 300)

        self.contentLayout = QVBoxLayout()

        self.actionLabel = QLabel("To begin calibration procedures, depress the Cal Enable switch.")
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.continueButton = QPushButton("Continue")
        self.continueButton.setFixedWidth(75)
        self.continueButton.setFixedHeight(50)
        self.continueButton.setStyleSheet(""
                                          "background-color: rgb(0, 200, 50);"
                                          "color: rgb(255, 255, 255);")
        self.continueButton.clicked.connect(self.ContinueButtonClicked)
        self.buttonLayout.addWidget(self.continueButton)

        self.backButton = QPushButton("Back")
        self.backButton.setFixedWidth(75)
        self.backButton.setFixedHeight(50)
        self.backButton.setStyleSheet(""
                                      "background-color: rgb(200, 0, 50);"
                                      "color: rgb(255, 255, 255);")
        self.backButton.clicked.connect(self.BackButtonClicked)
        self.buttonLayout.addWidget(self.backButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def ContinueButtonClicked(self):
        try:
            self.close()
            print(f"alltests?: {allTests}")
            print(f"adCalibration?: {adCalibration}")
            print(f"dcCalibration?: {dcCalibration}")
            print(f"acCalibration?: {acCalibration}")
            print(f"twoWire?: {twoWire}")
            print(f"fourWire?: {fourWire}")
            print(f"dcCurrent?: {dcCurrent}")
            print(f"acCurrent?: {acCurrent}")

            if allTests:
                self.adCalibration = ADCalibration()
                self.adCalibration.exec()
            if adCalibration:
                self.adCalibration = ADCalibration()
                self.adCalibration.exec()
            if dcCalibration:
                self.dcCalibration = DCCalibration()
                self.dcCalibration.exec()
            if acCalibration:
                self.acCalibration = ACCalibration()
                self.acCalibration.exec()
            if twoWire:
                self.twoWire = TwoWire()
                self.twoWire.exec()
            if fourWire:
                self.fourWire = FourWire()
                self.fourWire.exec()
            if dcCurrent:
                self.dcCurrent = DCCurrent()
                self.dcCurrent.exec()
            if acCurrent:
                self.acCurrent = ACCurrent()
                self.acCurrent.exec()
        except Exception as e:
            print(f"error: {e}")


    def BackButtonClicked(self):
        print("Back!")

class ADCalibration(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Short the HI and LO jacks of the Fluke 8840A.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested 0 V input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range
            try:

                my_instrument.write("C0")
                time.sleep(8)
                self.calStatus = my_instrument.query("G2")
                print(float(self.calStatus))


                if float(self.calStatus) == -0.03:
                    print("Yup.")
                    self.close()
                    self.neg03 = Neg03()
                    self.neg03.exec()

                else:
                    self.close()
                    self.error = Error()
#                   self.error.exec()
            except Exception as e:
                print(f"error: {e}")

class Neg03(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -0.03 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == -1.01:
                self.close()
                self.neg101 = Neg101()
                self.neg101.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class Neg101(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -1.01 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.99:
                self.close()
                self.nine9 = Nine9()
                self.nine9.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class Nine9(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.99 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.51:
                self.close()
                self.five1 = Five1()
                self.five1.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class Five1(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.51 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == -0.51:
                self.close()
                self.negFive1 = NegFive1()
                self.negFive1.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class NegFive1(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -0.51 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == -0.26:
                self.close()
                self.negTwo6 = NegTwo6()
                self.negTwo6.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class NegTwo6(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -0.26 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.26:
                self.close()
                self.two6 = Two6()
                self.two6.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class Two6(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.26 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.135:
                self.close()
                self.one35 = One35()
                self.one35.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class One35(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.135 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == -0.135:
                self.close()
                self.negOne35 = NegOne35()
                self.negOne35.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class NegOne35(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -0.135 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == -0.0725:
                self.close()
                self.negSeven25 = NegSeven25()
                self.negSeven25.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class NegSeven25(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -0.0725 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.0725:
                self.close()
                self.seven25 = Seven25()
                self.seven25.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class Seven25(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "A/D Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with -0.0725 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input to the A/D.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(8)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.0725:
                self.close()
                if allTests:
                    self.dcCalibration = DCCalibration()
                    self.dcCalibration.exec()
                else:
                    self.complete = Complete()
                    self.complete.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class DCCalibration(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect HI and LO input jacks of the Fluke 8840A to the provided calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Press continue to begin DC Voltage Calibration procedures.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Continue")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("F1")

            self.close()
            self.dc0 = DC0()
            self.dc0.exec()



class DC0(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.0 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.019:
                self.close()
                if allTests:
                    self.hundred90MV = DCHundred90MV()
                    self.gundred90MV.exec()
                elif dcCalibration:
                    self.hundred90MV = DCHundred90MV()
                    self.gundred90MV.exec()
                else:
                    self.complete = Complete()
                    self.complete.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class DCHundred90MV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.19 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.19:
                self.close()
                if allTests:
                    self.dcOne9 = DCOne9V()
                    self.dcOne9.exec()
                elif dcCalibration:
                    self.dcOne9 = DCOne9V()
                    self.dcOne9.exec()
                else:
                    self.complete = Complete()
                    self.complete.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class DCOne9V(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +1.9 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)



    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.19:
                self.close()
                if allTests:
                    self.nineteenV = DCNineteenV()
                    self.nineteenV.exec()
                elif dcCalibration:
                    self.nineteenV = DCNineteenV()
                    self.nineteenV.exec()
                else:
                    self.complete = Complete()
                    self.complete.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class DCNineteenV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +19.0 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.19:
                self.close()
                if allTests:
                    self.hundred90V = Hundred90V()
                    self.hundred90V.exec()
                elif dcCalibration:
                    self.hundred90V = Hundred90V()
                    self.hundred90V.exec()
                else:
                    self.complete = Complete()
                    self.complete.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class Hundred90V(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +190.0 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)




    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.19:
                self.close()
                if allTests:
                    self.thousandV = ThousandV()
                    self.thousandV.exec()
                elif dcCalibration:
                    self.thousandV = ThousandV()
                    self.thousandV.exec()
                else:
                    self.complete = Complete()
                    self.complete.exec()

            else:
                self.close()
                self.error = Error()
                self.error.exec()

class ThousandV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +1000.0 V DC.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)




    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.19:
                self.close()
                if allTests:
                    self.acCalibration = ACCalibration()
                    self.acCalibration.exec()
                elif dcCalibration:
                    self.complete = Complete()
                    self.complete.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()


class ACCalibration(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect HI and LO input jacks of the Fluke 8840A to the provided calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Press continue to begin AC Voltage Calibration procedures.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Continue")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("F2")

            self.close()
            self.zero1V = Zero1V()
            self.zero1V.exec()

        else:
            self.close()
            self.error = Error()
            self.error.exec()

class Zero1V(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.01 V AC at 1 kHz.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 0.1:
                self.close()
                if allTests:
                    self.achundredMV = ACHundredMV()
                    self.achundredMV.exec()
                elif acCalibration:
                    self.aconeV = ACHundredMV()
                    self.aconeV.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class ACHundredMV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +0.1 V AC at 1 kHz.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 1.0:
                self.close()
                if allTests:
                    self.acOneV = ACOneV()
                    self.acOneV.exec()
                elif acCalibration:
                    self.acOneV = ACOneV()
                    self.acOneV.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class ACOneV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +1.0 V AC at 1 kHz.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 10.0:
                self.close()
                if allTests:
                    self.acTenV = ACTenV()
                    self.acTenV.exec()
                elif acCalibration:
                    self.complete = Complete()
                    self.complete.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class ACTenV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +10.0 V AC at 1 kHz.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 100.0:
                self.close()
                if allTests:
                    self.acHundredV = ACHundredV()
                    self.acHundredV.exec()
                elif acCalibration:
                    self.acHundredV = ACHundredV()
                    self.acHundredV.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class ACHundredV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +100.0 V AC at 1 kHz.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)
            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 500.0:
                self.close()
                if allTests:
                    self.acFiveHundredV = ACFiveHundredV()
                    self.acFiveHundredV.exec()
                elif acCalibration:
                    self.acFiveHundredV = ACFiveHundredV()
                    self.acFiveHundredV.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class ACFiveHundredV(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Voltage Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Supply the Fluke 8840A Hi and Lo inputs with +500.0 V AC at 1 kHz.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)


    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)


            if allTests:
                self.twoWire = TwoWire()
                self.twoWire.exec()
            elif acCalibration:
                self.complete = Complete()
                self.complete.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()


class TwoWire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect HI and LO input jacks of the Fluke 8840A to the provided calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Press continue to begin the Two Wire Resistance Calibration procedures.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Continue")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("F3")

            self.close()
            self.twoWireZero = TwoWireZero()
            self.twoWireZero.exec()


class TwoWireZero(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Short the HI and LO Jacks of the Fluke 8840A.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 100:
                if allTests:
                    self.close()
                    self.twoWireHundred = TwoWireHundred()
                    self.twoWireHundred.exec()
                elif twoWire:
                    self.close()
                    self.twoWireHundred = TwoWireHundred()
                    self.twoWireHundred.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class TwoWireHundred(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect the HI and LO Jacks of the Fluke 8840A to the provided Calibrator\n"
                                  "and supply it with 100 ohms of resistance.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 1000:
                if allTests:
                    self.close()
                    self.twoWireThousand = TwoWireThousand()
                    self.twoWireThousand.exec()
                elif twoWire:
                    self.close()
                    self.twoWireThousand = TwoWireThousand()
                    self.twoWireThousand.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class TwoWireThousand(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 1000 ohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 10000:
                if allTests:
                    self.close()
                    self.twoWireTenK = TwoWireTenK()
                    self.twoWireTenK.exec()
                elif twoWire:
                    self.close()
                    self.twoWireTenK = TwoWireTenK()
                    self.twoWireTenK.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class TwoWireTenK(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 10 Kohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 100000:
                if allTests:
                    self.close()
                    self.twoWireHundredK = TwoWireHundredK()
                    self.twoWireHundredK.exec()
                elif twoWire:
                    self.close()
                    self.twoWireHundredK = TwoWireHundredK()
                    self.twoWireHundredK.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()


class TwoWireHundredK(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 100 Kohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 1000000:
                if allTests:
                    self.close()
                    self.twoWireMega = TwoWireMega()
                    self.twoWireMega.exec()
                elif twoWire:
                    self.close()
                    self.twoWireMega = TwoWireMega()
                    self.twoWireMega.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class TwoWireMega(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 1 Mohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 10000000:
                if allTests:
                    self.close()
                    self.twoWireTenMega = TwoWireTenMega()
                    self.twoWireMega.exec()
                elif twoWire:
                    self.close()
                    self.twoWireTenMega = TwoWireTenMega()
                    self.twoWireTenMega.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class TwoWireTenMega(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Two Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 10 Mohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            if allTests:
                self.close()
                self.fourWire = FourWire()
                self.fourWire.exec()
            elif twoWire:
                print("here")
                self.close()
                self.complete = Complete()
                self.complete.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()



class FourWire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Short the HI and LO input jacks to the HI and LO Sense jacks of the Fluke 8840A\n"
                                  "Connect these to the provided calibrator."
                                 )
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Press continue to begin Four Wire Resistance Calibration procedures.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Continue")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("F4")

            self.close()
            self.fourWireZero = FourWireZero()
            self.fourWireZero.exec()

        else:
            self.close()
            self.error = Error()
            self.error.exec()


class FourWireZero(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Short the HI and LO Jacks of the Fluke 8840A.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(40)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 10:
                if allTests:
                    self.close()
                    self.fourWireTen = FourWireTen()
                    self.fourWireTen.exec()
                elif fourWire:
                    self.close()
                    self.fourWireTen = FourWireTen()
                    self.fourWireTen.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class FourWireTen(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect the HI and LO Jacks of the Fluke 8840A to the provided Calibrator\n"
                                  "and supply it with 10 ohms of resistance.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 100:
                if allTests:
                    self.close()
                    self.fourWireHundred = FourWireHundred()
                    self.fourWireHundred.exec()
                elif fourWire:
                    self.close()
                    self.fourWireHundred = FourWireHundred()
                    self.fourWireHundred.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class FourWireHundred(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 100 ohms of resistance with the provided Calibrator")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 1000:
                if allTests:
                    self.close()
                    self.fourWireThousand = FourWireThousand()
                    self.fourWireThousand.exec()
                elif fourWire:
                    self.close()
                    self.fourWireThousand = FourWireThousand()
                    self.fourWireThousand.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class FourWireThousand(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 1000 ohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 10000:
                if allTests:
                    self.close()
                    self.fourWireTenK = FourWireTenK()
                    self.fourWireTenK.exec()
                elif fourWire:
                    self.close()
                    self.fourWireTenK = FourWireTenK()
                    self.fourWireTenK.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class FourWireTenK(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 10 Kohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 100000:
                if allTests:
                    self.close()
                    self.fourWireHundredK = FourWireHundredK()
                    self.fourWireHundredK.exec()
                elif fourWire:
                    self.close()
                    self.fourWireHundredK = FourWireHundredK()
                    self.fourWireHundredK.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()


class FourWireHundredK(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 100 Kohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 1000000:
                if allTests:
                    self.close()
                    self.fourWireMega = FourWireMega()
                    self.fourWireMega.exec()
                elif fourWire:
                    self.close()
                    self.fourWireMega = FourWireMega()
                    self.fourWireMega.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class FourWireMega(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 1 Mohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            self.calStatus = my_instrument.query("G2")
            print(float(self.calStatus))

            if float(self.calStatus) == 10000000:
                if allTests:
                    self.close()
                    self.fourWireTenMega = FourWireTenMega()
                    self.fourWireTenMega.exec()
                elif fourWire:
                    self.close()
                    self.twoWireTenMega = FourWireTenMega()
                    self.twoWireTenMega.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class FourWireTenMega(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Four Wire Resistance Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Supply the Fluke 8840A with 10 Mohms of resistance from the provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select Store Point to provide requested input.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.measureButton = QPushButton("Store Point")
        self.measureButton.setFixedWidth(75)
        self.measureButton.setFixedHeight(50)
        self.measureButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.measureButton.clicked.connect(self.MeasureButtonClicked)
        self.buttonLayout.addWidget(self.measureButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MeasureButtonClicked(self):
        if USE_INSTRUMENT:

            # --------------------------------------------------- +100 mv range

            my_instrument.write("C0")
            time.sleep(10)

            if allTests:
                self.close()
                self.fourWire = FourWire()
                self.fourWire.exec()
            elif twoWire:
                self.close()
                self.complete = Complete()
                self.complete.exec()
            else:
                self.close()
                self.error = Error()
                self.error.exec()

class DCCurrent(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Current Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect HI and LO input jacks of the Fluke 8840A to the provided calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Press continue to begin DC Current Calibration procedures.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Continue")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("F5")

            my_instrument.write("G2?")
            my_instrument.read()

            self.calStatus = float(my_instrument.read().strip())

            print(float(self.calStatus))
"""
        if self.calStatus == 0.00:
            self.close()
            self.adCalibration = ADCalibration()
            self.adCalibration.exec()

        else:
            self.close()
            self.error = Error()
            self.error.exec()
"""

class ACCurrent(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Current Calibration"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect HI and LO input jacks of the Fluke 8840A to the provided calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Press continue to begin AC Current Calibration procedures.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Continue")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("F6")

            my_instrument.write("G2?")
            my_instrument.read()

            self.calStatus = float(my_instrument.read().strip())

            print(float(self.calStatus))
"""
        if self.calStatus == 0.00:
            self.close()
            self.adCalibration = ADCalibration()
            self.adCalibration.exec()

        else:
            self.close()
            self.error = Error()
            self.error.exec()
"""


class Error(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Error"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Calibration error.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select restart to start A/D Calibration over.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Restart")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def RestartButtonClicked(self):
        if USE_INSTRUMENT:
            # --------------------------------------------------- +100 mv range

            my_instrument.write("C1")

            my_instrument.write("G2?")
            my_instrument.read()

            self.calStatus = float(my_instrument.read().strip())

        if self.calStatus == 0.00:
            self.close()
            self.adCalibration = ADCalibration()
            self.adCalibration.exec()

        else:
            self.close()
            self.error = Error()
            self.error.exec()

class Complete(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Calibrations Complete"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("All selected Calibrations have been completed!")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Select main menu to select a new calibration procedure.")
        self.actionLabel.setStyleSheet("""
                                            font-size: 18px;
                                            font-weight: bold;
                """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)

        self.buttonSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.buttonSpacer)

        self.buttonLayout = QHBoxLayout()
        self.contentLayout.addLayout(self.buttonLayout)

        self.buttonLayout.addStretch(1)

        self.restartButton = QPushButton("Main Menu")
        self.restartButton.setFixedWidth(75)
        self.restartButton.setFixedHeight(50)
        self.restartButton.setStyleSheet(""
                                         "background-color: rgb(0, 200, 50);"
                                         "color: rgb(255, 255, 255);")
        self.restartButton.clicked.connect(self.RestartButtonClicked)
        self.buttonLayout.addWidget(self.restartButton)

        self.buttonLayout.addStretch(1)

        self.contentLayout.addStretch(1)

        self.setLayout(self.contentLayout)

    def MainButtonClicked(self):

        self.close()
        self.home = FlukeCalibration()
        self.home.exec()




if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = FlukeCalibration()
    window.show()
    sys.exit(app.exec())