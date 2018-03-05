
"""Common routines for the Archive Utilities suite of programs."""

# Version 2.2, 2011
# Version 3.0, November 2017 - Qt5 version
# Version 3.0.1 February 2018 - checkIfLocatorIsInCorrectCountry now uses
#   locsquares.py and LocSquares.ini from Minos2
# Version 3.0.2 - March 2018
#   unittests from test_utilities.py developed
#   checkformat.py used to validate input
#   Some functions re-written to be more `Pythonic`
#   Helper functions added
#   Now needs Python >= 3.6
# Version 3.0.3 - March 2018 - unQuote reinstated


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

import locsquares
import checkformat
import csv
from itertools import zip_longest, repeat
from functools import partial
from copy import copy, deepcopy

def readEntryFile(fileName, entryList):
    """Parses the .edi file and adds the contact details to the list."""

    warnings = ''

    # Open the input file
    with open(fileName, 'r') as f:

        for line in f:
            if '[QSORecords' in line:
                # skip until the line contains [QSORecords
                break

        for line in f:
            # fields in 'line' are separated by ';'
            # split the line and create a list of the fields
            fields = line.split(';')

            if len(fields) >= 10: # check >=10 fields (i.e. is a qso record)

                #create a tuple (callsign, locator, exchange)
                callsign, locator, exchange = fields[2], fields[9], fields[8]

                if not checkformat.checkCallsign(callsign):
                    warnings += f'{line.strip()}\n    Callsign: {callsign} does not appear to be a valid callsign.\n\n'

                if not checkformat.checkLocator(locator):
                    warnings += f'{line.strip()}\n    Locator: {locator} does not appear to be a valid locator.\n\n'

                contact = (callsign, locator, exchange)

                entryList.append(contact)

    entryList.sort()

    return warnings

def unQuote(s):
    """Removes quotes from around string s (if present)."""

    return s.strip('"')

def csvRows(filename: str, delimiter=',', quotechar='"')-> list:
    """Generator to yield the rows of csv file `filename`.

        Yields -> List of strings of the fields in the row
        """

    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in csvreader:
            yield row

def pipeline(data, *funcs):
    """Call the functions in turn on `data`,
        piping the output from function to function.

        Use:
        pipeline(data, f1, f2, f3, ... fn)
        or
        pipeline(data, *sequence_of_functions)

        Return -> the result of f3(f2(f1(data))) etc.
        """

    accumulator = deepcopy(data) # avoid any chance of changing data in-place
    for func in funcs:
        accumulator = func(accumulator)

    return accumulator


def cslRows(csvRows)-> list:
    """Generator to yield the rows of csl file `filename`.

        Delimiter `,` Quote character = `"`

        Uses Functional(ish!) paradigm

        Yields -> List of the fields in the row, with defaults if row length has less than 5 fields:
            [callsign: str, locator: str, exchange: str, timesWorked: int, dates: str]
        """

    defaults = ['', '', '', 1, '']

    # row processing functions
    padTheRow = partial(padListWithDefaults, padding=defaults) # make into a single arg func
    stripRowFields = lambda row: [f.strip()  for f in row]

    for i, row in enumerate(csvRows):

        # Skip any title row at begining
        if i == 0 and len(row) < 2:
            continue

        # Equivalent to: yield convertTimesWorkedToInt( padTheRow( stripRow(row)))
        yield pipeline(row, stripRowFields, padTheRow, convertTimesWorkedToInt)

def padListWithDefaults(in_seq, padding)-> list:
    """Pad the in_seq with the appropriate values(s) from
        padding if in_seq is shorter than padding.

        if in_list item is None the default will be applied to that item.
        padding is a sequence.
        """

    return [a if a is not None else b  for a, b in zip_longest(in_seq, padding)]

def convertTimesWorkedToInt(paddedRow: list)-> list:
    """Convert field 3 (timesWorked) to an int (if not an int already)."""

    paddedRow[3] = int(paddedRow[3])

    return paddedRow

def readArchiveFile(fileName, archiveDict):
    """Reads an existing .csl file and appends the contents
        to the archiveDict Dictionary.

        Assume the file exists, read the current contents."""

    warnings = ''

    #read the current contents of the .csl file
    for row in cslRows(csvRows(fileName)): # iterate through each row in the file

        try:
            line = ",".join([f'"{f}"' if isinstance(f, str) else str(f)  for f in row]) # put line back together
            checkformat.checkLine(line)
        except checkformat.CheckFormatError as e:
            warnings += f'{e}\n'

        callsign, locator, exchange, timesSeen, dates = row[:5] # ignore extra fields

        contact = (callsign, locator, exchange)

        # add timesSeen and dates to the dictionary with contact as key
        archiveDict[contact] = [timesSeen, dates]

    return warnings

def simularity(s1, s2):
    """Checks to see how many places that characters match
        in the strings `s1` and `s2`."""

    # Use a generator comprehension to sum the places that characters match
    same = sum(1 for c1, c2 in zip(s1, s2) if c1 == c2)

    return same

def removePrefix(callsign):
    """Return a string consisting of a callsign with its prefix removed."""

    posn = 0
    clen = len(callsign)

    if callsign:
        if callsign[0].isnumeric():
            # callsign starts with a number
            posn += 1 # skip past it

        while (posn < clen) and (not callsign[posn].isnumeric()):
            posn += 1 # skip past prefix letters

        while (posn < clen) and callsign[posn].isnumeric():
            posn += 1 # skip past prefix numbers

        # posn now points to rest of callsign after the prefix

        return callsign[posn:] # return rest of callsign
    else:
        return ''

def getPrefix(callsign):
    """Return a string consisting of the callsign prefix without the last number.

        No longer used?."""

    posn=0
    clen=len(callsign)

    if callsign != '':
        if callsign[0].isnumeric():
            # callsign starts with a number
            posn += 1 # skip past it

        while (posn < clen) and (not callsign[posn].isnumeric()):
            posn += 1 # skip past prefix letters

        while (posn < clen) and (callsign[posn].isnumeric()):
            posn += 1 # skip past prefix numbers

        # `posn` now points to rest of callsign after the prefix

        # return prefix of callsign, less last number
        return callsign[:posn - 1]
    else:
        return ''

def removeSuffix(callsign):
        """Return a string consisting of a callsign with its suffix removed."""

        slashPosn = callsign.rfind('/')
        if slashPosn != -1:
            return callsign[:slashPosn]
        else:
            return callsign

def fuzzyMatch(contact: tuple, similarLocatorsChecked: bool, archiveDict: dict)-> list:
    """Find matches of contact in the archiveList in a fuzzy manner.

        contact -> (callsign: str, locator: str, exchange: str)

        archiveDict -> e.g.  {('G0SKA', 'IO91QN', 'SL'): [2, '2017/04/04;2017/03/07;'],
                             ('G1KAW', 'IO91RH', ''): [1, '2017/03/07;']
                             }

        Return a list of matching contacts which is a list of tuples like:
            ('G4AUC', 'IO91OJ', 'RG', 1, (same locator), dates)"""

    # How fuzzy locator and callsign matches should be, 0=exact match
    locatorThreshold = 1
    callsignThreshold = 1

    fuzzyMatchesList = [] # Contents eg: ('G4AUC', 'IO91OJ', 'RG', 1, (same locator), dates)

    for archiveContact, whenWorked in archiveDict.items():

        # whenWorked e.g. [1, '2018/1/2;']
        # archiveContact = (callsign, locator, exchange)

        if not (contact == archiveContact):

            #similar locators (performed ONLY if Checked is True)
            if similarLocatorsChecked and (contact[1]):
                if simularity(contact[1], archiveContact[1]) >= len(contact[1]) - locatorThreshold:
                    fuzzyMatchesList.append((archiveContact[0], archiveContact[1], archiveContact[2], whenWorked[0], '(similar locator)', whenWorked[1]))

            #Same locator
            if contact[1] == archiveContact[1]:
                fuzzyMatchesList.append((archiveContact[0], archiveContact[1], archiveContact[2], whenWorked[0], '(same locator)', whenWorked[1]))

            #Different locators
            if (contact[0] == archiveContact[0]) and (contact[1] != archiveContact[1]):
                fuzzyMatchesList.append((archiveContact[0], archiveContact[1], archiveContact[2], whenWorked[0], '(different locator)', whenWorked[1]))

            #check callsigns
            sameness = simularity(contact[0], archiveContact[0])
            if (sameness >= len(contact[0]) - callsignThreshold) and (sameness != len(contact[0])):
                fuzzyMatchesList.append((archiveContact[0], archiveContact[1], archiveContact[2], whenWorked[0], '(similar callsign)', whenWorked[1]))

            if contact[0] != archiveContact[0]:

                #different prefix
                if removeSuffix(contact[0]) == removeSuffix(archiveContact[0]):
                    fuzzyMatchesList.append((archiveContact[0], archiveContact[1], archiveContact[2], whenWorked[0], '(different suffix)', whenWorked[1]))

                #different suffix
                if removePrefix(contact[0]) == removePrefix(archiveContact[0]):
                    fuzzyMatchesList.append((archiveContact[0], archiveContact[1], archiveContact[2], whenWorked[0], '(different prefix)', whenWorked[1]))

    return fuzzyMatchesList

def checkLocatorIsInCorrectCountry(Callsign, Locator):
    """Checks to see if the Callsign and Locator square are consistent.
        """
    # Initialise the module if not already done
    if locsquares.locatorsquares is None:
        locsquares.initModule()

    if not locsquares.isLocInCountry(Callsign, Locator):
        report = f'    Prefix of {Callsign} is not in Locator Square {Locator}'
    else:
        report = None

    return report

def sortDates(dates):
    """Sort a string of dates into reverse date order.

        e.g.
        '1970/01/01;2069/12/31;2018/02/24;' to '2069/12/31;2018/02/24;1970/01/01;'

        """

    # create a list of the dates, separated by ';'
    dList = dates.split(';')

    # sort the dates
    dList.sort(reverse=True)

    # make a string of the sorted dates
    datesOut = ''.join([f'{s};'  for s in dList if s])

    return datesOut

def reWriteCSL(fileName, archiveDict):
    """Re-writes (or creates) the .csl file from the archiveDict.

        always include timesSeen and quotes in this version."""

    # re-open the csl file, for write this time
    with open(fileName,'w') as fs:

        keyList = list(archiveDict.keys())
        keyList.sort() # Sort the keys so that the Dict can be written in callsign order

        # re-write the list
        for p in keyList:
            callsignOut, locatorOut, exchangeOut = p
            timesSeen, dates = archiveDict[p]
            datesSorted = sortDates(dates)

            if (callsignOut) or (exchangeOut):  # ignore blank callsign entries unless title
                fs.write('"{:s}","{:s}","{:s}","{:d}","{:s}"\n'.format(callsignOut, locatorOut,
                                                                       exchangeOut, timesSeen, datesSorted))

def formatDate(DateIn):
    """Format the date as 'yyyy/mm/dd'

        DateIn is 'yymmdd'
        Century break taken as year==70."""

    year=DateIn[:2]
    month=DateIn[2:4]
    day=DateIn[4:]

    #Convert the year to an integer, allowing for leading zeroes
    if year[0] == '0':
        yearInt = int(year[1:2])
    else:
        yearInt=int(year)

    #00 to 69 as 2000+year, 70 to 99 as 1900+year
    if yearInt >= 70:
        yearOut ='19' + year
    else:
        yearOut ='20' + year

    return f'{yearOut}/{month}/{day}'
