# -*- coding: utf-8 -*-

'''Help Collection Browser.

    A Qt5 based module for Python 3.5 or greater.

    A HelpTextBrowser class and a general purpose
    HelpBrowser main window class with HTML and
    Qt help collection support.'''


# Version 1.0, December 2017

# standard imports
import sys
import os

# Third party dependencies (install using pip):

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtHelp import *
import PyQt5.uic as uic

TITLE = 'Help Browser'

class HelpTextBrowser(QTextBrowser):

    """A subclass of QTextBrowser that handles Qt help collection files."""

    def __init__(self, helpEngine=None, parent=None):
        """Constructor."""

        super().__init__(parent)

        self.helpEngine = helpEngine
        self.anchorClicked.connect(self.on_anchorClicked)

    @pyqtSlot(QUrl)
    def on_anchorClicked(self, url: QUrl):
        """Action slot for the anchorClicked signal.

            If url scheme is qthelp or file, set url to the
            help text browser source otherwise open
            the url with QDesktopServices
            for external links etc."""

        if url.scheme() in  ["qthelp", "file"]:
            self.setSource(url)
        else:
            self.reload()
            QDesktopServices.openUrl(url) # Open in default web browser

    def loadResource(self, type_: int, url: QUrl):
        """Override inherited loadResource method.

            If url scheme is qthelp set the file data to the
            help text browser otherwise pass arguments
            on to the inherited method."""

        if self.helpEngine and (url.scheme() == "qthelp"):
            data = self.helpEngine.fileData(url)
            return data
        else:
            return super().loadResource(type_, url)

class HelpBrowser(QMainWindow):

    '''Main Qt5 Window.'''

    edited = False
    fileName = ''
    header = ''

    def __init__(self, helpCollection, startUrl=None)-> None:
        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        path = os.path.dirname(os.path.realpath(__file__))

        self.helpEngine = QHelpEngine(helpCollection)
        self.helpEngine.setupData()

        # Create the Qt User Interface
        self.ui = uic.loadUi(os.path.join(path, 'helpbrowser.ui'), self)
        self.createUI(self.helpEngine)

        if startUrl:
            self.textBrowser.setSource(startUrl)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ArchiveUtilities/HelpBrowser')
        #self.settings.clear()

        # Restore window position etc. from saved settings
        self.restoreGeometry(self.settings.value('geometry', type=QByteArray))

        # Set attribute so the Help Browser is deleted completly when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Show the Browser
        self.show()

        # restore the splitter positition after the app is showing
        self.splitter.restoreState(self.settings.value("splitterSizes", type=QByteArray))

        self.setWindowTitle(TITLE)

    def createUI(self, helpEngine: QHelpEngine)-> None:
        """Create and initialise the user interface elements that
            cannot be set up in the ui file."""

        #self.frame_layout_index.addWidget(helpEngine.indexWidget())
        self.contents_layout.addWidget(helpEngine.contentWidget())
        self.index_layout.addWidget(helpEngine.indexWidget())

        # Delete the placehoder
        self.textBrowserPlaceholder.hide()
        del self.textBrowserPlaceholder

        # Create help text browser
        self.textBrowser = HelpTextBrowser(helpEngine)
        self.splitter.addWidget(self.textBrowser)
        self.textBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add the browser to the splitter
        self.splitter.addWidget(self.textBrowser)

        # Back action
        self.actionBack.triggered.connect(self.textBrowser.backward)
        self.textBrowser.backwardAvailable.connect(self.actionBack.setEnabled)

        # Forward action
        self.actionForward.triggered.connect(self.textBrowser.forward)
        self.textBrowser.forwardAvailable.connect(self.actionForward.setEnabled)

        # Zoom In action
        self.actionZoomIn.triggered.connect(self.textBrowser.zoomIn)

        # Zoom Out action
        self.actionZoomOut.triggered.connect(self.textBrowser.zoomOut)

        # Link helpEngine signals
        helpEngine.contentWidget().linkActivated.connect(self.textBrowser.setSource)
        helpEngine.indexWidget().linkActivated.connect(self.textBrowser.setSource)
        helpEngine.indexWidget().linksActivated.connect(self.on_linksActivated)

    @pyqtSlot(str)
    def on_indexFilter_textChanged(self, text: str)-> None:
        """Slot triggered when the text in QLineEdit indexFilter is changed.

            Filters the Index Widget contents using the text."""

        self.helpEngine.indexModel().filter(text, '')

    def on_linksActivated(self, map: dict, keyword: str)-> None:
        """Slot triggered when the text in the index window
            is double clicked and the keyword refers to more than
            one topic.

            map: dict {topic : QUrl} : The topics and their QUrls

            Shows a QInputDialog and displays the topic selected
            from the combo box.

            The HTML files must have unique <title> tags
            to indicate the topic."""

        topic, ok = QInputDialog.getItem(self, 'Choose', 'Select topic for: ' + keyword,
                                         list(map.keys()), editable=False)

        if ok:
            self.textBrowser.setSource(map[topic])

    def setHtmlText(self, html: str)-> None:
        """Set raw HTML text to the text browser."""

        self.textBrowser.clear()
        self.textBrowser.setHtml(html)

    def loadHtmlFromFile(self, fileName: str)-> None:
        """Set raw HTML text from the file to the text browser."""

        self.textBrowser.clear()

        path, name = os.path.split(fileName)

        self.textBrowser.setSearchPaths([path])
        self.textBrowser.setSource(QUrl().fromLocalFile(fileName))

    @pyqtSlot(int, int)
    def on_splitter_splitterMoved(self, pos, index):
        """Slot triggered when the splitter is moved.

            Saves the new position in the settings."""

        self.settings.setValue("splitterSizes", self.splitter.saveState())

    def closeEvent(self, event: QCloseEvent)-> None:
        '''Override inherited QMainWindow closeEvent.

            Do any cleanup actions before the application closes.

            Saves the application geometry.
            '''

        self.settings.setValue("geometry", self.saveGeometry())

        event.accept()

    def resizeEvent(self, event: QResizeEvent)-> None:
        """Override inherited QMainWindow resize event.

            Saves the window geometry."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().resizeEvent(event)

    def moveEvent(self, event: QMoveEvent)-> None:
        """Override inherited QMainWindow move event.

            Saves the window geometry.."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().moveEvent(event)


if __name__ == "__main__":

    # When testing can run as a standalone application

    app = QApplication(sys.argv)

    head, tail = os.path.split(sys.argv[0])
    helpCollection = os.path.join(head, r"helpfiles\archiveutilities.qhc")

    startUrl = QUrl(r"qthelp://G4AUC/archiveutilities/ArchiveUtilities.html")

    mainWindow = HelpBrowser(helpCollection, startUrl)

    sys.exit(app.exec_())

