import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QFileDialog, QGridLayout, \
    QScrollArea, QToolBar


# Класс ShowImage является главным окном программы
class ShowImage(QMainWindow):
    def __init__(self):
        # Инициализация родительского класса
        super().__init__()
        # Установка заголовка окна
        self.setWindowTitle('Программа просмотра картинки')

        # Создание области прокрутки
        self.scroll_area = QScrollArea()
        # Создание табличного макета
        grid = QGridLayout()

        # Создание виджета
        widget = QWidget()
        # Установка табличного макета в виджет
        widget.setLayout(grid)
        # Установка виджета в центральный виджет окна
        self.setCentralWidget(widget)

        # Создание заголовка для пути к файлу
        self.path_caption = QLabel(self)
        self.path_caption.setText('Путь к файлу:')

        # Создание заголовка для отображения пути к текущему изображению
        self.header = QLabel(self)
        self.header.setText('')

        # Добавление заголовка пути к файлу в табличный макет
        grid.addWidget(self.path_caption, 0, 0)
        # Добавление пути в  табличный макет

        grid.addWidget(self.header, 1, 0)

        # панель инструментов
        toolbar = QToolBar("Main toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setFixedHeight(32)
        self.addToolBar(toolbar)

        self.image_zoom = 1.0
        self.zoom_plus = QPushButton(self)
        self.zoom_plus.setGeometry(0, 0, 64, 32)
        self.zoom_plus.setText(" + ")
        self.zoom_plus.setStyleSheet("background-color:white;\n"
                                     "border-style: outset;\n"
                                     "border-width:2px;\n"
                                     "border-radius:15px;\n"
                                     "border-color:black;")
        # lambda это такая локальная мини функция
        # connect(self.change_zoom) нельзя, т.к. есть параметр - масштаб
        # а писать отдельно change_zoom_plus, change_zoom_minus не обязятельно :)
        self.zoom_plus.clicked.connect(lambda: self.change_zoom(1.2))

        self.zoom_minus = QPushButton(self)
        self.zoom_minus.setText(" - ")
        self.zoom_minus.setStyleSheet("background-color:white;\n"
                                      "border-style: outset;\n"
                                      "border-width:2px;\n"
                                      "border-radius:15px;\n"
                                      "border-color:black;")
        self.zoom_minus.clicked.connect(lambda: self.change_zoom(0.8))

        # Двк кнопки на панели инструментов

        toolbar.addWidget(self.zoom_plus)
        toolbar.addWidget(self.zoom_minus)

        # Кнопка для выбора файла
        self.choice_image = QPushButton(self)
        self.choice_image.setGeometry(10, 450, 980, 40)
        self.choice_image.setText("Выбрать картинку")
        self.choice_image.setStyleSheet("background-color:white;\n"
                                        "border-style: outset;\n"
                                        "border-width:2px;\n"
                                        "border-radius:15px;\n"
                                        "border-color:black;")
        # кнопка будет в Gridlayout и размеры будут меняться, но зададим мнимальные
        self.choice_image.setMinimumWidth(150)
        self.choice_image.setMinimumHeight(50)
        grid.addWidget(self.choice_image, 3, 0, alignment=Qt.AlignCenter)

        # действие при нажатии на кнопку
        self.choice_image.clicked.connect(self.select_image_file)

        # пока файл не выбран, поле пустое
        self.current = ''

        # объект для загрузки картинки создаем

        self.pixmap = QPixmap()

        # отображение картинки на форме

        self.image = QLabel()

        self.image.setScaledContents(True)

        # контрол для картинки вносим в scroll_area
        self.scroll_area.setWidget(self.image)

        grid.addWidget(self.scroll_area, 2, 0)

    def change_zoom(self, change_value):
        new_zoom = self.image_zoom * change_value

        if new_zoom > 100:
            new_zoom = 100
        elif new_zoom < 0.001:
            new_zoom = 0.001
        self.image_zoom = new_zoom

        self.resize_image()

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
        self.image.setPixmap(self.pixmap)
        self.resize_image()

    def resize_image(self):
        new_width = self.pixmap.width() * self.image_zoom
        new_height = self.pixmap.height() * self.image_zoom

        print(f"new_width = {new_width}, new_height = {new_height}")

        self.image.resize(self.pixmap.size() * self.image_zoom)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    si = ShowImage()
    si.showMaximized()
    sys.exit(app.exec())
