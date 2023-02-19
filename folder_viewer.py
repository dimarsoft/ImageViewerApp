import sys
import numpy as np
from pathlib import Path

from PyQt5.QtGui import QPixmap, QPainter, QPen, QIntValidator, QFont, QColor
from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QFileDialog, QGridLayout, \
    QScrollArea, QToolBar, QLineEdit, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem

from enum import Enum


class Labels(Enum):
    human = 0
    helmet = 1
    uniform = 2


class DetectedLabel:
    def __init__(self, label, x, y, width, height):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.above = None


class ViewImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        # пока файл не выбран, поле пустое
        self.current = ''
        self.labels = []


        # объект для загрузки картинки создаем

        self.pixmap = QPixmap()

        self.image_zoom = 1

        self.line_a = -0.2
        self.line_b = 0.68

        QColor(0, 255, 255)
        self.pen = QPen(Qt.red, 2)

        self.pens = {Labels.human: QPen(QColor(0, 255, 255), 1),
                     Labels.helmet: QPen(QColor(255, 0, 255), 1),
                     Labels.uniform: QPen(QColor(255, 255, 255), 1)}

        self.pen_above = QPen(Qt.green, 1)
        self.pen_below = QPen(Qt.red, 1)

        self.folder_label_path = "d:\\AI\\2023\\Github\\yolov7\\runs\\detect\\exp7\\labels"
        self.folder_label_path = "d:\\AI\\2023\\corridors\\dataset-v1.0\\train\\labels"

    def set_ab(self, a, b):
        self.line_a = a
        self.line_b = b
        self.repaint()

    @staticmethod
    def parse_row(info):
        box = info.split(" ")
        if np.char.isnumeric(box[0].replace('\n', '')):
            return DetectedLabel(Labels(int(box[0])), float(box[1]), float(box[2]), float(box[3]), float(box[4]))

        return None

    def test_human(self, label):

        y_turniket = self.get_y(label.x)

        if y_turniket > label.y:
            label.above = True
        else:
            label.above = False

    def read_labels(self, image_number):
        labels = []
        labels_file = f"{self.folder_label_path}/{image_number}.txt"
        try:
            with open(labels_file, 'r') as handle:
                box_info = handle.readlines()
                for txt in box_info:
                    lab = self.parse_row(txt)
                    if lab is not None:
                        if lab.label is Labels.human:
                            self.test_human(lab)
                        labels.append(lab)
                return labels
        except FileNotFoundError as e:
            print(labels_file, e)
            return labels
        return labels

    def set_image(self, path):
        self.current = path
        self.pixmap.load(path)

        try:
            image_number = int(Path(path).stem)
            self.labels = self.read_labels(image_number)
        except Exception as e:
            print(e)
            self.labels = []

        self.resize_image()
        self.repaint()

    def set_zoom(self, zoom):
        self.image_zoom = zoom
        self.resize_image()

    def resize_image(self):
        new_width = self.pixmap.width() * self.image_zoom
        new_height = self.pixmap.height() * self.image_zoom

        print(f"new_width = {new_width}, new_height = {new_height}")

        self.resize(self.pixmap.size() * self.image_zoom)

    def get_y(self, x):
        return self.line_a * x + self.line_b

    def paintEvent(self, event):
        painter = QPainter(self)
        rc = QRect(self.rect())
        rc.setWidth(int(rc.width() * self.image_zoom))
        rc.setHeight(int(rc.height() * self.image_zoom))

        painter.drawPixmap(rc, self.pixmap)

        painter.setPen(self.pen)

        y1 = self.get_y(0) * rc.height()
        y2 = self.get_y(1) * rc.height()
        painter.drawLine(0, int(y1), rc.width(), int(y2))

        for lab in self.labels:
            painter.setPen(self.pens[lab.label])
            h = int(lab.height * rc.height())
            w = int(lab.width * rc.width())
            x = int(lab.x * rc.width() - w / 2)
            y = int(lab.y * rc.height() - h / 2)
            painter.drawRect(x, y, w, h)

            if lab.label is Labels.human:
                x = int(x + w / 2)
                y = int(y + h / 2)

                if lab.above is True:
                    painter.setPen(self.pen_above)
                else:
                    painter.setPen(self.pen_below)

                painter.drawEllipse(x, y, 10, 10)


class LabelledFloatField(QWidget):
    def __init__(self, title, initial_value=None):
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()
        self.label.setText(title)
        # self.label.setFixedWidth(100)
        self.label.setFont(QFont("Arial", weight=QFont.Bold))
        layout.addWidget(self.label)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setFixedWidth(40)
        # self.lineEdit.setValidator(QIntValidator())
        if initial_value is not None:
            self.lineEdit.setText(str(initial_value))
        layout.addWidget(self.lineEdit)
        layout.addStretch()

    def setLabelWidth(self, width):
        self.label.setFixedWidth(width)

    def setInputWidth(self, width):
        self.lineEdit.setFixedWidth(width)

    def getValue(self):
        return float(self.lineEdit.text())


class LabeledPathField(QWidget):
    def __init__(self, title, initial_value=None):
        QWidget.__init__(self)

        layout_v = QVBoxLayout()
        self.setLayout(layout_v)
        self.label = QLabel()
        self.label.setText(title)
        self.label.setFont(QFont("Arial", weight=QFont.Bold))
        layout_v.addWidget(self.label)

        windget = QWidget(self)
        layout = QHBoxLayout()
        windget.setLayout(layout)

        self.lineEdit = QLineEdit(windget)
        # self.lineEdit.setFixedWidth(40)
        if initial_value is not None:
            self.lineEdit.setText(str(initial_value))
        layout.addWidget(self.lineEdit)

        self.select_path = QPushButton("...")
        self.select_path.setFixedWidth(30)
        layout.addWidget(self.select_path)

        self.apply_path = QPushButton("Apply")
        self.apply_path.setFixedWidth(60)
        # self.apply_path.clicked.connect(self.on_apply_path)
        layout.addWidget(self.apply_path)

        layout.addStretch()

        layout_v.addWidget(windget)
        layout_v.addStretch()

    def setLabelWidth(self, width):
        self.label.setFixedWidth(width)

    def setInputWidth(self, width):
        self.lineEdit.setFixedWidth(width)

    def get_path(self):
        return self.lineEdit.text()


class ControlImageWidget(QWidget):
    ab_changed = pyqtSignal()
    path_changed = pyqtSignal()
    path_txt_changed = pyqtSignal()

    def __init__(self):
        # Инициализация родительского класса
        super().__init__()

        # Создание табличного макета
        grid = QVBoxLayout()

        # Создание виджета
        widget = QWidget()
        # Установка табличного макета в виджет
        self.setLayout(grid)
        # Установка виджета в центральный виджет окна
        # self.setCentralWidget(widget)
        # widget_path = QWidget(self)

        # box_path = QHBoxLayout()
        # widget_path.setLayout(box_path)

        self.select_path = LabeledPathField("Путь к картинкам")
        grid.addWidget(self.select_path, 0)
        self.select_path.apply_path.clicked.connect(self.on_apply_path)

        self.label_path = LabeledPathField("Путь к txt")
        grid.addWidget(self.label_path, 1)
        self.label_path.apply_path.clicked.connect(self.on_apply_path_to_txt)


        #box_path.addWidget(self.apply_path)
        # box_path.addStretch()

        # grid.addWidget(widget_path)

        # widget_ab = QWidget(self)
        box_ab = QHBoxLayout()
        # widget_ab.setLayout(box_ab)

        self.edit_a = LabelledFloatField("A", 0.5)
        box_ab.addWidget(self.edit_a, 0)

        self.edit_b = LabelledFloatField("B", 0.5)
        box_ab.addWidget(self.edit_b, 0)

        self.apply_ab = QPushButton("Apply (A, B)")

        self.apply_ab.clicked.connect(self.apply_ab_value)

        box_ab.addWidget(self.apply_ab, 2)


        #grid.addWidget(widget_ab, 1)

        grid.addLayout(box_ab, 1)

        # grid.addStretch()

    def get_path(self):
        return self.select_path.get_path()

    def get_ab(self):
        return self.edit_a.getValue(), self.edit_b.getValue()

    def apply_ab_value(self):
        self.ab_changed.emit()
        pass

    def on_apply_path(self):
        self.path_changed.emit()
        pass

    def on_apply_path_to_txt(self):
        self.path_txt_changed.emit()


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

        # пока файл не выбран, поле пустое
        self.current = ''

        # объект для загрузки картинки создаем

        self.pixmap = QPixmap()

        # отображение картинки на форме

        self.image = QLabel()

        self.image.setScaledContents(True)

        self.image_view = ViewImageWidget()

        # контрол для картинки вносим в scroll_area
        self.scroll_area.setWidget(self.image_view)

        grid.addWidget(self.scroll_area, 2, 0)

        self.list_view = QListWidget(self)
        self.list_view.setFixedWidth(100)
        self.list_view.currentItemChanged.connect(self.on_image_selected)
        grid.addWidget(self.list_view, 2, 1)

        self.ctrl = ControlImageWidget()
        self.ctrl.setMinimumWidth(100)
        self.ctrl.setFixedWidth(300)
        self.ctrl.ab_changed.connect(self.update_ab)
        self.ctrl.path_changed.connect(self.on_path_changed)
        self.ctrl.path_txt_changed.connect(self.on_path_txt_changed)
        grid.addWidget(self.ctrl, 2, 2)

    def on_image_selected(self):
        item = self.list_view.currentItem()
        if item is not None:
            image_file = str(self.list_view.currentItem().text())
            folder = self.ctrl.get_path()

            self.show_image(f"{folder}\\{image_file}")

    def on_path_txt_changed(self):
        self.image_view.folder_label_path = self.ctrl.label_path.get_path()

    def on_path_changed(self):
        self.list_view.clear()

        try:
            dir_path = Path(self.ctrl.get_path())
            for item in dir_path.iterdir():
                if item.is_file():
                    self.list_view.addItem(QListWidgetItem(str(item.name)))
        except Exception as ex:
            print(ex)

    def update_ab(self):
        a, b = self.ctrl.get_ab()
        print(a, " ", b)

        self.image_view.set_ab(a, b)

    def change_zoom(self, change_value):
        new_zoom = self.image_zoom * change_value

        if new_zoom > 100:
            new_zoom = 100
        elif new_zoom < 0.001:
            new_zoom = 0.001
        self.image_zoom = new_zoom
        self.image_view.set_zoom(new_zoom)

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

        self.image_view.set_image(file_name)

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
