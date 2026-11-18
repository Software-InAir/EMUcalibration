import sys
import time
from datetime import datetime

import pyvisa
from PyQt6.QtCore import pyqtSignal, Qt, QObject, pyqtSlot, QElapsedTimer, QTimer
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSpacerItem, QLineEdit, QRadioButton, QSizePolicy, QDialog, QProgressBar, QStyleFactory

import requests

USE_INSTRUMENT = True

allTests = False
diagnosticsConfig = False
dcVerificationConfig = False
linearityTestConfig = False
acVerificationConfig = False
resistanceVerificationConfig = False
fourWireConfig = False
twoWireConfig = False
dcCurrentConfig = False
acCurrentConfig = False


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

class FlukePerformance(QDialog):
    def __init__(self):
        super().__init__()

        print(diagnosticsConfig)

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
        self.setFixedSize(1280, 800)

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

        self.diagnostictests = QRadioButton("Self Diagnostic Tests")
        self.diagnostictests.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.diagnostictests)

        self.dcverification = QRadioButton("DC Voltage Verification")
        self.dcverification.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.dcverification)

        self.linearity = QRadioButton("Linearity Check")
        self.linearity.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.linearity)

        self.acverification = QRadioButton("AC Voltage Verification")
        self.acverification.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.acverification)

        self.resistanceverification = QRadioButton("Resistance Verification")
        self.resistanceverification.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.resistanceverification)

        self.fourwire = QRadioButton("4-Wire Resistance")
        self.fourwire.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.fourwire)

        self.twowire = QRadioButton("2-Wire Resistance")
        self.twowire.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.twowire)

        self.dccurrent = QRadioButton("DC Current")
        self.dccurrent.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.dccurrent)

        self.accurrent = QRadioButton("AC Current")
        self.accurrent.setChecked(False)
        self.procedureButtonsLayout.addWidget(self.accurrent)

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

            if self.diagnostictests.isChecked():
                global diagnosticsConfig
                diagnosticsConfig = True
                print(diagnosticsConfig)

            if self.dcverification.isChecked():
                global dcVerificationConfig
                dcVerificationConfig = True

            if self.linearity.isChecked():
                global linearityTestConfig
                linearityTestConfig = True

            if self.acverification.isChecked():
                global acVerificationConfig
                acVerificationConfig = True

            if self.resistanceverification.isChecked():
                global resistanceVerificationConfig
                resistanceVerificationConfig = True

            if self.fourwire.isChecked():
                global fourWireConfig
                fourWireConfig = True

            if self.twowire.isChecked():
                global twoWireConfig
                twoWireConfig = True

            if self.dccurrent.isChecked():
                global dcCurrentConfig
                dcCurrentConfig = True

            if self.accurrent.isChecked():
                try:
                    global acCurrentConfig
                    acCurrentConfig = True
                    print(f"AC Test: {acCurrentConfig}")
                except Exception as e:
                    print(f"error: {e}")

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
        try:
            self.close()
            if allTests:
                self.diagnostics = Diagnostics()
                self.diagnostics.exec()
            if diagnosticsConfig:
                self.diagnostics = Diagnostics()
                self.diagnostics.exec()
            if dcVerificationConfig:
                self.dcVerification = DCVoltageVerification()
                self.dcVerification.exec()
            if linearityTestConfig:
                self.linearity = PointOne()
                self.linearity.exec()
            if acVerificationConfig:
                self.acVerification = TenmVAC()
                self.acVerification.exec()
            if resistanceVerificationConfig:
                self.resistanceVerification = ResistanceVerification()
                self.resistanceVerification.exec()
            if fourWireConfig:
                self.fourWireTests = HundredOhm4Wire()
                self.fourWireTests.exec()
            if twoWireConfig:
                self.twoWireTests = HundredOhm2Wire()
                self.twoWireTests.exec()
            if dcCurrentConfig:
                self.dcCurrent = DCCurrent0()
                self.dcCurrent.exec()
            if acCurrentConfig:
                try:
                    print("here 2")
                    self.acCurrent = ACCurrent0()
                    self.acCurrent.exec()
                except Exception as e:
                    print(f"error: {e}")
        except Exception as e:
            print(f"Continue error: {e}")


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
        self.StartDiagnosticTestProgress()

        if USE_INSTRUMENT:
            my_instrument.write("Z0")

            self.diagnostictest = True

            errors = []

            while True:
                percent = self.diagnosticTestElapsed.elapsed() * 100 // 25_000
                self.progressBar.setValue(percent)
                if self.progressBar.value() == 100:
                    self.FinishDiagnosticTestProgress()
                my_instrument.write("G7")
                error = my_instrument.read().strip()
                print(f"G7: {error!r}")

                if error != "1000":
                    errors.append(error)
                    my_instrument.write("X0")

                my_instrument.write("G0")
                status = my_instrument.read().strip()
                print(f"G0: {status!r}")

                if not status.startswith("9"):
                    print("Diagnostics complete")
                    break

            my_instrument.write("G7")
            error = my_instrument.read().strip()
            print(f"Final G7: {error!r}")

            if error != "1000":
                errors.append(error)

            run["diagnostics"] = errors
            print(f"Diagnostic errors: {errors}")


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
        self.diagnostictest = False
        #if USE_INSTRUMENT:
            #my_instrument.write("G7")
            #run["diagnostics"] = my_instrument.read().strip()
            #print(run["diagnostics"])
            #status = my_instrument.read().strip()

            #if status == "1000":
             #   print("Fluke 8840A Passed all Diagnostic Tests")
            #else:
             #   print(f"Fluke 8840A returned {status}. Consult provided reference in utilities for error code.")

        self.diagnosticTimer.stop()
        self.progressBar.setValue(100)
        self.progressBar.setFormat("Self Diagnostics Test Complete!")

        time.sleep(3)
        try:
            if allTests:
                self.close()
                self.dcVoltageVerification = DCVoltageVerification()
                self.dcVoltageVerification.exec()
            elif diagnosticsConfig:
                self.close()
                self.completed = Completed()
                self.completed.exec()
        except Exception as e:
            print(f"Error: {e!r}")

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


            print(run["dc_200mv_short_slow_v"])
            print(run["dc_200mv_short_slow_v_result"])

            print(run["dc_200mv_short_medium_v"])
            print(run["dc_200mv_short_medium_v_result"])

            print(run["dc_200mv_short_fast_v"])
            print(run["dc_200mv_short_fast_v_result"])


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


            print(run["dc_2v_short_slow_v"])
            print(run["dc_2v_short_slow_v_result"])

            print(run["dc_2v_short_medium_v"])
            print(run["dc_2v_short_medium_v_result"])

            print(run["dc_2v_short_fast_v"])
            print(run["dc_2v_short_fast_v_result"])

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


            print(run["dc_20v_short_slow_v"])
            print(run["dc_20v_short_slow_v_result"])

            print(run["dc_20v_short_medium_v"])
            print(run["dc_20v_short_medium_v_result"])

            print(run["dc_20v_short_fast_v"])
            print(run["dc_20v_short_fast_v_result"])

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


            print(run["dc_200v_short_slow_v"])
            print(run["dc_200v_short_slow_v_result"])

            print(run["dc_200v_short_medium_v"])
            print(run["dc_200v_short_medium_v_result"])

            print(run["dc_200v_short_fast_v"])
            print(run["dc_200v_short_fast_v_result"])

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


            print(run["dc_1000v_short_slow_v"])
            print(run["dc_1000v_short_slow_v_result"])

            print(run["dc_1000v_short_medium_v"])
            print(run["dc_1000v_short_medium_v_result"])

            print(run["dc_1000v_short_fast_v"])
            print(run["dc_1000v_short_fast_v_result"])


            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.mVDC100 = mVDC100()
            self.mVDC100.exec()
        else:
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
            #my_instrument.write("B1?")
            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["mvdc_100mv_short_slow_v"] = self.mvdc_1_reading
            if 0.099989 <= self.mvdc_1_reading <= 0.100011:
                run["mvdc_100mv_short_slow_v_result"] = "PASS"
            else:
                run["mvdc_100mv_short_slow_v_result"] = "FAIL"

            print(run["mvdc_100mv_short_slow_v"])
            print(run["mvdc_100mv_short_slow_v_result"])

            my_instrument.write("F1R1S1T0Y0B0?")
            my_instrument.read()
            #my_instrument.write("B1?")
            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["mvdc_100mv_short_medium_v"] = self.mvdc_1_reading
            if 0.099987 <= self.mvdc_1_reading <= 0.100013:
                run["mvdc_100mv_short_medium_v_result"] = "PASS"
            else:
                run["mvdc_100mv_short_medium_v_result"] = "FAIL"

            print(run["mvdc_100mv_short_medium_v"])
            print(run["mvdc_100mv_short_medium_v_result"])

            my_instrument.write("F1R1D1S2T0Y0B0?")
            my_instrument.read()
            #my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.mvdc_1_reading = float(my_instrument.read().strip())

            run["mvdc_100mv_short_fast_v"] = self.mvdc_1_reading
            if 0.099970 <= self.mvdc_1_reading <= 0.100030:
                run["mvdc_100mv_short_fast_v_result"] = "PASS"
            else:
                run["mvdc_100mv_short_fast_v_result"] = "FAIL"

            print(run["mvdc_100mv_short_fast_v"])
            print(run["mvdc_100mv_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.OneVDC100 = OneVDC100()
            self.OneVDC100.exec()

        else:
            self.close()
            self.OneVDC100 = OneVDC100()
            self.OneVDC100.exec()



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
            #my_instrument.write("B1?")
            self.vdc_1_reading = float(my_instrument.read().strip())

            run["vdc_1v_short_slow_v"] = self.vdc_1_reading
            if 0.99993 <= self.vdc_1_reading <= 1.00007:
                run["vdc_1v_short_slow_v_result"] = "PASS"
            else:
                run["vdc_1v_short_slow_v_result"] = "FAIL"

            print(run["vdc_1v_short_slow_v"])
            print(run["vdc_1v_short_slow_v_result"])

            my_instrument.write("F1R2S1T0Y0B0?")
            my_instrument.read()
            #my_instrument.write("B1?")
            self.vdc_1_reading = float(my_instrument.read().strip())

            run["vdc_1v_short_medium_v"] = self.vdc_1_reading
            if 0.99991 <= self.vdc_1_reading <= 1.00009:
                run["vdc_1v_short_medium_v_result"] = "PASS"
            else:
                run["vdc_1v_short_medium_v_result"] = "FAIL"

            print(run["vdc_1v_short_medium_v"])
            print(run["vdc_1v_short_medium_v_result"])

            my_instrument.write("F1R2D1S2T0Y0B0?")
            my_instrument.read()
            #my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.vdc_1_reading = float(my_instrument.read().strip())

            run["vdc_1v_short_fast_v"] = self.vdc_1_reading
            if 0.9997 <= self.vdc_1_reading <= 1.0003:
                run["vdc_1v_short_fast_v_result"] = "PASS"
            else:
                run["vdc_1v_short_fast_v_result"] = "FAIL"

            print(run["vdc_1v_short_fast_v"])
            print(run["vdc_1v_short_fast_v_result"])

            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.tenVDC = TenVDC100()
            self.tenVDC.exec()

        else:
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
            #my_instrument.write("B1?")
            self.vdc_10_reading = float(my_instrument.read().strip())

            run["vdc_10v_short_slow_v"] = self.vdc_10_reading
            if 9.9992 <= self.vdc_10_reading <= 10.0008:
                run["vdc_10v_short_slow_v_result"] = "PASS"
            else:
                run["vdc_10v_short_slow_v_result"] = "FAIL"

            print(run["vdc_10v_short_slow_v"])
            print(run["vdc_10v_short_slow_v_result"])

            my_instrument.write("F1R3S1T0Y0B0?")
            my_instrument.read()
            #my_instrument.write("B1?")
            self.vdc_10_reading = float(my_instrument.read().strip())

            run["vdc_10v_short_medium_v"] = self.vdc_10_reading
            if 9.9990 <= self.vdc_10_reading <= 10.0010:
                run["vdc_10v_short_medium_v_result"] = "PASS"
            else:
                run["vdc_10v_short_medium_v_result"] = "FAIL"

            print(run["vdc_10v_short_medium_v"])
            print(run["vdc_10v_short_medium_v_result"])

            my_instrument.write("F1R3D1S2T0Y0B0?")
            my_instrument.read()
            #my_instrument.write("B1?")
            my_instrument.write("D0?")

            self.vdc_10_reading = float(my_instrument.read().strip())

            run["vdc_10v_short_fast_v"] = self.vdc_10_reading
            if 9.997 <= self.vdc_10_reading <= 1.003:
                run["vdc_10v_short_fast_v_result"] = "PASS"
            else:
                run["vdc_10v_short_fast_v_result"] = "FAIL"

            print(run["vdc_10v_short_fast_v"])
            print(run["vdc_10v_short_fast_v_result"])

            my_instrument.write("F1R3S0T0Y0B0?")
            my_instrument.read()
            my_instrument.write("B1?")

            self.close()
            self.hundredVDC = HundredVDC()
            self.hundredVDC.exec()

        else:
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

        else:
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

        else:
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
            self.negmvdc_1_reading = float(my_instrument.read().strip())

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

        else:
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
            self.negvdc_1_reading = float(my_instrument.read().strip())

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

        else:
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
            self.negvdc_10_reading = float(my_instrument.read().strip())

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

        else:
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
            self.negvdc_100_reading = float(my_instrument.read().strip())

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

        else:
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
            if allTests:
                self.close()
                self.linearPointOne = PointOne()
                self.linearPointOne.exec()
            elif dcVerificationConfig:
                self.close()
                self.testComplete = Completed()
                self.testComplete.exec()




class PointOne(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point One"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Connect the HI and LO jacks of the calibrator output and Fluke 8840A input.\n"
                                  )
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Supply Fluke 8840A with +0 VDC output from provided calibrator.\n"
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
            self.point1_vdc_1_reading = float(my_instrument.read().strip())

            run["point1_vdc_short_slow_v"] = self.point1_vdc_1_reading
            if -0.00002 <= self.point1_vdc_1_reading <= 0.00002:
                run["point1_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point1_vdc_short_slow_v_result"] = "FAIL"

            print(run["point1_vdc_short_slow_v"])
            print(run["point1_vdc_short_slow_v_result"])


            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.pointTwo = PointTwo()
            self.pointTwo.exec()

        else:
            self.close()
            self.pointTwo = PointTwo()
            self.pointTwo.exec()


class PointTwo(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point Two"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel("Reconnect the calibrator to the HI and LO jacks of the Fluke 8840A.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)

        self.actionLabel = QLabel("Supply Fluke 8840A with -0.03 VDC output from provided calibrator.\n"
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
            self.point2_vdc_1_reading = float(my_instrument.read().strip())

            run["point2_vdc_short_slow_v"] = self.point2_vdc_1_reading
            if -0.03002 <= self.point2_vdc_1_reading <= -0.02998:
                run["point2_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point2_vdc_short_slow_v_result"] = "FAIL"

            print(run["point2_vdc_short_slow_v"])
            print(run["point2_vdc_short_slow_v_result"])


            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.pointThree = PointThree()
            self.pointThree.exec()

        else:
            self.close()
            self.pointThree = PointThree()
            self.pointThree.exec()


class PointThree(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point Three"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +0.03 VDC output from provided calibrator.\n"
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
            self.point3_vdc_1_reading = float(my_instrument.read().strip())

            run["point3_vdc_short_slow_v"] = self.point3_vdc_1_reading
            if 0.02998 <= self.point3_vdc_1_reading <= 0.03002:
                run["point3_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point3_vdc_short_slow_v_result"] = "FAIL"

            print(run["point3_vdc_short_slow_v"])
            print(run["point3_vdc_short_slow_v_result"])


            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.pointFour = PointFour()
            self.pointFour.exec()

        else:
            self.close()
            self.pointFour = PointFour()
            self.pointFour.exec()


class PointFour(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point Four"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -0.66 VDC output from provided calibrator.\n"
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
            self.point4_vdc_1_reading = float(my_instrument.read().strip())

            run["point4_vdc_short_slow_v"] = self.point4_vdc_1_reading
            if -0.66003 <= self.point4_vdc_1_reading <= -.65997:
                run["point4_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point4_vdc_short_slow_v_result"] = "FAIL"

            print(run["point4_vdc_short_slow_v"])
            print(run["point4_vdc_short_slow_v_result"])


            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.pointFive = PointFive()
            self.pointFive.exec()

        else:
            self.close()
            self.pointFive = PointFive()
            self.pointFive.exec()


class PointFive(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point Five"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +0.66 VDC output from provided calibrator.\n"
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
            self.point5_vdc_1_reading = float(my_instrument.read().strip())

            run["point5_vdc_short_slow_v"] = self.point5_vdc_1_reading
            if 0.65997 <= self.point5_vdc_1_reading <= 0.66003:
                run["point5_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point5_vdc_short_slow_v_result"] = "FAIL"

            print(run["point5_vdc_short_slow_v"])
            print(run["point5_vdc_short_slow_v_result"])


            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.pointSix = PointSix()
            self.pointSix.exec()

        else:
            self.close()
            self.pointSix = PointSix()
            self.pointSix.exec()


class PointSix(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point Six"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with -1.97 VDC output from provided calibrator.\n"
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
            self.point6_vdc_1_reading = float(my_instrument.read().strip())

            run["point6_vdc_short_slow_v"] = self.point6_vdc_1_reading
            if -1.97004 <= self.point6_vdc_1_reading <= -1.96996:
                run["point6_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point6_vdc_short_slow_v_result"] = "FAIL"

            print(run["point6_vdc_short_slow_v"])
            print(run["point6_vdc_short_slow_v_result"])



            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.pointSeven = PointSeven()
            self.pointSeven.exec()

        else:
            self.close()
            self.pointSeven = PointSeven()
            self.pointSeven.exec()


class PointSeven(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Voltage Linearity Verification Point Seven"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Supply Fluke 8840A with +1.97 VDC output from provided calibrator.\n"
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
            self.point7_vdc_1_reading = float(my_instrument.read().strip())

            run["point7_vdc_short_slow_v"] = self.point7_vdc_1_reading
            if 1.96996 <= self.point7_vdc_1_reading <= 1.97004:
                run["point7_vdc_short_slow_v_result"] = "PASS"
            else:
                run["point7_vdc_short_slow_v_result"] = "FAIL"

            print(run["point7_vdc_short_slow_v"])
            print(run["point7_vdc_short_slow_v_result"])


            my_instrument.write("F1R2S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.tenmVAC = TenmVAC()
                self.tenmVAC.exec()
            elif linearityTestConfig:
                self.close()
                self.testComplete = Completed()
                self.testComplete.exec()


class TenmVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10 mV AC Voltage Verification"
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

        self.actionLabel = QLabel("Supply Fluke 8840A with +10 mV AC output at 100 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.mvac_10_reading = float(my_instrument.read().strip())

            run["mvac_10mv_short_slow_v"] = self.mvac_10_reading
            if 0.00799 <= self.mvac_10_reading <= 0.01201:
                run["mvac_10mv_short_slow_v_result"] = "PASS"
            else:
                run["mvac_10mv_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.HundredmVAC = HundredmVAC()
            self.HundredmVAC.exec()


        else:
            self.close()
            self.HundredmVAC = HundredmVAC()
            self.HundredmVAC.exec()

class HundredmVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 mV AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +100 mV AC output at 100 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.mvac_100_reading = float(my_instrument.read().strip())

            run["mvac_100mv_short_slow_v"] = self.mvac_100_reading
            if 0.09886 <= self.mvac_100_reading <= 0.10114:
                run["mvac_100mv_short_slow_v_result"] = "PASS"
            else:
                run["mvac_100mv_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.threeHundredmVAC = ThreeHundredmVAC()
            self.threeHundredmVAC.exec()

        else:
            self.close()
            self.threeHundredmVAC = ThreeHundredmVAC()
            self.threeHundredmVAC.exec()


class ThreeHundredmVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "300 mV AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +300 mV AC output at 100 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.mvac_300_reading = float(my_instrument.read().strip())

            run["mvac_300mv_short_slow_v"] = self.mvac_300_reading
            if 0.29858 <= self.mvac_300_reading <= 0.30142:
                run["mvac_300mv_short_slow_v_result"] = "PASS"
            else:
                run["mvac_300mv_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.OneVAC = OneVAC()
            self.OneVAC.exec()

        else:
            self.close()
            self.OneVAC = OneVAC()
            self.OneVAC.exec()


class OneVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1 V AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +1 V AC output at 100 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.vac_1_reading = float(my_instrument.read().strip())

            run["vac_1_v_short_slow_v"] = self.vac_1_reading
            if 0.99760 <= self.vac_1_reading <= 1.00240:
                run["vac_1_v_short_slow_v_result"] = "PASS"
            else:
                run["vac_1_v_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.oneNineVAC = OneNineVAC()
            self.oneNineVAC.exec()

        else:
            self.close()
            self.oneNineVAC = OneNineVAC()
            self.oneNineVAC.exec()


class OneNineVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1.9 V AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +1.9 V AC output at 100 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.vac_19_reading = float(my_instrument.read().strip())

            run["vac_19_short_slow_v"] = self.vac_19_reading
            if 1.89634 <= self.vac_19_reading <= 1.90366:
                run["vac_19_short_slow_v_result"] = "PASS"
            else:
                run["vac_19_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.hundredmVAC100 = Hundred20mVAC()
            self.hundredmVAC100.exec()

        else:
            self.close()
            self.hundredmVAC = Hundred20mVAC()
            self.hundredmVAC.exec()

class Hundred20mVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 mV AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +100 mV AC output at 20 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.mvac_100_reading = float(my_instrument.read().strip())

            run["mvac_100_short_slow_v"] = self.mvac_100_reading
            if 0.09780 <= self.mvac_100_reading <= 0.10220:
                run["mvac_100_short_slow_v_result"] = "PASS"
            else:
                run["mvac_100_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.OneNine20VAC = OneNine20VAC()
            self.OneNine20VAC.exec()

        else:
            self.close()
            self.OneNine20VAC = OneNine20VAC()
            self.OneNine20VAC.exec()

class OneNine20VAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1.9 V 20 Hz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +1.9 V AC output at 20 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.vac_1920_reading = float(my_instrument.read().strip())

            run["vac_1920_short_slow_v"] = self.vac_1920_reading
            if 1.87620 <= self.vac_1920_reading <= 1.92380:
                run["vac_1920_short_slow_v_result"] = "PASS"
            else:
                run["vac_1920_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.hundred45mVAC = Hundred45mVAC()
            self.hundred45mVAC.exec()

        else:
            self.close()
            self.hundred45mVAC = Hundred45mVAC()
            self.hundred45mVAC.exec()

class Hundred45mVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 mV 45 Hz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +100 mV AC output at 45 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.mvac_100_45_reading = float(my_instrument.read().strip())

            run["mvac_100_45_short_slow_v"] = self.mvac_100_45_reading
            if 0.09865 <= self.mvac_100_45_reading <= 0.10135:
                run["mvac_100_45_short_slow_v_result"] = "PASS"
            else:
                run["mvac_100_45_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.OneNine45VAC = OneNine45VAC()
            self.OneNine45VAC.exec()

        else:
            self.close()
            self.OneNine45VAC = OneNine45VAC()
            self.OneNine45VAC.exec()


class OneNine45VAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1.9 V 45 Hz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +1.9 V AC output at 45 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.vac_19_45_reading = float(my_instrument.read().strip())

            run["vac_19_45_short_slow_v"] = self.vac_19_45_reading
            if 1.89235 <= self.vac_19_45_reading <= 1.90765:
                run["vac_19_45_short_slow_v_result"] = "PASS"
            else:
                run["vac_19_45_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.onemVAC = OnemVAC()
            self.onemVAC.exec()

        else:
            self.close()
            self.onemVAC = OnemVAC()
            self.onemVAC.exec()

class OnemVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1 mV 100 Hz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +1 mV AC output at 100 Hz from provided calibrator.\n"
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

            my_instrument.write("F2R1S0T0Y0B0?")
            my_instrument.read()

            self.mvac_1_100_reading = float(my_instrument.read().strip())

            run["mvac_1_100_short_slow_v"] = self.mvac_1_100_reading
            if 0.00799 <= self.mvac_1_100_reading <= 0.001201:
                run["mvac_1_100_short_slow_v_result"] = "PASS"
            else:
                run["mvac_1_100_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.hundred90mVAC = Hundred90mVAC()
            self.hundred90mVAC.exec()

        else:
            self.close()
            self.hundred90mVAC = Hundred90mVAC()
            self.hundred90mVAC.exec()

class Hundred90mVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "190 mV 20 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +190 mV AC output at 20 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R1S0T0Y0B0?")
            my_instrument.read()

            self.mvac_190_20000_reading = float(my_instrument.read().strip())

            run["mvac_190_20000_short_slow_v"] = self.mvac_190_20000_reading
            if 0.189634 <= self.mvac_190_20000_reading <= 0.190366:
                run["mvac_190_20000_short_slow_v_result"] = "PASS"
            else:
                run["mvac_190_20000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.ten100kmVAC = TenmV100kAC()
            self.ten100kmVAC.exec()

        else:
            self.close()
            self.ten100kmVAC = TenmV100kAC()
            self.ten100kmVAC.exec()

class TenmV100kAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10 mV 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +10 mV AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R1S0T0Y0B0?")
            my_instrument.read()

            self.mvac_10_100000_reading = float(my_instrument.read().strip())

            run["mvac_10_100000_short_slow_v"] = self.mvac_10_100000_reading
            if 0.009650 <= self.mvac_10_100000_reading <= 0.010350:
                run["mvac_10_100000_short_slow_v_result"] = "PASS"
            else:
                run["mvac_10_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.hundred100kmVAC = Hundred100kmVAC()
            self.hundred100kmVAC.exec()

        else:
            self.close()
            self.hundred100kmVAC = Hundred100kmVAC()
            self.hundred100kmVAC.exec()

class Hundred100kmVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 mV 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +100 mV AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R2S0T0Y0B0?")
            my_instrument.read()

            self.mvac_100_100000_reading = float(my_instrument.read().strip())

            run["mvac_100_100000_short_slow_v"] = self.mvac_100_100000_reading
            if 0.09650 <= self.mvac_100_100000_reading <= 0.10350:
                run["mvac_100_100000_short_slow_v_result"] = "PASS"
            else:
                run["mvac_100_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.one100kVAC = One100kVAC()
            self.one100kVAC.exec()

        else:
            self.close()
            self.one100kVAC = One100kVAC()
            self.one100kVAC.exec()

class One100kVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1 V 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +1 V AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R3S0T0Y0B0?")
            my_instrument.read()

            self.vac_1_100000_reading = float(my_instrument.read().strip())

            run["vac_1_100000_short_slow_v"] = self.vac_1_100000_reading
            if 0.9650 <= self.vac_1_100000_reading <= 1.0350:
                run["vac_1_100000_short_slow_v_result"] = "PASS"
            else:
                run["vac_1_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.ten100kVAC = Ten100kVAC()
            self.ten100kVAC.exec()

        else:
            self.close()
            self.ten100kVAC = Ten100kVAC()
            self.ten100kVAC.exec()

class Ten100kVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10 V 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +10 V AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R4S0T0Y0B0?")
            my_instrument.read()

            self.vac_10_100000_reading = float(my_instrument.read().strip())

            run["vac_10_100000_short_slow_v"] = self.vac_10_100000_reading
            if 9.650 <= self.vac_10_100000_reading <= 10.350:
                run["vac_10_100000_short_slow_v_result"] = "PASS"
            else:
                run["vac_10_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.hundred100kVAC = Hundred100kVAC()
            self.hundred100kVAC.exec()

        else:
            self.close()
            self.hundred100kVAC = Hundred100kVAC()
            self.hundred100kVAC.exec()

class Hundred100kVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 V 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +100 V AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R5S0T0Y0B0?")
            my_instrument.read()

            self.vac_100_100000_reading = float(my_instrument.read().strip())

            run["vac_100_100000_short_slow_v"] = self.vac_100_100000_reading
            if 96.50 <= self.vac_100_100000_reading <= 103.50:
                run["vac_100_100000_short_slow_v_result"] = "PASS"
            else:
                run["vac_100_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.nineteen100kVAC = Nineteen100kVAC()
            self.nineteen100kVAC.exec()

        else:
            self.close()
            self.nineteen100kVAC = Nineteen100kVAC()
            self.nineteen100kVAC.exec()

class Nineteen100kVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "19 V 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +19 V AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R3S0T0Y0B0?")
            my_instrument.read()

            self.vac_19_100000_reading = float(my_instrument.read().strip())

            run["vac_19_100000_short_slow_v"] = self.vac_19_100000_reading
            if 18.8750 <= self.vac_19_100000_reading <= 19.1250:
                run["vac_19_100000_short_slow_v_result"] = "PASS"
            else:
                run["vac_19_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.hundred90100kmVAC = Hundred90100kmVAC()
            self.hundred90100kmVAC.exec()

        else:
            self.close()
            self.hundred90100kmVAC = Hundred90100kmVAC()
            self.hundred90100kmVAC.exec()

class Hundred90100kmVAC(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "190 mV 100 kHz AC Voltage Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with +190 mV AC output at 100 kHz from provided calibrator.\n"
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

            my_instrument.write("F2R1S0T0Y0B0?")
            my_instrument.read()

            self.mvac_190_100000_reading = float(my_instrument.read().strip())

            run["mvac_190_100000_short_slow_v"] = self.mvac_190_100000_reading
            if 0.188750 <= self.mvac_190_100000_reading <= 0.191250:
                run["mvac_190_100000_short_slow_v_result"] = "PASS"
            else:
                run["mvac_190_100000_short_slow_v_result"] = "FAIL"

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.resistanceVerification = ResistanceVerification()
                self.resistanceVerification.exec()
            elif acVerificationConfig:
                self.close()
                self.testComplete = Completed()
                self.testComplete.exec()


#---------------------------------------------------------------------------------- Change from tolerances to limits
#---------------------------------------------------------------------------------- Implement numbers to see where break happens

class ResistanceVerification(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Short the HI, HI Sense, LO, and LO Sense jacks of the Fluke 8840A with provided cable.")
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

#--------------------------------------------------- Shorted 200 ohm range

            my_instrument.write("F4R1D1S0T0Y0B0")
            my_instrument.read()
            self.res_200_reading = float(my_instrument.read().strip())

            run["res_200ohm_short_slow_v"] = self.res_200_reading
            if -0.004 <= self.res_200_reading <= 0.004:
                run["res_200ohm_short_slow_v_result"] = "PASS"
            else:
                run["res_200ohm_short_slow_v_result"] = "FAIL"

            print(run["res_200ohm_short_slow_v"])
            print(run["res_200ohm_short_slow_v_result"])

            my_instrument.write("F4R1D1S1T0Y0B0")
            my_instrument.read()
            self.res_200_reading = float(my_instrument.read().strip())

            run["res_200ohm_short_medium_v"] = self.res_200_reading
            if -0.006 <= self.res_200_reading <= 0.006:
                run["res_200ohm_short_medium_v_result"] = "PASS"
            else:
                run["res_200ohm_short_medium_v_result"] = "FAIL"


            print(run["res_200ohm_short_medium_v"])
            print(run["res_200ohm_short_medium_v_result"])

            my_instrument.write("F4R1D1S2T0Y0B0")
            my_instrument.read()
            my_instrument.write("D0?")

            self.res_200_reading = float(my_instrument.read().strip())

            run["res_200ohm_short_fast_v"] = self.res_200_reading
            if -0.03 <= self.res_200_reading <= 0.03:
                run["res_200ohm_short_fast_v_result"] = "PASS"
            else:
                run["res_200ohm_short_fast_v_result"] = "FAIL"

            print(run["res_200ohm_short_fast_v"])
            print(run["res_200ohm_short_fast_v_result"])

#-------------------------------------------------------- Shorted 2 kohm range

            my_instrument.write("F4R2D1S0T0Y0B0")
            my_instrument.read()
            self.res_2kohm_reading = float(my_instrument.read().strip())

            run["res_2kohm_short_slow_v"] = self.res_2kohm_reading
            if -0.03 <= self.res_2kohm_reading <= 0.03:
                run["res_2kohm_short_slow_v_result"] = "PASS"
            else:
                run["res_2kohm_short_slow_v_result"] = "FAIL"

            print(run["res_2kohm_short_slow_v"])
            print(run["res_2kohm_short_slow_v_result"])

            my_instrument.write("F4R2D1S1T0Y0B0")
            self.res_2kohm_reading = float(my_instrument.read().strip())

            run["res_2kohm_short_medium_v"] = self.res_2kohm_reading
            if -0.05 <= self.res_2kohm_reading <= 0.05:
                run["res_2kohm_short_medium_v_result"] = "PASS"
            else:
                run["res_2kohm_short_medium_v_result"] = "FAIL"

            print(run["res_2kohm_short_medium_v"])
            print(run["res_2kohm_short_medium_v_result"])

            my_instrument.write("F4R2D1S2T0Y0B0")
            my_instrument.read()
            my_instrument.write("D0?")

            self.res_2kohm_reading = float(my_instrument.read().strip())

            run["res_2kohm_short_fast_v"] = self.res_2kohm_reading
            if -0.2 <= self.res_2kohm_reading <= 0.2:
                run["res_2kohm_short_fast_v_result"] = "PASS"
            else:
                run["res_2kohm_short_fast_v_result"] = "FAIL"


            print(run["res_2kohm_short_fast_v"])
            print(run["res_2kohm_short_fast_v_result"])

#-------------------------------------------------------- Shorted 20 kohm range

            my_instrument.write("F4R3D1S0T0Y0B0")
            my_instrument.read()
            self.res_20k_reading = float(my_instrument.read().strip())

            run["res_20k_short_slow_v"] = self.res_20k_reading
            if -0.3 <= self.res_20k_reading <= 0.3:
                run["res_20k_short_slow_v_result"] = "PASS"
            else:
                run["res_20k_short_slow_v_result"] = "FAIL"

            print(run["res_20k_short_slow_v"])
            print(run["res_20k_short_slow_v_result"])

            my_instrument.write("F4R3D1S1T0Y0B0")
            self.res_20k_reading = float(my_instrument.read().strip())

            run["res_20k_short_medium_v"] = self.res_20k_reading
            if -0.5 <= self.res_20k_reading <= 0.5:
                run["res_20k_short_medium_v_result"] = "PASS"
            else:
                run["res_20k_short_medium_v_result"] = "FAIL"


            print(run["res_20k_short_medium_v"])
            print(run["res_20k_short_medium_v_result"])

            my_instrument.write("F4R3D1S2T0Y0B0")
            my_instrument.read()
            my_instrument.write("D0?")

            self.res_20k_reading = float(my_instrument.read().strip())

            run["res_20k_short_fast_v"] = self.res_20k_reading
            if -2 <= self.res_20k_reading <= 2:
                run["res_20k_short_fast_v_result"] = "PASS"
            else:
                run["res_20k_short_fast_v_result"] = "FAIL"


            print(run["res_20k_short_fast_v"])
            print(run["res_20k_short_fast_v_result"])

#-------------------------------------------------------- Shorted 200 kohm range

            my_instrument.write("F4R4D1S0T0Y0B0")
            my_instrument.read()
            self.res_200k_reading = float(my_instrument.read().strip())

            run["res_200k_short_slow_v"] = self.res_200k_reading
            if -3 <= self.res_200k_reading <= 3:
                run["res_200k_short_slow_v_result"] = "PASS"
            else:
                run["res_200k_short_slow_v_result"] = "FAIL"

            print(run["res_200k_short_slow_v"])
            print(run["res_200k_short_slow_v_result"])

            my_instrument.write("F4R4D1S1T0Y0B0")
            self.res_200k_reading = float(my_instrument.read().strip())

            run["res_200k_short_medium_v"] = self.res_200k_reading
            if -5 <= self.res_200k_reading <= 5:
                run["res_200k_short_medium_v_result"] = "PASS"
            else:
                run["res_200k_short_medium_v_result"] = "FAIL"


            print(run["res_200k_short_medium_v"])
            print(run["res_200k_short_medium_v_result"])

            my_instrument.write("F4R4D1S2T0Y0B0")
            my_instrument.read()
            my_instrument.write("D0?")

            self.res_200k_reading = float(my_instrument.read().strip())

            run["res_200k_short_fast_v"] = self.res_200k_reading
            if -20 <= self.res_200k_reading <= 20:
                run["res_200k_short_fast_v_result"] = "PASS"
            else:
                run["res_200k_short_fast_v_result"] = "FAIL"


            print(run["res_200k_short_fast_v"])
            print(run["res_200k_short_fast_v_result"])

#-------------------------------------------------------- Shorted 2 mohm range

            my_instrument.write("F4R5D1S0T0Y0B0")
            my_instrument.read()
            self.res_2mohm_reading = float(my_instrument.read().strip())

            run["res_2mohm_short_slow_v"] = self.res_2mohm_reading
            if -30 <= self.res_2mohm_reading <= 30:
                run["res_2mohm_short_slow_v_result"] = "PASS"
            else:
                run["res_2mohm_short_slow_v_result"] = "FAIL"


            print(run["res_2mohm_short_slow_v"])
            print(run["res_2mohm_short_slow_v_result"])

            my_instrument.write("F4R5D1S1T0Y0B0")
            self.res_2mohm_reading = float(my_instrument.read().strip())

            run["res_2mohm_short_medium_v"] = self.res_2mohm_reading
            if -60 <= self.res_2mohm_reading <= 60:
                run["res_2mohm_short_medium_v_result"] = "PASS"
            else:
                run["res_2mohm_short_medium_v_result"] = "FAIL"


            print(run["res_2mohm_short_medium_v"])
            print(run["res_2mohm_short_medium_v_result"])

            my_instrument.write("F4R5D1S2T0Y0B0")
            my_instrument.read()
            my_instrument.write("D0?")

            self.res_2mohm_reading = float(my_instrument.read().strip())

            run["res_2mohm_short_fast_v"] = self.res_2mohm_reading
            if -200 <= self.res_2mohm_reading <= 200:
                run["res_2mohm_short_fast_v_result"] = "PASS"
            else:
                run["res_2mohm_short_fast_v_result"] = "FAIL"


            print(run["res_2mohm_short_fast_v"])
            print(run["res_2mohm_short_fast_v_result"])

#-------------------------------------------------------- Shorted 20 mohm range

            my_instrument.write("F4R6D1S0T0Y0B0")
            my_instrument.read()
            self.res_20mohm_reading = float(my_instrument.read().strip())

            run["res_20mohm_short_slow_v"] = self.res_20mohm_reading
            if -400 <= self.res_20mohm_reading <= 400:
                run["res_20mohm_short_slow_v_result"] = "PASS"
            else:
                run["res_20mohm_short_slow_v_result"] = "FAIL"

            print(run["res_20mohm_short_slow_v"])
            print(run["res_20mohm_short_slow_v_result"])

            my_instrument.write("F4R5D1S1T0Y0B0")
            self.res_20mohm_reading = float(my_instrument.read().strip())

            run["res_20mohm_short_medium_v"] = self.res_20mohm_reading
            if -600 <= self.res_20mohm_reading <= 600:
                run["res_20mohm_short_medium_v_result"] = "PASS"
            else:
                run["res_20mohm_short_medium_v_result"] = "FAIL"


            print(run["res_20mohm_short_medium_v"])
            print(run["res_20mohm_short_medium_v_result"])

            my_instrument.write("F4R5D1S2T0Y0B0")
            my_instrument.read()
            my_instrument.write("D0?")

            self.res_20mohm_reading = float(my_instrument.read().strip())

            run["res_20mohm_short_fast_v"] = self.res_20mohm_reading
            if -2000 <= self.res_20mohm_reading <= 2000:
                run["res_20mohm_short_fast_v_result"] = "PASS"
            else:
                run["res_20mohm_short_fast_v_result"] = "FAIL"


            print(run["res_20mohm_short_fast_v"])
            print(run["res_20mohm_short_fast_v_result"])


            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.twoWireVerification = ResistanceVerification2Wire()
            self.twoWireVerification.exec()

#------------------------------------------------------------- 2-wire Ohm Test
#------------------------------------------------------------- 200 ohm

class ResistanceVerification2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel(
            "Short the HI and LO jacks of the Fluke 8840A with provided cable.\n"
            "Ensure the HI Sense and LO Sense jacks are disconnected.")
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

            try:

                print("Beginning of Two Wire Resistance Verification Results")

                # Throw some D's on it. (Delays)

                my_instrument.write("F3R1D1S0T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_200_reading = float(my_instrument.read().strip())

                run["res_2_200ohm_short_slow_v"] = self.res_2_200_reading
                if -0.004 <= self.res_2_200_reading <= 0.004:
                    run["res_2_200ohm_short_slow_v_result"] = "PASS"
                else:
                    run["res_2_200ohm_short_slow_v_result"] = "FAIL"

                print(run["res_2_200ohm_short_slow_v"])
                print(run["res_2_200ohm_short_slow_v_result"])

                my_instrument.write("F3R1D1S1T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_200_reading = float(my_instrument.read().strip())

                run["res_2_200ohm_short_medium_v"] = self.res_2_200_reading
                if -0.006 <= self.res_2_200_reading <= 0.006:
                    run["res_2_200ohm_short_medium_v_result"] = "PASS"
                else:
                    run["res_2_200ohm_short_medium_v_result"] = "FAIL"


                print(run["res_2_200ohm_short_medium_v"])
                print(run["res_2_200ohm_short_medium_v_result"])

                my_instrument.write("F3R1D1S2T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                my_instrument.write("D0?")

                self.res_2_200_reading = float(my_instrument.read().strip())

                run["res_2_200ohm_short_fast_v"] = self.res_2_200_reading
                if -0.03 <= self.res_2_200_reading <= 0.03:
                    run["res_2_200ohm_short_fast_v_result"] = "PASS"
                else:
                    run["res_2_200ohm_short_fast_v_result"] = "FAIL"


                print(run["res_2_200ohm_short_fast_v"])
                print(run["res_2_200ohm_short_fast_v_result"])

    #-------------------------------------------------------- Shorted 2 kohm range

                my_instrument.write("F3R2D1S0T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_2kohm_reading = float(my_instrument.read().strip())

                run["res_2_2kohm_short_slow_v"] = self.res_2_2kohm_reading
                if -0.03 <= self.res_2_2kohm_reading <= 0.03:
                    run["res_2_2kohm_short_slow_v_result"] = "PASS"
                else:
                    run["res_2_2kohm_short_slow_v_result"] = "FAIL"


                print(run["res_2_2kohm_short_slow_v"])
                print(run["res_2_2kohm_short_slow_v_result"])

                my_instrument.write("F3R2D1S1T0Y0B0")
                my_instrument.write("B1")
                self.res_2_2kohm_reading = float(my_instrument.read().strip())

                run["res_2_2kohm_short_medium_v"] = self.res_2_2kohm_reading
                if -0.05 <= self.res_2_2kohm_reading <= 0.05:
                    run["res_2_2kohm_short_medium_v_result"] = "PASS"
                else:
                    run["res_2_2kohm_short_medium_v_result"] = "FAIL"


                print(run["res_2_2kohm_short_medium_v"])
                print(run["res_2_2kohm_short_medium_v_result"])

                my_instrument.write("F3R2D1S2T0Y0B0")
                my_instrument.read()
                my_instrument.write("D0?")
                my_instrument.write("B1")

                self.res_2_2kohm_reading = float(my_instrument.read().strip())

                run["res_2_2kohm_short_fast_v"] = self.res_2_2kohm_reading
                if -0.2 <= self.res_2_2kohm_reading <= 0.2:
                    run["res_2_2kohm_short_fast_v_result"] = "PASS"
                else:
                    run["res_2_2kohm_short_fast_v_result"] = "FAIL"


                print(run["res_2_2kohm_short_fast_v"])
                print(run["res_2_2kohm_short_fast_v_result"])

    #-------------------------------------------------------- Shorted 20 kohm range

                my_instrument.write("F3R3D1S0T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_20kohm_reading = float(my_instrument.read().strip())

                run["res_2_20kohm_short_slow_v"] = self.res_2_20kohm_reading

                if -0.3 <= self.res_2_20kohm_reading <= 0.3:
                    run["res_2_20kohm_short_slow_v_result"] = "PASS"
                else:
                    run["res_2_20kohm_short_slow_v_result"] = "FAIL"


                print(run["res_2_20kohm_short_slow_v"])
                print(run["res_2_20kohm_short_slow_v_result"])

                my_instrument.write("F3R3D1S1T0Y0B0")
                my_instrument.write("B1")
                self.res_2_20kohm_reading = float(my_instrument.read().strip())

                run["res_2_20kohm_short_medium_v"] = self.res_2_20kohm_reading
                if -0.5 <= self.res_2_20kohm_reading <= 0.5:
                    run["res_2_20kohm_short_medium_v_result"] = "PASS"
                else:
                    run["res_2_20kohm_short_medium_v_result"] = "FAIL"


                print(run["res_2_20kohm_short_medium_v"])
                print(run["res_2_20kohm_short_medium_v_result"])

                my_instrument.write("F3R3D1S2T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                my_instrument.write("D0?")

                self.res_2_20kohm_reading = float(my_instrument.read().strip())

                run["res_2_20kohm_short_fast_v"] = self.res_2_20kohm_reading
                if -2 <= self.res_2_20kohm_reading <= 2:
                    run["res_2_20kohm_short_fast_v_result"] = "PASS"
                else:
                    run["res_2_20kohm_short_fast_v_result"] = "FAIL"


                print(run["res_2_20kohm_short_fast_v"])
                print(run["res_2_20kohm_short_fast_v_result"])

    #-------------------------------------------------------- Shorted 200 kohm range

                my_instrument.write("F3R4D1S0T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_200kohm_reading = float(my_instrument.read().strip())

                run["res_2_200kohm_short_slow_v"] = self.res_2_200kohm_reading
                if -3 <= self.res_2_200kohm_reading <= 3:
                    run["res_2_200kohm_short_slow_v_result"] = "PASS"
                else:
                    run["res_2_200kohm_short_slow_v_result"] = "FAIL"


                print(run["res_2_200kohm_short_slow_v"])
                print(run["res_2_200kohm_short_slow_v_result"])

                my_instrument.write("F3R4D1S1T0Y0B0")
                my_instrument.write("B1")
                self.res_2_200k_reading = float(my_instrument.read().strip())

                run["res_2_200kohm_short_medium_v"] = self.res_2_200k_reading
                if -5 <= self.res_2_200kohm_reading <= 5:
                    run["res_2_200kohm_short_medium_v_result"] = "PASS"
                else:
                    run["res_2_200kohm_short_medium_v_result"] = "FAIL"


                print(run["res_2_200kohm_short_medium_v"])
                print(run["res_2_200kohm_short_medium_v_result"])

                my_instrument.write("F3R4D1S2T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                my_instrument.write("D0?")

                self.res_2_200kohm_reading = float(my_instrument.read().strip())

                run["res_2_200kohm_short_fast_v"] = self.res_2_200kohm_reading
                if -20 <= self.res_2_200kohm_reading <= 20:
                    run["res_2_200kohm_short_fast_v_result"] = "PASS"
                else:
                    run["res_2_200kohm_short_fast_v_result"] = "FAIL"


                print(run["res_2_200kohm_short_fast_v"])
                print(run["res_2_200kohm_short_fast_v_result"])

    #-------------------------------------------------------- Shorted 2 mohm range

                my_instrument.write("F3R5D1S0T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_2mohm_reading = float(my_instrument.read().strip())

                run["res_2_2mohm_short_slow_v"] = self.res_2_2mohm_reading
                if -30 <= self.res_2_2mohm_reading <= 30:
                    run["res_2_2mohm_short_slow_v_result"] = "PASS"
                else:
                    run["res_2_2mohm_short_slow_v_result"] = "FAIL"


                print(run["res_2_2mohm_short_slow_v"])
                print(run["res_2_2mohm_short_slow_v_result"])

                my_instrument.write("F3R5D1S1T0Y0B0")
                my_instrument.write("B1")
                self.res_2_2mohm_reading = float(my_instrument.read().strip())

                run["res_2_2mohm_short_medium_v"] = self.res_2_2mohm_reading
                if -60 <= self.res_2_2mohm_reading <= 60:
                    run["res_2_2mohm_short_medium_v_result"] = "PASS"
                else:
                    run["res_2_2mohm_short_medium_v_result"] = "FAIL"


                print(run["res_2_2mohm_short_medium_v"])
                print(run["res_2_2mohm_short_medium_v_result"])

                my_instrument.write("F3R5D1S2T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                my_instrument.write("D0?")

                self.res_2_2mohm_reading = float(my_instrument.read().strip())

                run["res_2_2mohm_short_fast_v"] = self.res_2_2mohm_reading
                if -200 <= self.res_2_2mohm_reading <= 200:
                    run["res_2_2mohm_short_fast_v_result"] = "PASS"
                else:
                    run["res_2_2mohm_short_fast_v_result"] = "FAIL"


                print(run["res_2_2mohm_short_fast_v"])
                print(run["res_2_2mohm_short_fast_v_result"])

    #-------------------------------------------------------- Shorted 20 mohm range

                my_instrument.write("F3R6D1S0T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                self.res_2_20mohm_reading = float(my_instrument.read().strip())

                run["res_2_20mohm_short_slow_v"] = self.res_2_20mohm_reading
                if -400 <= self.res_2_20mohm_reading <= 400:
                    run["res_2_20mohm_short_slow_v_result"] = "PASS"
                else:
                    run["res_2_20mohm_short_slow_v_result"] = "FAIL"


                print(run["res_2_20mohm_short_slow_v"])
                print(run["res_2_20mohm_short_slow_v_result"])

                my_instrument.write("F3R5D1S1T0Y0B0")
                my_instrument.write("B1")
                self.res_2_20mohm_reading = float(my_instrument.read().strip())

                run["res_2_20mohm_short_medium_v"] = self.res_2_20mohm_reading
                if -600 <= self.res_2_20mohm_reading <= 600:
                    run["res_2_20mohm_short_medium_v_result"] = "PASS"
                else:
                    run["res_2_20mohm_short_medium_v_result"] = "FAIL"


                print(run["res_2_20mohm_short_medium_v"])
                print(run["res_2_20mohm_short_medium_v_result"])

                my_instrument.write("F3R5D1S2T0Y0B0")
                my_instrument.read()
                my_instrument.write("B1")
                my_instrument.write("D0?")

                self.res_2_20mohm_reading = float(my_instrument.read().strip())

                run["res_2_20mohm_short_fast_v"] = self.res_2_20mohm_reading
                if -2000 <= self.res_2_20mohm_reading <= 2000:
                    run["res_2_20mohm_short_fast_v_result"] = "PASS"
                else:
                    run["res_2_20mohm_short_fast_v_result"] = "FAIL"

                print(run["res_2_20mohm_short_fast_v"])
                print(run["res_2_20mohm_short_fast_v_result"])


                my_instrument.write("F1R1S0T0Y0B0?")
                my_instrument.read()

                if allTests:
                    self.close()
                    self.hundredOhm4Wire = HundredOhm4Wire()
                    self.hundredOhm4Wire.exec()
                elif resistanceVerificationConfig:
                    self.close()
                    self.testComplete = Completed()
                    self.testComplete.exec()
            except Exception as e:
                print(f"Error: {e}")


class HundredOhm4Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 ohm supplied 4 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.promptLabel = QLabel(
            "Connect the HI, LO, HI Sense, and LO Sense jacks of the calibrator output and Fluke 8840A input.")
        self.promptLabel.setStyleSheet("""
                                            font-size: 18px
                """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 100 ohm output at from provided calibrator.\n"
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

            my_instrument.write("F4R1S0T0Y0B0?")
            my_instrument.read()

            self.res_100_4wire_reading = float(my_instrument.read().strip())

            run["res_100_4wire_short_slow_v"] = self.res_100_4wire_reading
            if 99.985 <= self.res_100_4wire_reading <= 100.015:
                run["res_100_4wire_short_slow_v_result"] = "PASS"
            else:
                run["res_100_4wire_short_slow_v_result"] = "FAIL"

            print(run["res_100_4wire_short_slow_v"])
            print(run["res_100_4wire_short_slow_v_result"])

            my_instrument.write("F4R1S1T0Y0B0?")
            my_instrument.read()

            self.res_100_4wire_reading = float(my_instrument.read().strip())

            run["res_100_4wire_short_med_v"] = self.res_100_4wire_reading
            if 99.983 <= self.res_100_4wire_reading <= 100.017:
                run["res_100_4wire_short_med_v_result"] = "PASS"
            else:
                run["res_100_4wire_short_med_v_result"] = "FAIL"

            print(run["res_100_4wire_short_med_v"])
            print(run["res_100_4wire_short_med_v_result"])

            my_instrument.write("F4R1S2T0Y0B0?")
            my_instrument.read()


            self.res_100_4wire_reading = float(my_instrument.read().strip())

            run["res_100_4wire_short_fast_v"] = self.res_100_4wire_reading
            if 99.960 <= self.res_100_4wire_reading <= 100.040:
                run["res_100_4wire_short_fast_v_result"] = "PASS"
            else:
                run["res_100_4wire_short_fast_v_result"] = "FAIL"

            print(run["res_100_4wire_short_fast_v"])
            print(run["res_100_4wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.thousandOhm4Wire = ThousandOhm4Wire()
            self.thousandOhm4Wire.exec()

        else:
            self.close()
            self.thousandOhm4Wire = ThousandOhm4Wire()
            self.thousandOhm4Wire.exec()

class ThousandOhm4Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1000 ohm supplied 4 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 1000 ohm output from provided calibrator.\n"
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

            my_instrument.write("F4R2S0T0Y0B0?")
            my_instrument.read()

            self.res_1000_4wire_reading = float(my_instrument.read().strip())

            run["res_1000_4wire_short_slow_v"] = self.res_1000_4wire_reading
            if 999.87 <= self.res_1000_4wire_reading <= 1000.13:
                run["res_1000_4wire_short_slow_v_result"] = "PASS"
            else:
                run["res_1000_4wire_short_slow_v_result"] = "FAIL"

            print(run["res_1000_4wire_short_slow_v"])
            print(run["res_1000_4wire_short_slow_v_result"])

            my_instrument.write("F4R2S1T0Y0B0?")
            my_instrument.read()

            self.res_1000_4wire_reading = float(my_instrument.read().strip())

            run["res_1000_4wire_short_med_v"] = self.res_1000_4wire_reading
            if 999.85 <= self.res_1000_4wire_reading <= 1000.15:
                run["res_1000_4wire_short_med_v_result"] = "PASS"
            else:
                run["res_1000_4wire_short_med_v_result"] = "FAIL"

            print(run["res_1000_4wire_short_med_v"])
            print(run["res_1000_4wire_short_med_v_result"])

            my_instrument.write("F4R2S2T0Y0B0?")
            my_instrument.read()

            self.res_1000_4wire_reading = float(my_instrument.read().strip())

            run["res_1000_4wire_short_fast_v"] = self.res_1000_4wire_reading
            if 999.70 <= self.res_1000_4wire_reading <= 1000.30:
                run["res_1000_4wire_short_fast_v_result"] = "PASS"
            else:
                run["res_1000_4wire_short_fast_v_result"] = "FAIL"

            print(run["res_1000_4wire_short_fast_v"])
            print(run["res_1000_4wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.tenThousandOhm4Wire = TenThousandOhm4Wire()
            self.tenThousandOhm4Wire.exec()

        else:
            self.close()
            self.tenThousandOhm4Wire = TenThousandOhm4Wire()
            self.tenThousandOhm4Wire.exec()

class TenThousandOhm4Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10,000 ohm supplied 4 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 10,000 ohm output from provided calibrator.\n"
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

            my_instrument.write("F4R3S0T0Y0B0?")
            my_instrument.read()

            self.res_10000_4wire_reading = float(my_instrument.read().strip())

            run["res_10000_4wire_short_slow_v"] = self.res_10000_4wire_reading
            if 9998.70 <= self.res_10000_4wire_reading <= 10001.30:
                run["res_10000_4wire_short_slow_v_result"] = "PASS"
            else:
                run["res_10000_4wire_short_slow_v_result"] = "FAIL"

            print(run["res_10000_4wire_short_slow_v"])
            print(run["res_10000_4wire_short_slow_v_result"])

            my_instrument.write("F4R3S1T0Y0B0?")
            my_instrument.read()

            self.res_10000_4wire_reading = float(my_instrument.read().strip())

            run["res_10000_4wire_short_med_v"] = self.res_10000_4wire_reading
            if 9998.50 <= self.res_10000_4wire_reading <= 10001.50:
                run["res_10000_4wire_short_med_v_result"] = "PASS"
            else:
                run["res_10000_4wire_short_med_v_result"] = "FAIL"

            print(run["res_10000_4wire_short_med_v"])
            print(run["res_10000_4wire_short_med_v_result"])

            my_instrument.write("F4R3S2T0Y0B0?")
            my_instrument.read()

            self.res_10000_4wire_reading = float(my_instrument.read().strip())

            run["res_10000_4wire_short_fast_v"] = self.res_10000_4wire_reading
            if 9997.00 <= self.res_10000_4wire_reading <= 10003.00:
                run["res_10000_4wire_short_fast_v_result"] = "PASS"
            else:
                run["res_10000_4wire_short_fast_v_result"] = "FAIL"

            print(run["res_10000_4wire_short_fast_v"])
            print(run["res_10000_4wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.hundredThousandOhm4Wire = HundredThousandOhm4Wire()
            self.hundredThousandOhm4Wire.exec()

        else:
            self.close()
            self.hundredThousandOhm4Wire = HundredThousandOhm4Wire()
            self.hundredThousandOhm4Wire.exec()

class HundredThousandOhm4Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100,000 ohm supplied 4 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 100,000 ohm output from provided calibrator.\n"
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

            my_instrument.write("F4R4S0T0Y0B0?")
            my_instrument.read()

            self.res_100000_4wire_reading = float(my_instrument.read().strip())

            run["res_100000_4wire_short_slow_v"] = self.res_100000_4wire_reading
            if 99987.0 <= self.res_100000_4wire_reading <= 100013.0:
                run["res_100000_4wire_short_slow_v_result"] = "PASS"
            else:
                run["res_100000_4wire_short_slow_v_result"] = "FAIL"

            print(run["res_100000_4wire_short_slow_v"])
            print(run["res_100000_4wire_short_slow_v_result"])

            my_instrument.write("F4R4S0T0Y0B0?")
            my_instrument.read()


            self.res_100000_4wire_reading = float(my_instrument.read().strip())

            run["res_100000_4wire_short_med_v"] = self.res_100000_4wire_reading
            if 99985.0 <= self.res_100000_4wire_reading <= 100015.0:
                run["res_100000_4wire_short_med_v_result"] = "PASS"
            else:
                run["res_100000_4wire_short_med_v_result"] = "FAIL"

            print(run["res_100000_4wire_short_med_v"])
            print(run["res_100000_4wire_short_med_v_result"])

            my_instrument.write("F4R4S0T0Y0B0?")
            my_instrument.read()


            self.res_100000_4wire_reading = float(my_instrument.read().strip())

            run["res_100000_4wire_short_fast_v"] = self.res_100000_4wire_reading
            if 99970.0 <= self.res_100000_4wire_reading <= 100030.0:
                run["res_100000_4wire_short_fast_v_result"] = "PASS"
            else:
                run["res_100000_4wire_short_fast_v_result"] = "FAIL"

            print(run["res_100000_4wire_short_fast_v"])
            print(run["res_100000_4wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.megaOhm4Wire = MegaOhm4Wire()
            self.megaOhm4Wire.exec()

        else:
            self.close()
            self.megaOhm4Wire = MegaOhm4Wire()
            self.megaOhm4Wire.exec()

class MegaOhm4Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1,000,000 ohm supplied 4 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 1 Mohm output from provided calibrator.\n"
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

            my_instrument.write("F4R5S0T0Y0B0?")
            my_instrument.read()

            self.res_1000000_4wire_reading = float(my_instrument.read().strip())

            run["res_1000000_4wire_short_slow_v"] = self.res_1000000_4wire_reading
            if 999870.0 <= self.res_1000000_4wire_reading <= 1000130.0:
                run["res_1000000_4wire_short_slow_v_result"] = "PASS"
            else:
                run["res_1000000_4wire_short_slow_v_result"] = "FAIL"

            print(run["res_1000000_4wire_short_slow_v"])
            print(run["res_1000000_4wire_short_slow_v_result"])

            my_instrument.write("F4R5S1T0Y0B0?")
            my_instrument.read()

            self.res_1000000_4wire_reading = float(my_instrument.read().strip())

            run["res_1000000_4wire_short_med_v"] = self.res_1000000_4wire_reading
            if 999850.0 <= self.res_1000000_4wire_reading <= 1000150.0:
                run["res_1000000_4wire_short_med_v_result"] = "PASS"
            else:
                run["res_1000000_4wire_short_med_v_result"] = "FAIL"

            print(run["res_1000000_4wire_short_med_v"])
            print(run["res_1000000_4wire_short_med_v_result"])

            my_instrument.write("F4R5S2T0Y0B0?")
            my_instrument.read()

            self.res_1000000_4wire_reading = float(my_instrument.read().strip())

            run["res_1000000_4wire_short_fast_v"] = self.res_1000000_4wire_reading
            if 999700.0 <= self.res_1000000_4wire_reading <= 1000300.0:
                run["res_1000000_4wire_short_fast_v_result"] = "PASS"
            else:
                run["res_1000000_4wire_short_fast_v_result"] = "FAIL"

            print(run["res_1000000_4wire_short_fast_v"])
            print(run["res_1000000_4wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.tenMegaOhm4Wire = TenMegaOhm4Wire()
            self.tenMegaOhm4Wire.exec()

        else:
            self.close()
            self.tenMegaOhm4Wire = TenMegaOhm4Wire()
            self.tenMegaOhm4Wire.exec()

class TenMegaOhm4Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10,000,000 ohm supplied 4 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 10 Mohm output from provided calibrator.\n"
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

            my_instrument.write("F4R6S0T0Y0B0?")
            my_instrument.read()

            self.res_10000000_4wire_reading = float(my_instrument.read().strip())

            run["res_10000000_4wire_short_slow_v"] = self.res_10000000_4wire_reading
            if 9998700.0 <= self.res_10000000_4wire_reading <= 10001300.0:
                run["res_10000000_4wire_short_slow_v_result"] = "PASS"
            else:
                run["res_10000000_4wire_short_slow_v_result"] = "FAIL"

            print(run["res_10000000_4wire_short_slow_v"])
            print(run["res_10000000_4wire_short_slow_v_result"])

            my_instrument.write("F4R6S1T0Y0B0?")
            my_instrument.read()

            self.res_10000000_4wire_reading = float(my_instrument.read().strip())

            run["res_10000000_4wire_short_med_v"] = self.res_10000000_4wire_reading
            if 9998500.0 <= self.res_10000000_4wire_reading <= 10001500.0:
                run["res_10000000_4wire_short_med_v_result"] = "PASS"
            else:
                run["res_10000000_4wire_short_med_v_result"] = "FAIL"

            print(run["res_10000000_4wire_short_med_v"])
            print(run["res_10000000_4wire_short_med_v_result"])

            my_instrument.write("F4R6S2T0Y0B0?")
            my_instrument.read()

            self.res_10000000_4wire_reading = float(my_instrument.read().strip())

            run["res_10000000_4wire_short_fast_v"] = self.res_10000000_4wire_reading
            if 9997000.0 <= self.res_10000000_4wire_reading <= 10003000.0:
                run["res_10000000_4wire_short_fast_v_result"] = "PASS"
            else:
                run["res_10000000_4wire_short_fast_v_result"] = "FAIL"

            print(run["res_10000000_4wire_short_fast_v"])
            print(run["res_10000000_4wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.hundredOhm2Wire = HundredOhm2Wire()
                self.hundredOhm2Wire.exec()
            elif fourWireConfig:
                self.close()
                self.testComplete = Completed()
                self.testComplete.exec()

class HundredOhm2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100 ohm supplied Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel(
            "Connect the HI and LO jacks of the calibrator output and Fluke 8840A input.\n"
            "Ensure that the HI Sense and LO Sense jacks are disconnected.")
        self.promptLabel.setStyleSheet("""
                                            font-size: 18px
                """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 100 ohm output from provided calibrator.\n"
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

            my_instrument.write("F3R1S0T0Y0B0?")
            my_instrument.read()

            self.res_100_2wire_reading = float(my_instrument.read().strip())

            run["res_100_2wire_short_slow_v"] = self.res_100_2wire_reading
            if 99.985 <= self.res_100_2wire_reading <= 100.015:
                run["res_100_2wire_short_slow_v_result"] = "PASS"
            else:
                run["res_100_2wire_short_slow_v_result"] = "FAIL"

            print(run["res_100_2wire_short_slow_v"])
            print(run["res_100_2wire_short_slow_v_result"])

            my_instrument.write("F3R1S1T0Y0B0?")
            my_instrument.read()

            self.res_100_2wire_reading = float(my_instrument.read().strip())

            run["res_100_2wire_short_med_v"] = self.res_100_2wire_reading
            if 99.983 <= self.res_100_2wire_reading <= 100.017:
                run["res_100_2wire_short_med_v_result"] = "PASS"
            else:
                run["res_100_2wire_short_med_v_result"] = "FAIL"

            print(run["res_100_2wire_short_med_v"])
            print(run["res_100_2wire_short_med_v_result"])

            my_instrument.write("F3R1S2T0Y0B0?")
            my_instrument.read()

            self.res_100_2wire_reading = float(my_instrument.read().strip())

            run["res_100_2wire_short_fast_v"] = self.res_100_2wire_reading
            if 99.960 <= self.res_100_2wire_reading <= 100.040:
                run["res_100_2wire_short_fast_v_result"] = "PASS"
            else:
                run["res_100_2wire_short_fast_v_result"] = "FAIL"

            print(run["res_100_2wire_short_fast_v"])
            print(run["res_100_2wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.thousandOhm2Wire = ThousandOhm2Wire()
            self.thousandOhm2Wire.exec()

        else:
            self.close()
            self.thousandOhm2Wire = ThousandOhm2Wire()
            self.thousandOhm2Wire.exec()

class ThousandOhm2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1000 ohm supplied 2 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 1000 ohm output from provided calibrator.\n"
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

            my_instrument.write("F3R2S0T0Y0B0?")
            my_instrument.read()

            self.res_1000_2wire_reading = float(my_instrument.read().strip())

            run["res_1000_2wire_short_slow_v"] = self.res_1000_2wire_reading
            if 999.87 <= self.res_1000_2wire_reading <= 1000.13:
                run["res_1000_2wire_short_slow_v_result"] = "PASS"
            else:
                run["res_1000_2wire_short_slow_v_result"] = "FAIL"

            print(run["res_1000_2wire_short_slow_v"])
            print(run["res_1000_2wire_short_slow_v_result"])

            my_instrument.write("F3R2S1T0Y0B0?")
            my_instrument.read()

            self.res_1000_2wire_reading = float(my_instrument.read().strip())

            run["res_1000_2wire_short_med_v"] = self.res_1000_2wire_reading
            if 999.85 <= self.res_1000_2wire_reading <= 1000.15:
                run["res_1000_2wire_short_med_v_result"] = "PASS"
            else:
                run["res_1000_2wire_short_med_v_result"] = "FAIL"

            print(run["res_1000_2wire_short_med_v"])
            print(run["res_1000_2wire_short_med_v_result"])

            my_instrument.write("F3R2S2T0Y0B0?")
            my_instrument.read()

            self.res_1000_2wire_reading = float(my_instrument.read().strip())

            run["res_1000_2wire_short_fast_v"] = self.res_1000_2wire_reading
            if 999.70 <= self.res_1000_2wire_reading <= 1000.30:
                run["res_1000_2wire_short_fast_v_result"] = "PASS"
            else:
                run["res_1000_2wire_short_fast_v_result"] = "FAIL"

            print(run["res_1000_2wire_short_fast_v"])
            print(run["res_1000_2wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.tenThousandOhm2Wire = TenThousandOhm2Wire()
                self.tenThousandOhm2Wire.exec()

            elif twoWireConfig:
                self.close()
                self.tenThousandOhm2Wire = TenThousandOhm2Wire()
                self.tenThousandOhm2Wire.exec()



class TenThousandOhm2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10,000 ohm supplied 2 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 10,000 ohm output from provided calibrator.\n"
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

            my_instrument.write("F3R3S0T0Y0B0?")
            my_instrument.read()

            self.res_10000_2wire_reading = float(my_instrument.read().strip())

            run["res_10000_2wire_short_slow_v"] = self.res_10000_2wire_reading
            if 9998.70 <= self.res_10000_2wire_reading <= 10001.30:
                run["res_10000_2wire_short_slow_v_result"] = "PASS"
            else:
                run["res_10000_2wire_short_slow_v_result"] = "FAIL"

            print(run["res_10000_2wire_short_slow_v"])
            print(run["res_10000_2wire_short_slow_v_result"])

            my_instrument.write("F3R3S1T0Y0B0?")
            my_instrument.read()

            self.res_10000_2wire_reading = float(my_instrument.read().strip())

            run["res_10000_2wire_short_med_v"] = self.res_10000_2wire_reading
            if 9998.50 <= self.res_10000_2wire_reading <= 10001.50:
                run["res_10000_2wire_short_med_v_result"] = "PASS"
            else:
                run["res_10000_2wire_short_med_v_result"] = "FAIL"

            print(run["res_10000_2wire_short_med_v"])
            print(run["res_10000_2wire_short_med_v_result"])

            my_instrument.write("F3R3S2T0Y0B0?")
            my_instrument.read()

            self.res_10000_2wire_reading = float(my_instrument.read().strip())

            run["res_10000_2wire_short_fast_v"] = self.res_10000_2wire_reading
            if 9997.00 <= self.res_10000_2wire_reading <= 10003.00:
                run["res_10000_2wire_short_fast_v_result"] = "PASS"
            else:
                run["res_10000_2wire_short_fast_v_result"] = "FAIL"

            print(run["res_10000_2wire_short_fast_v"])
            print(run["res_10000_2wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.hundredThousandOhm2Wire = HundredThousandOhm2Wire()
            self.hundredThousandOhm2Wire.exec()

        else:
            self.close()
            self.hundredThousandOhm2Wire = HundredThousandOhm2Wire()
            self.hundredThousandOhm2Wire.exec()

class HundredThousandOhm2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "100,000 ohm supplied 2 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 100,000 ohm output from provided calibrator.\n"
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

            my_instrument.write("F3R4S0T0Y0B0?")
            my_instrument.read()

            self.res_100000_2wire_reading = float(my_instrument.read().strip())

            run["res_100000_2wire_short_slow_v"] = self.res_100000_2wire_reading
            if 99987.0 <= self.res_100000_2wire_reading <= 100013.0:
                run["res_100000_2wire_short_slow_v_result"] = "PASS"
            else:
                run["res_100000_2wire_short_slow_v_result"] = "FAIL"

            print(run["res_100000_2wire_short_slow_v"])
            print(run["res_100000_2wire_short_slow_v_result"])

            my_instrument.write("F3R4S0T0Y0B0?")
            my_instrument.read()

            self.res_100000_2wire_reading = float(my_instrument.read().strip())

            run["res_100000_2wire_short_med_v"] = self.res_100000_2wire_reading
            if 99985.0 <= self.res_100000_2wire_reading <= 100015.0:
                run["res_100000_2wire_short_med_v_result"] = "PASS"
            else:
                run["res_100000_2wire_short_med_v_result"] = "FAIL"

            print(run["res_100000_2wire_short_med_v"])
            print(run["res_100000_2wire_short_med_v_result"])

            my_instrument.write("F3R4S0T0Y0B0?")
            my_instrument.read()


            self.res_100000_2wire_reading = float(my_instrument.read().strip())

            run["res_100000_2wire_short_fast_v"] = self.res_100000_2wire_reading
            if 99970.0 <= self.res_100000_2wire_reading <= 100030.0:
                run["res_100000_2wire_short_fast_v_result"] = "PASS"
            else:
                run["res_100000_2wire_short_fast_v_result"] = "FAIL"

            print(run["res_100000_2wire_short_fast_v"])
            print(run["res_100000_2wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.megaOhm2Wire = MegaOhm2Wire()
            self.megaOhm2Wire.exec()

        else:
            self.close()
            self.megaOhm2Wire = MegaOhm2Wire()
            self.megaOhm2Wire.exec()

class MegaOhm2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "1,000,000 ohm supplied 2 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 1 Mohm output from provided calibrator.\n"
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

            my_instrument.write("F3R5S0T0Y0B0?")
            my_instrument.read()

            self.res_1000000_2wire_reading = float(my_instrument.read().strip())

            run["res_1000000_2wire_short_slow_v"] = self.res_1000000_2wire_reading
            if 999870.0 <= self.res_1000000_2wire_reading <= 1000130.0:
                run["res_1000000_2wire_short_slow_v_result"] = "PASS"
            else:
                run["res_1000000_2wire_short_slow_v_result"] = "FAIL"

            print(run["res_1000000_2wire_short_slow_v"])
            print(run["res_1000000_2wire_short_slow_v_result"])

            my_instrument.write("F3R5S1T0Y0B0?")
            my_instrument.read()

            self.res_1000000_2wire_reading = float(my_instrument.read().strip())

            run["res_1000000_2wire_short_med_v"] = self.res_1000000_2wire_reading
            if 999850.0 <= self.res_1000000_2wire_reading <= 1000150.0:
                run["res_1000000_2wire_short_med_v_result"] = "PASS"
            else:
                run["res_1000000_2wire_short_med_v_result"] = "FAIL"

            print(run["res_1000000_2wire_short_med_v"])
            print(run["res_1000000_2wire_short_med_v_result"])

            my_instrument.write("F3R5S2T0Y0B0?")
            my_instrument.read()

            self.res_1000000_2wire_reading = float(my_instrument.read().strip())

            run["res_1000000_2wire_short_fast_v"] = self.res_1000000_2wire_reading
            if 999700.0 <= self.res_1000000_2wire_reading <= 1000300.0:
                run["res_1000000_2wire_short_fast_v_result"] = "PASS"
            else:
                run["res_1000000_2wire_short_fast_v_result"] = "FAIL"

            print(run["res_1000000_2wire_short_fast_v"])
            print(run["res_1000000_2wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()


            self.close()
            self.tenMegaOhm2Wire = TenMegaOhm2Wire()
            self.tenMegaOhm2Wire.exec()

        else:
            self.close()
            self.tenMegaOhm2Wire = TenMegaOhm2Wire()
            self.tenMegaOhm2Wire.exec()

class TenMegaOhm2Wire(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "10,000,000 ohm supplied 2 Wire Resistance Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 10 Mohm output from provided calibrator.\n"
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

            my_instrument.write("F3R6S0T0Y0B0?")
            my_instrument.read()

            self.res_10000000_2wire_reading = float(my_instrument.read().strip())

            run["res_10000000_2wire_short_slow_v"] = self.res_10000000_2wire_reading
            if 9998700.0 <= self.res_10000000_2wire_reading <= 10001300.0:
                run["res_10000000_2wire_short_slow_v_result"] = "PASS"
            else:
                run["res_10000000_2wire_short_slow_v_result"] = "FAIL"

            print(run["res_10000000_2wire_short_slow_v"])
            print(run["res_10000000_2wire_short_slow_v_result"])

            my_instrument.write("F3R6S1T0Y0B0?")
            my_instrument.read()

            self.res_10000000_2wire_reading = float(my_instrument.read().strip())

            run["res_10000000_2wire_short_med_v"] = self.res_10000000_2wire_reading
            if 9998500.0 <= self.res_10000000_2wire_reading <= 10001500.0:
                run["res_10000000_2wire_short_med_v_result"] = "PASS"
            else:
                run["res_10000000_2wire_short_med_v_result"] = "FAIL"

            print(run["res_10000000_2wire_short_med_v"])
            print(run["res_10000000_2wire_short_med_v_result"])

            my_instrument.write("F3R6S2T0Y0B0?")
            my_instrument.read()

            self.res_10000000_2wire_reading = float(my_instrument.read().strip())

            run["res_10000000_2wire_short_fast_v"] = self.res_10000000_2wire_reading
            if 9997000.0 <= self.res_10000000_2wire_reading <= 10003000.0:
                run["res_10000000_2wire_short_fast_v_result"] = "PASS"
            else:
                run["res_10000000_2wire_short_fast_v_result"] = "FAIL"

            print(run["res_10000000_2wire_short_fast_v"])
            print(run["res_10000000_2wire_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.dcCurrent0 = DCCurrent0()
                self.dcCurrent0.exec()
            elif twoWireConfig:
                self.close()
                self.testComplete = Completed()
                self.testComplete.exec()



class DCCurrent0(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Current Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.promptLabel = QLabel("Connect the 2A and LO jacks of the Fluke 8840A and provided Calibrator.")
        self.promptLabel.setStyleSheet("""
                                    font-size: 18px
        """)
        self.promptLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.promptLabel)

        self.textSpacer = QSpacerItem(0, 30)
        self.contentLayout.addItem(self.textSpacer)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 0 A output from provided calibrator.\n"
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

            my_instrument.write("F5R5D1S0T0Y0B0")
            my_instrument.read()

            self.dc_current_0_reading = float(my_instrument.read().strip())

            run["dc_current_0_short_slow_v"] = self.dc_current_0_reading
            if -0.00004 <= self.dc_current_0_reading <= 0.00004:
                run["dc_current_0_short_slow_v_result"] = "PASS"
            else:
                run["dc_current_0_short_slow_v_result"] = "FAIL"

            print(run["dc_current_0_short_slow_v"])
            print(run["dc_current_0_short_slow_v_result"])

            my_instrument.write("F5R5D1S1T0Y0B0")
            my_instrument.read()

            self.dc_current_0_reading = float(my_instrument.read().strip())

            run["dc_current_0_short_med_v"] = self.dc_current_0_reading
            if -0.00006 <= self.dc_current_0_reading <= 0.00006:
                run["dc_current_0_short_med_v_result"] = "PASS"
            else:
                run["dc_current_0_short_med_v_result"] = "FAIL"

            print(run["dc_current_0_short_med_v"])
            print(run["dc_current_0_short_med_v_result"])

            my_instrument.write("F5R5D1S2T0Y0B0")
            my_instrument.read()

            self.dc_current_0_reading = float(my_instrument.read().strip())

            run["dc_current_0_short_fast_v"] = self.dc_current_0_reading
            if -0.0002 <= self.dc_current_0_reading <= 0.0002:
                run["dc_current_0_short_fast_v_result"] = "PASS"
            else:
                run["dc_current_0_short_fast_v_result"] = "FAIL"

            print(run["dc_current_0_short_fast_v"])
            print(run["dc_current_0_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.dcCurrent1 = DCCurrent1()
            self.dcCurrent1.exec()

        else:
            self.close()
            self.dcCurrent1 = DCCurrent1()
            self.dcCurrent1.exec()


class DCCurrent1(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "DC Current Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)



        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 1 A output from provided calibrator.\n"
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

            my_instrument.write("F5R5D1S0T0Y0B0")
            my_instrument.read()

            self.dc_current_1_reading = float(my_instrument.read().strip())

            run["dc_current_1_short_slow_v"] = self.dc_current_1_reading
            if 0.99956 <= self.dc_current_1_reading <= 1.00044:
                run["dc_current_1_short_slow_v_result"] = "PASS"
            else:
                run["dc_current_1_short_slow_v_result"] = "FAIL"

            print(run["dc_current_1_short_slow_v"])
            print(run["dc_current_1_short_slow_v_result"])

            my_instrument.write("F5R5D1S1T0Y0B0")
            my_instrument.read()

            self.dc_current_1_reading = float(my_instrument.read().strip())

            run["dc_current_1_short_med_v"] = self.dc_current_1_reading
            if 0.99954 <= self.dc_current_1_reading <= 1.00046:
                run["dc_current_1_short_med_v_result"] = "PASS"
            else:
                run["dc_current_1_short_med_v_result"] = "FAIL"

            print(run["dc_current_1_short_med_v"])
            print(run["dc_current_1_short_med_v_result"])

            my_instrument.write("F5R5D1S2T0Y0B0")
            my_instrument.read()

            self.dc_current_1_reading = float(my_instrument.read().strip())

            run["dc_current_1_short_fast_v"] = self.dc_current_1_reading
            if 0.99940 <= self.dc_current_1_reading <= 1.0006:
                run["dc_current_1_short_fast_v_result"] = "PASS"
            else:
                run["dc_current_1_short_fast_v_result"] = "FAIL"

            print(run["dc_current_1_short_fast_v"])
            print(run["dc_current_1_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.acCurrent19 = ACCurrent19()
                self.acCurrent19.exec()
            elif dcCurrentConfig:
                self.close()
                self.testComplete = Completed()
                self.testComplete.exec()


#---------------------------------------------------------- Implement Branch Selection here



class ACCurrent0(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Current 0.1 A Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 0.1 A output at 1 kHz from provided calibrator.\n"
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

            my_instrument.write("F6R5D1S0T0Y0B0")
            my_instrument.read()

            self.ac_current_0_reading = float(my_instrument.read().strip())

            run["ac_current_0_short_slow_v"] = self.ac_current_0_reading
            if 0.09760 <= self.ac_current_0_reading <= 0.10240:
                run["ac_current_0_short_slow_v_result"] = "PASS"
            else:
                run["ac_current_0_short_slow_v_result"] = "FAIL"

            print(run["ac_current_0_short_slow_v"])
            print(run["ac_current_0_short_slow_v_result"])

            my_instrument.write("F6R5D1S1T0Y0B0")
            my_instrument.read()

            self.ac_current_0_reading = float(my_instrument.read().strip())

            run["ac_current_0_short_med_v"] = self.ac_current_0_reading
            if 0.09760 <= self.ac_current_0_reading <= 0.10240:
                run["ac_current_0_short_med_v_result"] = "PASS"
            else:
                run["ac_current_0_short_med_v_result"] = "FAIL"

            print(run["ac_current_0_short_med_v"])
            print(run["ac_current_0_short_med_v_result"])

            my_instrument.write("F6R5D1S2T0Y0B0")
            my_instrument.read()

            self.ac_current_0_reading = float(my_instrument.read().strip())

            run["ac_current_0_short_fast_v"] = self.ac_current_0_reading
            if 0.09760 <= self.ac_current_0_reading <= 0.10240:
                run["ac_current_0_short_fast_v_result"] = "PASS"
            else:
                run["ac_current_0_short_fast_v_result"] = "FAIL"

            print(run["ac_current_0_short_fast_v"])
            print(run["ac_current_0_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            if allTests:
                self.close()
                self.acCurrent19 = ACCurrent19()
                self.acCurrent19.exec()

            elif acCurrentConfig:
                self.close()
                self.acCurrent19 = ACCurrent19()
                self.acCurrent19.exec()

class ACCurrent19(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "AC Current 1.9 A Verification"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)


        self.actionLabel = QLabel("Continue by supplying Fluke 8840A with 1.9 A output at 1 kHz from provided calibrator.\n"
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

            my_instrument.write("F6R5D1S0T0Y0B0")
            my_instrument.read()

            self.ac_current_19_reading = float(my_instrument.read().strip())

            run["ac_current_19_short_slow_v"] = self.ac_current_19_reading
            if 1.89040 <= self.ac_current_19_reading <= 1.90960:
                run["ac_current_19_short_slow_v_result"] = "PASS"
            else:
                run["ac_current_19_short_slow_v_result"] = "FAIL"

            print(run["ac_current_19_short_slow_v"])
            print(run["ac_current_19_short_slow_v_result"])

            my_instrument.write("F6R5D1S1T0Y0B0")
            my_instrument.read()

            self.ac_current_19_reading = float(my_instrument.read().strip())

            run["ac_current_19_short_med_v"] = self.ac_current_19_reading
            if 1.89040 <= self.ac_current_19_reading <= 1.90960:
                run["ac_current_19_short_med_v_result"] = "PASS"
            else:
                run["ac_current_19_short_med_v_result"] = "FAIL"

            print(run["ac_current_19_short_med_v"])
            print(run["ac_current_19_short_med_v_result"])

            my_instrument.write("F6R5D1S2T0Y0B0")
            my_instrument.read()

            self.ac_current_19_reading = float(my_instrument.read().strip())

            run["ac_current_19_short_fast_v"] = self.ac_current_19_reading
            if 1.89040 <= self.ac_current_19_reading <= 1.90960:
                run["ac_current_19_short_fast_v_result"] = "PASS"
            else:
                run["ac_current_19_short_fast_v_result"] = "FAIL"

            print(run["ac_current_19_short_fast_v"])
            print(run["ac_current_19_short_fast_v_result"])

            my_instrument.write("F1R1S0T0Y0B0?")
            my_instrument.read()

            self.close()
            self.testComplete = Completed()
            self.testComplete.exec()

        else:
            self.close()
            self.testComplete = Completed()
            self.testComplete.exec()



class Completed(QDialog):
    def __init__(self):
        super().__init__()

        self.windowTitle = "Temp Test Complete Route"
        self.setFixedSize(800, 300)

        self.contentLayout = QVBoxLayout()

        self.contentLayout.addStretch(1)

        self.actionLabel = QLabel(
            "HOOORAYYYYYYYYYYYYYYYYYYYYYYYYYY!")
        self.actionLabel.setStyleSheet("""
                                                    font-size: 18px;
                                                    font-weight: bold;
                        """)
        self.actionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentLayout.addWidget(self.actionLabel)


        self.setLayout(self.contentLayout)









if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FlukePerformance()
    window.show()
    sys.exit(app.exec())