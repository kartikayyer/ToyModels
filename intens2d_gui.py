import sys

import numpy as np
from scipy import ndimage
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg

class ExampleViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.auto_level = None
        self._init_ui()

    def _init_ui(self):
        self.resize(1600, 800)

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        self.view_boxes = QtWidgets.QHBoxLayout()
        layout.addLayout(self.view_boxes, stretch=1)
        self.dens_view = pg.ImageView(self, 'densView')
        self.dens_view.setPredefinedGradient('magma')
        self.view_boxes.addWidget(self.dens_view, stretch=1)
        self.intens_view = pg.ImageView(self, 'intensView')
        self.intens_view.setPredefinedGradient('viridis')
        self.view_boxes.addWidget(self.intens_view, stretch=1)

        self.plot_options = QtWidgets.QHBoxLayout()
        layout.addLayout(self.plot_options)
        self.log_intens = QtWidgets.QCheckBox('Log Intens', self)
        self.log_intens.stateChanged.connect(lambda: self.update_intens(log_changed=True))
        self.plot_options.addWidget(self.log_intens)
        self.plot_options.addStretch(1)
        button = QtWidgets.QPushButton('Quit', self)
        button.clicked.connect(self.close)
        self.plot_options.addWidget(button)

        self.shape_options = QtWidgets.QTabWidget(self)
        self.shape_options.currentChanged.connect(self._tab_changed)
        layout.addWidget(self.shape_options)
        tab = self._init_rect_tab()
        self.shape_options.insertTab(0, tab, 'Rectangle')

        self.auto_level = True
        self._rect_draw()
        self.auto_level = False

        self.show()

    def _tab_changed(self):
        self.auto_level = True

    def _init_rect_tab(self):
        tab = QtWidgets.QWidget(self)
        tlayout = QtWidgets.QVBoxLayout()
        tab.setLayout(tlayout)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('FOV size:', self)
        line.addWidget(label)
        self._rect_fov = QtWidgets.QLineEdit('127', self)
        self._rect_fov.editingFinished.connect(self._rect_draw)
        line.addWidget(self._rect_fov)
        label = QtWidgets.QLabel('pixels', self)
        line.addWidget(label)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('Rect width:', self)
        line.addWidget(label)
        self._rect_x = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._rect_x.setRange(4, 20)
        self._rect_x.setValue(10)
        self._rect_x.setFixedWidth(300)
        self._rect_x.sliderMoved.connect(self._rect_draw)
        line.addWidget(self._rect_x)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('Rect height:', self)
        line.addWidget(label)
        self._rect_y = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._rect_y.setRange(4, 20)
        self._rect_y.setValue(10)
        self._rect_y.setFixedWidth(300)
        self._rect_y.sliderMoved.connect(self._rect_draw)
        line.addWidget(self._rect_y)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('Blurring:', self)
        line.addWidget(label)
        self._rect_blur = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._rect_blur.setRange(0, 400)
        self._rect_blur.setValue(0)
        self._rect_blur.setFixedWidth(300)
        self._rect_blur.sliderMoved.connect(self._rect_draw)
        line.addWidget(self._rect_blur)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        button = QtWidgets.QPushButton('Update', self)
        button.clicked.connect(self._rect_draw)
        line.addWidget(button)
        line.addStretch(1)

        tlayout.addStretch(1)

        return tab

    def _rect_draw(self):
        fov = int(self._rect_fov.text())
        dens = np.zeros((fov, fov))
        sx, sy = self._rect_x.value(), self._rect_y.value()
        ox = fov // 2 - sx // 2
        oy = fov // 2 - sy // 2
        dens[ox:ox+sx, oy:oy+sy] = 1
        blur_sigma = self._rect_blur.value() / 100.
        if blur_sigma > 0.:
            dens = ndimage.gaussian_filter(dens, blur_sigma)

        self.set_dens(dens)

    def set_dens(self, dens):
        self.curr_dens = dens
        self.dens_view.setImage(dens, autoHistogramRange=False, autoLevels=self.auto_level)
        self.update_intens()

    def update_intens(self, log_changed=False):
        intens = np.abs(np.fft.fftshift(np.fft.fftn(self.curr_dens)))**2
        if self.log_intens.isChecked():
            intens[intens<=0] = 1e-20
            intens = np.log10(intens)
        if log_changed:
            self.intens_view.setImage(intens, autoHistogramRange=False, autoLevels=True)
        else:
            self.intens_view.setImage(intens, autoHistogramRange=False, autoLevels=self.auto_level)

def main():
    app = QtWidgets.QApplication([])
    ev = ExampleViewer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
