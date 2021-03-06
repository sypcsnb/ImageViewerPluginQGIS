# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImageViewer
                                 A QGIS plugin
 Import private geotag panorama photo and view it.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-02-24
        copyright            : (C) 2020 by Sayumporn Thammasen
        email                : sayumporncs27@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

import sys

try:
    sys.path.append(
        "D:\eclipse\plugins\org.python.pydev.core_7.0.3.201811082356\pysrc")
    from pydevd import *
except ImportError:
    None

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ImageViewer class from file ImageViewer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .image_viewer import ImageViewer
    return ImageViewer(iface)
