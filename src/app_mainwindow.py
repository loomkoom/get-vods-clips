# Controller (receiving input)

import sys

from PyQt5 import QtCore, QtWidgets
from UI_mainwindow import Ui_MainWindow
from app_model import Model


class MainWindow_app(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        """Initialize the super class"""
        super().__init__(*args, **kwargs)
        self.model = Model()
        sys.stdout = EmittingStream(textWritten = self.LogPrint)
        sys.stderr = EmittingStream(textWritten = self.LogPrint)

    def setupUi(self, MW):
        """ Setup the UI of the super class, and add here code
        that relates to the way we want our UI to operate."""
        super().setupUi(MW)

        self.pushButton_start.clicked.connect(self.get_info)
        self.pushButton_download.clicked.connect(self.test)
        self.radioButton_latest.clicked.connect(self.set_widget)
        self.radioButton_all.clicked.connect(self.set_widget)
        self.radioButton_date.clicked.connect(self.set_widget)
        self.radioButton_daterange.clicked.connect(self.set_widget)

    def test(self):
        self.textBrowser_logs_2.append(
            f"<a href='https://clips-media-assets2.twitch.tv/40697511198-offset-5876.mp4'>https://clips-media-assets2.twitch.tv/40697511198-offset-5876.mp4</a>")
        self.textBrowser_logs_2.append(
            f"<a href='https://vod-secure.twitch.tv/a165eac6f976c52dda31_buhn_39915836510_1601514163/chunked/index-dvr.m3u8'>https://vod-secure.twitch.tv/a165eac6f976c52dda31_buhn_39915836510_1601514163/chunked/index-dvr.m3u8</a>")

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def set_progressbar(self, progress):
        self.progressBar_links.setValue(int(progress))

    def LogPrint(self, msg):
        """Prints logs in logtext box."""
        if "%" in msg:
            progress = msg[(msg.find("% done") - 3):(msg.find("% done"))]
            self.set_progressbar(progress)
        if "URL:" in msg:
            link = msg[(msg.find("URL:") + 4):(msg.find("\nstreams"))].strip()
            if "no" not in link[2:5]:
                msg = msg.replace(link, f" <a href='{link}'>{link}</a> ")

        self.set_stream_info(msg)
        self.textBrowser_logs.append(msg)

    def set_stream_info(self, msg):
        if "TITLE:" in msg:
            text = msg[(msg.find("TITLE:") + 6):(msg.find(", CATEGORIES:"))]
            self.textBrowser_title.setText(text)
        if "LENGTH:" in msg:
            text = msg[(msg.find("LENGTH:") + 7):(msg.find(", TITLE:"))]
            self.textBrowser_length.setText(text)
        if "DATE:" in msg:
            text = msg[(msg.find("DATE:") + 5):(msg.find(", ID:"))]
            self.textBrowser_timestamp.setText(text)
        if "CATEGORIES:" in msg:
            text = msg[(msg.find("CATEGORIES:") + 11):(msg.find(", \nURL:"))]
            self.textBrowser_categories.setText(text)

    def get_info(self):
        """ Called when a the get links button is pressed"""
        channel_name = self.lineEdit_channelname.text()
        if self.radioButton_clips.isChecked():
            vods_clips = "clips"
        elif self.radioButton_vods.isChecked():
            vods_clips = "vods"
        else:
            vods_clips = ""
        if self.radioButton_all.isChecked():
            date_type = "all"
            date = [None, None, 0]
        elif self.radioButton_latest.isChecked():
            date_type = "latest"
            date = [None, None, self.comboBox_latest.currentText()]
        elif self.radioButton_date.isChecked():
            date_type = "date"
            date = [self.dateEdit_date.date().toString(QtCore.Qt.ISODate), self.dateEdit_date.date().toString(QtCore.Qt.ISODate)]
        elif self.radioButton_daterange.isChecked():
            date_type = "daterange"
            date = [self.dateEdit_dateStart.date().toString(QtCore.Qt.ISODate), self.dateEdit_dateEnd.date().toString(QtCore.Qt.ISODate)]
        else:
            date_type = ""
            date = ""
        data = [channel_name, vods_clips, date_type, date]
        if self.model.link_data_isvalid(data):
            self.thread = QtCore.QThread()
            self.worker = Worker(data)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
        else:
            m = QtWidgets.QMessageBox()
            m.setText(f"Invalid Data entered!\n channel:'{data[0]}', vods/clips:'{data[1]}', datetype:'{data[2]}', date:'{data[3]}'")
            m.setIcon(QtWidgets.QMessageBox.Warning)
            m.setStandardButtons(QtWidgets.QMessageBox.Ok
                                 | QtWidgets.QMessageBox.Cancel)
            m.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            m.exec_()
            self.LogPrint(f"Invalid Data entered!\n + channel:'{data[0]}', vods/clips:'{data[1]}', datetype:'{data[2]}', date:'{data[3]}'")

    def set_widget(self):
        """ Called when a date radiobutton is pressed"""
        names = ["All", "Latest", "Date", "Date Range"]
        radiobtn = self.sender().text()
        index = names.index(radiobtn)
        self.stackedwidget.setCurrentIndex(index)


class Worker(QtCore.QObject):

    def __init__(self, data):
        super().__init__()
        self.model = Model()
        self.data = data

    # method which will execute algorithm in another thread
    def run(self):
        self.model.set_data(self.data)
        self.model.get_links()


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


def main():
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()

    ui = MainWindow_app()
    ui.setupUi(MainWindow)

    MainWindow.show()
    app.exec_()


if __name__ == "__main__":
    sys.excepthook = trap_exc_during_debug
    main()
