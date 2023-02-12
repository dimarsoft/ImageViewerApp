import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel


class ShowImage(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(450, 300, 1000, 500)
        self.setWindowTitle('Программа просмотра картинки')
        self.header = QLabel(self)
        self.header.move(400, 20)
        self.header.setText('Программа просмотра картинки')
        self.choice_image = QPushButton(self)
        self.choice_image.setGeometry(10, 450, 980, 40)
        self.choice_image.setText("Выбрать картинку")
        self.choice_image.clicked.connect(self.select_image_file)
        self.current = 'beauty.jpg'
        self.pixmap = QPixmap(self.current)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(900, 50)
        self.show()

    def select_image_file(self):
        pass

    def when_a_picture_is_selected(self, file_name):
        self.current = 'beauty.jpg'
        self.pixmap = QPixmap(self.current)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    si = ShowImage()
    si.show()
    sys.exit(app.exec())
