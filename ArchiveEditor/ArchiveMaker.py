# -*- coding: utf-8 -*-

'''Archive Maker 3.

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

# standard imports
import sys
from copy import copy, deepcopy
import math
import os

import ArchiveUtilities3

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.uic as uic


# Archive modules
from Utilities import *
import helpbrowser

TITLE = 'Archive Maker 3.0'

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
        self.ui = uic.loadUi('ArchiveMakerForm.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ArchiveMaker')

        # Restore window position etc. from saved settings
        self.restoreGeometry(self.settings.value('geometry', type=QByteArray))

        # Set attribute so the window is deleted completely when closed
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

        self.browser = helpbrowser.HelpBrowser(collectionFile, QUrl(r"qthelp://G4AUC/archiveutilities/ArchiveMaker.html"))

    @pyqtSlot(bool)
    def on_pushButtonCreate_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Creates a new .csl file."""

        cslDir = self.settings.value('CslDir', '') # default = ''
        defaultFile = os.path.join(cslDir, 'untitled.csl')
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                "New csl file",
                defaultFile,
                "csl Files (*.csl);;All Files (*)",
                options=options)

        if fileName:
            head, tail = os.path.split(fileName)
            self.settings.setValue('CslDir', head)

            with open(fileName, 'w') as fs:
                fs.write('\r\n')

            self.display(fileName, colour='darkgreen')
            self.display('Created.', colour='darkgreen')
            self.display()
            self.fileName = fileName

            self.setWindowTitle(TITLE + ' - ' + tail)

    @pyqtSlot(bool)
    def on_pushButtonAdd_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Adds .edi files to a .csl file."""

        # get the file name to open
        cslDir = self.settings.value('CslDir', '') # default = ''
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Open csl file",
                cslDir,
                "csl Files (*.csl);;All Files (*)",
                options = options)

        if fileName:    # fileName is empty if cancelled
            head, tail = os.path.split(fileName)
            self.settings.setValue('CslDir', head)

            self.display(fileName, colour='darkgreen')
            self.display('Opened.', colour='darkgreen')
            self.display()

            self.setWindowTitle(TITLE + ' - ' + tail)

            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.redraw()
            self.addEdiFiles(fileName, head, tail)
            QApplication.restoreOverrideCursor()

    def addEdiFiles(self, cslFile, head, tail):

        ediDir = self.settings.value('EdiDir', '') # default = ''
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,
                "Open .edi file(s) to add to " + tail,
                ediDir,
                "edi Files (*.edi, *.EDI);;All Files (*)", options=options)

        if files:
            head, tail = os.path.split(files[0])
            self.settings.setValue('EdiDir', head)

            #display the file names
            self.display('Opening Edi File(s):', colour='darkgreen')
            for f in files:
                self.display(f, colour='darkgreen')
            self.display()

            #initialise the dictionary
            self.archiveDict=dict()

            warnings = read_archive_file(cslFile, self.archiveDict)
            # check returned warnings and display any
            if warnings:
                QMessageBox.warning(self, "File Format Warning!",
                    warnings,
                    QMessageBox.Ok)

            self.processAllEdiFiles(files, cslFile)

    def processAllEdiFiles(self, ediFileNames, cslFile):
        """Process one or more files whos file names are in 'EdiFileNames' """
        for ediFile in ediFileNames:
            self.display(ediFile + ':')
            self.display('Contacts not already in Archive:')
            self.display()
            self.addNewContacts(ediFile, self.archiveDict)
            self.display()

        #Re-write the processed archive
        re_write_csl(cslFile, self.archiveDict)

    def addNewContacts(self, FileName, archiveDict):

        """Parses the .edi file and adds the contact details to the list."""

        #initialise
        gettingData = False

        #Open the input file
        f = open(FileName,'r')

        try:
            for line in f:      # iterate through all the lines in file 'f'

                if gettingData:

                    #parameters in 'line' are separated by ';'
                    #split the line and create a list of the parameters
                    parameters=line.split(';')

                    if len(parameters)>=10:     #check line contains 10 or more parameters

                        #create a tuple (callsign,locator,exchange)
                        contact=(parameters[2],parameters[9],parameters[8])
                        date = format_date(parameters[0])

                        if contact not in archiveDict:
                            if contact[0]!='': #ignore blank callsign entries
                                #append the parameters to the list and text display
                                timesSeen=1
                                archiveDict[contact]=[timesSeen,date+';']
                                self.display(contact[0]+','+contact[1]+','+contact[2]+' on '+ date)
                        else:
                             #don't repeatedly add the same contact on the same date
                            if date not in archiveDict[contact][1]:
                                #increment times seen
                                archiveDict[contact][0]+=1

                                #add date to contact
                                archiveDict[contact][1]+=date+';'


                elif '[QSORecords' in line:
                    #skip until the line contains [QSORecords
                    gettingData=True
        finally:
            if not gettingData:
                archiveDict[('','','')]=[0,';'] #Create dummy entry if file does not contain [QSORecords

            #close file at end of input
            f.close()

    def closeEvent(self, event):

        '''Override inherited QMainWindow closeEvent.

            Do any cleanup actions before the application closes.

            Saves the application geometry.
            '''

        self.settings.setValue("geometry", self.saveGeometry())
        #ArchiveUtilities3.mainWindow.maker = None
        
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



