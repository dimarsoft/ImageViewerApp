import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QFileDialog, QGridLayout, \
    QScrollArea


class ShowImage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Программа просмотра картинки')

        self.scroll_area = QScrollArea()
        grid = QGridLayout()
        # elf.setLayout(grid)

        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        self.path_caption = QLabel(self)
        self.path_caption.setText('Путь к файлу:')

        self.header = QLabel(self)
        self.header.setText('')

        grid.addWidget(self.path_caption, 0, 0)
        grid.addWidget(self.header, 1, 0)

        self.choice_image = QPushButton(self)
        self.choice_image.setGeometry(10, 450, 980, 40)
        self.choice_image.setText("Выбрать картинку")
        self.choice_image.setStyleSheet("background-color:white;\n"
                                        "border-style: outset;\n"
                                        "border-width:2px;\n"
                                        "border-radius:15px;\n"
                                        "border-color:black;")
        self.choice_image.setMinimumWidth(150)
        self.choice_image.setMinimumHeight(50)
        grid.addWidget(self.choice_image, 3, 0, alignment=Qt.AlignCenter)

        self.choice_image.clicked.connect(self.select_image_file)
        self.current = ''
        self.pixmap = QPixmap()

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(900, 50)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image)

        grid.addWidget(self.scroll_area, 2, 0)

    def select_image_file(self):
        # getOpenFileName Return type:
        # (fileName, selectedFilter)
        # selectedFilter - выбранный пользователем фильтр по типу файлов,
        # selectedFilter нам не нужен, поэтому _
        file_name, _ = QFileDialog.getOpenFileName(self, "Select image file", "",
                                                   "All Files (*);;Jpeg Files (*.jpg)")

        if file_name:
            self.show_image(file_name)

    def show_image(self, file_name):
        self.header.setText(file_name)
        self.current = file_name
        self.pixmap.load(file_name)
        self.image.resize(self.pixmap.width(), self.pixmap.height())
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    si = ShowImage()
    si.showMaximized()
    sys.exit(app.exec())
