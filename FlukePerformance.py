import sys
import time
from datetime import datetime

import pyvisa
from PyQt6.QtCore import pyqtSignal, Qt, QObject, pyqtSlot, QElapsedTimer, QTimer
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSpacerItem, QLineEdit, QRadioButton, QSizePolicy, QDialog, QProgressBar, QStyleFactory

import requests

USE_INSTRUMENT = False

if USE_INSTRUMENT:
    rm = pyvisa.ResourceManager()

    my_instrument = rm.open_resource('GPIB0::1::INSTR')
    serial = my_instrument.query('G3')
    run = {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "serial": serial,
    }

API_URL = "http://100.125.162.5:8000/readings"

class FlukePerformance(QDialog):
    def __init__(self):
        super().__init__()

        columns = [
            "date",
            "serial",
            "diagnostics",
            "test1",
            "test2",
        ]

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


        self.procedureLabel = QLabel("Performance Verification Procedures")
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


        self.allTests = QRadioButton("Run All Performance Verification Tests")
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
                self.frontJacks.exec()


            if self.initialization.isChecked():
                self.frontJacks = FrontJacks()
                self.frontJacks.exec()

        except Exception as e:
            print(f"Error: {e}")

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



class FrontJacks(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Front Jack Selection"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Ensure that all input jacks remain disconnected from external sources.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Set unit to use front jacks by depressing the Front switch on the Fluke 8840A.")
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
        self.close()
        self.diagnostics = Diagnostics()
        self.diagnostics.exec()


    def BackButtonClicked(self):
        print("Back!")


class Diagnostics(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Self Diagnostics"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Self Diagnostic Tests")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.progressSpacer = QSpacerItem(0, 40)
        self.contentLayout.addItem(self.progressSpacer)

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setFormat("Press begin to start diagnostics.")
        self.progressBar.setStyle(QStyleFactory.create("Fusion"))
        self.contentLayout.addWidget(self.progressBar)

        print(repr(self.progressBar.text()))

        self.diagnosticTestElapsed = QElapsedTimer()
        self.diagnosticTimer = QTimer()
        self.diagnosticTimer.setInterval(100)
        self.diagnosticTimer.timeout.connect(self.UpdateDiagnosticTestProgress)



        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Consult file output for errors and proceed as necessary.")
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

        self.beginButton = QPushButton("Begin")
        self.beginButton.setFixedWidth(75)
        self.beginButton.setFixedHeight(50)
        self.beginButton.setStyleSheet(""
                                          "background-color: rgb(0, 200, 50);"
                                          "color: rgb(255, 255, 255);")
        self.beginButton.clicked.connect(self.BeginButtonClicked)
        self.buttonLayout.addWidget(self.beginButton)

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

    def BeginButtonClicked(self):
        if USE_INSTRUMENT:
            my_instrument.write("Z0")
        self.StartDiagnosticTestProgress()

    def BackButtonClicked(self):
        print("Back!")

    def StartDiagnosticTestProgress(self):
        self.diagnosticsStarted = True
        self.progressBar.setFormat("Self Diagnostics Test Running...")
        self.progressBar.setValue(0)
        self.diagnosticTestElapsed.start()
        self.diagnosticTimer.start()

    def UpdateDiagnosticTestProgress(self):
        percent = self.diagnosticTestElapsed.elapsed() * 100 // 25_000
        self.progressBar.setValue(percent)
        if self.progressBar.value() == 100:
            self.FinishDiagnosticTestProgress()

    def FinishDiagnosticTestProgress(self):
        print("Here")
        if USE_INSTRUMENT:
            my_instrument.write("G7")
            run["diagnostics"] = my_instrument.read().strip()
            status = my_instrument.read().strip()


            if status == "1000":
                print("Fluke 8840A Passed all Diagnostic Tests")
            else:
                print(f"Fluke 8840A returned {status}. Consult provided reference in utilities for error code.")

        self.diagnosticTimer.stop()
        self.progressBar.setValue(100)
        self.progressBar.setFormat("Self Diagnostics Test Complete!")

        time.sleep(3)
        self.close()

class DCVoltageVerification(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Short the HI and LO jacks of the Fluke 8840A with provided cable.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Proceed by selecting 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

#--------------------------------------------------- Shorted 200 mv range

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.dc_1_reading = float(my_instrument.read().strip())

            run["dc_200mv_short_slow_v"] = self.dc_1_reading
            if -3e-6 <= self.dc_1_reading <= 3e-6:
                run["dc_200mv_short_slow_v_result"] = "PASS"
            else:
                run["dc_200mv_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.dc_1_reading = float(my_instrument.read().strip())

            run["dc_200mv_short_medium_v"] = self.dc_1_reading
            if -5e6 <= self.dc_1_reading <= 5e-6:
                run["dc_200mv_short_medium_v_result"] = "PASS"
            else:
                run["dc_200mv_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R1D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.dc_1_reading = float(my_instrument.read().strip())

            run["dc_200mv_short_fast_v"] = self.dc_1_reading
            if -3e-6 <= self.dc_1_reading <= 3e-6:
                run["dc_200mv_short_fast_v_result"] = "PASS"
            else:
                run["dc_200mv_short_fast_v_result"] = "FAIL"

#-------------------------------------------------------- Shorted 2 V range

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            self.dc_2_reading = float(my_instrument.read().strip())

            run["dc_2v_short_slow_v"] = self.dc_2_reading
            if -30e-6 <= self.dc_2_reading <= 30e-6:
                run["dc_2v_short_slow_v_result"] = "PASS"
            else:
                run["dc_2v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R2S1T0Y0B0?")
            self.dc_2_reading = float(my_instrument.read().strip())

            run["dc_2v_short_medium_v"] = self.dc_2_reading
            if -50e-6 <= self.dc_2_reading <= 50e-6:
                run["dc_2v_short_medium_v_result"] = "PASS"
            else:
                run["dc_2v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R2D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("D0?")

            self.dc_2_reading = float(my_instrument.read().strip())

            run["dc_2v_short_fast_v"] = self.dc_2_reading
            if -200e-6 <= self.dc_2_reading <= 200e-6:
                run["dc_2v_short_fast_v_result"] = "PASS"
            else:
                run["dc_2v_short_fast_v_result"] = "FAIL"

#-------------------------------------------------------- Shorted 20 V range

            my_instrument.write("F1R3S0T0Y0B0?")
            my_instrument.read()
            self.dc_3_reading = float(my_instrument.read().strip())

            run["dc_20v_short_slow_v"] = self.dc_3_reading
            if -3e-4 <= self.dc_3_reading <= 3e-4:
                run["dc_20v_short_slow_v_result"] = "PASS"
            else:
                run["dc_20v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R3S1T0Y0B0?")
            self.dc_3_reading = float(my_instrument.read().strip())

            run["dc_20v_short_medium_v"] = self.dc_3_reading
            if -5e-4 <= self.dc_2_reading <= 5e-4:
                run["dc_20v_short_medium_v_result"] = "PASS"
            else:
                run["dc_20v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R3D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("D0?")

            self.dc_3_reading = float(my_instrument.read().strip())

            run["dc_20v_short_fast_v"] = self.dc_3_reading
            if -2e-3 <= self.dc_3_reading <= 2e-3:
                run["dc_20v_short_fast_v_result"] = "PASS"
            else:
                run["dc_20v_short_fast_v_result"] = "FAIL"

#-------------------------------------------------------- Shorted 200 V range

            my_instrument.write("F1R4S0T0Y0B0?")
            my_instrument.read()
            self.dc_4_reading = float(my_instrument.read().strip())

            run["dc_200v_short_slow_v"] = self.dc_4_reading
            if -3e-3 <= self.dc_3_reading <= 3e-3:
                run["dc_200v_short_slow_v_result"] = "PASS"
            else:
                run["dc_200v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R4S1T0Y0B0?")
            self.dc_4_reading = float(my_instrument.read().strip())

            run["dc_200v_short_medium_v"] = self.dc_4_reading
            if -5e-3 <= self.dc_4_reading <= 5e-3:
                run["dc_200v_short_medium_v_result"] = "PASS"
            else:
                run["dc_200v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R4D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("D0?")

            self.dc_4_reading = float(my_instrument.read().strip())

            run["dc_200v_short_fast_v"] = self.dc_4_reading
            if -2e-2 <= self.dc_4_reading <= 2e-2:
                run["dc_200v_short_fast_v_result"] = "PASS"
            else:
                run["dc_200v_short_fast_v_result"] = "FAIL"

#-------------------------------------------------------- Shorted 1000 V range

            my_instrument.write("F1R5S0T0Y0B0?")
            my_instrument.read()
            self.dc_5_reading = float(my_instrument.read().strip())

            run["dc_1000v_short_slow_v"] = self.dc_5_reading
            if -3e-2 <= self.dc_3_reading <= 3e-2:
                run["dc_1000v_short_slow_v_result"] = "PASS"
            else:
                run["dc_1000v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R5S1T0Y0B0?")
            self.dc_5_reading = float(my_instrument.read().strip())

            run["dc_1000v_short_medium_v"] = self.dc_5_reading
            if -5e-2 <= self.dc_5_reading <= 5e-2:
                run["dc_1000v_short_medium_v_result"] = "PASS"
            else:
                run["dc_1000v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R5D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("D0?")

            self.dc_5_reading = float(my_instrument.read().strip())

            run["dc_1000v_short_fast_v"] = self.dc_5_reading
            if -2e-1 <= self.dc_5_reading <= 2e-1:
                run["dc_1000v_short_fast_v_result"] = "PASS"
            else:
                run["dc_1000v_short_fast_v_result"] = "FAIL"


            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.mVDC100 = mVDC100()
            self.mVDC100.exec()


class mVDC100(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 mV DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect the HI and LO jacks of the calibrator output and Fluke 8840A input.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Supply Fluke 8840A with +100mV DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["mvdc_100mv_short_slow_v"] = self.mvdc_1_reading
            if 0.099989 <= self.mvdc_1_reading <= 0.100011:
                run["mvdc_100mv_short_slow_v_result"] = "PASS"
            else:
                run["mvdc_100mv_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["mvdc_100mv_short_medium_v"] = self.mvdc_1_reading
            if 0.099987 <= self.mvdc_1_reading <= 0.100013:
                run["mvdc_100mv_short_medium_v_result"] = "PASS"
            else:
                run["mvdc_100mv_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R1D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["mvdc_100mv_short_fast_v"] = self.mvdc_1_reading
            if 0.099970 <= self.mvdc_1_reading <= 0.100030:
                run["mvdc_100mv_short_fast_v_result"] = "PASS"
            else:
                run["mvdc_100mv_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.OneVDC100 = OneVDC100()
            OneVDC100.exec()

class OneVDC100(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "+1V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +1 V DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_1_reading = float(my_instrument.read().strip())

            run["vdc_1v_short_slow_v"] = self.vdc_1_reading
            if 0.99993 <= self.vdc_1_reading <= 1.00007:
                run["vdc_1v_short_slow_v_result"] = "PASS"
            else:
                run["vdc_1v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R2S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_1_reading = float(my_instrument.read().strip())

            run["vdc_1v_short_medium_v"] = self.vdc_1_reading
            if 0.99991 <= self.vdc_1_reading <= 1.00009:
                run["vdc_1v_short_medium_v_result"] = "PASS"
            else:
                run["vdc_1v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R2D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.vdc_1_reading = float(my_instrument.read().strip())

            run["vdc_1v_short_fast_v"] = self.vdc_1_reading
            if 0.9997 <= self.vdc_1_reading <= 1.0003:
                run["vdc_1v_short_fast_v_result"] = "PASS"
            else:
                run["vdc_1v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.tenVDC = TenVDC100()
            self.tenVDC.exec()


class TenVDC100(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "+10V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +10 V DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R3S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_10_reading = float(my_instrument.read().strip())

            run["vdc_10v_short_slow_v"] = self.vdc_10_reading
            if 9.9992 <= self.vdc_10_reading <= 10.0008:
                run["vdc_10v_short_slow_v_result"] = "PASS"
            else:
                run["vdc_10v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R3S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_10_reading = float(my_instrument.read().strip())

            run["vdc_10v_short_medium_v"] = self.vdc_10_reading
            if 9.9990 <= self.vdc_10_reading <= 10.0010:
                run["vdc_10v_short_medium_v_result"] = "PASS"
            else:
                run["vdc_10v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R3D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.vdc_10_reading = float(my_instrument.read().strip())

            run["vdc_10v_short_fast_v"] = self.vdc_10_reading
            if 9.997 <= self.vdc_10_reading <= 1.003:
                run["vdc_10v_short_fast_v_result"] = "PASS"
            else:
                run["vdc_10v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R3S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.hundredVDC = HundredVDC()
            self.hundredVDC.exec()

class HundredVDC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "+100V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +100 V DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R4S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_100_reading = float(my_instrument.read().strip())

            run["vdc_100v_short_slow_v"] = self.vdc_100_reading
            if 99.992 <= self.vdc_100_reading <= 100.008:
                run["vdc_100v_short_slow_v_result"] = "PASS"
            else:
                run["vdc_100v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R4S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_100_reading = float(my_instrument.read().strip())

            run["vdc_100v_short_medium_v"] = self.vdc_100_reading
            if 99.990 <= self.vdc_100_reading <= 100.010:
                run["vdc_100v_short_medium_v_result"] = "PASS"
            else:
                run["vdc_100v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R4D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.vdc_100_reading = float(my_instrument.read().strip())

            run["vdc_100v_short_fast_v"] = self.vdc_100_reading
            if 99.97 <= self.vdc_100_reading <= 100.03:
                run["vdc_100v_short_fast_v_result"] = "PASS"
            else:
                run["vdc_100v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R4S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.thousandVDC = ThousandVDC()
            self.thousandVDC.exec()

class ThousandVDC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "+1000V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +1000 VDC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R5S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_1000_reading = float(my_instrument.read().strip())

            run["vdc_1000v_short_slow_v"] = self.vdc_1000_reading
            if 999.92 <= self.vdc_1000_reading <= 1000.08:
                run["vdc_1000v_short_slow_v_result"] = "PASS"
            else:
                run["vdc_1000v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R5S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_1000_reading = float(my_instrument.read().strip())

            run["vdc_1000v_short_medium_v"] = self.vdc_1000_reading
            if 999.90 <= self.vdc_1000_reading <= 1000.10:
                run["vdc_1000v_short_medium_v_result"] = "PASS"
            else:
                run["vdc_1000v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R5D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.vdc_1000_reading = float(my_instrument.read().strip())

            run["vdc_1000v_short_fast_v"] = self.vdc_1000_reading
            if 999.7 <= self.vdc_1000_reading <= 1000.3:
                run["vdc_1000v_short_fast_v_result"] = "PASS"
            else:
                run["vdc_1000v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R5S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.negmVDC = NegmVDC100()
            self.negmVDC.exec()


class NegmVDC100(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "-100 mV DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -100mV DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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
            #----------------- Somewhere in the future.. Someone will be like....
            #..... Why in the f*#@ is the first one different than  the rest....
            #...... And All I can tell you... is.... well.......
            #... I was lazy on this day... And.. You should be lazy today as well..
            #... Catch a breath...
            #....... Unless the world is overrun by cyborgs....
            #.... In that case?
            #.................... God speed.....................................

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["negmvdc_100mv_short_slow_v"] = self.negmvdc_1_reading
            if -0.100011 <= self.negmvdc_1_reading <= -0.099989:
                run["negmvdc_100mv_short_slow_v_result"] = "PASS"
            else:
                run["negmvdc_100mv_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.negmvdc_1_reading = float(my_instrument.read().strip())

            run["negmvdc_100mv_short_medium_v"] = self.negmvdc_1_reading
            if -0.100013 <= self.negmvdc_1_reading <= -0.099987:
                run["negmvdc_100mv_short_medium_v_result"] = "PASS"
            else:
                run["negmvdc_100mv_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R1D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.negmvdc_1_reading = float(my_instrument.read().strip())

            run["negmvdc_100mv_short_fast_v"] = self.negmvdc_1_reading
            if -0.100030 <= self.negmvdc_1_reading <= -0.099970:
                run["negmvdc_100mv_short_fast_v_result"] = "PASS"
            else:
                run["negmvdc_100mv_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.negOneVDC100 = NegOneVDC100()
            self.negOneVDC100.exec()

class NegOneVDC100(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "-1V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -1 V DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_1_reading = float(my_instrument.read().strip())

            run["negvdc_1v_short_slow_v"] = self.negvdc_1_reading
            if -0.99993 >= self.negvdc_1_reading >= -1.00007:
                run["negvdc_1v_short_slow_v_result"] = "PASS"
            else:
                run["negvdc_1v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R2S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.negvdc_1_reading = float(my_instrument.read().strip())

            run["negvdc_1v_short_medium_v"] = self.negvdc_1_reading
            if -0.99991 >= self.negvdc_1_reading >= -1.00009:
                run["negvdc_1v_short_medium_v_result"] = "PASS"
            else:
                run["negvdc_1v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R2D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.negvdc_1_reading = float(my_instrument.read().strip())

            run["negvdc_1v_short_fast_v"] = self.negvdc_1_reading
            if -0.9997 >= self.negvdc_1_reading >= -1.0003:
                run["negvdc_1v_short_fast_v_result"] = "PASS"
            else:
                run["negvdc_1v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.negTenVDC = NegTenVDC100()
            self.negTenVDC.exec()


class NegTenVDC100(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "-10V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -10 V DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R3S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_10_reading = float(my_instrument.read().strip())

            run["negvdc_10v_short_slow_v"] = self.negvdc_10_reading
            if -9.9992 >= self.negvdc_10_reading >= -10.0008:
                run["negvdc_10v_short_slow_v_result"] = "PASS"
            else:
                run["negvdc_10v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R3S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.negvdc_10_reading = float(my_instrument.read().strip())

            run["negvdc_10v_short_medium_v"] = self.negvdc_10_reading
            if -9.9990 >= self.negvdc_10_reading >= -10.0010:
                run["negvdc_10v_short_medium_v_result"] = "PASS"
            else:
                run["negvdc_10v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R3D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.negvdc_10_reading = float(my_instrument.read().strip())

            run["negvdc_10v_short_fast_v"] = self.negvdc_10_reading
            if -9.997 >= self.negvdc_10_reading >= -1.003:
                run["negvdc_10v_short_fast_v_result"] = "PASS"
            else:
                run["negvdc_10v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R3S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.negHundredVDC = NegHundredVDC()
            self.negHundredVDC.exec()

class NegHundredVDC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "-100V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -100 V DC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R4S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.vdc_100_reading = float(my_instrument.read().strip())

            run["negvdc_100v_short_slow_v"] = self.negvdc_100_reading
            if -99.992 >= self.negvdc_100_reading >= -100.008:
                run["negvdc_100v_short_slow_v_result"] = "PASS"
            else:
                run["negvdc_100v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R4S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.negvdc_100_reading = float(my_instrument.read().strip())

            run["negvdc_100v_short_medium_v"] = self.negvdc_100_reading
            if -99.990 >= self.negvdc_100_reading >= -100.010:
                run["negvdc_100v_short_medium_v_result"] = "PASS"
            else:
                run["negvdc_100v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R4D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.negvdc_100_reading = float(my_instrument.read().strip())

            run["negvdc_100v_short_fast_v"] = self.negvdc_100_reading
            if -99.97 >= self.negvdc_100_reading >= -100.03:
                run["negvdc_100v_short_fast_v_result"] = "PASS"
            else:
                run["negvdc_100v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R4S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.negThousandVDC = NegThousandVDC()
            self.negThousandVDC.exec()

class NegThousandVDC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "-1000V DC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -1000 VDC output from provided calibrator.\n"
                                  "After enabling output, select 'Measure' to collect data.")
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

        self.measureButton = QPushButton("Measure")
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

            my_instrument.write("F1R5S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.negvdc_1000_reading = float(my_instrument.read().strip())

            run["negvdc_1000v_short_slow_v"] = self.negvdc_1000_reading
            if -999.92 >= self.negvdc_1000_reading >= -1000.08:
                run["negvdc_1000v_short_slow_v_result"] = "PASS"
            else:
                run["negvdc_1000v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R5S1T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            self.negvdc_1000_reading = float(my_instrument.read().strip())

            run["negvdc_1000v_short_medium_v"] = self.negvdc_1000_reading
            if -999.90 >= self.negvdc_1000_reading >= -1000.10:
                run["negvdc_1000v_short_medium_v_result"] = "PASS"
            else:
                run["negvdc_1000v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R5D1S2T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.negvdc_1000_reading = float(my_instrument.read().strip())

            run["negvdc_1000v_short_fast_v"] = self.negvdc_1000_reading
            if -999.7 <= self.negvdc_1000_reading <= -1000.3:
                run["negvdc_1000v_short_fast_v_result"] = "PASS"
            else:
                run["negvdc_1000v_short_fast_v_result"] = "FAIL"

            my_instrument.write("F1R5S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.hundredVDC = HundredVDC()
            self.hundredVDC.exec()





if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FlukePerformance()
    window.show()
    sys.exit(app.exec())