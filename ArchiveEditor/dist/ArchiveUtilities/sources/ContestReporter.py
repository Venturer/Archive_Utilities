# -*- coding: utf-8 -*-

'''Contest Reporter 3.

    A Qt5 based program for Python3.

    Check .edi files used by Minos.'''

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

TITLE = 'Contest Reporter 3.0'

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
        self.ui = uic.loadUi('ContestReporterForm.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ContestReporter')

        # Restore window position etc. from saved settings
        self.restoreGeometry(self.settings.value('geometry', type=QByteArray))

        # Set attribute so the window is deleted completly when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Show the Application
        self.show()

        self.setWindowTitle(TITLE)

    @pyqtSlot(bool)
    def on_pushButtonHelp_clicked(self, similarLocatorsChecked):

        """Slot triggered when the button is clicked.

            Creates a new help window."""

        path = os.path.dirname(os.path.realpath(__file__))

        collectionFile = os.path.join(
                path,
                r"archiveutilities.qhc")

        self.browser = helpbrowser.HelpBrowser(collectionFile, QUrl(r"qthelp://G4AUC/archiveutilities/ContestReporter.html"))

    @pyqtSlot(bool)
    def on_pushButtonReport_clicked(self, similarLocatorsChecked):

        """Slot triggered when the button is clicked.

            Creates a report on the edi file."""

        # get the file name to open
        ediDir = self.settings.value('EdiDir', '') # default = ''
        options = QFileDialog.Options()
        theEntryFileName, _ = QFileDialog.getOpenFileName(self,
                'Open the Contest Entry (.edi) file to be checked',
                ediDir,
                "edi Files (*.edi, *.EDI);;All Files (*)",
                options = options)

        if theEntryFileName:

            head, tail = os.path.split(theEntryFileName)
            self.settings.setValue('EdiDir', head)

            self.display() # blank line
            self.display('Opening:', theEntryFileName, colour='darkgreen')

            # get the file name to open
            cslDir = self.settings.value('CslDir', '') # default = ''
            options = QFileDialog.Options()
            theArchiveFileName, _ = QFileDialog.getOpenFileName(self,
                    'Open the Archive file to check against',
                    cslDir,
                    "csl Files (*.csl);;All Files (*)",
                    options = options)

            if theArchiveFileName:

                head, tail = os.path.split(theArchiveFileName)
                self.settings.setValue('CslDir', head)

                self.display() # blank line
                self.display('Reporting on:', theEntryFileName,
                             'Checking aginst:', theArchiveFileName,
                             colour='darkgreen')
                self.display()
                self.display('Checking aginst:', theArchiveFileName,
                             colour='darkgreen')

                head, tail = os.path.split(theEntryFileName)
                self.setWindowTitle(TITLE + ' - ' + tail)

                similarLocatorsChecked = self.checkBoxSimilarLocators.isChecked()

                #Create the report
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.createReport(theArchiveFileName, theEntryFileName, similarLocatorsChecked)
                QApplication.restoreOverrideCursor()

    def processUniques(self, similarLocatorsChecked):

        self.display()
        self.display('The following are not in the archive:')
        self.display()

        #iterate over the uniqueList
        for contact in self.uniqueList:
            #Display the contact
            self.display('  '+contact[0]+','+contact[1]+','+contact[2])
            #Get any fuzzy matches
            matchesList= fuzzyMatch(contact, similarLocatorsChecked, self.archiveDict)
            #Display the fuzzy matches list
            if matchesList!=[]:
                self.display('    Near Matches:')
                for match in matchesList:
                    self.display('    '+match[0]+','+match[1]+','+match[2]+' '+match[4])
                    if match[3]==1:
                        self.display('       worked once on '+match[5])
                    else:
                        self.display('       worked '+str(match[3])+' times on '+match[5])

            report = checkLocatorIsInCorrectCountry(contact[0], contact[1])
            if report:
                self.display(report, colour='red')

            self.display()

    def processWorkedBefore(self, similarLocatorsChecked):

        self.display()
        self.display('The following already exist in the archive:')

        #iterate over the workedBeforeList
        for contact in self.workedBeforeList:

            #Find timesSeen and dates in archiveDict
            seen=self.archiveDict[contact]

            #Display the contact
            self.display('')
            self.display('  '+contact[0]+','+contact[1]+','+contact[2])
            if seen[0]==1:
                self.display('      worked once on '+seen[1])
            else:
                self.display('      worked '+str(seen[0])+' times on '+seen[1])
            #Get ant fuzzy matches
            matchesList= fuzzyMatch(contact, similarLocatorsChecked, self.archiveDict)
            #Display the fuzzy match list
            if matchesList!=[]:
                self.display('    Near Matches:')
                for match in matchesList:
                    self.display('    '+match[0]+','+match[1]+','+match[2]+' '+match[4])
                    if match[3]==1:
                        self.display('       worked once on '+match[5])
                    else:
                        self.display('       worked '+str(match[3])+' times on '+match[5])
            report= checkLocatorIsInCorrectCountry(contact[0], contact[1])
            if report:
                self.display(report, colour='red')

    def createReport(self, theArchiveFileName, theEntryFileName, similarLocatorsChecked):

        #Initialise Lists and dictionary
        self.entryList=[]
        self.uniqueList=[]
        self.workedBeforeList=[]
        self.archiveDict=dict()

        self.display()
        self.display('Date Format: yyyy/mm/dd')

        readEntryFile(theEntryFileName, self.entryList)

        readArchiveFile(theArchiveFileName, self.archiveDict)

        for contact in self.entryList:
            if contact not in self.archiveDict:
                self.uniqueList.append(contact)
            else:
                self.workedBeforeList.append(contact)

        self.processUniques(similarLocatorsChecked)
        self.processWorkedBefore(similarLocatorsChecked)

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



