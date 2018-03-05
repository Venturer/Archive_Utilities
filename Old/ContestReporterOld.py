#Contest Reporter, part of the Archive Utilities Suite

#Copyright (c) 2009-2011 S. J. Baugh, G4AUC
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
#- Neither the name of S. J. Baugh nor the names of its contributors may be used to
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

#Version
#   2.2.1       First .net 4.0  beta release
#   2.2.2.0     Help shown when program starts
#   2.2.2.1     worked before: changed to worked once on etc
#   2.3.0.0
#           Checks for QSO line with greater than 9 parameters
#           Separate Help Window
#           'All Files' removed from file dialogues
#   2.3.1.0 Dates shown in reversed order, newline on display changed to '\r\n' so text copies to Notepad
#   2.3.1.6 synccontext no longer used
#   2.4.0.6 Release Issue

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

from System.Windows.Controls import *
import sys

from wpfutilities import *


from ArchiveUtilities import *


stream = FileStream('ContestReporter.xaml', FileMode.Open)
window = XamlReader.Load(stream)


## Version
window.Title+=Version


class Main(object):
    def __init__(self, controls):
        """Link up the events and ititialise."""
        for i in controls:

            if isinstance(i, Button):
                if hasattr(self, "on_" + i.Name):
                    i.Click += getattr(self, "on_" + i.Name)
                if i.Name == "buttonReport":
                    self.buttonReport = i

            elif isinstance(i, TextBox):
                if i.Name == "TextBoxOutput":
                    self.TextOutput = i
                    self.TextOutput.Clear()
            elif isinstance(i, CheckBox):
                if i.Name == "checkBoxSimilarLocators":
                    self.CheckBoxSimilarLocators = i

#       #show the help on start up
#
#       self.on_buttonHelp(None, None)
#       self.ScrollDisplayToEnd()

    @UIThread   #This method always runs in the GUI thread
    def AddLine(self,Text=''):
        """"Adds a line of text to the TextBox."""
        self.TextOutput.AppendText(Text+'\r\n')
        self.ScrollDisplayToEnd()

    def AddToDisplay(self, Text=''):
        """"Adds a line of text to the TextBox without scrolling to end."""
        self.TextOutput.AppendText(Text+'\r\n')

    def ScrollDisplayToEnd(self):
        """"Scrolls to end of TextBox."""
        self.TextOutput.ScrollToEnd()

    def ProcessUniques(self, Checked):
        self.AddLine('The following are not in the archive:')

        #iterate over the uniqueList
        for contact in self.uniqueList:
            #Display the contact
            self.AddLine('\n'+'  '+contact[0]+','+contact[1]+','+contact[2])
            #Get any fuzzy matches
            matchesList=FuzzyMatch(contact, Checked, self.archiveDict)
            #Display the fuzzy matches list
            if matchesList!=[]:
                self.AddLine('  Near Matches:')
                for match in matchesList:
                    self.AddLine('  '+match[0]+','+match[1]+','+match[2]+' '+match[4])
                    if match[3]==1:
                        self.AddLine('                worked once on '+match[5])
                    else:
                        self.AddLine('                worked '+str(match[3])+' times on '+match[5])
            report=CheckLocatorIsInCorrectCountry(contact[0], contact[1])
            if report!=None:
                self.AddLine(report)

    def ProcessWorkedBefore(self, Checked):

        self.AddLine('\nThe following already exist in the archive:')

        #iterate over the workedBeforeList
        for contact in self.workedBeforeList:

            #Find timesSeen and dates in archiveDict
            seen=self.archiveDict[contact]

            #Display the contact
            self.AddLine('')
            self.AddLine('  '+contact[0]+','+contact[1]+','+contact[2])
            if seen[0]==1:
                self.AddLine('     worked once on '+seen[1])
            else:
                self.AddLine('     worked '+str(seen[0])+' times on '+seen[1])
            #Get ant fuzzy matches
            matchesList=FuzzyMatch(contact, Checked, self.archiveDict)
            #Display the fuzzy match list
            if matchesList!=[]:
                self.AddLine('  Near Matches:')
                for match in matchesList:
                    self.AddLine('  '+match[0]+','+match[1]+','+match[2]+' '+match[4])
                    if match[3]==1:
                        self.AddLine('                worked once on '+match[5])
                    else:
                        self.AddLine('                worked '+str(match[3])+' times on '+match[5])
            report=CheckLocatorIsInCorrectCountry(contact[0], contact[1])
            if report!=None:
                self.AddLine(report)

    @BGThread #This method runs in a background thread
    def CreateReport(self,TheArchiveFilename,TheEntryFileName,Checked):

        #Initialise Lists and dictionary
        self.entryList=[]
        self.uniqueList=[]
        self.workedBeforeList=[]
        self.archiveDict=dict()

        self.AddLine('Date Format: yyyy/mm/dd')
        self.AddLine()

        ReadEntryFile(TheEntryFileName, self.entryList)

        ReadArchiveFile(TheArchiveFilename, self.archiveDict)

        for contact in self.entryList:
            if contact not in self.archiveDict:
                self.uniqueList.append(contact)
            else:
                self.workedBeforeList.append(contact)

        self.ProcessUniques(Checked)
        self.ProcessWorkedBefore(Checked)

        self.ReenableButtons()

    @UIThread #This runs in the GUI thread, so can be called by the background thread to update the GUI
    def ReenableButtons(self):
        self.buttonReport.IsEnabled=True
        self.AddLine()
        self.AddLine('Report Created.')
        self.AddLine()

    def on_buttonReport(self, b, e):
            """Responds to button clicks."""

            #Create a dialogue to open the csl file
            dialog = OpenFileDialog()
            #Dialogue Options
            dialog.Title = 'Open the Contest Entry (.edi) file to be checked'
            dialog.Filter = 'Entry Files(*.edi)|*.edi;*.EDI'

            #Run the entry open dialogue
            if dialog.ShowDialog() == DialogResult.OK:

                #Get the file name
                self.EntryFileName = dialog.FileName

                #display the filename
                self.AddLine('Report:')
                self.AddLine(self.EntryFileName)

                dialogArchive = OpenFileDialog()
                #Dialogue Options
                dialogArchive.Title = 'Open the Archive file to check against'
                dialogArchive.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

                #Run the entry open dialogue
                if dialogArchive.ShowDialog() == DialogResult.OK:

                    #Get the file name
                    self.ArchiveFileName = dialogArchive.FileName

                    #display the filename
                    self.AddLine('Archive:')
                    self.AddLine(self.ArchiveFileName)

                    #self.TextOutput.Cursor='Wait'
                    try:
                        self.buttonReport.IsEnabled=False
                        self.Checked=self.CheckBoxSimilarLocators.IsChecked

                        #Create the report in a background thread
                        self.CreateReport(self.ArchiveFileName, self.EntryFileName, self.Checked)

                    finally:
                        #wx.EndBusyCursor()
                        pass

                dialogArchive.Dispose() #finished with the dialogue

            dialog.Dispose() #finished with the dialogue


    def on_buttonClose(self, b, e):
        """Responds to Close button clicks."""
        app.Shutdown()


    def on_buttonHelp(self, b, e):
        """Displays a help text on the display."""
        Txt='Contest Reporter Version'+Version+"""

Help for the Contest Reporter

This program is intended to suggest where typographic errors in your log MAY exist (such as typing G9BAC instead of G9ABC).
Remember that there may already be erroneous entries in the archive from earlier mis-typed QSOs.

Click button:
 Create Report on Contest Entry
In the dialogue that opens select a .EDI file produced by Minos that you wish to check
against an archive. Click Open.

Another dialogue will open.
Select an existing .csl archive file. Click Open.

The Entries in the .EDI file will be checked against those already in the existing .csl file.

A report showing each entry in the .edi file and possible matches in the archive will be produced.

Date format: yyyy/mm/dd

Remember people do change QTH from time to time and change callsign,
particularly from Foundation to Intermediate to Full.

Whether a problem exists is entirely up to your judgement.

Right click on the report for an edit menu which will allow you to cut and paste the report
into another document. Click in the Report and tpye <control> A to select all the text.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS &AS IS& AND ANY EXPRESS
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

        #Link up control variables and events automatically with prefix=Help
        LinkUpControls(self,self.HelpWindow,'Help')

        self.Help_TextBoxOutput.Text=Txt

        self.HelpWindow.Show()

    def on_Help_Close_click(self, *args):
        """Close the Help window."""

        self.HelpWindow.Close()

def Walk(tree):
    yield tree
    if hasattr(tree, 'Children'):
        for child in tree.Children:
            for x in Walk(child):
                yield x
    elif hasattr(tree, 'Child'):
        for x in Walk(tree.Child):
            yield x
    elif hasattr(tree, 'Content'):
        for x in Walk(tree.Content):
            yield x
    elif hasattr(tree, 'Text'):
        for x in Walk(tree.Text):
            yield x

def enliven(w):
    try:
        controls = [ n for n in Walk(w) if isinstance(n, Button) or isinstance(n, TextBox) or isinstance(n, CheckBox)]
        Main(controls)
    except:
        print "Function failed. Did you pass in the window?"

enliven(window)
app = Application()
app.Run(window)
