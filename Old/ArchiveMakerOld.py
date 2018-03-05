#Archive Maker
#
#by S. J. Baugh
#
#
#Archive Maker, part of Archive Utilities Suite
#Copyright (c) 2009,-2011, S J Baugh, G4AUC
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
#   2.2.1   First .net 4.0  beta release
#   2.2.2.0 Create archive is now followed by add .edi file(s) dialogue
#           Fixed crash if .edi file does not contain [QSORecords
#   2.3.0.0
#           Checks for QSO line with greater than 9 parameters
#           Separate Help Window
#           'All Files' removed from file dialogues
#   2.3.1.0 Dates shown in reversed order, newline on display changed to '\r\n' so text copies to Notepad
#   2.3.1.5 synccontext no longer used
#   2.4.0.6 Does not add a contact if a contact with the same details and date already exists in the archive

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

from ArchiveUtilities import *

from wpfutilities import *


stream = FileStream('ArchiveMaker.xaml', FileMode.Open)
window = XamlReader.Load(stream)
window.Title='Archive Maker'

#Version
window.Title+=Version

class Main:
    def __init__(self, controls):
        """Link up the events and ititialise."""
        for i in controls:
            if isinstance(i, Button):
                if hasattr(self, "on_" + i.Name):
                    i.Click += getattr(self, "on_" + i.Name)
            elif isinstance(i, TextBox):
                if i.Name == "TextBoxOutput":
                    self.TextOutput = i
                    self.TextOutput.Clear()

    @UIThread   #This method always runs in the GUI thread
    def AddLine(self,txt):
        """"Adds a line of text to the Text Box."""
        self.TextOutput.AppendText(txt+'\r\n')
        self.ScrollDisplayToEnd()

    def ScrollDisplayToEnd(self):
        """"Scrolls to end of Text Box."""
        self.TextOutput.ScrollToEnd()

    def AddNewContacts(self, FileName, archiveDict):
        """Parses the .edi file and adds the contact details to the list."""

        #initialise
        gettingData=False

        #Open the input file
        f = open(FileName,'r')

        try:
            for line in f:      #iterate through all the lines in file 'f'

                if gettingData:

                    #parameters in 'line' are separated by ';'
                    #split the line and create a list of the parameters
                    parameters=line.split(';')

                    if len(parameters)>=10:     #check line contains 10 or more parameters

                        #create a tuple (callsign,locator,exchange)
                        contact=(parameters[2],parameters[9],parameters[8])
                        date=FormatDate(parameters[0])

                        if contact not in archiveDict:
                            if contact[0]!='': #ignore blank callsign entries
                                #append the parameters to the list and text display
                                timesSeen=1
                                archiveDict[contact]=[timesSeen,date+';']
                                self.AddLine(contact[0]+','+contact[1]+','+contact[2]+' on '+ date)
                        else:
                            if date not in archiveDict[contact][1]: #don't repeatedly add the same contact on rthe same date
                                #increment times seen
                                archiveDict[contact][0]+=1

                                #add date to contact
                                archiveDict[contact][1]+=date+';'


                elif '[QSORecords' in line:
                    #skip until the line contains [QSORecords
                    gettingData=True
        finally:
            if not gettingData:
                archiveDict[('','','')]=[0,';'] #Create dummy entry if file does not contain [QSORecords

            #close file at end of input
            f.close()


    @BGThread #This method runs in a background thread
    def ProcessAllEdiFiles(self, EdiFileNames, cslFile):
        """Process one or more files whos file names are in 'EdiFileNames' """
        for EdiFile in EdiFileNames:
            self.AddLine(EdiFile+':')
            self.AddLine('Contacts not already in Archive:')
            self.AddNewContacts(EdiFile, self.archiveDict)

        #Re-write the processed archive
        ReWriteCSL(cslFile,self.archiveDict)

    def AddEdiFiles(self, cslFile):
        """Shows the Open Edi file(s) dialogue, reads the existing archive and calls ProccessAllEdiFiles"""

        #Create a dialogue to open the edi file(s)
        dialogEdi = OpenFileDialog()
        #Dialogue Options
        dialogEdi.Title = 'Open a .edi file (or files)'
        dialogEdi.Filter = 'EDI Files(*.edi)|*.edi;*.EDI'
        dialogEdi.Multiselect=True

        #Run the edi open dialogue
        if dialogEdi.ShowDialog() == DialogResult.OK:
            #the file names selected are returned as a list of strings
            EdiFileNames = dialogEdi.FileNames
            #display the file names
            self.AddLine('Edi File(s):')
            for f in EdiFileNames:
                self.AddLine(f)
            self.AddLine('Opened.')

            #initialise the dictionary
            self.archiveDict=dict()

            ReadArchiveFile(cslFile, self.archiveDict)

            self.ProcessAllEdiFiles(EdiFileNames, cslFile)


        dialogEdi.Dispose() #finished with the dialogue

    def on_buttonCreate(self, b, e):
        """Creates a blank archive then calls AddEdiFiles"""

        dialog = SaveFileDialog()
        dialog.Title = 'Save New Archive As'
        dialog.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

        if dialog.ShowDialog() == DialogResult.OK:
            CreateFileName = dialog.FileName
            fs = open(CreateFileName,'wb')
            fs.write('\r\n')
            fs.close()
            self.AddLine(CreateFileName)
            self.AddLine('Created.')

            self.AddEdiFiles(CreateFileName)

    def on_buttonAdd(self, b, e):
        """"Adds Edi file(s) to an existing archive"""

        if True: #keep indentaion
            #Create a dialogue to open the csl file
            dialog = OpenFileDialog()
            #Dialogue Options
            dialog.Title = 'Open an existing Archive to add .edi files to'
            dialog.Filter = 'Archive Files(*.csl)|*.csl;*.CSL'

            #Run the csl open dialogue
            if dialog.ShowDialog() == DialogResult.OK:

                #Get the file name
                ArchiveFileName = dialog.FileName
                #display the filename
                self.AddLine('Archive:')
                self.AddLine(ArchiveFileName)
                self.AddLine('Opened.')

                self.AddEdiFiles(ArchiveFileName)

            dialog.Dispose() #finished with the dialogue

    def on_buttonClose(self, b, e):
        """Closes the appication."""
        app.Shutdown()

    def on_buttonHelp(self, b, e):
        """Display help for Archive Maker."""
        Txt='Archive Maker Version'+Version+"""

To CREATE or UPDATE an Archive:

To Create a NEW ARCHIVE click button:
  Create A  New Archive (.csl file) and add .edi file(s) to it
Enter the new Archive file name, click Save.
In the the next dialogue that opens select a .EDI file (or multiselect two or more .edi files) produced by Minos. Click Open.
The Archive will be created and will be given a .csl extension.

To ADD a .edi file (or files) to an EXISTING ARCHIVE click button:
  Add .edi file (or files) to an Existing Archive
Select an existing Archive (.csl file) from the dialogue.
In the the next dialogue that opens select a .EDI file (or multiselect two or more .edi files) produced by Minos. Click Open.

The callsigns, Locators and Location (if needed) that are being added will be displayed.

A fouth field is added to the entries in the .csl file which shows the number of times a callsign/locator combination has been included from .EDI files.
Times Worked is shown in the "Comments" field in Minos.
An etxra field is added showing the dates that the contact has been worked, this is not displayed in Minos.
Quotation marks will be placed around text fields in the .csl file. Some spreadsheets/databases require this.

Right click on the report for an edit menu which will allow you to cut and paste the report
into another document. Click in the report and type <Control> A to select all the text.

If a contact already exists in the archive on the same same date it will not be added again.
This means that if you select edi files that have already been added to the archive by mistake they will not be added again.

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

        #Link up control variables and events automatically with prefix=Help
        LinkUpControls(self,self.HelpWindow,'Help')

        self.Help_TextBoxOutput.Text=Txt

        self.HelpWindow.Show()

    def on_Help_Close_click(self, *args):
        """Close the Help window."""

        self.HelpWindow.Close()



def Walk(tree):
    """Find all the components"""
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

def enliven(w):
    """Enliven the window 'w' """
    try:
        controls = [ n for n in Walk(w) if isinstance(n, Button) or isinstance(n, TextBox) ]
        Main(controls)
    except:
        print "Function failed. Did you pass in the window?"

enliven(window)
app = Application()
app.Run(window)

