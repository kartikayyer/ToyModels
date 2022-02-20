import sys

import numpy as np
from scipy import ndimage
from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg

class ExampleViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.auto_level = None
        self.rng = np.random.default_rng()
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
        self.dens_view.ui.roiBtn.hide()
        self.dens_view.ui.menuBtn.hide()
        self.view_boxes.addWidget(self.dens_view, stretch=1)
        self.intens_view = pg.ImageView(self, 'intensView')
        self.intens_view.setPredefinedGradient('viridis')
        self.intens_view.ui.roiBtn.hide()
        self.intens_view.ui.menuBtn.hide()
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
        self.shape_options.insertTab(0, tab, 'Uniform Rectangle')
        tab = self._init_rand_mask_tab()
        self.shape_options.insertTab(1, tab, 'Random Mask')

        self.auto_level = True
        self._rect_draw()

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

    def _init_rand_mask_tab(self):
        tab = QtWidgets.QWidget(self)
        tlayout = QtWidgets.QVBoxLayout()
        tab.setLayout(tlayout)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('FOV size:', self)
        line.addWidget(label)
        self._rmask_fov = QtWidgets.QLineEdit('1023', self)
        self._rmask_fov.editingFinished.connect(self._rand_mask_draw)
        line.addWidget(self._rmask_fov)
        label = QtWidgets.QLabel('pixels', self)
        line.addWidget(label)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('Num points:', self)
        line.addWidget(label)
        self._rmask_npts = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._rmask_npts.setRange(5, 100)
        self._rmask_npts.setValue(10)
        self._rmask_npts.setFixedWidth(300)
        self._rmask_npts.sliderMoved.connect(self._rand_mask_draw)
        line.addWidget(self._rmask_npts)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        label = QtWidgets.QLabel('Contrast:', self)
        line.addWidget(label)
        self._rmask_contr = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._rmask_contr.setRange(1, 100)
        self._rmask_contr.setValue(1)
        self._rmask_contr.setFixedWidth(300)
        self._rmask_contr.sliderMoved.connect(self._rand_mask_draw)
        line.addWidget(self._rmask_contr)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        tlayout.addLayout(line)
        button = QtWidgets.QPushButton('Update', self)
        button.clicked.connect(self._rand_mask_draw)
        line.addWidget(button)
        self._rmask_masked = QtWidgets.QCheckBox('Masked', self)
        self._rmask_masked.setChecked(True)
        self._rmask_masked.stateChanged.connect(self._rand_mask_draw)
        line.addWidget(self._rmask_masked)
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
        self.auto_level = False

    def _rand_mask_draw(self):
        fov = int(self._rmask_fov.text())
        mask = np.zeros((fov, fov))
        mask[fov//2-10:fov//2+11, fov//2-10:fov//2+11] = 1
        npts = self._rmask_npts.value()
        var = 1.
        contrast = 10. / self._rmask_contr.value()

        pos = np.round(self.rng.uniform(fov//2-10, fov//2+10, size=(npts, 2))).astype('i8')
        vals = self.rng.gamma(var, 1./var, size=npts)
        sigma = 100./npts

        arr = np.zeros_like(mask)
        arr[pos[:,0], pos[:,1]] = vals
        arr = ndimage.gaussian_filter(arr, sigma)
        if self._rmask_masked.isChecked():
            arr[mask==0.] = 0
            arr[mask==1.] += contrast
        arr *= 441 / arr.sum()

        self.set_dens(arr)
        self.auto_level = False

    def set_dens(self, dens):
        self.curr_dens = dens
        vr = self.dens_view.getImageItem().getViewBox().targetRect()
        self.dens_view.setImage(dens, autoHistogramRange=False, autoLevels=self.auto_level)
        if not self.auto_level:
            self.dens_view.getImageItem().getViewBox().setRange(vr, padding=0)
        self.update_intens()

    def update_intens(self, log_changed=False):
        intens = np.abs(np.fft.fftshift(np.fft.fftn(self.curr_dens)))**2
        if self.log_intens.isChecked():
            intens[intens<=0] = 1e-20
            intens = np.log10(intens)

        vr = self.intens_view.getImageItem().getViewBox().targetRect()
        if log_changed:
            self.intens_view.setImage(intens, autoHistogramRange=False, autoLevels=True)
        else:
            self.intens_view.setImage(intens, autoHistogramRange=False, autoLevels=self.auto_level)
        if not self.auto_level:
            self.intens_view.getImageItem().getViewBox().setRange(vr, padding=0)

def main():
    app = QtWidgets.QApplication([])
    ev = ExampleViewer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
