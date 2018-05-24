# -*- coding: utf-8 -*-

'''Merge Archives 3.

    A Qt5 based program for Python3.

    Merges csl files used by Minos.'''

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

# standard imports
import sys
from copy import copy, deepcopy
import math
import os

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.uic as uic

# Archive modules
from Utilities import *
import helpbrowser

TITLE = 'Merge Archives 3.0'

def AppendTextToTextEdit(tEdit, txt, colour = 'black'):

    '''Appends the text in txt to the end of the tEdit, a QTextEdit.

        The text colour is set by the parameter colour.
        The text is added as a new line in an html table.'''

    # convert spaces to html escape characters
    text = txt.replace(' ', '&nbsp;')

    # build the html string
    html = '<table cellspacing=0 width=100%><tr><td style= "color:'
    html += colour
    html += '">'
    html += text
    html += '</td></tr></table>'

    # get the cursor from the tEdit
    cursor = tEdit.textCursor()

    # position at end of line
    cursor.movePosition(cursor.End)
    pos = cursor.position()

    # insert the text
    cursor.insertHtml(html)

    cursor.setPosition(pos, cursor.MoveAnchor)
    cursor.movePosition(cursor.End, cursor.KeepAnchor)
    cursor.clearSelection()

    # position so viewport scrolled to left
    cursor.movePosition(cursor.Up)
    cursor.movePosition(cursor.StartOfLine)
    tEdit.setTextCursor(cursor)
    tEdit.ensureCursorVisible()


class MainApp(QWidget):

    '''Main Qt5 Window.'''

    edited = False
    fileName = ''

    def __init__(self):

        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        # Load the GUI definition file
        # use 2nd parameter self so that events can be overriden
        self.ui = uic.loadUi('MergeArchivesForm.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'MergeArchives')

        # Restore window position etc. from saved settings
        self.restoreGeometry(self.settings.value('geometry', type=QByteArray))

        # Set attribute so the window is deleted completly when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Show the Application
        self.show()

        self.setWindowTitle(TITLE)

    @pyqtSlot(bool)
    def on_pushButtonHelp_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Creates a new help window."""

        path = os.path.dirname(os.path.realpath(__file__))

        collectionFile = os.path.join(
                path,
                r"archiveutilities.qhc")

        self.browser = helpbrowser.HelpBrowser(collectionFile, QUrl(r"qthelp://G4AUC/archiveutilities/MergeArchives.html"))

    @pyqtSlot(bool)
    def on_pushButtonMerge_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Creates a new .csl file."""

        # get the file name to open
        cslDir = self.settings.value('CslDir', '') # default = ''
        options = QFileDialog.Options()
        self.archiveFirstFileName, _ = QFileDialog.getOpenFileName(self,
                'Choose Archive file to merge from',
                cslDir,
                "csl Files (*.csl);;All Files (*)",
                options = options)

        if self.archiveFirstFileName:

            self.display() # blank line
            self.display('Opening:', self.archiveFirstFileName, colour='darkgreen')

            # get the file name to open
            options = QFileDialog.Options()
            self.ArchiveSecondFile, _ = QFileDialog.getOpenFileName(self,
                    'Choose an Archive to merge contacts into',
                    cslDir,
                    "csl Files (*.csl);;All Files (*)",
                    options = options)

            if self.ArchiveSecondFile:

                self.display() # blank line
                self.display('Merging into:', self.ArchiveSecondFile, colour='darkgreen')

                head, tail = os.path.split(self.ArchiveSecondFile)
                self.settings.setValue('CslDir', head)
                self.setWindowTitle(TITLE + ' - ' + tail)

                #Merge the archives
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.Merge(self.archiveFirstFileName, self.ArchiveSecondFile)
                QApplication.restoreOverrideCursor()

    def Merge(self, ArchiveFirstFileName, ArchiveSecondFileName):

        #Initialise Lists and dictionary

        self.archiveFirstDict=dict()
        self.archiveSecondDict=dict()

        self.display()
        self.display('Contacts added to Archive')

        warnings = read_archive_file(ArchiveFirstFileName, self.archiveFirstDict)
        # check returned warnings and display any
        if warnings:
            QMessageBox.warning(self, "First archive file Format Warning!",
                                warnings,
                                QMessageBox.Ok)

        warnings = read_archive_file(ArchiveSecondFileName, self.archiveSecondDict)
        # check returned warnings and display any
        if warnings:
            QMessageBox.warning(self, "Second archive file Format Warning!",
                                warnings,
                                QMessageBox.Ok)

        for contact in self.archiveFirstDict:
            if contact not in self.archiveSecondDict:
                self.archiveSecondDict[contact]=self.archiveFirstDict[contact]
                self.display(contact[0]+','+contact[1]+','+contact[2])
            else:
                self.archiveSecondDict[contact][0]+=self.archiveFirstDict[contact][0]
                self.archiveSecondDict[contact][1]+=self.archiveFirstDict[contact][1]

        re_write_csl(ArchiveSecondFileName, self.archiveSecondDict)

    def closeEvent(self, event):

        '''Override inherited QMainWindow closeEvent.

            Do any cleanup actions before the application closes.

            Saves the application geometry.
            '''

        self.settings.setValue("geometry", self.saveGeometry())

        event.accept()

    # --- Methods not normally modified:

    def display(self, *items, colour = 'black'):

        '''Display the items on the text edit control using their normal
            string representations on a single line.
            A space is added between the items.
            Any trailing spaces are removed.

            If the colour is not given the default
            colour ('black') is used. The colour, if used, must be given
            as a keyword argument.

            The colour may be be any string that may be
            passed to QColor, such as a name like 'red' or
            a hex value such as '#F0F0F0'.
            '''

        display_string = ''
        for item in items:
            display_string += '{} '.format(item)

        tEdit = self.textEdit
        AppendTextToTextEdit(tEdit, display_string.rstrip(' '), colour)

    def resizeEvent(self, event):

        """Override inherited QMainWindow resize event.

            Saves the window geometry."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().resizeEvent(event)

    def moveEvent(self, event):

        """Override inherited QMainWindow move event.

            Saves the window geometry.."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().moveEvent(event)


if __name__ == "__main__":

        app = QApplication(sys.argv)
        mainWindow = MainApp()
        sys.exit(app.exec_())



