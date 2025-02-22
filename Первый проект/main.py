import sys

from PIL import Image
from PIL import ImageFilter
from PIL.ImageQt import ImageQt

from random import randint

from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import (QWidget, QApplication, QFileDialog, QScrollArea, QPushButton, QLabel,
                             QCheckBox, QComboBox)

IMAGE_SIZE = [400, 400]  # стартовый размер изображения на экране
ZOOM = 0.25  # величина приближения/отдаления изображения


def change_size(current_width, current_height):
    width, height = IMAGE_SIZE
    if current_height >= current_width and current_height > height:
        height = height
        height_percent = height / current_height
        width = int(current_width * height_percent)
    elif current_width > width:
        width = width
        width_percent = width / current_width
        height = int(current_height * width_percent)
    return width, height


def make_negative(image):
    width, height = image.size
    pixels = image.load()
    for i in range(width):
        for j in range(height):
            r, g, b = pixels[i, j]
            pixels[i, j] = 255 - r, 255 - g, 255 - b


def make_noisy(image):
    width, height = image.size
    pixels = image.load()
    for i in range(width):
        for j in range(height):
            k = randint(-50, 50)
            r, g, b = pixels[i, j]
            r, g, b = r + k, g + k, b + k
            if r > 255:
                r = 255
            if g > 255:
                g = 255
            if b > 255:
                b = 255
            if r < 0:
                r = 0
            if g < 0:
                g = 0
            if b < 0:
                b = 0
            pixels[i, j] = r, g, b


def make_black_and_white(image):
    width, height = image.size
    pixels = image.load()
    for i in range(width):
        for j in range(height):
            r, g, b = pixels[i, j]
            c = (r + g + b)
            if c > 255:
                r, g, b = 255, 255, 255
            else:
                r, g, b = 0, 0, 0
            pixels[i, j] = r, g, b


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start()
        self.setMouseTracking(True)

    def mouseDoubleClickEvent(self, event):
        if self.fileOpened and 250 < event.x() < 650 and 100 <= event.y() <= 500:
            value = not (self.zoomUpBtn.isVisible() and
                         self.zoomDownBtn.isVisible() and self.rotateBtn.isVisible())
            self.hide_buttons(value)

    def hide_buttons(self, value):
        self.zoomUpBtn.setVisible(value)
        self.zoomDownBtn.setVisible(value)
        self.rotateBtn.setVisible(value)

    def initUI(self):
        self.setGeometry(300, 100, 670, 515)

        self.downloadBtn = QPushButton('Загрузить изображение', self)
        self.downloadBtn.clicked.connect(self.load_image)
        self.downloadBtn.resize(150, 40)
        self.downloadBtn.move(240, 240)

        self.saveBtn = QPushButton('Сохранить', self)
        self.saveBtn.resize(650, 30)
        self.saveBtn.move(10, 10)
        self.saveBtn.clicked.connect(self.save_image)

        self.deleteBtn = QPushButton('Удалить', self)
        self.deleteBtn.resize(650, 30)
        self.deleteBtn.move(10, 50)
        self.deleteBtn.clicked.connect(self.start)

        self.image = QLabel(self)
        self.image.setScaledContents(True)

        # создаем рабочую область для фоторедактора
        self.scrollArea = QScrollArea(self)  # вот сама рабочаяя область
        self.scrollArea.setWidget(self.image)
        self.scrollArea.resize(*IMAGE_SIZE)
        self.scrollArea.move(250, 100)
        self.scrollArea.setStyleSheet("""
        QScrollArea{
            background-color: #808080
        }
        """)

        # кнопки зума
        self.zoomUpBtn = QPushButton('+', self)
        self.zoomUpBtn.resize(23, 23)
        self.zoomUpBtn.move(600, 455)
        self.zoomUpBtn.clicked.connect(self.zoom)

        self.zoomDownBtn = QPushButton('-', self)
        self.zoomDownBtn.resize(23, 23)
        self.zoomDownBtn.move(570, 455)
        self.zoomDownBtn.clicked.connect(self.zoom)

        self.rotateBtn = QPushButton('⟲', self)
        self.rotateBtn.resize(23, 23)
        self.rotateBtn.move(540, 455)
        self.rotateBtn.clicked.connect(self.rotation)

        self.setMirrorBox = QCheckBox('Отразить зеркально', self)
        self.setMirrorBox.clicked.connect(self.mirror)
        self.setMirrorBox.move(10, 100)

        self.lbl = QLabel('Фильтр', self)
        self.lbl.move(10, 122)

        self.filtresBox = QComboBox(self)
        self.filtresBox.addItem('Ничего')
        self.filtresBox.addItem('Черно-белое')
        self.filtresBox.addItem('Серый оттенок')
        self.filtresBox.addItem('Добавить шум')
        self.filtresBox.addItem('Размытие')
        self.filtresBox.addItem('Негатив')
        self.filtresBox.addItem('Повышение контрастности')
        self.filtresBox.addItem('Выделить контур')
        self.filtresBox.addItem('Тиснение')
        self.filtresBox.addItem('Выделение краев')
        self.filtresBox.resize(150, 20)
        self.filtresBox.move(55, 120)
        self.filtresBox.activated[str].connect(self.set_filter)

    def save_image(self):
        saveFileName = QFileDialog.getSaveFileName(self, 'Сохранить', '',
                                                   'Картинка (*.png);;Картинка (*.jpg)')[0]
        self.current_image.save(saveFileName)

    def start(self):
        self.fileOpened = False
        self.setMirrorBox.setChecked(False)
        self.filtresBox.setCurrentText('Ничего')
        for i in self.children():
            i.setVisible(False)
        self.downloadBtn.setVisible(True)

    def set_filter(self, text):
        self.current_image = self.original_image.copy()

        if text == 'Серый оттенок':
            self.current_image = self.current_image.convert('L')
        elif text == 'Черно-белое':
            make_black_and_white(self.current_image)
        elif text == 'Добавить шум':
            make_noisy(self.current_image)
        elif text == 'Размытие':
            self.current_image = self.current_image.filter(ImageFilter.SMOOTH)
        elif text == 'Негатив':
            make_negative(self.current_image)
        elif text == 'Повышение контрастности':
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
        elif text == 'Выделить контур':
            self.current_image = self.current_image.filter(ImageFilter.CONTOUR)
        elif text == 'Тиснение':
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
        elif text == 'Выделение краев':
            self.current_image = self.current_image.filter(ImageFilter.FIND_EDGES)

        self.im = ImageQt(self.current_image)
        self.pm = QPixmap.fromImage(self.im)
        self.image.setPixmap(self.pm)

    # загругка изображения
    def load_image(self):
        # сичтываем имя файла
        self.fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                                 'Картинка (*.png);;Картинка (*.jpg)')[0]
        # устанавливаем изображение в специальный контейнер
        self.pm = QPixmap(self.fname)

        # пропорционально меняем размер изображения, чтобы влезало на рабочую область
        width, height = change_size(self.pm.width(), self.pm.height())

        # загружаем изображение на рабочюю область
        self.image.resize(width, height)
        self.image.setPixmap(self.pm)

        self.original_image = Image.open(self.fname)
        self.current_image = self.original_image.copy()

        # если мы загрузили изображения, то нужно открыть рабочую область,
        # а кнопку загрузки спрятать
        for i in self.children():
            i.setVisible(True)
        self.downloadBtn.setVisible(False)

        self.fileOpened = True

    # приближение/отдаление картинки
    def zoom(self):
        # берем текущие размеры изображения
        width, height = self.image.width(), self.image.height()
        if self.sender().text() == '+':
            percent = ZOOM
        else:
            percent = -ZOOM
        # меняем размеры
        width = int(width * percent + width)
        height = int(height * percent + height)
        # сохраняем
        self.image.resize(width, height)

    def rotation(self):
        self.original_image = self.original_image.transpose(Image.ROTATE_90)
        self.current_image = self.current_image.transpose(Image.ROTATE_90)

        self.im = ImageQt(self.current_image)
        self.pm = QPixmap.fromImage(self.im)
        self.image.resize(self.image.height(), self.image.width())
        self.image.setPixmap(self.pm)

    def mirror(self):
        self.original_image = self.original_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)

        self.im = ImageQt(self.current_image)
        self.pm = QPixmap.fromImage(self.im)
        self.image.setPixmap(self.pm)

    def closeEvent(self, event):
        print('Вы закрыли приложение :(')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWidget()
    w.show()
    sys.exit(app.exec_())
