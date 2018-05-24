# -*- coding: utf-8 -*-

'''Archive Utilities 3.

    A Qt5 based program for Python3.

    Manages csl files used by Minos.'''

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

# Version 3.0, November 2017
# Version 3.0 rc2, rc3 May 2018

# standard imports
import sys
import os

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.uic as uic

# Archive modules
import ArchiveEditor
import ArchiveMaker
import ArchiveCheckerThreaded
import MergeArchives
import ContestReporter
import helpbrowser


TITLE = 'Archive Utilities 3.0 rc3'


class MainApp(QMainWindow):

    '''Main Qt5 Window.'''

    fileName = ''

    def __init__(self):

        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        # Load the GUI definition file
        # use 2nd parameter self so that events can be overriden
        self.ui = uic.loadUi('ArchiveUtilities.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ArchiveUtilities3')

        # Restore window position etc. from saved settings
        self.restoreGeometry(self.settings.value('geometry', type=QByteArray))

        # Initialise instance variables
        self.maker = None
        self.checker = None
        self.merger = None
        self.editor = None
        self.reporter = None
        self.help = None

        # Show the Application
        self.show()

        self.setWindowTitle(TITLE)

    @pyqtSlot(bool)
    def on_pushButtonHelp_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Shows help file."""

        try:
            self.help.show()
        except (AttributeError, RuntimeError):
            path = os.path.dirname(os.path.realpath(__file__))

            collectionFile = os.path.join(
                path,
                r"archiveutilities.qhc")

            self.browser = helpbrowser.HelpBrowser(collectionFile,
                                                   QUrl(r"qthelp://G4AUC/archiveutilities/ArchiveUtilities.html"))


    @pyqtSlot(bool)
    def on_pushButtonArchiveMaker_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Opens the .csl file maker."""

        try:
            self.maker.show()
        except (AttributeError, RuntimeError):
            self.maker = ArchiveMaker.MainApp()


    @pyqtSlot(bool)
    def on_pushButtonArchiveChecker_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Opens the .csl file and checks it."""

        try:
            self.checker.show()
        except (AttributeError, RuntimeError):
            self.checker = ArchiveCheckerThreaded.MainApp()

    @pyqtSlot(bool)
    def on_pushButtonMergeArchives_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Opens the .csl file Merger."""

        try:
            self.merger.show()
        except (AttributeError, RuntimeError):
            self.merger = MergeArchives.MainApp()

    @pyqtSlot(bool)
    def on_pushButtonArchiveEditor_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Opens the .csl file Editor."""

        try:
            self.editor.show()
        except (AttributeError, RuntimeError):
            self.editor = ArchiveEditor.MainApp()

    @pyqtSlot(bool)
    def on_pushButtonContestReporter_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Opens the .csl file Reporter."""

        try:
            self.reporter.show()
        except (AttributeError, RuntimeError):
            self.reporter = ContestReporter.MainApp()

    def closeEvent(self, event):

        '''Override inherited QMainWindow closeEvent.

            Do any cleanup actions before the application closes.

            Saves the application geometry.
            '''

        self.settings.setValue("geometry", self.saveGeometry())
        if self.help:
            self.help.close()
            del self.help
        event.accept()

    # --- Methods not normally modified:

    def resizeEvent(self, event):

        """Extend inherited QMainWindow resize event.

            Saves the window geometry."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().resizeEvent(event)

    def moveEvent(self, event):

        """Extend inherited QMainWindow move event.

            Saves the window geometry.."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().moveEvent(event)


if __name__ == "__main__":

        app = QApplication(sys.argv)
        mainWindow = MainApp()
        sys.exit(app.exec_())


