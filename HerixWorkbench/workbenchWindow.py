#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from spec2nexus.spec import SpecDataFile
from specguiutils.scanbrowser import ScanBrowser
from specguiutils.scantypeselector import ScanTypeSelector, SCAN_TYPES
from HerixWorkbench.source.DetectorSelector import SelectorContainer
from HerixWorkbench.source.PlotWidget import PlotWidget



class HerixWorkbenchWindow(QMainWindow):
    """Main window class"""
    def __init__(self, parent=None):
        super(HerixWorkbenchWindow, self).__init__(parent)
        self.setGeometry(50, 50, 1500, 800)
        self.setWindowTitle("Herix Workbench")
        self.setMinimumSize(1000, 650)
        self.windowSplitter = QSplitter()
        self.PlotWidget = PlotWidget()
        self.plotWidget = self.PlotWidget.plotWidget
        self.selectedDetectors = []

        self.CreateSpecDataSplitter()
        self.createMenuBar()
        self.windowSplitter.addWidget(self.specSplitter)
        self.windowSplitter.addWidget(self.plotWidget)
        self.setCentralWidget(self.windowSplitter)

    def CreateSpecDataSplitter(self):
        """Creates the QSplitter with the spec and detector widgets."""
        self.specSplitter = QSplitter()
        self.specSplitter.setOrientation(Qt.Vertical)
        self.createPlotTypeComboBox()

        self.scanBrowser = ScanBrowser()
        self.scanBrowser.setFixedWidth(405)
        self.scanTypeSelector = ScanTypeSelector()
        self.scanTypeSelector.setFixedWidth(400)
        self.selectorContainer = SelectorContainer()
        self.selectorContainer.detectorsSelected.connect(self.setSelectedPlotDetectors)

        self.specSplitter.addWidget(self.scanTypeSelector)
        self.specSplitter.addWidget(self.scanBrowser)
        self.specSplitter.addWidget(self.plotTypeWidget)
        self.specSplitter.addWidget(self.selectorContainer)
        self.specSplitter.addWidget(QWidget())

    def createMenuBar(self):
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        fileMenu = menuBar.addMenu("File")

        openAction = QAction("Open", self)
        openAction.triggered.connect(self.openSpecFile)

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

    def createPlotTypeComboBox(self):
        """Creates the plot type QComboBox:single or multi."""
        self.plotTypeWidget = QWidget()
        self.plotTypeWidget.setFixedWidth(400)
        hLayout = QHBoxLayout()
        self.plotTypeCB = QComboBox()
        self.plotTypeCB.addItem("Single")
        self.plotTypeCB.addItem("Multi")
        self.plotTypeCB.currentIndexChanged.connect(self.updatePlot)

        hLayout.addWidget(QLabel("Plot Type: "))
        hLayout.addWidget(self.plotTypeCB)

        self.plotTypeWidget.setLayout(hLayout)

    def openSpecFile(self):
        fileName, specFilterName = QFileDialog.getOpenFileName(self, "Open spec file", None, "*.spec")
        self.specFile = None

        if fileName != "":
            try:
                self.PlotWidget.loadSpecFile(fileName)
                self.scans = self.PlotWidget.getScans()
                self.loadScans()
            except Exception as ex:
                QMessageBox.warning(self, "Loading error",
                                    "There was an error loading the spec file. \n\nException: " + str(ex))

    def loadScans(self):
        """Loads the spec information to specguiutils widgets.
        :return:
        """
        self.scanBrowser.loadScans(self.scans)
        scanTypes = self.PlotWidget.getScanTypes()
        self.scanTypeSelector.loadScans(scanTypes)
        self.scanTypeSelector.scanTypeChanged.connect(self.filterScansByType)
        self.scanBrowser.scanSelected.connect(self.PlotWidget.scanSelection)
        self.scanBrowser.scanList.setSelectionMode(QAbstractItemView.SingleSelection)
        # Might need this for later, for multi selection.
        #self.scanBrowser.scanList.setSelectionMode(QAbstractItemView.MultiSelection)

    def filterScansByType(self):
        """Reloads the ScanBrowser filter by the selected scan type."""
        if self.scanTypeSelector.getCurrentType() == 'All':
            self.scanBrowser.loadScans(self.scans)
        else:
            self.scanBrowser.filterByScanTypes(self.scans, self.scanTypeSelector.getCurrentType())

    def setSelectedPlotDetectors(self, detectors):
        """Method will be called when a detector is selected or unselected. """
        self.selectedDetectors = []
        for d in detectors:
            self.selectedDetectors.append('Ana'+str(d))
        self.updatePlot()

    def updatePlot(self):
        """This method gets called when the plot type QCombox changes index."""
        if self.PlotWidget.specOpen == True:
            plotType = self.plotTypeCB.currentText()
            if plotType == "Single":
                self.PlotWidget.singlePlot(self.selectedDetectors)
            else:
                self.PlotWidget.multiPlot(self.selectedDetectors)


def main():
    """Main method.
    """
    app = QApplication(sys.argv)
    herixWindow = HerixWorkbenchWindow()
    herixWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()