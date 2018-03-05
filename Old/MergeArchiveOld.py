#MergeArchive, part of the Archive Utilities Suite

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
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY EXPRESS
#OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
#IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#Version
#   2.2.1       First .net 4.0  beta release
#   2.2.1.1     Changes to Close button caption and help text
#   2.2.2.0     Help shown when program starts
#   2.3.0.0
#           Separate Help Window
#           'All Files' removed from file dialogues
#   2.3.1.0 Dates shown in reversed order, newline on display changed to '\r\n' so text copies to Notepad
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


stream = FileStream('MergeArchive.xaml', FileMode.Open)
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
                if i.Name == "buttonMerge":
                    self.buttonMerge = i

            elif isinstance(i, TextBox):
                if i.Name == "TextBoxOutput":
                    self.TextOutput = i
                    self.TextOutput.Clear()

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

    @UIThread #This runs in the GUI thread, so can be called by the background thread to update the GUI
    def ReenableButtons(self):
        self.buttonMerge.IsEnabled=True
        self.AddLine()
        self.AddLine('Archives Merged.')
        self.AddLine()

    @BGThread #This method runs in a background thread
    def Merge(self,ArchiveFirstFileName,ArchiveSecondFileName):

        #Initialise Lists and dictionary

        self.archiveFirstDict=dict()
        self.archiveSecondDict=dict()

        self.AddLine('Contacts added to Archive')
        self.AddLine()

        ReadArchiveFile(ArchiveFirstFileName, self.archiveFirstDict)

        ReadArchiveFile(ArchiveSecondFileName, self.archiveSecondDict)

        for contact in self.archiveFirstDict:
            if contact not in self.archiveSecondDict:
                self.archiveSecondDict[contact]=self.archiveFirstDict[contact]
                self.AddLine(contact[0]+','+contact[1]+','+contact[2])
            else:
                self.archiveSecondDict[contact][0]+=self.archiveFirstDict[contact][0]
                self.archiveSecondDict[contact][1]+=self.archiveFirstDict[contact][1]

        ReWriteCSL(ArchiveSecondFileName, self.archiveSecondDict)

        self.ReenableButtons()

    def on_buttonMerge(self, b, e):
            """Responds to button clicks."""

            #Create a dialogue to open the csl file
            dialog = OpenFileDialog()
            #Dialogue Options
            dialog.Title = 'Choose Archive file to merge'
            dialog.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

            #Run the entry open dialogue
            if dialog.ShowDialog() == DialogResult.OK:

                #Get the file name
                self.ArchiveFirstFileName = dialog.FileName

                #display the filename
                self.AddLine('Archive:')
                self.AddLine(self.ArchiveFirstFileName)

                dialogArchive = OpenFileDialog()
                #Dialogue Options
                dialogArchive.Title = 'Choose an Archive to merge contacts into'
                dialogArchive.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

                #Run the entry open dialogue
                if dialogArchive.ShowDialog() == DialogResult.OK:

                    #Get the file name
                    self.ArchiveSecondFileName = dialogArchive.FileName

                    #display the filename
                    self.AddLine('Merging into Archive:')
                    self.AddLine(self.ArchiveSecondFileName)

                    #self.TextOutput.Cursor='Wait'
                    try:
                        self.buttonMerge.IsEnabled=False

                        #Merge the archives in a background thread
                        self.Merge(self.ArchiveFirstFileName, self.ArchiveSecondFileName)

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
        Txt='Merge Archives Version'+Version+"""

Click:
 Merge .csl list archives

In the dialogue that opens, select a .csl archive to merge the information FROM
Click OK.

Another dialogue will open.
Select an existing .csl archive file to merge the information INTO.
The Entries in the first archive will be merged with those
already in this .csl file.

Quotation marks will be placed around text fields in the .csl file, some spreadsheets/databases require this.

Times Worked is shown in the "Comments" field in Minos.

Right click on the report for an edit menu which will allow you to cut and paste the report
into another document

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS' AND ANY EXPRESS
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
        controls = [ n for n in Walk(w) if isinstance(n, Button) or isinstance(n, TextBox)]
        Main(controls)
    except:
        print "Function failed. Did you pass in the window?"

enliven(window)
app = Application()
app.Run(window)
