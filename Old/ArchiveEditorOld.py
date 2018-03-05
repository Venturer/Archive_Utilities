#Archive Editor
#
#by S. J. Baugh
#
#
#Archive Editor, part of Archive Utilities Suite
#Copyright (c) 2009,-2012, S J Baugh, G4AUC
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are
#permitted provided that the following conditions are met:
#
#- Redistributions of source code must retain the above copyright notice, this list
#  of conditions and the following disclaimer.
#
#- Redistributions in binary form must reproduce the above copyright notice, this list
#  of conditions and the following disclaimer in the documentation and/or other materials
#  provided with the distribution.
#
#- Neither the name of S J Baugh nor the names of its contributors may be used to
#  endorse or promote products derived from this software without specific prior written
#  permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS &AS IS& AND ANY EXPRESS
#OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
#IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#Version
#   2.4.0.6     First Version. Given this Version number to match rest of suite

Version=' 2.4.0.6'

import clr

clr.AddReferenceByPartialName("PresentationCore")
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName("WindowsBase")
clr.AddReferenceByPartialName("System.Windows.Forms")
clr.AddReferenceByPartialName("IronPython")
clr.AddReferenceByPartialName("Microsoft.Scripting")

from System.IO import FileMode, FileStream
from System.Windows import Application
from System.Windows.Markup import XamlReader
from System.Windows.Forms import DialogResult, SaveFileDialog, OpenFileDialog
from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon

from System.Windows.Controls import *

import sys

from ArchiveUtilities import *

from wpfutilities import *


stream = FileStream('ArchiveEditor.xaml', FileMode.Open)
window = XamlReader.Load(stream)
window.Title='Archive Editor'

#Version
window.Title+=Version

class Main:

    OpenFileName=''
    Selecting = False
    LineIndex=-1
    DatesList=[]

    def __init__(self, MainWindow):
        """Initialise (construct) the object."""

        self.MainWindow=MainWindow

        #Link up control variables and clicked/changed events automatically, no prefix
        LinkUpControls(self,MainWindow)
        self.TextOutput.SelectionChanged += getattr(self, "on_SelectionChanged")


    def SelectLine(self, LineIndex):
        """Select the line at LineIndex in the TextDisplay"""

        FirstChar = self.TextOutput.GetCharacterIndexFromLineIndex(LineIndex)
        LineLength = self.TextOutput.GetLineLength(LineIndex)
        self.TextOutput.Select(FirstChar, LineLength)

    def UnQuote(s):
        """Removes quotes from around string s (if present)."""

        return s.strip('"').rstrip('"')

    def ParseLine(self, Line):
        """Parses the line.

            Returns the callsign, locator and exchange as strings,
            timesSeen as an integer and the dates as a list of strings."""

        #initialise to default values
        callsign=''
        locator=''
        exchange=''
        timesSeen=1
        dates=''

        #Remove trailing whitespace and
        #create a list of the comma separated variables in the line
        parameters=Line.rstrip().split(',')

        #how many parameters are there?
        noOfParameters=len(parameters)

        #get the parameters, if present
        if noOfParameters>=1:
            callsign=UnQuote(parameters[0])

        if noOfParameters>=2:
            locator=UnQuote(parameters[1])

        if noOfParameters>=3:
            exchange=UnQuote(parameters[2])

        if noOfParameters>=4:
            timesSeen=eval(parameters[3])

        if noOfParameters>=5:
            dates=UnQuote(parameters[4])

        DatesList=dates.split(';')[:-1]  #split into dates separated by ';' and remove a blank entry at end of list

        return callsign, locator, exchange, timesSeen, DatesList

    def on_SelectionChanged(self, b, e):
        """SelectionChanged event handler.

            Occurs when caret position is changed."""

        if not self.Selecting: #Prevent SelectLine causing reentrancy as SelectLine method also creates a SelectionChanged event
            self.Selecting=True
            self.LineIndex = self.TextOutput.GetLineIndexFromCharacterIndex(self.TextOutput.CaretIndex)
            self.SelectLine(self.LineIndex)
        else:
            self.Selecting=False

    def on_buttonOpen_click(self, b, e):
        """Respond to the Open button click event."""

        dialog = OpenFileDialog()
        dialog.Title = 'Open the Archive to be edited'
        dialog.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

        if dialog.ShowDialog() == DialogResult.OK:

            #Open the file
            self.OpenFileName = dialog.FileName
            fs = open(self.OpenFileName,'r')

            #read file into TextOutput
            for line in fs:
                self.TextOutput.AppendText(line)

            fs.close()

            #set up the text box insert point
            self.TextOutput.ScrollToHome()
            self.TextOutput.CaretIndex = 0
            self.TextOutput.Focus()

        dialog.Dispose() #finished with the dialogue

    def on_buttonEdit_click(self, b, e):
        """Respond to the Edit button click event."""

        if self.LineIndex!=-1:

            #Create a dialogue
            stream = FileStream('EditLine.xaml', FileMode.Open)
            self.EditLineDialogue = XamlReader.Load(stream)

            #Link up control variables and events automatically with prefix=EditLineDialogue
            LinkUpControls(self,self.EditLineDialogue,prefix='EditLineDialogue')

            #set the initial dialogue entries
            self.EditLineDialogue_Callsign.Text, self.EditLineDialogue_Locator.Text,self.EditLineDialogue_Location.Text, timesSeen, self.DatesList = self.ParseLine(self.TextOutput.SelectedText)
            self.EditLineDialogue_TimesSeen.Text=str(timesSeen)
            #fill combo box
            for date in self.DatesList:
                self.EditLineDialogue_Dates.AddText(date)
            self.EditLineDialogue_Dates.SelectedIndex=0

            #show the dialogue
            self.EditLineDialogue.ShowDialog()

            if self.EditLineDialogue.DialogResult==True: #If not cancelled
                pass

    def on_EditLineDialogue_okButton_click(self,*args):
        """Respond to EditLineDialogue OK button and validate."""

        self.EditLineDialogue.Close()

    def on_EditLineDialogue_DeleteDate_click(self,*args):
        """Respond to EditLineDialogue Delete Date button and validate."""

        #Check there is at least one date to delete
        NoOfDates= self.EditLineDialogue_Dates.Items.Count

        if NoOfDates>0:
            #Get the selected date from the combo box
            date=self.EditLineDialogue_Dates.SelectedItem

            #Confirm Deletetion
            result = MessageBox.Show('Delete this date: '+date+' ?', 'Delete Date', MessageBoxButtons.YesNo, MessageBoxIcon.Question)

            #If the Yes button was pressed ...
            if (result == DialogResult.Yes):

                #Remove the date from the list in the combo box
                self.EditLineDialogue_Dates.Items.Remove(date)
                self.EditLineDialogue_Dates.SelectedIndex=0

                #Update the Times Seen
                timesSeen=eval(self.EditLineDialogue_TimesSeen.Text)
                self.EditLineDialogue_TimesSeen.Text=str(timesSeen-1)

    def on_EditLineDialogue_EditDate_click(self,*args):
        """Respond to EditLineDialogue Edit Date button and validate."""

        #Check there is at least one date to edit
        NoOfDates= self.EditLineDialogue_Dates.Items.Count

        if NoOfDates>0:
            #Get the selected date from the combo box
            date=self.EditLineDialogue_Dates.SelectedItem

            #Create a dialogue
            stream = FileStream('AskText.xaml', FileMode.Open)
            self.AskTextDialogue = XamlReader.Load(stream)

            #Link up control variables and events automatically with prefix=AskTextDialogue
            LinkUpControls(self,self.AskTextDialogue,prefix='AskTextDialogue')

            #set the initial dialogue entries
            self.AskTextDialogue_InputLabel.Content='Edit Date:'
            self.AskTextDialogue_InputText.Text=date

            #show the dialogue
            self.AskTextDialogue.ShowDialog()

            #If the Ok button was pressed ...
            if self.AskTextDialogue.DialogResult==True :

                #Get the text
                newDate=self.AskTextDialogue_InputText.Text

                #Remove the date from the list in the combo box
                self.EditLineDialogue_Dates.Items.Remove(date)
                self.EditLineDialogue_Dates.SelectedIndex=0

                #create a new dates list from the unmodified dates
                #and delete all the current combo box entries as we go
                newDatesList=[]
                for i in range(NoOfDates-1):
                    #get the date that is at top of the list (index 0) for this iteration
                    theDate=self.EditLineDialogue_Dates.SelectedItem
                    newDatesList.append(theDate)
                    self.EditLineDialogue_Dates.Items.Remove(theDate)
                    self.EditLineDialogue_Dates.SelectedIndex=0 #index 0 is now a different item

                #add the modified date
                newDatesList.append(newDate)
                newDatesList.sort(reverse=True) #reverse sort it

                #put the modified, sorted list back into the combo box
                for d in newDatesList:
                    self.EditLineDialogue_Dates.AddText(d)

                #ensure top item is selected
                self.EditLineDialogue_Dates.SelectedIndex=0

    def on_EditLineDialogue_InsertDate_click(self,*args):
        """Respond to EditLineDialogue Insert Date button and validate."""

        #Create a dialogue
        stream = FileStream('AskText.xaml', FileMode.Open)
        self.AskTextDialogue = XamlReader.Load(stream)

        #Link up control variables and events automatically with prefix=AskTextDialogue
        LinkUpControls(self,self.AskTextDialogue,prefix='AskTextDialogue')

        #set the initial dialogue entries
        self.AskTextDialogue_InputLabel.Content='Date To Insert (yyyy/mm/dd) :'
        self.AskTextDialogue_InputText.Text=''

        #show the dialogue
        self.AskTextDialogue.ShowDialog()

        #If the Ok button was pressed ...
        if self.AskTextDialogue.DialogResult==True :
            NoOfDates= self.EditLineDialogue_Dates.Items.Count

            #Get the text
            newDate=self.AskTextDialogue_InputText.Text

            self.EditLineDialogue_Dates.SelectedIndex=0

            #create a new dates list from the current dates
            #and delete all the current combo box entries as we go
            newDatesList=[]
            if NoOfDates>0:
                for i in range(NoOfDates):
                    #get the date that is at top of the list (index 0) for this iteration
                    theDate=self.EditLineDialogue_Dates.SelectedItem
                    newDatesList.append(theDate)
                    self.EditLineDialogue_Dates.Items.Remove(theDate)
                    self.EditLineDialogue_Dates.SelectedIndex=0 #index 0 is now a different item

            #add the modified date
            newDatesList.append(newDate)
            newDatesList.sort(reverse=True) #reverse sort it

            #put the modified, sorted list back into the combo box
            for d in newDatesList:
                self.EditLineDialogue_Dates.AddText(d)

            #ensure top item is selected
            self.EditLineDialogue_Dates.SelectedIndex=0

            #Update the Times Seen
            timesSeen=eval(self.EditLineDialogue_TimesSeen.Text)
            self.EditLineDialogue_TimesSeen.Text=str(timesSeen+1)

    def on_AskTextDialogue_okButton_click(self,*args):
        """Respond to AskTextDialogue OK button and validate."""
        self.AskTextDialogue.DialogResult=True
        self.AskTextDialogue.Close()


    def on_buttonSave_click(self, b, e):
        """"Saves the edited file."""

        #Create a dialogue to open the csl file
        dialog = SaveFileDialog()
        #Dialogue Options
        dialog.Title = 'Save the edited file'
        dialog.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'
        #Set the file name
        dialog.FileName=self.OpenFileName

        #Run the csl save dialogue
        if dialog.ShowDialog() == DialogResult.OK:

            pass

        dialog.Dispose() #finished with the dialogue

    def on_buttonClose_click(self, b, e):
        """Closes the appication."""
        app.Shutdown()

    def on_buttonHelp_click(self, b, e):
        """Display help."""
        Txt='Archive Editor Version'+Version+"""




THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

73s and good contesting,
Steve, G4AUC"""

        #Create a Window
        stream = FileStream('Help.xaml', FileMode.Open)
        self.HelpWindow = XamlReader.Load(stream)

        #Link up control variables and events automatically with prefix=Help_ ...
        LinkUpControls(self,self.HelpWindow,prefix='Help')

        self.Help_TextBoxOutput.Text=Txt

        self.HelpWindow.Show()


    def on_Help_Close_click(self, *args):
        """Close the Help window."""

        self.HelpWindow.Close()
        self.TextOutput.Focus()

#Start the application
Main(window)
app = Application()
app.Run(window)

