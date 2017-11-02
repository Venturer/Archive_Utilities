
"""Common routines for the Archive Utilities suite of programs."""

# Version 2.2, 2011
# Version 3.0, November 2017 - Qt5 version



#Copyright (c) 2009,-2011, S J Baugh, G4AUC
#All rights reserved.
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

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS &AS IS& AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def readEntryFile(FileName, EntryList):
    """Parses the .edi file and adds the contact details to the list."""

    #initialise
    gettingData=False

    #Open the input file
    f = open(FileName,'r')

    try:
        for line in f:

            if gettingData:

                #parameters in 'line' are separated by ';'
                #split the line and create a list of the parameters
                parameters=line.split(';')

                if len(parameters)>=10: #check >=10 parameters (i.e. is a qso record)

                    #create a tuple (callsign,locator,exchange)
                    contact=(parameters[2],parameters[9],parameters[8])

                    EntryList.append(contact)

            elif '[QSORecords' in line:
                #skip until the line contains [QSORecords
                gettingData=True

    finally:
        #close file at end of input
        f.close()

    EntryList.sort()

def unQuote(s):
    """Removes quotes from around string s (if present)."""
    return s.strip('"').rstrip('"')

def readArchiveFile(FileName, archiveDict):
        """Reads an existing .csl file and appends the contents
            to the archiveDict Dictionary."""

        #assume the file exists, read the current contents
        if True:

            #read the current contents of the .csl file into a list
            fs = open(FileName,'r')

            try:
                for line in fs: #iterate through each line in the file

                    #initialise
                    callsign=''
                    locator=''
                    exchange=''
                    timesSeen=1
                    dates=''

                    #Remove trailing whitespace and
                    #create a list of the comma separated variables in the line
                    parameters=line.rstrip().split(',')

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

                    contact=(callsign,locator,exchange)

                    #add timesSeen and dates to the dictionary with contact as key
                    archiveDict[contact]=[timesSeen,dates]

            finally:
                fs.close()

def simularity(s1,s2):
        """Checks to see how many places in the strings that differences oocur."""

        same = 0

        for i in range( min(len(s1),len(s2)) ):
            if s1[i] == s2[i]:
                same += 1

        return same

def removePrefix(callsign):
        """Return a string consisting of a callsign with its prefix removed."""

        posn=0
        clen=len(callsign)

        if callsign!='':
            if callsign[0] in '0123456789':
                #callsign starts with a number
                posn=posn+1 #skip past it

            while (posn<clen) and (callsign[posn] not in '0123456789'):
                posn=posn+1 #skip past prefix letters

            while (posn<clen) and (callsign[posn] in '0123456789'):
                posn=posn+1 #skip past prefix numbers

            #posn now points to rest of callsign after the prefix

            return callsign[posn:]      #return rest of callsign
        else:
            return ''

def getPrefix(callsign):
        """Return a string consisting of a callsign prefix."""

        posn=0
        clen=len(callsign)

        if callsign!='':
            if callsign[0] in '0123456789':
                #callsign starts with a number
                posn += 1 #skip past it

            while (posn<clen) and (callsign[posn] not in '0123456789'):
                posn=posn+1 #skip past prefix letters

            while (posn<clen) and (callsign[posn] in '0123456789'):
                posn=posn+1 #skip past prefix numbers

            #posn now points to rest of callsign after the prefix

            return callsign[:posn-1]      #return prefix of callsign, less last number
        else:
            return ''

def removeSuffix(callsign):
        """Return a string consisting of a callsign with its suffix removed."""

        slashPosn=callsign.rfind('/')
        if slashPosn!=-1:
            return callsign[:slashPosn]
        else:
            return callsign

def fuzzyMatch(contact, Checked, archiveDict):
        """Find matches of contact in the archiveList in a fuzzy manner.

        Return a list of matching contacts which is a list of tuples like:
            ('G4AUC','IO91OJ','RG',1,(same locator), dates)"""

        #How fuzzy locator and callsign matches should be, 0=exact match
        locatorThreshold=1
        callsignThreshold=1

        fuzzyMatchesList=[] # Contents eg: ('G4AUC','IO91OJ','RG',1,(same locator), dates)


        for archiveContact, seen in archiveDict.iteritems():

            if not (contact==archiveContact):

                #similar locators (performed ONLY if Checked is True)
                if Checked and (contact[1]!=''):
                    if Simularity(contact[1],archiveContact[1])>=len(contact[1])-locatorThreshold:
                        fuzzyMatchesList.append((archiveContact[0],archiveContact[1],archiveContact[2],seen[0],'(similar locator)',seen[1]))

                #Same locator
                if contact[1]==archiveContact[1]:
                    fuzzyMatchesList.append((archiveContact[0],archiveContact[1],archiveContact[2],seen[0],'(same locator)',seen[1]))

                #Different locators
                if (contact[0]==archiveContact[0]) and (contact[1]!=archiveContact[1]):
                    fuzzyMatchesList.append((archiveContact[0],archiveContact[1],archiveContact[2],seen[0],'(different locator)',seen[1]))

                #check callsigns
                sameness=Simularity(contact[0],archiveContact[0])
                if (sameness>=len(contact[0])-callsignThreshold) and (sameness!=len(contact[0])):
                    fuzzyMatchesList.append((archiveContact[0],archiveContact[1],archiveContact[2],seen[0],'(similar callsign)',seen[1]))

                if contact[0]!=archiveContact[0]:

                    #different prefix
                    if RemoveSuffix(contact[0])==RemoveSuffix(archiveContact[0]):
                        fuzzyMatchesList.append((archiveContact[0],archiveContact[1],archiveContact[2],seen[0],'(different suffix)',seen[1]))

                    #different suffix
                    if RemovePrefix(contact[0])==RemovePrefix(archiveContact[0]):
                        fuzzyMatchesList.append((archiveContact[0],archiveContact[1],archiveContact[2],seen[0],'(different prefix)',seen[1]))

        return fuzzyMatchesList

def checkLocatorIsInCorrectCountry(Callsign, Locator):
        """ Checks to see if the Callsign and Locator square are consistent.
                Countries supported:
                    England
                    Wales
                    """
        GLocators=['IN69','IN79',
                    'IO70','IO71',
                    'IO80','IO81','IO82','IO83','IO84','IO85',
                    'IO90','IO91','IO92','IO93','IO94','IO95',
                    'JO00','JO01','JO02','JO03']
        GWLocators=['IO71','IO72','IO73','IO81','IO82','IO83']

        prefix=GetPrefix(Callsign)
        square=Locator[:4]

        report=None

        if prefix in ['G', 'GX', '2E', '2X', 'M', 'MX']:
            if square not in GLocators:
                report='    Prefix '+prefix+' is not in Locator Square '+square
        elif prefix in ['GW', 'GC', '2W', '2C', 'MW', 'MC']:
            if square not in GWLocators:
                report='    Prefix '+prefix+' is not in Locator Square '+square

        return report


def sortDates(dates):
    """Sort a string of dates into date order."""

    #create a list of the dates, separated by ';'
    dList=[]
    dList=dates.split(';')

    #sort the dates
    dList.sort()

    #make a string of the sorted dates
    datesOut=''
    for s in reversed(dList):
        if s!='':
            datesOut+=s+';'

    return datesOut

def reWriteCSL(FileName,archiveDict):
        """Re-writes (or creates) the .csl file from the archiveDict."""

        #re-open the csl file, for write this time
        fs = open(FileName,'wb')

        keyList=archiveDict.keys()
        keyList.sort() #Sort the keys so that the Dict can be written in callsign order

        #re-write the list

        Q='"' #always use quotes in this version

        try:
            for p in keyList:
                callsignOut,locatorOut,exchangeOut=p
                timesSeen,dates=archiveDict[p]
                datesSorted=SortDates(dates)
                if (callsignOut != '') or (exchangeOut != ''):  #ignore blank callsign entries unless title
                    fs.write(Q+callsignOut+Q+','+Q+locatorOut+Q+','+Q+exchangeOut+Q+','+repr(timesSeen)+','+Q+datesSorted+Q+'\r\n') #always include timesSeen in this version

        finally:
            fs.close()

def formatDate(DateIn):
        """Format the date as 'yyyy/mm/dd'

            DateIn is 'yymmdd'
            Century break taken as year=70."""

        year=DateIn[:2]
        month=DateIn[2:4]
        day=DateIn[4:]
        yearInt=int(0)

        #Convert the year to an integer, allowing for leading zeroes
        if year[0] == '0':
            yearInt = eval(year[1:2])
        else:
            yearInt=eval(year)

        #00 to 69 as 2000+year, 70 to 99 as 1900+year
        if yearInt > 70:
            yearOut ='19' + year
        else:
            yearOut ='20' + year

        return yearOut + '/' + month + '/' + day
