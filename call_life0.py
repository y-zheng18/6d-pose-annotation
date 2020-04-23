

from life0 import Ui_annotation
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pptk
import os
import numpy as np
import json
import math
from utils import rotate_delta, get_bbox


class annatation_tool(QtWidgets.QMainWindow,Ui_annotation):
    def __init__(self):
        super(annatation_tool, self).__init__()
        self.setupUi(self)
        self.initUi()
        self.init_data()

    def init_data(self):
        self.anno_json = {}
        self.pc = None
        self.loadroot = None
        self.save_root = None
        self.viewer = None
        self.rt = np.eye(4)
        self.phi = 0
        self.theta = 0
        self.index = 0
        self.anno_list = []
        self.rotate_degree = 5
        if os.path.exists('conf.json'):
            conf = json.load(open('conf.json', 'r'))
            if not len(conf['anno_json']) and not conf['load_root']:
                return
            self.anno_json = conf['anno_json']
            self.init_instance()
            self.loadroot = conf['load_root']
            self.save_root = conf['save_root']

            self.lineEdit_loadroot.setText(self.loadroot)
            self.lineEdit_saveroot.setText(self.save_root)


    def initUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle('annatation')
        self.resize(1800, 1200)
        palette1 = QPalette()
        # palette1.setColor(self.backgroundRole(), QColor(192,253,123))   # 设置背景颜色
        palette1.setBrush(self.backgroundRole(), QBrush(QPixmap('./icon/background.png')))  # 设置背景图片
        self.setPalette(palette1)
        self.setWindowIcon(QIcon('./icon/fire.png'))

        self.statusbar.hide()
        self.btn_nxt.setIcon(QIcon('icon/right.png'))
        self.btn_nxt.setText('next')
        self.btn_back.setIcon(QIcon('icon/left.png'))
        self.btn_back.setText('pre')
        self.actionexit.setIcon(QIcon('icon/exit.png'))
        self.tbtn_loadroot.setIcon(QIcon('icon/file.png'))
        self.tbtn_saveroot.setIcon(QIcon('icon/file.png'))
        self.btn_continue.setIcon(QIcon('icon/start.png'))
        self.btn_a.setIcon(QIcon('icon/arrow-left.png'))
        self.btn_d.setIcon(QIcon('icon/arrow-right.png'))
        self.btn_w.setIcon(QIcon('icon/arrow-up.png'))
        self.btn_s.setIcon(QIcon('icon/arrow-down.png'))
        p = QPixmap('./icon/raven.png')
        self.label.setScaledContents(True)
        self.label.setPixmap(p)


        self.comboBox_rotate_degree.addItem('1')
        self.comboBox_rotate_degree.addItem('3')
        self.comboBox_rotate_degree.addItem('5')
        self.comboBox_rotate_degree.addItem('10')
        self.comboBox_rotate_degree.addItem('15')
        self.comboBox_rotate_degree.addItem('20')
        self.comboBox_rotate_degree.addItem('30')
        self.comboBox_rotate_degree.setCurrentIndex(2)

        self.btn_a.setEnabled(False)
        self.btn_d.setEnabled(False)
        self.btn_w.setEnabled(False)
        self.btn_s.setEnabled(False)
        self.btn_nxt.setEnabled(False)
        self.btn_back.setEnabled(False)
        self.checkBox_Sym.setEnabled(False)
        self.checkBox_del.setEnabled(False)

        self.tbtn_loadroot.clicked.connect(self.on_tbtn_load_clicked)
        self.tbtn_saveroot.clicked.connect(self.on_tbtn_save_clicked)
        self.btn_continue.clicked.connect(self.on_btn_start_clicked)
        self.btn_a.clicked.connect(self.on_btn_left_clicked)
        self.btn_d.clicked.connect(self.on_btn_right_clicked)
        self.btn_w.clicked.connect(self.on_btn_up_clicked)
        self.btn_s.clicked.connect(self.on_btn_down_clicked)
        self.btn_nxt.clicked.connect(self.on_btn_next_clicked)
        self.btn_back.clicked.connect(self.on_btn_pre_clicked)
        self.comboBox_rotate_degree.currentIndexChanged.connect(self.on_degree_changed)
        self.btn_d.setShortcut(_translate("annotation", "D"))
        self.btn_w.setShortcut(_translate("annotation", "W"))
        self.btn_s.setShortcut(_translate("annotation", "S"))
        self.btn_a.setShortcut(_translate("annotation", "A"))
        self.btn_nxt.setShortcut(_translate("annotation", "L"))
        self.btn_back.setShortcut(_translate("annotation", "K"))
        self.checkBox_del.setShortcut(_translate("annotation", "del"))
        self.checkBox_Sym.setShortcut(_translate("annotation", "P"))

    def on_tbtn_load_clicked(self):
        file_name = QFileDialog.getExistingDirectory()
        self.loadroot = file_name
        self.lineEdit_loadroot.setText(file_name)

    def on_tbtn_save_clicked(self):
        if not self.loadroot:
            QMessageBox.warning(self, 'warning',  'load point clouds first!', QMessageBox.Cancel)
            return
        file_name = QFileDialog.getExistingDirectory()
        self.save_root = file_name
        self.lineEdit_saveroot.setText(file_name)
        if not len(self.anno_json):
            self.init_json()

    def on_btn_start_clicked(self):
        if not len(self.anno_json) and not len(self.anno_list):
            QMessageBox.warning(self, 'warning', 'load point clouds first!', QMessageBox.Cancel)
            return
        #print(self.anno_json)
        self.init_instance()
        if len(self.anno_list) == 0:
            QMessageBox.information(self, 'congratulations', 'annotation done!', QMessageBox.Ok)
            return
        self.pc = np.load(os.path.join(self.loadroot, self.anno_list[self.index]))
        pmin, pmax = get_bbox(self.pc)
        center = (pmin + pmax) / 2
        self.pc -= center
        self.rt = np.eye(4)
        self.rt[:3, 3] = -center[:3]
        self.viewer = pptk.viewer(self.pc)
        self.init_viewer()
        #self.btn_continue.setEnabled(False)
        self.btn_a.setEnabled(True)
        self.btn_d.setEnabled(True)
        self.btn_w.setEnabled(True)
        self.btn_s.setEnabled(True)
        self.btn_back.setEnabled(True)
        self.btn_nxt.setEnabled(True)
        self.checkBox_Sym.setEnabled(True)
        self.checkBox_del.setEnabled(True)

    def on_btn_right_clicked(self):
        self.phi += self.rotate_degree
        self.init_viewer()
        # rt = rotate_delta(self.rotate_degree)
        # self.rt = np.dot(rt, self.rt)
        # print(self.phi)

    def on_btn_left_clicked(self):
        self.phi -= self.rotate_degree
        self.init_viewer()
        # rt = rotate_delta(-self.rotate_degree)
        # self.rt = np.dot(rt, self.rt)
        # print(self.phi)


    def on_btn_up_clicked(self):
        self.theta += self.rotate_degree
        self.init_viewer()
        # rt = rotate_delta(self.rotate_degree, axis='y')
        # self.rt = np.dot(rt, self.rt)

        #print(self.theta)

    def on_btn_down_clicked(self):
        self.theta -= self.rotate_degree
        self.init_viewer()
        # rt = rotate_delta(-self.rotate_degree, axis='y')
        # self.rt = np.dot(rt, self.rt)
        # print(self.theta)

    def on_btn_next_clicked(self):
        if self.index >= len(self.anno_list):
            return
        if not '/' in self.anno_list[self.index].split('\\'):
            scene_id, instance = self.anno_list[self.index].split('\\')
        else:
            scene_id, instance = self.anno_list[self.index].split('/')

        self.anno_json[scene_id][instance]['annotated'] = True
        self.anno_json[scene_id][instance]['symmetric'] = self.checkBox_Sym.isChecked()
        self.anno_json[scene_id][instance]['delete'] = self.checkBox_del.isChecked()
        self.save_6d(scene_id, instance)
        self.index += 1
        if self.index >= len(self.anno_list):
            self.index = len(self.anno_list)
            QMessageBox.information(self, 'congratulations', 'annotation done!', QMessageBox.Ok)
            return
        pc_path = os.path.join(self.loadroot, self.anno_list[self.index])
        # print(pc_path)
        self.pc = np.load(pc_path)
        pmin, pmax = get_bbox(self.pc)
        center = (pmin + pmax) / 2
        self.pc -= center
        self.viewer.clear()
        self.viewer.load(self.pc)
        self.phi = 0
        self.theta = 0
        self.rt = np.eye(4)
        self.rt[:3, 3] = -center[:3]
        self.init_viewer()
        self.save_conf()
        self.checkBox_Sym.setChecked(False)
        self.checkBox_del.setChecked(False)

    def on_btn_pre_clicked(self):
        if self.index <= 0:
            return
        self.index -= 1
        # print(self.index)
        self.pc = np.load(os.path.join(self.loadroot, self.anno_list[self.index]))
        pmin, pmax = get_bbox(self.pc)
        center = (pmin + pmax) / 2
        self.pc -= center
        self.viewer.clear()
        self.viewer.load(self.pc)
        self.phi = 0
        self.theta = 0
        self.rt = np.eye(4)
        center = np.mean(self.pc, axis=0)
        self.rt[:3, 3] = -center[:3]
        self.init_viewer()

    def on_degree_changed(self):
        self.rotate_degree = int(self.comboBox_rotate_degree.currentText())

    def init_json(self):
        scene_id_list = os.listdir(self.loadroot)
        #print(scene_id_list)
        for scene_id in scene_id_list:
            self.anno_json[scene_id] = {}
            obj_list = os.listdir(os.path.join(self.loadroot, scene_id))
            for i in obj_list:
                self.anno_json[scene_id][i] = {}
                self.anno_json[scene_id][i]['annotated'] = False
                self.anno_json[scene_id][i]['symmetric'] = False
                self.anno_json[scene_id][i]['delete'] = False
        #json.dump(self.anno_json, open(os.path.join(self.save_root, 'annotation.json'), 'w'))

    def init_instance(self):
        self.anno_list = []
        for scene_id in self.anno_json.keys():
            scene = self.anno_json[scene_id]
            for instance in scene.keys():
                if not scene[instance]['annotated']:  # to be annotated
                    self.anno_list.append(os.path.join(scene_id, instance))

    def init_viewer(self):
        self.viewer.set(lookat=(0, 0, 0))
        self.viewer.set(theta=self.theta * math.pi / 180)
        self.viewer.set(r=1.5)
        self.viewer.set(phi=self.phi * math.pi / 180)

    def save_6d(self, scene_id, instance):
        save_root = os.path.join(self.save_root, scene_id)
        if not os.path.exists(save_root):
            os.mkdir(save_root)
        save_name = os.path.join(save_root, instance.rstrip('.npy') + '_6d.npy')
        self.rt = np.dot(rotate_delta(self.phi, axis='z'), self.rt)
        self.rt = np.dot(rotate_delta(self.theta, axis='y'), self.rt)
        #print(self.theta, self.phi)
        if os.path.exists(save_name):
            if np.sum(self.rt == np.eye(4)) == 16:
                return

        np.save(save_name, self.rt)



    def save_conf(self):
        conf = {}
        conf['load_root'] = self.loadroot
        conf['save_root'] = self.save_root
        conf['anno_json'] = self.anno_json
        json.dump(conf, open('conf.json', 'w'), indent=1)

    def closeEvent(self, event):
        self.save_conf()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = annatation_tool()
    mainWindow.show()

    sys.exit(app.exec_())
