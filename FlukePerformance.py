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

        self.actionLabel = QLabel("Proceed by selecting 'Measure'.")
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
            if -3e6 <= self.dc_1_reading <= 3e-6:
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
            self.dc_1_reading = float(my_instrument.read().strip())

            run["dc_200mv_short_fast_v"] = self.dc_1_reading
            if -3e6 <= self.dc_1_reading <= 3e-6:
                run["dc_200mv_short_fast_v_result"] = "PASS"
            else:
                run["dc_200mv_short_fast_v_result"] = "FAIL"

#-------------------------------------------------------- Shorted 2 V range

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            self.dc_2_reading = float(my_instrument.read().strip())

            run["dc_2v_short_slow_v"] = self.dc_2_reading
            if -30e6 <= self.dc_2_reading <= 30e-6:
                run["dc_2v_short_slow_v_result"] = "PASS"
            else:
                run["dc_2v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R2S1T0Y0B0?")
            self.dc_2_reading = float(my_instrument.read().strip())

            run["dc_2v_short_medium_v"] = self.dc_2_reading
            if -50e6 <= self.dc_2_reading <= 50e-6:
                run["dc_2v_short_medium_v_result"] = "PASS"
            else:
                run["dc_2v_short_medium_v_result"] = "FAIL"

            my_instrument.write("F1R1D1S2T0Y0B0?")
            my_instrument.read()
            self.dc_2_reading = float(my_instrument.read().strip())

            run["dc_2v_short_fast_v"] = self.dc_2_reading
            if -200e6 <= self.dc_2_reading <= 200e-6:
                run["dc_2v_short_fast_v_result"] = "PASS"
            else:
                run["dc_2v_short_fast_v_result"] = "FAIL"






if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FlukePerformance()
    window.show()
    sys.exit(app.exec())