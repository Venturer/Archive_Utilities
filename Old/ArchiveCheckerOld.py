#Archive Cheker, part of the Archive Utilities Suite

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
#   2.2.2.1     Help changed
#               Report is in callsign order
#   2.3.0.0
#           Separate Help Window
#           'All Files' removed from file dialogues
#   2.3.1.0 Dates shown in reversed order, newline on display changed to '\r\n' so text copies to Notepad
#   2.3.1.6 No longer uses synccontext
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

from wpfutilities import *

import sys

from ArchiveUtilities import *

stream = FileStream('ArchiveChecker.xaml', FileMode.Open)
window = XamlReader.Load(stream)
window.Title='Archive Checker'

#Version
window.Title+=Version

class Main(object):
    def __init__(self, controls):
        """Link up the events and ititialise."""
        for i in controls:
            if isinstance(i, Button):
                if hasattr(self, "on_" + i.Name):
                    i.Click += getattr(self, "on_" + i.Name)
                if i.Name == "buttonCheck":
                    self.buttonCheck = i

            elif isinstance(i, TextBox):
                if i.Name == "TextBoxOutput":
                    self.TextOutput = i
                    self.TextOutput.Clear()
            elif isinstance(i, CheckBox):
                if i.Name == "checkBoxSimilarLocators":
                    self.CheckBoxSimilarLocators = i



    @UIThread   #This method always runs in the GUI thread
    def AddLine(self,txt):
        """"Adds a line of text to the TextBox."""
        self.TextOutput.AppendText(txt+'\r\n')
        self.ScrollDisplayToEnd()

    def ScrollDisplayToEnd(self):
        """"Scrolls to end of TextBox."""
        self.TextOutput.ScrollToEnd()


    @BGThread #This method runs in a background thread
    def CreateReport(self,TheArchiveFilename,Checked):

        #Initialise Lists
        self.archiveDict=dict()
        self.entryList=[]

        ReadArchiveFile(TheArchiveFilename, self.archiveDict)

        Keys=self.archiveDict.keys()

        Keys.sort()

        #iterate over the archiveList
        for contact in Keys:

            timesSeen,dates=self.archiveDict[contact]

            #Display the contact
            self.AddLine('\n'+'  '+contact[0]+','+contact[1]+','+contact[2])
            if timesSeen==1:
                self.AddLine('   worked once on '+dates)
            else:
                self.AddLine('   worked '+str(timesSeen)+' times on '+dates)
            #Get ant fuzzy matches
            matchesList=FuzzyMatch(contact,Checked,self.archiveDict)
            #Display the fuzzy match list
            if matchesList!=[]:
                self.AddLine('    Near Matches:')
                for match in matchesList:
                    pass
                    self.AddLine('    '+match[0]+','+match[1]+','+match[2]+' '+match[4])
                    if match[3]==1:
                        self.AddLine('     worked once on '+match[5])
                    else:
                        self.AddLine('     worked '+str(match[3])+' times on '+match[5])
            report=CheckLocatorIsInCorrectCountry(contact[0], contact[1])
            if report!=None:
                self.AddLine(report)

        self.ReenableButtons()

    @UIThread #This runs in the GUI thread, so can be called by the background thread to update the GUI
    def ReenableButtons(self):
        self.buttonCheck.IsEnabled=True


    def on_buttonCheck(self, b, e):

            #Create a dialogue to open the csl file
            dialog = OpenFileDialog()
            #Dialogue Options
            dialog.Title = 'Open the Archive to be checked'
            dialog.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

            #Run the csl open dialogue
            if dialog.ShowDialog() == DialogResult.OK:

                #Get the file name
                self.ArchiveFileName = dialog.FileName

                #display the filename
                self.AddLine('Archive:')
                self.AddLine(self.ArchiveFileName)

                #self.TextOutput.Cursor='Wait'
                try:
                    self.buttonCheck.IsEnabled=False
                    self.Checked=self.CheckBoxSimilarLocators.IsChecked
                    self.CreateReport(self.ArchiveFileName,self.Checked)

                finally:
                    #wx.EndBusyCursor()
                    pass


            dialog.Dispose() #finished with the dialogue


    def on_buttonClose(self, b, e):
        app.Shutdown()

    def on_buttonHelp(self, b, e):
        Txt='Archive Checker Version'+Version+"""

Help for Archive Checker:

Click button:

Check an Archive for possible erroneous entries

A dialogue will open.
Select an existing .csl archive file.

The Entries in the archive will be checked
against all other entries in the .csl file.

A report showing each entry
and possible matches in the archive will be
produced.

Look at the report to see if there are any questionable entries
in the archive that need to be checked.

Remember people do change QTH and change callsign,
particularly from Foundation to Intermediate to Full.

Date format is: yyyy/mm/dd

Right click on the report for an edit menu
which will allow you to cut and paste the report
into another document.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS &AS IS& AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

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
