# -*- coding: utf-8 -*-
import math
import os
from qgis.core import (QgsPointXY,
                       QgsProject,
                       QgsFeatureRequest,
                       QgsVectorLayer,
                       QgsWkbTypes,
                       QgsApplication)
from qgis.gui import QgsRubberBand
import qgis.utils
import re
import shutil
import platform
import time
from threading import Timer

from PyQt5.QtCore import QObject, QSettings, Qt, QPropertyAnimation, QSize, QTimer
from PyQt5.QtWidgets import QDialog, QWidget, QMessageBox
from PyQt5.QtGui import QWindow
import image_viewer.config as config
from image_viewer.geom.transformgeom import transformGeometry
from image_viewer.gui.ui_orbitalDialog import Ui_orbitalDialog
from image_viewer.server.local_server import *
from image_viewer.utils.qgsutils import qgsutils

try:
    from pydevd import *
except ImportError:
    None

try:
    from image_viewer.cefpython3 import cefpython
except ImportError:
    None

try:
    from PIL import Image
except ImportError:
    None

WindowUtils = cefpython .WindowUtils()
# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")


class CefWidget(QWidget):
    """ CefPython Viewer"""
    browser = None

    def __init__(self, parent=None):
        super(CefWidget, self).__init__(parent)
        self.parent = parent
        self.browser = None
        self.hidden_window = None  # Required for PyQt5 on Linux
        self.show()

    def focusInEvent(self, _):
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSetFocus(self.getHandle(), 0, 0, 0)
            self.browser.SetFocus(True)

    def focusOutEvent(self, _):
        if self.browser:
            self.browser.SetFocus(False)

    def embedBrowser(self):
        windowInfo = cefpython.WindowInfo() #create object WindowInfo
        rect = [0, 0, self.width(), self.height()]#กำหนดค่า window rect
        windowInfo.SetAsChild(self.getHandle(), rect)

        self.browser = cefpython.CreateBrowserSync(windowInfo,
                                                   browserSettings={},
                                                   navigateUrl=config.DEFAULT_URL)

        # Add Handler
        self.browser.SetClientHandler(ClientHandler())


    def getHandle(self):
        try:
            return int(self.winId()) #winId ใน qt เป็นค่าที่แสดงถึง window นั้นๆ
        except Exception:
            ctypes.pythonapi.PyCapsule_GetPointer.restype = (
                    ctypes.c_void_p)
            ctypes.pythonapi.PyCapsule_GetPointer.argtypes = (
                    [ctypes.py_object])
            return ctypes.pythonapi.PyCapsule_GetPointer(
                    self.winId(), None)

    def moveEvent(self, _):
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSize(self.getHandle(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(self.x, self.y,
                                       self.width(), self.height())
            self.browser.NotifyMoveOrResizeStarted()

    def resizeEvent(self, event):
        size = event.size()
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSize(self.getHandle(), 0, 0, 0)
            self.browser.NotifyMoveOrResizeStarted()


class Geo360Dialog(QWidget, Ui_orbitalDialog):

    """Geo360 Dialog Class"""

    def __init__(self, iface, parent=None, featuresId=None, layer=None):

        QDialog.__init__(self)

        self.setupUi(self) #call def setupUi
        self.s = QSettings()#create class obj for setting layout qt

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))

        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.parent = parent
        self.timer_flag = False
    

        # Orientation from image
        self.yaw = math.pi
        self.bearing = None

        self.layer = layer
        self.featuresId = featuresId

        self.actualPointDx = None
        self.actualPointSx = None
        self.actualPointOrientation = None

        self.selected_features = qgsutils.getToFeature(
            self.layer, self.featuresId)

        self.layer_names = open(self.plugin_path + "/layer_names.txt","r")

        # Get image path
        self.current_image = self.GetImage()
        extens = ['jpg', 'jpeg', 'JPG', 'JPEG']
        basename = os.path.basename(self.current_image)  # basename เอาเฉพาะชื่อไฟล์+สกุลไฟล์
        file_name = basename[:-len(extens)]  # แยกเอาแค่ชื่อไฟล์
        f = open(self.plugin_path + "/viewer/img_tmp.txt",
                 "w")
        f.write(file_name)
        f.close()
        # Create Viewer
        self.CreateViewer()
        self.RestoreSize()
        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"There is no associated image.")
            self.resetQgsRubberBand()
            time.sleep(1)
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            return

        # Copy file to local server
        self.CopyFile(self.current_image)

        # Set RubberBand
        self.resetQgsRubberBand()
        self.setOrientation()
        self.setPosition()

    def SetInitialYaw(self):
        ''' Set Initial Yaw '''
        self.bearing = self.B_degree
        self.view.browser.GetMainFrame().ExecuteFunction("InitialYaw",
                                                         self.bearing)
        return

    def CreateViewer(self):
        ''' Create Viewer '''
        qgsutils.showUserAndLogMessage(
            u"Information: ", u"Create viewer", onlyLog=True)

        self.view = CefWidget(self)
        self.ViewerLayout.addWidget(self.view)
        self.view.embedBrowser()
        return

    def RemoveImage(self):
        ''' Remove Image '''
        try:
            os.remove(self.plugin_path + "\\viewer\\image.jpg")
        except OSError:
            pass

    def CopyFile(self, src):
        ''' Copy Image File in Local Server '''
        qgsutils.showUserAndLogMessage(
            u"Information: ", u"Copiar imagem",
            onlyLog=True)
        src_dir = src
        dst_dir = self.plugin_path + "\\viewer"

        # Copy image in local folder
        img = Image.open(src_dir)
        dst_dir = dst_dir + "\\image.jpg"
        try:
            os.remove(dst_dir)
        except OSError:
            pass
        shutil.copy(src_dir, dst_dir)
        return

    def RestoreSize(self):
        ''' Restore Dialog Size '''
        dw = self.s.value("360Viewer/width")
        dh = self.s.value("360Viewer/height")

        if dw is None:
            return
        size = self.size()

        anim = QPropertyAnimation(self, b'size', self)
        anim.setStartValue(size)
        anim.setEndValue(QSize(int(dw), int(dh)))
        anim.setDuration(1)
        anim.start()
        return

    def SaveSize(self):
        ''' Save Dialog Size '''
        dw = self.width()
        dh = self.height()
        self.s.setValue("360Viewer/width", dw)
        self.s.setValue("360Viewer/height", dh)
        return

    def GetImage(self):
        ''' Get Selected Image '''
        try:
            path = qgsutils.getAttributeFromFeature(
                self.selected_features, config.column_name)
            if not os.path.isabs(path):  # Relative Path to Project
                path_project = QgsProject.instance().readPath("./")
                path = os.path.normpath(os.path.join(path_project, path))
        except Exception:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"Column not found.")
            return

        #qgsutils.showUserAndLogMessage(str(path))
        return path

    def ChangeUrlViewer(self, new_url):
        ''' Change Url Viewer '''
        self.view.browser.GetMainFrame().ExecuteJavascript(
            "window.location='%s'" % new_url)

        return

    def ReloadView(self, newId):
        ''' Reaload Image viewer '''
        self.setWindowState(self.windowState() & ~
                            Qt.WindowMinimized | Qt.WindowActive)
        # this will activate the window
        self.activateWindow()
        self.selected_features = qgsutils.getToFeature(
            self.layer, newId)

        self.current_image = self.GetImage()

        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"There is no associated image.")
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            self.resetQgsRubberBand()
            return

        # Set RubberBand
        self.resetQgsRubberBand()
        self.setOrientation()
        self.setPosition()

        extens = ['jpg', 'jpeg', 'JPG', 'JPEG']
        basename = os.path.basename(self.current_image)  # basename เอาเฉพาะชื่อไฟล์+สกุลไฟล์
        file_name = basename[:-len(extens)]  # แยกเอาแค่ชื่อไฟล์
        f = open(self.plugin_path + "/viewer/img_tmp.txt","w")
        f.write(file_name)
        f.close()
        # Copy file to local server

        self.CopyFile(self.current_image)
        self.ChangeUrlViewer(config.DEFAULT_URL)

        return

    def ResizeDialog(self):
        ''' Expanded/Decreased Dialog '''
        sender = QObject.sender(self)

        w = self.width()
        h = self.height()

        size = self.size()
        anim = QPropertyAnimation(self, b'size', self)
        anim.setStartValue(size)

        if sender.objectName() == "btn_ZoomOut":
            anim.setEndValue(QSize(w - 50, h - 50))
        else:
            anim.setEndValue(QSize(w + 50, h + 50))

        anim.setDuration(300)
        anim.start()
        return

    def GetBackNextImage(self):
        ''' Get to Back Image '''
        self.layer_names = open(self.plugin_path + "/layer_names.txt","r")
        sender = QObject.sender(self)
        lys = self.canvas.layers()  # Check if mapa foto is loaded
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")
            return

        for layer in lys:
            for x in self.layer_names:
                if layer.name() in x:
                    self.encontrado = True
                    self.iface.setActiveLayer(layer)

                    f = self.selected_features

                    self.ac_lordem = f.attribute(config.column_order)

                    if sender.objectName() == "btn_back" :
                        self.new_lordem = int(self.ac_lordem) - 1
                    else:
                        self.new_lordem = int(self.ac_lordem) + 1

                    # Filter mapa foto layer
                    ids = [feat.id() for feat in layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(config.column_order + " ='" + 
                                                            str(self.new_lordem) +
                                                            "'"))]

                    if len(ids) == 0:
                        qgsutils.showUserAndLogMessage(
                            u"Information: ", u"There is no superiority that follows.")
                        # Filter mapa foto layer
                        ids = [feat.id() for feat in layer.getFeatures(
                            QgsFeatureRequest().setFilterExpression(config.column_order + " ='" + 
                                                                str(self.ac_lordem) +
                                                                "'"))]
                        # Update selected feature
                        self.ReloadView(ids[0])
                        return

                    self.ReloadView(ids[0])

        if self.encontrado is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")

        return

    def timer_play_image(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.PlayImage)
        self.timer.start(1500)
        self.timer_flag = True

    def PlayImage(self):
        self.layer_names = open(self.plugin_path + "/layer_names.txt","r")
        lys = self.canvas.layers()  # Check if mapa foto is loaded
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")
            return

        for layer in lys:
            for x in self.layer_names:
                if layer.name() in x:
                    self.encontrado = True
                    self.iface.setActiveLayer(layer)

                    f = self.selected_features

                    self.ac_lordem = f.attribute(config.column_order)

                    self.new_lordem = int(self.ac_lordem) + 1

                    # Filter mapa foto layer
                    ids = [feat.id() for feat in layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(config.column_order + " ='" +
                                                            str(self.new_lordem) +
                                                            "'"))]

                    if len(ids) == 0:
                        qgsutils.showUserAndLogMessage(
                            u"Information: ", u"There is no superiority that follows.")
                        # Filter mapa foto layer
                        ids = [feat.id() for feat in layer.getFeatures(
                            QgsFeatureRequest().setFilterExpression(config.column_order + " ='" +
                                                                str(self.ac_lordem) +
                                                                "'"))]
                        # Update selected feature
                        self.ReloadView(ids[0])
                        return

                    self.ReloadView(ids[0])

        if self.encontrado is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")
        return

    def PauseImage(self):
        if self.timer_flag is True:
            self.timer.stop()
            self.timer_flag = False
        return

    def FullScreen(self, value):
        ''' FullScreen action button '''
        qgsutils.showUserAndLogMessage(
            u"Information: ", u"Fullscreen.",
            onlyLog=True)
        if(value):
            self.showFullScreen()
        else:
            self.showNormal()
        return

    def ExportImage(self):
        msg = QMessageBox()
        self.current_image = self.GetImage()
        folder = QgsApplication.qgisSettingsDirPath() + 'python/plugins/image_viewer/viewer/project'
        path = qgsutils.getAttributeFromFeature(
                self.selected_features, config.column_name)
        extens = ['jpg', 'jpeg', 'JPG', 'JPEG']
        basename = os.path.basename(path)  # basename เอาเฉพาะชื่อไฟล์+สกุลไฟล์
        file_name = basename[:-len(extens)]# เอาแค่ชื่อไฟล์
        shutil.copy(self.current_image, folder)
        os.rename(QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/viewer/project/{}.JPG".format(file_name), 
                QgsApplication.qgisSettingsDirPath() + "python/plugins/image_viewer/viewer/project/{}_add.JPG".format(file_name))
        msg.setText("Export to project complete!")
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_() 
        return


    @staticmethod
    def ActualOrientation(yaw):
        ''' Get Actual yaw '''
        geo360Plugin = qgis.utils.plugins["image_viewer"]
        if geo360Plugin is not None:
            geo360Dialog = qgis.utils.plugins["image_viewer"].dlg1
            if geo360Dialog is not None:
                geo360Dialog.UpdateOrientation(yaw=float(yaw))
        return

    def UpdateOrientation(self, yaw=None):
        ''' Update Orientation '''
        self.bearing = self.B_degree
        try:
            self.actualPointOrientation.reset()
        except Exception:
            pass

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
        self.actualPointOrientation.setColor(Qt.blue)
        self.actualPointOrientation.setWidth(5)
        self.actualPointOrientation.addPoint(self.actualPointDx)

        # End Point
        CS = self.canvas.mapUnitsPerPixel() * 25
        A1x = self.actualPointDx.x() - CS * math.cos(math.pi / 2)
        A1y = self.actualPointDx.y() + CS * math.sin(math.pi / 2)

        self.actualPointOrientation.addPoint(QgsPointXY(float(A1x), float(A1y)))

        # Vision Angle
        if yaw is not None:
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180

        tmpGeom = self.actualPointOrientation.asGeometry()

        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(
            tmpGeom, self.actualPointDx, angle), self.dumLayer)

    def orientation_calulate(self):
        f = self.selected_features
        self.cur_order = f.attribute(config.column_order)
        self.next_order = int(self.cur_order) + 1
        ids = [feat.id() for feat in self.layer.getFeatures(
                    QgsFeatureRequest().setFilterExpression(config.column_order + " ='" +
                                                            str(self.next_order) +
                                                            "'"))]
        if len(ids) == 0:
            return 0

        lon = f.attribute(config.column_lon)
        lat = f.attribute(config.column_lat)
        f2 = open(QgsApplication.qgisSettingsDirPath() + 'python/plugins/image_viewer/viewer/gps_tmp.txt', "w")
        arr_lat_lon = [lat, lon]
        for i in arr_lat_lon:
            f2.write(str(i)+" ")
        f2.close()
        
        next_lon = [feat.attribute("Lon") for feat in self.layer.getFeatures(
                    QgsFeatureRequest().setFilterExpression(config.column_order + " ='" +
                                                            str(self.next_order) +
                                                            "'"))]
        next_lat = [feat.attribute("Lat") for feat in self.layer.getFeatures(
                    QgsFeatureRequest().setFilterExpression(config.column_order + " ='" +
                                                            str(self.next_order) +
                                                            "'"))]
        next_lon2 = next_lon[0]
        next_lat2 = next_lat[0]
       
                                                 
        X = math.cos(next_lat2)*math.sin(next_lon2-lon)
        Y = math.cos(lat)*math.sin(next_lat2)-math.sin(lat)*math.cos(next_lat2)*math.cos(next_lon2-lon)
        B = math.atan2(X, Y)
        self.B_degree = (B/math.pi)*180
        return self.B_degree
       
    def setOrientation(self, yaw=None):
        ''' Set Orientation in the firt time '''
        
       
        self.bearing = self.orientation_calulate()
        self.actualPointDx = self.selected_features.geometry().asPoint()
        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
        self.actualPointOrientation.setColor(Qt.blue)
        self.actualPointOrientation.setWidth(5)
        self.actualPointOrientation.addPoint(self.actualPointDx)

        # End Point
        CS = self.canvas.mapUnitsPerPixel() * 25
        A1x = self.actualPointDx.x() - CS * math.cos(math.pi / 2)
        A1y = self.actualPointDx.y() + CS * math.sin(math.pi / 2)

        self.actualPointOrientation.addPoint(QgsPointXY(float(A1x), float(A1y))) 

        # Vision Angle
        if yaw is not None:
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180

        tmpGeom = self.actualPointOrientation.asGeometry()

        self.rotateTool = transformGeometry()
        epsg = self.canvas.mapSettings().destinationCrs().authid()
        self.dumLayer = QgsVectorLayer(
            "Point?crs=" + epsg, "temporary_points", "memory")
        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(
           tmpGeom, self.actualPointDx, angle), self.dumLayer)


    def setPosition(self):
        ''' Set RubberBand Position '''
        self.actualPointDx = self.selected_features.geometry().asPoint()

        self.positionDx = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.positionDx.setWidth(6)
        self.positionDx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionDx.setIconSize(6)
        self.positionDx.setColor(Qt.black)
        self.positionSx = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.positionSx.setWidth(5)
        self.positionSx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionSx.setIconSize(4)
        self.positionSx.setColor(Qt.blue)
        self.positionInt = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.positionInt.setWidth(5)
        self.positionInt.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionInt.setIconSize(3)
        self.positionInt.setColor(Qt.white)

        self.positionDx.addPoint(self.actualPointDx)
        self.positionSx.addPoint(self.actualPointDx)
        self.positionInt.addPoint(self.actualPointDx)

    def closeEvent(self, _):
        ''' Close dialog '''
        self.resetQgsRubberBand()
        self.canvas.refresh()
        self.iface.actionPan().trigger()
        self.SaveSize()
        self.parent.dlg1 = None
        self.RemoveImage()
        self.PauseImage()
        return

    def resetQgsRubberBand(self):
        ''' Remove RubbeBand '''
        try:
            self.positionSx.reset()
            self.positionInt.reset()
            self.positionDx.reset()
            self.actualPointOrientation.reset()
        except Exception:
            None


class ClientHandler():
    ''' CefPython Event '''
    # hilarious method but work

    def OnConsoleMessage(self, browser, message, source, line, level):
        try:
            Geo360Dialog.ActualOrientation(yaw=message)
        except Exception:
            None
        return