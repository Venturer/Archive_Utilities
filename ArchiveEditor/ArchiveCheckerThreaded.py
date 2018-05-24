# -*- coding: utf-8 -*-

"""Archive Checker 3.

    A Qt5 based program for Python3.

    Manages csl files used by Minos."""

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

TITLE = 'Archive Checker 3.0'


def AppendTextToTextEdit(tEdit, txt, colour='black'):
    """Appends the text in txt to the end of the tEdit, a QTextEdit.

        The text colour is set by the parameter colour.
        The text is added as a new line in an html table."""

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


class Engine(QObject):
    """A calculation Engine that runs in a thread."""

    # Signals emitted by the engine
    finishedSig = pyqtSignal()
    displaySig = pyqtSignal(str, str)
    debugDisplaySig = pyqtSignal(str)
    warningDisplaySig = pyqtSignal(str)

    displayString = ''
    displayCount = 0

    @pyqtSlot(str, bool)
    def runEngine(self, TheArchiveFilename, similarLocatorsChecked):

        """Thread method that runs when the MainApp emits the signal to
            run it.

            Emits the signal finishedSig when it has finished."""

        # Initialise Lists
        self.archiveDict = dict()
        self.entryList = []
        self.displayString = ''

        warnings = read_archive_file(TheArchiveFilename, self.archiveDict)
        # check returned warnings and display
        if warnings:
            self.warningDisplaySig.emit(warnings)

        Keys = list(self.archiveDict.keys())

        Keys.sort()

        # iterate over the archiveList
        for contact in Keys:

            timesSeen, dates = self.archiveDict[contact]

            # Display the contact
            self.display('\n' + '  ' + contact[0] + ',' + contact[1] + ',' + contact[2])
            if timesSeen == 1:
                self.display('      worked once on ' + dates)
            else:
                self.display('      worked ' + str(timesSeen) + ' times on ' + dates)

            # Get any fuzzy matches
            matchesList = fuzzy_match(contact, similarLocatorsChecked, self.archiveDict)

            # Display the fuzzy match list
            if matchesList:
                self.display('    Near Matches:')
                for match in matchesList:
                    self.display('    ' + match[0] + ',' + match[1] + ',' + match[2] + ' ' + match[4])
                    if match[3] == 1:
                        self.display('       worked once on ' + match[5])
                    else:
                        self.display('       worked ' + str(match[3]) + ' times on ' + match[5])

            report = check_locator_is_in_correct_country(contact[0], contact[1])
            if report:
                self.display(report)

        self.sendDisplay('black')

        # tell the MainApp the action has finished
        self.finishedSig.emit()

    # --- Text Edit display methods, not normally modified:

    def sendDisplay(self, colour):
        """Emit signal to send the self.displayString and colour to the Main Window."""

        self.displaySig.emit(self.displayString, colour)

    def display(self, *items):

        """Add the items to self.displayString using their normal string representations
            so that they may be displayed on a text edit control in the Main Window using
            sendDisplay.
            """

        display_string = ''
        for item in items:
            display_string += '{} '.format(item)

        # add to self.displayString
        self.displayString += display_string + '\n'

    def debug(self, *items):

        """Display the items on a text edit control in the Main Window
            using their normal string representations.

            The colour is always orange.

            The display may be disabled once the program has
            been debugged by changing MainApp attribute self.showDebug.
            """

        display_string = ''
        for item in items:
            display_string += '{} '.format(item)

        # emit signal to send the string and colour to the Main Window
        self.debugDisplaySig.emit(display_string)


class MainApp(QWidget):
    """Main Qt5 Window."""

    # signals emitted by the MainApp
    runSig = pyqtSignal(str, bool)
    canClose = True

    showDebug = False  # Indicates whether debug info is shown on the text display

    def __init__(self):

        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        # 0 - Load the GUI definition file
        # use 2nd parameter self so that events can be overriden
        self.ui = uic.loadUi('ArchiveCheckerForm.ui', self)

        # 1 - Create Engine and Thread inside the MainApp
        self.engine = Engine()  # no parent!
        self.thread = QThread()  # with parent!

        # 2 - Connect Engine's Signals to MainApp method slots to post data
        self.engine.displaySig.connect(self.onThreadDisplay)
        self.engine.debugDisplaySig.connect(self.onThreadDebugDisplay)
        self.engine.warningDisplaySig.connect(self.on_thread_warning_display)

        # 3 - Move the Engine object to the Thread object
        self.engine.moveToThread(self.thread)

        # 4 - Connect Engine Finished Signal to the Form slot
        self.engine.finishedSig.connect(self.onThreadFinished)

        # 5 - Connect action signals to slot methods
        # methods of the form:
        # self.on_componentName_signalName
        # are connected automatically from the ui file
        self.runSig.connect(self.engine.runEngine)

        # 6 - Start the thread
        self.thread.start(QThread.LowPriority)  # pass parameter QThread.HighPriority etc. if needed

        # 7 - Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ArchiveChecker')

        # 8 - restore window position etc. from saved settings
        self.restoreGeometry(self.settings.value('geometry', type=QByteArray))

        # Set attribute so the window is deleted completely when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        # 9 - Show the Application
        self.show()

        self.setWindowTitle(TITLE)

    @pyqtSlot(bool)
    def on_pushButtonHelp_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Creates a new help window."""

        path = os.path.dirname(os.path.realpath(__file__))

        collection_file = os.path.join(
            path,
            r"archiveutilities.qhc")

        self.browser = helpbrowser.HelpBrowser(collection_file,
                                               QUrl(r"qthelp://G4AUC/archiveutilities/ArchiveChecker.html"))

    @pyqtSlot(bool)
    def on_pushButtonCheck_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Checks a .csl file."""

        # get the file name to open
        csl_dir = self.settings.value('CslDir', '')  # default = ''
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Open csl file",
                                                   csl_dir,
                                                   "csl Files (*.csl);;All Files (*)")  # ,
        # options = options)

        if file_name:
            self.display()  # blank line
            self.display('Checking:', file_name, colour='darkgreen')
            self.display()

            head, tail = os.path.split(file_name)
            self.settings.setValue('CslDir', head)
            self.setWindowTitle(TITLE + ' - ' + tail)

            self.pushButtonCheck.setEnabled(False)

            self.checked = self.checkBoxSimilarLocators.isChecked()

            qApp.setOverrideCursor(Qt.WaitCursor)
            qApp.processEvents(QEventLoop.AllEvents)

            self.canClose = False
            self.runSig.emit(file_name, self.checked)

    @pyqtSlot()
    def onThreadFinished(self):

        """Slot triggered when the thread issues signal finishedSig."""

        # reenable the button now thread method is finished
        self.pushButtonCheck.setEnabled(True)

        qApp.restoreOverrideCursor()
        self.canClose = True

        self.debug('Thread Method Finished!')

    def closeEvent(self, event):

        """Override inherited QMainWindow closeEvent.

            Do any cleanup actions before the application closes.

            if self.canClose:
            Saves the application geometry,
            deletes the engine and thread,
            accepts the event which closes the window.
            """

        if not self.canClose:
            event.ignore()
            return

        self.settings.setValue("geometry", self.saveGeometry())

        if self.thread:
            self.thread.terminate()
            del self.thread

        if self.engine:
            del self.engine

        event.accept()

    # --- Methods not normally modified:

    def resizeEvent(self, event):

        """Extends inherited QMainWindow resize event.

            Saves the window geometry."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().resizeEvent(event)

    def moveEvent(self, event):

        """Extends inherited QMainWindow move event.

            Saves the window geometry."""

        self.settings.setValue("geometry", self.saveGeometry())

        super().moveEvent(event)

    @pyqtSlot(str)
    def on_thread_warning_display(self, warnings):

        """Allows the thread to display warnings information as a message box."""

        QMessageBox.warning(self, "File Format Warning!",
                            warnings,
                            QMessageBox.Ok)

    # --- Text Edit display methods, not normally modified:

    @pyqtSlot(str, str)
    def onThreadDisplay(self, display_item, colour):

        """Allows the thread to display information on the text edit."""

        # self.display(display_item, colour = colour)
        self.textEdit.append(display_item)

    @pyqtSlot(str)
    def onThreadDebugDisplay(self, display_item):

        """Allows the thread to display debug information on the text edit."""

        self.debug(display_item)

    def display(self, *items, colour='black'):

        """Display the items on the text edit control using their normal
            string representations on a single line.
            A space is added between the items.
            Any trailing spaces are removed.

            If the colour is not given the default
            colour ('black') is used. The colour, if used, must be given
            as a keyword argument.

            The colour may be be any string that may be
            passed to QColor, such as a name like 'red' or
            a hex value such as '#F0F0F0'.
            """

        display_string = ''
        for item in items:
            display_string += '{} '.format(item)

        tEdit = self.textEdit
        # tx  = tEdit.text()
        # tEdit.append(display_string)
        AppendTextToTextEdit(tEdit, display_string.rstrip(' '), colour)

    def debug(self, *items):

        """Display the items on the text edit control using their normal
            string representations.

            The colour is fixed at orange.

            The display may be disabled once the program has
            been debugged by changing self.showDebug.
            """

        if self.showDebug:
            self.display(*items, colour='orange')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainApp()
    sys.exit(app.exec_())
