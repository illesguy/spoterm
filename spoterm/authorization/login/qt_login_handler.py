from PyQt5.Qt import QUrl
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from spoterm.authorization.login.login_handler import LoginHandler


class QtLoginHandlerMeta(type(QDialog), type(LoginHandler)):
    pass


class QtLoginHandler(QDialog, LoginHandler, metaclass=QtLoginHandlerMeta):

    def __init__(self):
        self.app = QApplication([])
        QDialog.__init__(self)
        self.resize(1200, 900)
        self.login_view = QWebEngineView(self)
        self.login_view.resize(self.width(), self.height())
        self.login_view.hide()

    def login(self, login_url: str, redirect_uri: str) -> str:
        self.login_view.load(QUrl(login_url))
        self.login_view.urlChanged.connect(lambda *args, **kwargs: self.check_url(redirect_uri))
        self.exec_()
        return self.login_view.url().toString()

    def check_url(self, redirect_uri):
        if self.login_view.url().toString().startswith(redirect_uri):
            self.close()
        else:
            self.login_view.show()
