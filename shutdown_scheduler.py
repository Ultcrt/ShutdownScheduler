import datetime
import os
import winsound
from PyQt5 import QtCore, QtWidgets, QtGui


class Ui_SchedulerWindow(object):
    def setupUi(self, SchedulerWindow):
        SchedulerWindow.setObjectName("SchedulerWindow")
        SchedulerWindow.resize(308, 125)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SchedulerWindow.sizePolicy().hasHeightForWidth())
        SchedulerWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(SchedulerWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit.setGeometry(QtCore.QRect(100, 10, 201, 22))
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.target_label = QtWidgets.QLabel(self.centralwidget)
        self.target_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        self.target_label.setObjectName("target_label")
        self.countdown_label = QtWidgets.QLabel(self.centralwidget)
        self.countdown_label.setGeometry(QtCore.QRect(10, 50, 81, 21))
        self.countdown_label.setObjectName("countdown_label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setGeometry(QtCore.QRect(100, 50, 201, 20))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.submit_button = QtWidgets.QPushButton(self.centralwidget)
        self.submit_button.setGeometry(QtCore.QRect(60, 80, 75, 31))
        self.submit_button.setObjectName("submit_button")
        self.withdrew_button = QtWidgets.QPushButton(self.centralwidget)
        self.withdrew_button.setGeometry(QtCore.QRect(170, 80, 75, 31))
        self.withdrew_button.setObjectName("withdrew_button")
        SchedulerWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SchedulerWindow)
        QtCore.QMetaObject.connectSlotsByName(SchedulerWindow)

    def retranslateUi(self, SchedulerWindow):
        _translate = QtCore.QCoreApplication.translate
        SchedulerWindow.setWindowTitle(_translate("SchedulerWindow", "关机计划"))
        self.target_label.setText(_translate("SchedulerWindow", "输入关机时间："))
        self.countdown_label.setText(_translate("SchedulerWindow", "关机倒计时："))
        self.submit_button.setText(_translate("SchedulerWindow", "提交"))
        self.withdrew_button.setText(_translate("SchedulerWindow", "撤销"))


class SchedulerWindow(QtWidgets.QMainWindow, Ui_SchedulerWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.show()

        # initial datetime
        self.target_stamp = None
        cur_time = datetime.datetime.now()
        self.dateTimeEdit.setMinimumDateTime(cur_time)
        self.dateTimeEdit.setDateTime(cur_time)

        # refresh
        self.timer = QtCore.QTimer()

        # connect to slot
        self.timer.timeout.connect(self.refresh)
        self.submit_button.clicked.connect(self.submit_slot)
        self.withdrew_button.clicked.connect(self.withdrew_slot)

    def refresh(self):
        delta_stamp = self.target_stamp - datetime.datetime.now().timestamp()
        # 1min waring
        if delta_stamp < 60:
            self.lineEdit.setStyleSheet("color : red;")
            # 10s warning
            if delta_stamp < 10:
                winsound.Beep(1000, 250)
        seconds = delta_stamp % 60
        minutes = int(delta_stamp / 60) % 60
        hours = int(int(delta_stamp / 60) / 60) % 24
        days = int(int(int(delta_stamp / 60) / 60) / 24)
        self.lineEdit.setText("%02d天 %02d:%02d:%02d" % (days, hours, minutes, seconds))
        # reset timer
        self.timer.start(1000)

    def submit_slot(self):
        submit_stamp = datetime.datetime.now().timestamp()
        tentative_target_stamp = self.dateTimeEdit.dateTime().toPyDateTime().timestamp()
        # target time is illegal -> insult user
        if submit_stamp > tentative_target_stamp:
            QtWidgets.QMessageBox.warning(self, "目标时间点已过", "You want a time machine? You dickhead.")
        # shutdown now -> insult user
        elif submit_stamp == tentative_target_stamp:
            QtWidgets.QMessageBox.warning(self, "目标时间点与当前时间相同",
                                          "Can't you press your power button? You lazy-ass.")
        # shutdown /t xxx, where xxx ranges from 0 to 315360000 -> insult user
        elif tentative_target_stamp - submit_stamp > 315360000:
            QtWidgets.QMessageBox.warning(self, "目标时间点过长", "You want to shutdown after 10 years? You dumb-ass.")
        # legal
        else:
            # extra 3s serves as buffer
            self.target_stamp = tentative_target_stamp + 3
            delta_time = int(self.target_stamp - submit_stamp)
            os.system("shutdown /a")
            os.system("shutdown /s /t %d" % delta_time)
            self.timer.start(1000)

    def withdrew_slot(self):
        os.system("shutdown /a")
        self.timer.stop()
        self.lineEdit.setText("")
        self.setStyleSheet("color : black;")
        QtWidgets.QMessageBox.information(self, "关机计划已取消", "You are a fucking liar.")

    def closeEvent(self, event: QtGui.QCloseEvent):
        os.system("shutdown /a")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main_window = SchedulerWindow()
    app.exec_()
