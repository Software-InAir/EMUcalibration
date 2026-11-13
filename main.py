import sys

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QPixmap

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication, QSpacerItem, QRadioButton, \
    QHBoxLayout, QPushButton

from Fluke import DMM
from Philips import PM
from Amrel import PPS
from CaliforniaInstruments import RP


#import instruments

USE_INSTRUMENT = True
DMM_ONE = True
PS_ONE = False
PS_TWO = False
PS_THREE = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            self.setWindowTitle("EMU Test Stand Calibration")
            self.setFixedSize(1280, 635)

            self.welcome = QWidget()
            self.setCentralWidget(self.welcome)

            self.welcomeLayout = QVBoxLayout()

            self.fluke = None
            self.amrel = None
            self.californiainstruments = None
            self.philips = None

            logoimage = "InAir"
            self.Logo = QPixmap(f"Images\\InAir.png")
            self.logoLabel = QLabel(self)
            self.logoLabel.setPixmap(self.Logo)
            self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logoLabel.setContentsMargins(100, 0, 100, 40)
            self.welcomeLayout.addWidget(self.logoLabel)

            spacer = QSpacerItem(0, 30)
            self.welcomeLayout.addSpacerItem(spacer)

            self.welcomeLabel = QLabel("InAir Electro-Mechanical Units TS Calibration")
            self.welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.welcomeLabel.setContentsMargins(100, 0, 100, 40)
            self.welcomeLayout.addWidget(self.welcomeLabel)
            self.welcomeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            spacer1 = QSpacerItem(0, 30)
            self.welcomeLayout.addSpacerItem(spacer1)

            self.bodyPrompt = QVBoxLayout()

            self.bodyLayout = QHBoxLayout()

            self.bodyButtons = QVBoxLayout()

            self.selectionPrompt = QLabel("Please select a test stand component to begin calibration: ")
            self.selectionPrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.selectionPrompt.setContentsMargins(100, 0, 100, 40)
            self.bodyPrompt.addWidget(self.selectionPrompt)
            self.bodyPrompt.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.welcomeLayout.addLayout(self.bodyPrompt)

            spacer2 = QSpacerItem(0, 10)
            self.welcomeLayout.addSpacerItem(spacer2)

            self.PSselectionLabel = QLabel("Test Stand Unit")
            self.PSselectionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # self.PSselectionLabel.setContentsMargins(100, 0, 100, 40)
            self.bodyLayout.addWidget(self.PSselectionLabel)

            self.DMMone = QRadioButton("Fluke 8840A")
            self.DMMone.setChecked(True)
            self.bodyButtons.addWidget(self.DMMone)

            self.PSone = QRadioButton("California Instruments 1251RP")
            self.PSone.setChecked(False)
            self.bodyButtons.addWidget(self.PSone)

            self.PStwo = QRadioButton("Amrel PPS-35-D2")
            self.PStwo.setChecked(False)
            self.bodyButtons.addWidget(self.PStwo)

            self.PSthree = QRadioButton("Philips PM2811")
            self.PSthree.setChecked(False)
            self.bodyButtons.addWidget(self.PSthree)

            self.bodyLayout.addLayout(self.bodyButtons)
            self.welcomeLayout.addLayout(self.bodyLayout)

            spacer3 = QSpacerItem(0, 60)
            self.welcomeLayout.addSpacerItem(spacer3)

            self.confirmbutton = QPushButton("Begin")
            self.confirmbutton.setFixedWidth(100)
            self.confirmbutton.setFixedHeight(100)
            self.confirmbutton.setStyleSheet(""
                                             "background-color: rgb(0, 200, 50);"
                                             "color: rgb(255, 255, 255);")
            self.confirmbutton.clicked.connect(self.confirmButtonClicked)
            self.welcomeLayout.addWidget(self.confirmbutton, alignment=Qt.AlignmentFlag.AlignCenter)

            spacer4 = QSpacerItem(0, 60)
            self.welcomeLayout.addSpacerItem(spacer4)

            self.welcome.setLayout(self.welcomeLayout)


        except Exception as e:
            print(f"Error: {e}")

    def confirmButtonClicked(self):
        try:

            if self.DMMone.isChecked():
                DMM_ONE = True
                self.fluke = DMM()
                self.fluke.exec()

            if self.PSone.isChecked():
                PS_ONE = True
                self.californiainstruments = RP()
                self.californiainstruments.show()

            if self.PStwo.isChecked():
                PS_ONE = True
                self.amrel = PPS()
                self.amrel.show()

            if self.PSthree.isChecked():
                PS_ONE = True
                self.philips = PM()
                self.philips.show()

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
