# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.resources\ui_orbitalDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
from qgis.core import (QgsRectangle, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsVectorLayer,
                       QgsLayerTreeLayer, QgsProject, QgsTask, QgsApplication, QgsMessageLog, QgsFields, QgsField,
                       QgsWkbTypes, QgsFeature, QgsPointXY, QgsGeometry,)
from PyQt5 import QtCore, QtGui, QtWidgets
from image_viewer.gui import resources_rc
class Ui_orbitalDialog(object):
    def setupUi(self, orbitalDialog):
        orbitalDialog.setObjectName("orbitalDialog")
        orbitalDialog.resize(567, 260)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(orbitalDialog.sizePolicy().hasHeightForWidth())
        orbitalDialog.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/images/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        orbitalDialog.setWindowIcon(icon)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(orbitalDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ViewerLayout = QtWidgets.QVBoxLayout()
        self.ViewerLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.ViewerLayout.setObjectName("ViewerLayout")
        self.verticalLayout_3.addLayout(self.ViewerLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.btn_export = QtWidgets.QPushButton(orbitalDialog)
        self.btn_export.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_export.setText("Export Image")
        self.btn_export.setObjectName("btn_export")
        self.horizontalLayout.addWidget(self.btn_export)
        
        spacerItem = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_back = QtWidgets.QPushButton(orbitalDialog)
        self.btn_back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_back.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/images/Previous_Arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_back.setIcon(icon3)
        self.btn_back.setObjectName("btn_back")
        self.horizontalLayout.addWidget(self.btn_back)

        self.btn_play = QtWidgets.QPushButton(orbitalDialog)
        self.btn_play.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_play.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/images/play.png"), QtGui.QIcon.Normal,QtGui.QIcon.Off)
        self.btn_play.setIcon(icon4)
        self.btn_play.setObjectName("btn_play")
        self.horizontalLayout.addWidget(self.btn_play)

        self.btn_pause = QtWidgets.QPushButton(orbitalDialog)
        self.btn_pause.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_pause.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/images/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_pause.setIcon(icon4)
        self.btn_pause.setObjectName("btn_play")
        self.horizontalLayout.addWidget(self.btn_pause)

        self.btn_next = QtWidgets.QPushButton(orbitalDialog)
        self.btn_next.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_next.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/images/Next_Arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_next.setIcon(icon5)
        self.btn_next.setObjectName("btn_next")
        self.horizontalLayout.addWidget(self.btn_next)
        spacerItem1 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)

        self.btn_fullscreen = QtWidgets.QPushButton(orbitalDialog)
        self.btn_fullscreen.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_fullscreen.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/images/full_screen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_fullscreen.setIcon(icon6)
        self.btn_fullscreen.setCheckable(True)
        self.btn_fullscreen.setObjectName("btn_fullscreen")
        self.horizontalLayout.addWidget(self.btn_fullscreen)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(orbitalDialog)
        self.btn_fullscreen.clicked['bool'].connect(orbitalDialog.FullScreen)
        self.btn_back.clicked.connect(orbitalDialog.GetBackNextImage)
        self.btn_next.clicked.connect(orbitalDialog.GetBackNextImage)
        self.btn_play.clicked.connect(orbitalDialog.timer_play_image)
        self.btn_pause.clicked.connect(orbitalDialog.PauseImage)
        self.btn_export.clicked.connect(orbitalDialog.ExportImage)
        QtCore.QMetaObject.connectSlotsByName(orbitalDialog)

    def retranslateUi(self, orbitalDialog):
        _translate = QtCore.QCoreApplication.translate
        orbitalDialog.setWindowTitle(_translate("orbitalDialog", "360 Viewer"))


