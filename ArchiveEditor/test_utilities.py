import unittest
import Utilities
from itertools import zip_longest, repeat
from pprint import pprint

# Use:
# exec(open('test_utilities.py', 'r').read())
# in interactive

class Test_sortDates(unittest.TestCase):

    values = (
        ('1970/01/01;', '1970/01/01;'), # Minimum 1970
        ('2069/12/31;', '2069/12/31;'), # Maximum 2069
        ('1970/01/01;2069/12/31;','2069/12/31;1970/01/01;'), # 2 dates
        ('1970/01/01;2069/12/31;2018/02/24;', '2069/12/31;2018/02/24;1970/01/01;'),    # 3 dates
        ('2069/12/31;2018/02/24;1970/01/01;', '2069/12/31;2018/02/24;1970/01/01;'),    # 3 dates already correct
    )

    def test_sortDates_values(self):

        for v in self.values:
            with self.subTest(v=v):
                self.assertEqual(Utilities.sortDates(v[0]), v[1], v)


class Test_formatDate(unittest.TestCase):

    values = (
        ('700101', '1970/01/01'), # Minimum 1970
        ('691231', '2069/12/31'), # Maximum 2069
        ('180224', '2018/02/24')    # 2018
    )

    def test_formatDate_values(self):

        for v in self.values:
            with self.subTest(v=v):
                self.assertEqual(Utilities.formatDate(v[0]), v[1], v)

class Test_checkLocatorIsInCorrectCountry(unittest.TestCase):

    values = (
        ('G4AUC', 'IO91oj', None),  # Correct LOC, supported country
        ('G4AUC', 'IO01oj', False), # Incorrect LOC, supported country
        ('PY4AUC', 'IO91oj', None), # Unsupported country
        ('ZZ4AUC', 'IO91oj', None), # Unsupported country, not main prefix
        ('ZE4AUC', 'IO91oj', None), # Prefix does not exist
        ('HE0AUC', 'IO910j', False), # Incorrect LOC, supported country, not main prefix
        ('HE0AUC', 'JN470j', None), # Correct LOC, supported country, not main prefix
        ('HB0AUC', 'JN470j', None), # # Correct LOC, supported country, main prefix
        ('g4auc', 'io91oj', None),  # Correct LOC, supported country, lowercase
        ('G4AUC', 'IO91', None),  # Correct LOC, supported country, 4 char LOC
        ('G4AUC', 'IO9', False),  # Short LOC, supported country
        ('G4AUC', 'IO91oj10', None),  # Correct 8 char LOC, supported country
    )

    def test_checkLocatorIsInCorrectCountry_values(self):

        for call, locator, correct in self.values:
            result = Utilities.checkLocatorIsInCorrectCountry(call, locator)
            #print(call, locator, correct, result)
            if correct is None:
                self.assertIsNone(result)
            else:
                self.assertIsInstance(result, str)

class Test_simularity(unittest.TestCase):

    values = (
        ('G4AUC', 'G4AUC', 5),
        ('G4AUC', 'G4AUZ', 4),
        ('G4AUC', 'Z4AUZ', 3),
        ('G4AUC', 'Z3AUZ', 2),
        ('G4AUC', 'Z3ARZ', 1),
        ('G4AUC', 'F6XYZ', 0),
        ('G4AUC', 'GM4AUC', 1),
        ('G4AUC', '', 0),
        ('', 'G4AUC', 0),
        ('', '', 0),
    )

    def test_simularity_values(self):

        for c1, c2, sim in self.values:
            with self.subTest(c1=c1, c2=c2, sim=sim):
                self.assertEqual(Utilities.simularity(c1, c2), sim)

class Test_removeSuffix(unittest.TestCase):

    values = (
        ('G4AUC/P', 'G4AUC'),
        ('G4AUC/MM', 'G4AUC'),
        ('G4AUC/VE3', 'G4AUC'),
        ('F/G4AUC/P', 'F/G4AUC'),
    )

    def test_removeSuffix_values(self):

        for v in self.values:
            with self.subTest(v=v):
                self.assertEqual(Utilities.removeSuffix(v[0]), v[1], v)

class Test_removePrefix(unittest.TestCase):

    values = (
        ('G4AUC', 'AUC'),
        ('2E0NEY', 'NEY'),
        ('G4AUC/VE3', 'AUC/VE3'),
        #('F/G4AUC/P', 'AUC/P'), # need to check requirement here
        #('F6/G4AUC/P', 'AUC/P'),
    )

    def test_removePrefix_values(self):

        for v in self.values:
            with self.subTest(v=v):
                self.assertEqual(Utilities.removePrefix(v[0]), v[1], v)

class Test_getPrefix(unittest.TestCase):

    values = (
        ('G4AUC/P', 'G'),
        ('2E0NEY', '2E'),
        ('C31AB', 'C3'),
        #('F/G4AUC/P', 'F'), # need to check requirement here
    )

    def test_getPrefix_values(self):

        for v in self.values:
            with self.subTest(v=v):
                self.assertEqual(Utilities.getPrefix(v[0]), v[1], v)

class Test_readArchiveFile(unittest.TestCase):

    correct_dict = {
        ('2E0NEY', 'IO81VK', ''): [1, '2017/03/07;'],
        ('F8BRK', 'IN99VF', ''): [1, ''],
        ('G0GJV', '', ''): [1, ''],
        ('G0ODQ', 'IO91MR', ''): [1, ''],
        ('G0S0A', 'IO91QN', ''): [2, '2017/04/04;2017/03/07;'],
        ('G1KAW', 'IO91RH', ''): [1, '2017/03/07;'],
        ('G3MEH', 'IO910S', ''): [1, '2017/03/07;'],
        ('G3YSX', 'IO91WG', ''): [2, '2017/04/04;2017/03/07;'],
        }

    correct_warnings = """The line: "F8BRK","IN99VF","",1,"" is not correctly formatted:
"" : date(s) are not correctly formatted!

The line: "G0GJV","","",1,"" is not correctly formatted:
"" : locator is not correctly formatted!
"" : date(s) are not correctly formatted!

The line: "G0ODQ","IO91MR","",1,"" is not correctly formatted:
"" : date(s) are not correctly formatted!

The line: "G0S0A","IO91QN","",2,"2017/04/04;2017/03/07;" is not correctly formatted:
"G0S0A" : callsign is not correctly formatted!

The line: "G3MEH","IO910S","",1,"2017/03/07;" is not correctly formatted:
"IO910S" : locator is not correctly formatted!

"""


    def test_readArchiveFile_produces_correct_dict(self):

        archiveDict = {}
        warnings = Utilities.readArchiveFile(r'readtest.csl', archiveDict)
        print('\nWarnings')
        print(warnings)
        print(archiveDict)
        self.assertEqual(archiveDict, self.correct_dict)
        self.assertEqual(warnings, self.correct_warnings)

class Test_readEdiFile(unittest.TestCase):

    correct_entries = [
        ('2E0PEY', 'IO81VK', ''), # 0
        ('F8BRK', 'IN99VF', ''), # 1
        ('G0GJV', 'IO910K', ''), # 2
        ('G0ODQ', 'IO91MR', ''), # 3
        ('G0SKA', 'IO91QN', ''), # 4
        ('G1O1FW', 'IO91QH', ''), # 5
        ('G3YSX', 'IO91WG', ''), # 6
        ('G4CLA', 'IO92JL', ''), # 7
        ('G4GFI', 'IO91VH', ''), # 8
        ('G4LDL/P', 'IO91DM', ''), # 9
        ('G4WJS', 'IO91NP', ''), # 10
        ('G4YPC', 'IO91RH', ''), # 11
        ('G6RC', 'IO91VC', ''), # 12
        ('G8MKC/P', 'IO92NC', ''), # 13
        ('M0DXR/P', 'JO01DH', ''), # 14
        ('M0RKX/P', 'IO92BA', ''), # 15
        ('M0SAT', 'IO91TP', ''), # 16
        ('M1MHZ', 'IO92WV', ''), # 17
        ]

    correct_warnings = """170606;1905;G1O1FW;1;59;002;58;003;;IO91QH;15;;;;
    Callsign: G1O1FW does not appear to be a valid callsign.

170606;1907;G0GJV;1;59;003;59;006;;IO910K;5;;;;
    Locator: IO910K does not appear to be a valid locator.

"""

    def test_readFromEdiFile(self):

        entries = []
        warnings = Utilities.readEntryFile('testread.EDI', entries)

        print(' ')
        print('Warnings:\n', warnings)


        for i, e in enumerate(entries):
            print(f'{e}, # {i}')

        self.assertEqual(entries, self.correct_entries)
        self.assertEqual(warnings, self.correct_warnings)



if __name__ == '__main__':
    unittest.main(verbosity=2)
