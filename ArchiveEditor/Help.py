# -*- coding: utf-8 -*-

'''Archive Utilities 3 Help Viewer.

    A Qt5 based program for Python3.

    Help for mamaging csl files used by Minos.'''

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

import mdconverter


TITLE = 'Help'

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


#class MainApp(QMainWindow):
class MainApp(QWidget):

    '''Main Qt5 Window.'''

    edited = False
    fileName = ''
    header = ''

    def __init__(self):

        """MainApp Constructor."""

        # call inherited init
        super().__init__()

        # Load the GUI definition file
        # use 2nd parameter self so that events can be overriden
        self.ui = uic.loadUi('HelpForm.ui', self)

        # Create an object to save and restore settings
        self.settings = QSettings('G4AUC', 'Help')

        # Restore window position etc. from saved settings
        try:
            self.restoreGeometry(self.settings.value('geometry'))
        except:
            # exception thrown when there are no saved settings yet
            pass # starts with geometry from ui file

        # Show the Application
        self.show()

        self.setWindowTitle(TITLE)

    def setMarkdownText(self, text):

        """Creates a ToHtml object from module mdconverter.

            Converts Markdown in text to HTML. Sets this
            text to the textEdit."""

        md = mdconverter.ToHtml(self.header)

        html = md.convert(text)

        self.textEdit.setHtml(html)

    def setHtmlText(self, html):

        """Set raw HTML text to the textEdit."""

        self.textEdit.setHtml(html)

    def addToMarkdownHeader(self, header):

        """Adds the text in header to the HTML header."""

        self.header += header

    def setStyles(self, **kwargs):

        """Adds the styles in kwargs to a <style>
            block in the HTML header.

            e.g.:
            self.setStyles(h1='color:red', h2='color:blue; text-decoration:underline;',
                li='font-size:large; color:Firebrick', body='background:oldlace')

            """

        style = '''
        <style type="text/css">\n'''

        for tag in kwargs.keys():

            tagStyles = kwargs[tag].rstrip()
            if not tagStyles.endswith(';'):
                tagStyles += ';'
            style += tag + ' {' + tagStyles + '\n}\n'

        style += '</style>'
        style = style.lstrip()

        self.addToMarkdownHeader(style)

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


