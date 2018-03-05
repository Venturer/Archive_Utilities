# -*- coding: utf-8 -*-

'''Archive Checker 3.

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

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.uic as uic

# Archive modules
from Utilities import *
import Help
import ArchiveUtilities3

TITLE = 'Archive Checker 3.0'

helpText = """
Help for Archive Checker:

Click button: Check an Archive for possible erroneous entries

A dialogue will open.
Select an existing .csl archive file.

The Entries in the archive will be checked against all other entries in the .csl file.

A report showing each entry and possible matches in the archive will be produced.

Look at the report to see if there are any questionable entries in the archive that need to be checked.

Remember people do change QTH and change callsign, particularly from Foundation to Intermediate to Full.

Date format is: yyyy/mm/dd

Right click on the report for an edit menu which will allow you to cut and paste the report into another document.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS &AS IS& AND ANY EXPRESSOR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

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


class MainApp(QMainWindow):

    '''Main Qt5 Window.'''

    edited = False
    fileName = ''

    def __init__(self):

        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        # Load the GUI definition file
        # use 2nd parameter self so that events can be overriden
        self.ui = uic.loadUi('ArchiveChecker.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ArchiveChecker')

        # Restore window position etc. from saved settings
        try:
            self.restoreGeometry(self.settings.value('geometry'))
        except:
            # exception thrown when there are no saved settings yet
            pass # starts with geometry from ui file

        # Show the Application
        self.show()

        self.setWindowTitle(TITLE)

    @pyqtSlot(bool)
    def on_pushButtonHelp_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Creates a new .csl file."""

        help = Help.MainApp()
        help.setWindowTitle('Help for ' + TITLE)
        help.show()

        help.textEdit.setText(helpText)

    @pyqtSlot(bool)
    def on_pushButtonCheck_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Creates a new .csl file."""

        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents(QEventLoop.AllEvents)

        # get the file name to open
        cslDir = self.settings.value('CslDir', '') # default = ''
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,
                "Open csl file",
                cslDir,
                "csl Files (*.csl);;All Files (*)",
                options = options)

        if fileName:

            self.display() # blank line
            self.display('Checking:', fileName, colour='darkgreen')
            self.display()

            head, tail = os.path.split(fileName)
            self.settings.setValue('CslDir', head)
            self.setWindowTitle(TITLE + ' - ' + tail)

            self.checked = self.checkBoxSimilarLocators.isChecked()


            self.createReport(fileName, self.checked)
        QApplication.restoreOverrideCursor()

    def createReport(self,TheArchiveFilename, Checked):

        #Initialise Lists
        self.archiveDict=dict()
        self.entryList=[]

        readArchiveFile(TheArchiveFilename, self.archiveDict)

        Keys= list(self.archiveDict.keys())

        Keys.sort()

        #iterate over the archiveList
        for contact in Keys:

            timesSeen, dates = self.archiveDict[contact]

            #Display the contact
            self.display('\n'+'  '+contact[0]+','+contact[1]+','+contact[2])
            if timesSeen==1:
                self.display('   worked once on '+dates)
            else:
                self.display('   worked '+str(timesSeen)+' times on '+dates)

            # Get ant fuzzy matches
            matchesList = fuzzyMatch(contact,Checked,self.archiveDict)

            # Display the fuzzy match list
            if matchesList!=[]:
                self.display('    Near Matches:')
                for match in matchesList:
                    self.display('    '+match[0]+','+match[1]+','+match[2]+' '+match[4])
                    if match[3]==1:
                        self.display('     worked once on '+match[5])
                    else:
                        self.display('     worked '+str(match[3])+' times on '+match[5])

            report = checkLocatorIsInCorrectCountry(contact[0], contact[1])
            if report:
                self.display(report)

            self.display()

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



