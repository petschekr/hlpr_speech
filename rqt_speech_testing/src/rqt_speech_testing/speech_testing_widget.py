import os
import signal
import threading

import rospkg
import rospy
from python_qt_binding import loadUi
from python_qt_binding.QtCore import Qt, Signal, qWarning
from python_qt_binding.QtGui import (QApplication, QFileDialog, QHeaderView, QIcon,
                                     QMessageBox, QTreeWidgetItem, QWidget)

from hlpr_speech_recognition.speech_recognizer import SpeechRecognizer


class SpeechTestWidget(QWidget):
    """
    Widget for testing speech recognition
    Handles all widget callbacks
    """

    def __init__(self, context):
        super(SpeechTestWidget, self).__init__()
        ui_file = os.path.join(rospkg.RosPack().get_path(
            "rqt_speech_testing"), "resource", "SpeechTest.ui")
        loadUi(ui_file, self)

        self.setObjectName('SpeechTestUi')
        self.setWindowTitle(self.windowTitle() + (' (%d)' %
                                                  context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self)

        self.recognizer = SpeechRecognizer(subnode=True)

        # Set icons for buttons because they don't persist from Qt creator
        self.openLocationButton.setIcon(QIcon.fromTheme("document-open"))
        self.recordButton.setIcon(QIcon.fromTheme("media-record"))

        # Attach event handlers
        self.openLocationButton.clicked[bool].connect(self.openAudio)
        self.location.returnPressed.connect(self.loadAudio)
        self.recordButton.toggled.connect(self.recordAudio)

    def openAudio(self):
        location = QFileDialog.getOpenFileName(filter="*.wav;;*", directory=os.path.dirname(self.location.text()))[0]
        if not location:
            return
        self.location.setText(location)
        self.loadAudio()

    def loadAudio(self):
        location = self.location.text()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.recognizer.begin_rec(file=location)
        QApplication.restoreOverrideCursor()

    def recordAudio(self, state):
        if state:
            threading.Thread(target=self.recordAudioThread).start()
        else:
            self.recognizer.end_rec()

    def loadAudioThread(self, file):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.recognizer.begin_rec(file=file)
        QApplication.restoreOverrideCursor()

    def recordAudioThread(self):
        self.recognizer.begin_rec()
