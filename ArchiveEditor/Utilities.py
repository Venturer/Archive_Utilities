"""Common routines for the Archive Utilities suite of programs."""

# Version 2.2, 2011
# Version 3.0, November 2017 - Qt5 version
# Version 3.0.1 February 2018 - checkIfLocatorIsInCorrectCountry now uses
#   locsquares.py and LocSquares.ini from Minos2
# Version 3.0.2 - March 2018
#   unittests from test_utilities.py developed
#   checkformat.py used to validate input
#   Some functions re-written to be more `Pythonic`
#   csv/csl processing functions added
#   Now needs Python >= 3.6
# Version 3.0.3 - March 2018 - un_quote reinstated (still used!)
# Version 3.0.4 - May 2018 - Added exception handling to csv_rows, convert_times_worked_to_int


# Copyright (c) 2009-2018, S J Baugh, G4AUC
# All rights reserved.
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


def read_entry_file(file_name: str, entryList: list)-> str:
    """Parses the .edi file and adds the contact details to the list.

        Returns a string containing any format warnings."""

    warnings = ''

    # Open the input file
    with open(file_name, 'r') as f:

        try:

            for line in f:
                if '[QSORecords' in line:
                    # skip until the line contains [QSORecords
                    break

            for line in f:
                # fields in 'line' are separated by ';'
                # split the line and create a list of the fields
                fields = line.split(';')

                if len(fields) >= 10:  # check >=10 fields (i.e. is a qso record)

                    # create a tuple: contact = (callsign, locator, exchange)

                    callsign, locator, exchange = fields[2], fields[9], fields[8]

                    if not checkformat.checkCallsign(callsign):
                        warnings += f'{line.strip()}\n    Callsign: {callsign} does not appear to be a valid callsign.\n\n'

                    if not checkformat.checkLocator(locator):
                        warnings += f'{line.strip()}\n    Locator: {locator} does not appear to be a valid locator.\n\n'

                    contact = (callsign, locator, exchange)

                    entryList.append(contact)
        except UnicodeDecodeError:
            pass

    entryList.sort()

    return warnings


def un_quote(s):
    """Removes quotes from around string s (if present)."""

    return s.strip('"')


def csv_rows(filename: str, delimiter=',', quotechar='"') -> list:
    """Generator to yield the rows of csv file `filename`.

        Yields -> List of strings of the fields in the row
        """

    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        try:
            for row in csvreader:
                yield row
        except UnicodeDecodeError:
            yield ''


def pipeline(data, *funcs):
    """Compose the functions. Call in turn on `data`,
        piping the output from function to function.

        Use:
        pipeline(data, f1[, f2, f3, ... fn])
        or
        pipeline(data, *sequence_of_functions)

        Return -> the result of f3(f2(f1(data))) etc.

        Also works with generator functions.
        Do not mix normal functions and generators.
        """

    accumulator = deepcopy(data)  # avoid any chance of changing data in-place
    for func in funcs:
        accumulator = func(accumulator)

    return accumulator


def csl_rows(csv_rows) -> list:
    """Generator to yield the rows of csl file.

        Delimiter `,` Quote character = `"`

        Yields -> List of the fields in the row, with defaults if row length has less than 5 fields:
            [callsign: str, locator: str, exchange: str, timesWorked: int, dates: str]
        """

    defaults = ['', '', '', 1, '']

    # row processing functions
    pad_the_row = partial(pad_list_with_defaults, padding=defaults)  # make into a single arg func

    def strip_row_fields(row):
        return [f.strip() for f in row]

    for i, row in enumerate(csv_rows):

        # Skip any title row at beginning
        if i == 0 and len(row) >= 2:
            # Equivalent to: yield convert_times_worked_to_int( pad_the_row( strip_row_fields(row)))
            yield pipeline(row, strip_row_fields, pad_the_row, convert_times_worked_to_int)


def pad_list_with_defaults(in_seq, padding) -> list:
    """Pad the in_seq with the appropriate values(s) from
        padding if in_seq is shorter than padding.

        if in_seq item is None the default will be applied to that item.
        padding is a sequence.
        """

    return [a if a is not None else b for a, b in zip_longest(in_seq, padding)]


def convert_times_worked_to_int(padded_row: list) -> list:
    """Convert field 3 (timesWorked) to an int (if not an int already)."""

    try:
        padded_row[3] = int(padded_row[3])
    except ValueError:
        # if field won't convert to int due to incorrect file format
        pass

    return padded_row


def read_archive_file(file_name: str, archiveDict: dict)-> str:
    """Reads an existing .csl file and appends the contents
        to the archiveDict Dictionary.

        Assume the file exists, read the current contents.

        Returns a string containing any format warnings."""

    warnings = ''

    # read the current contents of the .csl file
    for row in csl_rows(csv_rows(file_name)):  # iterate through each row in the file
        try:
            line = ",".join([f'"{f}"' if isinstance(f, str) else str(f) for f in row])  # put line back together
            checkformat.checkLine(line)
        except checkformat.CheckFormatError as e:
            warnings += f'{e}\n'

        callsign, locator, exchange, timesSeen, dates = row[:5]  # ignore extra fields

        contact = (callsign, locator, exchange)

        # add timesSeen and dates to the dictionary with contact as key
        archiveDict[contact] = [timesSeen, dates]

    return warnings


def similarity(s1: str, s2: str)-> int:
    """Checks to see how many places that characters match
        in the strings `s1` and `s2`."""

    # Use a generator comprehension to sum the places that characters match
    same = sum(1 for c1, c2 in zip(s1, s2) if c1 == c2)

    return same


def remove_prefix(callsign: str)-> str:
    """Return a string consisting of a callsign with its prefix removed."""

    posn = 0
    clen = len(callsign)

    if callsign:
        if callsign[0].isnumeric():
            # callsign starts with a number
            posn += 1  # skip past it

        while (posn < clen) and (not callsign[posn].isnumeric()):
            posn += 1  # skip past prefix letters

        while (posn < clen) and callsign[posn].isnumeric():
            posn += 1  # skip past prefix numbers

        # posn now points to rest of callsign after the prefix

        return callsign[posn:]  # return rest of callsign
    else:
        return ''


def get_prefix(callsign: str)-> str:
    """Return a string consisting of the callsign prefix without the last number."""

    posn = 0
    clen = len(callsign)

    if callsign != '':
        if callsign[0].isnumeric():
            # callsign starts with a number
            posn += 1  # skip past it

        while (posn < clen) and (not callsign[posn].isnumeric()):
            posn += 1  # skip past prefix letters

        while (posn < clen) and (callsign[posn].isnumeric()):
            posn += 1  # skip past prefix numbers

        # `posn` now points to rest of callsign after the prefix

        # return prefix of callsign, less last number
        return callsign[:posn - 1]
    else:
        return ''


def remove_suffix(callsign: str)-> str:
    """Return a string consisting of a callsign with its suffix removed."""

    slashPosn = callsign.rfind('/')
    if slashPosn != -1:
        return callsign[:slashPosn]
    else:
        return callsign


def fuzzy_match(contact: tuple, similar_locators_checked: bool, archive_dict: dict) -> list:
    """Find matches of `contact` in the archive_dict in a fuzzy manner.

        contact -> (callsign: str, locator: str, exchange: str)

        archive_dict -> e.g.  {('G0SKA', 'IO91QN', 'SL'): [2, '2017/04/04;2017/03/07;'],
                             ('G1KAW', 'IO91RH', ''): [1, '2017/03/07;']
                             }

        Return a list of matching contacts which is a list of tuples like:
            ('G4AUC', 'IO91OJ', 'RG', 1, '(same locator)', 'dates')"""

    # How fuzzy locator and callsign matches should be, 0=exact match
    locator_threshold = 1
    callsign_threshold = 1

    fuzzy_matches_list = []  # Contents eg: ('G4AUC', 'IO91OJ', 'RG', 1, '(same locator)', 'dates')

    for archive_contact, when_worked in archive_dict.items():

        # when_worked e.g. [1, '2018/1/2;']
        # archive_contact = (callsign, locator, exchange)

        if not (contact == archive_contact):

            # similar locators (performed ONLY if similar_locators_checked is True)
            if similar_locators_checked and (contact[1]):
                if similarity(contact[1], archive_contact[1]) >= len(contact[1]) - locator_threshold:
                    fuzzy_matches_list.append((archive_contact[0], archive_contact[1], archive_contact[2], when_worked[0],
                                             '(similar locator)', when_worked[1]))

            # Same locator
            if contact[1] == archive_contact[1]:
                fuzzy_matches_list.append((archive_contact[0], archive_contact[1], archive_contact[2], when_worked[0],
                                         '(same locator)', when_worked[1]))

            # Different locators
            if (contact[0] == archive_contact[0]) and (contact[1] != archive_contact[1]):
                fuzzy_matches_list.append((archive_contact[0], archive_contact[1], archive_contact[2], when_worked[0],
                                         '(different locator)', when_worked[1]))

            # check callsigns
            sameness = similarity(contact[0], archive_contact[0])
            if (sameness >= len(contact[0]) - callsign_threshold) and (sameness != len(contact[0])):
                fuzzy_matches_list.append((archive_contact[0], archive_contact[1], archive_contact[2], when_worked[0],
                                         '(similar callsign)', when_worked[1]))

            if contact[0] != archive_contact[0]:

                # different prefix
                if remove_suffix(contact[0]) == remove_suffix(archive_contact[0]):
                    fuzzy_matches_list.append((archive_contact[0], archive_contact[1], archive_contact[2], when_worked[0],
                                             '(different suffix)', when_worked[1]))

                # different suffix
                if remove_prefix(contact[0]) == remove_prefix(archive_contact[0]):
                    fuzzy_matches_list.append((archive_contact[0], archive_contact[1], archive_contact[2], when_worked[0],
                                             '(different prefix)', when_worked[1]))

    return fuzzy_matches_list


def check_locator_is_in_correct_country(callsign: str, locator: str)-> str:
    """Checks to see if the Callsign and Locator square are consistent.
        """

    # Initialise the module if not already done
    if locsquares.locatorsquares is None:
        locsquares.initModule()

    if not locsquares.isLocInCountry(callsign, locator):
        report = f'    Prefix of {callsign} is not in Locator Square {locator}'
    else:
        report = None

    return report


def sort_dates(dates: str)-> str:
    """Sort a string of dates into reverse date order.

        e.g.
        '1970/01/01;2069/12/31;2018/02/24;' to '2069/12/31;2018/02/24;1970/01/01;'

        """

    # create a list of the dates, separated by ';'
    d_list = dates.split(';')

    # sort the dates
    d_list.sort(reverse=True)

    # make a string of the sorted dates
    dates_out = ''.join([f'{s};' for s in d_list if s])

    return dates_out


def re_write_csl(file_name: str, archive_dict: dict)-> None:
    """Re-writes (or creates) the .csl file from the archive_dict.

        always include times_seen and quotes in this version."""

    # re-open the csl file, for write this time
    with open(file_name, 'w') as fs:

        key_list = list(archive_dict.keys())
        key_list.sort()  # Sort the keys so that the Dict can be written in callsign order

        # re-write the list
        for p in key_list:
            callsign_out, locator_out, exchange_out = p
            times_seen, dates = archive_dict[p]
            dates_sorted = sort_dates(dates)

            if callsign_out or exchange_out:  # ignore blank callsign entries unless title
                fs.write('"{:s}","{:s}","{:s}","{:d}","{:s}"\n'.format(callsign_out, locator_out,
                                                                       exchange_out, times_seen, dates_sorted))


def format_date(date_in: str)-> str:
    """Format the date as 'yyyy/mm/dd'

        Date In is 'yymmdd'
        Century break taken as year==70."""

    year = date_in[:2]
    month = date_in[2:4]
    day = date_in[4:]

    # Convert the year to an integer, allowing for leading zeroes
    if year[0] == '0':
        year_int = int(year[1:2])
    else:
        year_int = int(year)

    # 00 to 69 as 2000+year, 70 to 99 as 1900+year
    if year_int >= 70:
        year_out = '19' + year
    else:
        year_out = '20' + year

    return f'{year_out}/{month}/{day}'
