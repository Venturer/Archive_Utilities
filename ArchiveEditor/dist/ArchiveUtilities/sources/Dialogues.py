
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

# Version 1.0, October 2017
# Version 1.1, November 2017 - Fixed InsertDialogue bug

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.uic as uic

from Utilities import *


class EditDialogue(QDialog):

    """Edit Dialogue."""

    def __init__(self, lineIn):

        """Constructor for the dialogue."""

        # call inherited init
        super(EditDialogue, self).__init__()

        # Load the GUI definition file
        # use 2nd argument self so that events can be overriden
        self.ui = uic.loadUi('EditDialogue.ui', self)

        lineElements = lineIn.split(',')

        if len(lineElements) < 5:
            return

        self.lineEditCallsign.setText(un_quote(lineElements[0]))
        self.lineEditLocator.setText(un_quote(lineElements[1]))
        self.lineEditExchange.setText(un_quote(lineElements[2]))

        self.comboBoxWorked.clear()
        dates =  un_quote(lineElements[4]).split(';')
        self.comboBoxWorked.insertItems(-1, dates)
        count = self.comboBoxWorked.count()
        self.comboBoxWorked.removeItem(count - 1)

    @pyqtSlot()
    def on_pushButtonEditWorked_clicked(self):

        """Edit the current date in the comboBox
            using the DateDialogue."""

        currentIndex = self.comboBoxWorked.currentIndex()
        currentDate = self.comboBoxWorked.currentText()

        # Show a DateDialogue
        dateDialogue = DateDialogue(currentDate)
        if dateDialogue.exec_():
            date = dateDialogue.getDate()
            # update the combobox with the edited date
            self.comboBoxWorked.setItemText(currentIndex, date)
        dateDialogue.done(0)

    @pyqtSlot()
    def on_pushButtonInsertWorked_clicked(self):

        """Insert a date in the comboBox
            using the DateDialogue."""

        currentIndex = self.comboBoxWorked.currentIndex()

        # Show a DateDialogue
        dateDialogue = DateDialogue('2017/01/01')
        if dateDialogue.exec_():
            date = dateDialogue.getDate()

            # update the combobox with the edited date
            self.comboBoxWorked.insertItem(currentIndex, date)

            # enable the buttons if necessary
            self.pushButtonEditWorked.setEnabled(True)
            self.pushButtonDeleteWorked.setEnabled(True)
        dateDialogue.done(0)

    @pyqtSlot()
    def on_pushButtonDeleteWorked_clicked(self):

        """Delete a date in the comboBox."""

        currentIndex = self.comboBoxWorked.currentIndex()
        currentDate = self.comboBoxWorked.currentText()

        if self.comboBoxWorked.count() <= 1:
             QMessageBox.critical(self, "Cannot Delete!",
                'Cannot delete: ' + currentDate + '. There must be at least one date!',
                QMessageBox.Ok)
        else:
            # Confirm the deletion
            reply = QMessageBox.question(self, "Delete?",
                    'Do you want to delete date: ' + currentDate + '?',
                    QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # update the combobox by deleting the date
                self.comboBoxWorked.removeItem(currentIndex)

    @pyqtSlot()
    def accept(self):

        '''Override inherited QDialog accept method.

            Accepts the event which closes the dialogue
            if the validation succeeds, gives error messages
            and stays open if the validation fails.
            '''
        canClose = True

        if self.lineEditCallsign.text() == '':
            canClose = False
            QMessageBox.critical(self, "Validation Error!",
                'Cannot close: ' + 'Callsign cannot be blank!',
                QMessageBox.Ok)

        if self.lineEditLocator.text() == '':
            canClose = False
            QMessageBox.critical(self, "Validation Error!",
                'Cannot close: ' + 'Locator cannot be blank!',
                QMessageBox.Ok)

        exchange = self.lineEditExchange.text() # Can be blank

        timesWorked = self.comboBoxWorked.count()
        if timesWorked == 0:
            canClose = False
            QMessageBox.critical(self, "Validation Error!",
                'Cannot close: ' + 'There must be at least one date!',
                QMessageBox.Ok)

        if canClose:
            super(EditDialogue, self).accept()

    def getLine(self):

        """Return the new entry line."""

        callsign = self.lineEditCallsign.text().upper()
        locator = self.lineEditLocator.text().upper()
        exchange = self.lineEditExchange.text()
        timesWorked = self.comboBoxWorked.count()
        dates = ''
        for i in range(timesWorked):
            dates += '{:s};'.format(self.comboBoxWorked.itemText(i))

        dates = sort_dates(dates)

        editedLine = '"{:s}","{:s}","{:s}",{:d},"{:s}"'.format(callsign,
                                                               locator,
                                                               exchange,
                                                               timesWorked,
                                                               dates)
        return editedLine


class InsertDialogue(EditDialogue):

    """Insert Dialogue.

        Inherited from the EditDialog with window title
        changed and the EditWorked and DeleteWorked
        buttons initially disabled."""

    def __init__(self):

        # call inherited init
        super(InsertDialogue, self).__init__('')

        self.setWindowTitle('Insert Line')

        self.pushButtonEditWorked.setEnabled(False)
        self.pushButtonDeleteWorked.setEnabled(False)


class DateDialogue(QDialog):

    """Date Dialogue."""

    def __init__(self, date):

        """Constructor for the dialogue.

            date -- date to edit as YYYY/MM/DD -> str
            """

        # call inherited init
        super(DateDialogue, self).__init__()

        # Load the GUI definition file
        # use 2nd argument self so that events can be overriden
        self.ui = uic.loadUi('DateDialogue.ui', self)

        # set the initial date values
        dateSplit = date.split('/')
        self.spinBoxYear.setValue(int(dateSplit[0]))
        self.spinBoxMonth.setValue(int(dateSplit[1]))
        self.spinBoxDay.setValue(int(dateSplit[2]))

    def getDate(self):

        """Return the new entry line.

            returns: date -- edited date as YYYY/MM/DD -> str
            """
        year = self.spinBoxYear.value()
        month = self.spinBoxMonth.value()
        day = self.spinBoxDay.value()

        date = '{:d}/{:02d}/{:02d}'.format(year, month, day)

        return date
