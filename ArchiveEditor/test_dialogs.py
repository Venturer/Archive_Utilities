import unittest
import sys

# PyQt interface imports, Qt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtTest import QTest
import PyQt5.uic as uic

import Dialogues

app = QApplication(sys.argv)

class DateDialogueTestCase(unittest.TestCase):

    def setUp(self):
        """Create the dialog"""

        self.form = Dialogues.DateDialogue('2018/01/20')


    def test_initial_date(self):
        """Test that the initial value is returned by getDate."""

        new_date = self.form.getDate()

        self.assertEqual(new_date, '2018/01/20')

    def test_year_date(self):

        self.form.ui.spinBoxYear.setValue(2017)

        # Push OK with the left mouse button
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        new_date = self.form.getDate()

        self.assertEqual(new_date, '2017/01/20')

    def test_month_date(self):

        self.form.ui.spinBoxMonth.setValue(2)

        # Push OK with the left mouse button
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        new_date = self.form.getDate()

        self.assertEqual(new_date, '2018/02/20')

    def test_day_date(self):

        self.form.ui.spinBoxDay.setValue(21)

        # Push OK with the left mouse button
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        new_date = self.form.getDate()

        self.assertEqual(new_date, '2018/01/21')

    def test_day_date_incorrect_32(self):

        self.form.ui.spinBoxDay.setValue(32)

        # Push OK with the left mouse button
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        new_date = self.form.getDate()

        self.assertEqual(new_date, '2018/01/31') # changed to top value

    def test_day_date_incorrect_0(self):

        self.form.ui.spinBoxDay.setValue(0)

        # Push OK with the left mouse button
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        new_date = self.form.getDate()

        self.assertEqual(new_date, '2018/01/01') # changed to bottom value


class EditDialogueTestCase(unittest.TestCase):

    def setUp(self):
        """Create the dialog."""

        self.form = Dialogues.EditDialogue('"G4AUC","IO91OJ","RG",1,"2018/01/20;"')

    def test_initial_line(self):
        """Test that the initial value is returned by getLine."""

        # Push OK with the left mouse button
        okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        new = self.form.getLine()

        self.assertEqual(new, '"G4AUC","IO91OJ","RG",1,"2018/01/20;"')


if __name__ == '__main__':
    unittest.main(verbosity=2)
