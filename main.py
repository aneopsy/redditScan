from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread
import sys
import UI.gui
import urllib.request
import json
import codecs


class getPostsThread(QThread):

    add_post = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self, subreddits, nbrResult):
        QThread.__init__(self)
        self.subreddits = subreddits
        self.nbrResult = nbrResult

    def __del__(self):
        self.wait()

    @staticmethod
    def _get_top_post(subreddit, nbrResult):
        url = "https://www.reddit.com/r/{}.json?limit={}".format(subreddit, nbrResult)
        headers = {'User-Agent': 'AneoPsy'}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        reader = codecs.getreader("utf-8")
        data = json.load(reader(response))
        return_value = []
        for top_post in data['data']['children']:
            return_value.append("'{title}' by {author} in {subreddit}".format(**top_post['data']))
        return return_value

    def run(self):
        for subreddit in self.subreddits:
            top_post = self._get_top_post(subreddit, self.nbrResult)
            self.add_post.emit(top_post)
            self.sleep(1)
        self.finished.emit()


class RedditScan(QtWidgets.QMainWindow, UI.gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.btn_start.clicked.connect(self.start_getting_top_posts)

    def start_getting_top_posts(self):
        subreddit_list = str(self.edit_subreddits.text()).split(',')
        nbr_result = int(self.spinBox.value())
        if subreddit_list == ['']:
            QtWidgets.QMessageBox.critical(self, "No subreddits",
                                           "You didn't enter any subreddits.", QtWidgets.QMessageBox.Ok)
            return
        self.progress_bar.setMaximum(len(subreddit_list) * nbr_result)
        self.progress_bar.setValue(0)
        self.get_thread = getPostsThread(subreddit_list, nbr_result)
        self.get_thread.add_post.connect(self.add_post)
        self.get_thread.finished.connect(self.done)
        self.get_thread.start()
        self.btn_stop.setEnabled(True)
        self.btn_stop.clicked.connect(self.get_thread.terminate)
        self.btn_start.setEnabled(False)

    def add_post(self, post_text):
        for i in post_text:
            self.list_submissions.addItem(i)
            self.progress_bar.setValue(self.progress_bar.value() + 1)

    def done(self):
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    box = RedditScan()
    box.show()
    app.exec_()

if __name__ == '__main__':
    main()