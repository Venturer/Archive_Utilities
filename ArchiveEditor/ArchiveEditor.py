# -*- coding: utf-8 -*-

'''Archive Editor.

    A Qt5 based program template for Python3.

    Edits csl files used by Minos.'''

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

# Archive Editor modules
from Dialogues import EditDialogue, InsertDialogue
from ArchiveUtilities import *

TITLE = 'Archive Editor 3.0'


class MainApp(QMainWindow):

    '''Main Qt5 Window.'''

    # signals emitted by the MainApp
    runSig = pyqtSignal(str, QListWidget)

    edited = False
    fileName = ''

    def __init__(self):

        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        # Load the GUI definition file
        # use 2nd parameter self so that events can be overriden
        self.ui = uic.loadUi('ArchiveEditor.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'ArchiveEditor')

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
    def on_pushButtonOpen_clicked(self, checked):

        """Slot triggered when the button is clicked.

            Opens the .csl file."""
        # get the file name to open
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(self,
                "Open csl file",
                '.',
                "csl Files (*.csl);;All Files (*)",
                options = options)

        self.listWidget.clear()

        if self.fileName:    # fileName is empty if cancelled
            with open(self.fileName, 'r') as f:
                for line in f:
                    self.listWidget.addItem(line.strip())

            self.listWidget.setCurrentRow(0)

            self.pushButtonEdit.setEnabled(True)
            self.pushButtonDelete.setEnabled(True)
            self.pushButtonSave.setEnabled(True)
            self.pushButtonInsert.setEnabled(True)

            head, tail = os.path.split(self.fileName)
            self.setWindowTitle(TITLE + ' - ' + tail)

    @pyqtSlot(bool)
    def on_pushButtonEdit_clicked(self, checked):

        """Slot triggered when the Edit Line button is clicked.

            Edits the selected line in the csl file."""

        # Get the selected list item
        item = self.listWidget.currentItem()

        # simulate double click on item
        self.on_listWidget_itemDoubleClicked(item)

    @pyqtSlot(bool)
    def on_pushButtonDelete_clicked(self, checked):

        """Slot triggered when the Delete button is clicked.

            Deletes the selected line in the csl file."""

        item = self.listWidget.currentItem()
        row =  self.listWidget.currentRow()
        line = item.text()

        # Confirm the deletion
        reply = QMessageBox.question(self, "Delete?",
                'Do you want to delete line: ' + line + '?',
                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.listWidget.takeItem(row)
            self.edited = True

    @pyqtSlot(bool)
    def on_pushButtonInsert_clicked(self, checked):

        """Slot triggered when the Insert button is clicked.

            Inserts after the selected line in the csl file."""

        item = self.listWidget.currentItem()
        row =  self.listWidget.currentRow()

        # Show an Insert dialogue
        insertDialogue = InsertDialogue()
        if insertDialogue.exec_():
            newLine = insertDialogue.getLine()
            self.listWidget.insertItem(row, newLine)
            self.edited = True
        insertDialogue.done(0)

    @pyqtSlot(QListWidgetItem)
    def on_listWidget_itemDoubleClicked(self, item):

        """Slot triggered when the list is double clicked.

            Edits the selected line in the csl file."""

        line_text = item.text()

        # Show an Edit dialogue
        editDialogue = EditDialogue(line_text)
        if editDialogue.exec_():
            editedLine = editDialogue.getLine()
            item.setText(editedLine)
            self.edited = True
        editDialogue.done(0)

    @pyqtSlot()
    def onThreadFinished(self):

        """Slot triggered when the thread issues signal finishedSig."""

        # reenable the buttons now thread method is finished
        self.pushButtonOpen.setEnabled(True)
        self.pushButtonEdit.setEnabled(True)
        self.pushButtonDelete.setEnabled(True)
        self.pushButtonSave.setEnabled(True)
        self.pushButtonInsert.setEnabled(True)

    @pyqtSlot(bool)
    def on_pushButtonSave_clicked(self, checked):

        """Slot triggered when the Insert button is clicked.

            Saves to the csl file."""

        # disable the buttons until the save is finished
        self.pushButtonOpen.setEnabled(False)
        self.pushButtonEdit.setEnabled(False)
        self.pushButtonDelete.setEnabled(False)
        self.pushButtonSave.setEnabled(False)
        self.pushButtonInsert.setEnabled(False)

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                "Save csl file",
                self.fileName,
                "csl Files (*.csl);;All Files (*)",
                options=options)

        if fileName:
            with open(fileName, 'w') as f:
                for i in range(self.listWidget.count()):
                    line = self.listWidget.item(i).text()
                    f.write(line + '\n')
            self.edited = False
            self.fileName = fileName

        head, tail = os.path.split(self.fileName)
        self.setWindowTitle(TITLE + ' - ' + tail)

        # reenable the buttons now the save is finished
        self.pushButtonOpen.setEnabled(True)
        self.pushButtonEdit.setEnabled(True)
        self.pushButtonDelete.setEnabled(True)
        self.pushButtonSave.setEnabled(True)
        self.pushButtonInsert.setEnabled(True)

    def closeEvent(self, event):

        '''Override inherited QMainWindow closeEvent.

            Do any cleanup actions before the application closes.

            Saves the application geometry.
            If not edited accepts the event which closes the application.
            If edited asks whether save.'''

        if self.edited:
            # Confirm the close
            head, tail = os.path.split(self.fileName)
            reply = QMessageBox.question(self, "File Changed",
                    'Do you want to save the file: ' + tail + '?',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Cancel:
                event.ignore()
                return

            if reply == QMessageBox.Yes:
                self.on_pushButtonSave_clicked(False)

        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    # --- Methods not normally modified:

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

