import unittest
import checkformat

class Test_checklocator_test(unittest.TestCase):
    correct_locators = (
        'AA00AA',   # Minimum 6 char
        'RR99XX',   # Maximum 6 char
        'AA00AA00', # Minimum 8 char
        'RR99XX99', # Maximum 8 char
        )

    incorrect_locators = (
        'SS00AA',   # >RR 6 char
        'RR99YY',   # >XX 6 char
        'SS00AA00', # >RR 8 char
        'RR99YY99', # >YY 8 char
        ''          # null string
        'AA00AA00A', # too long
        'AA00'      # 4 char
        'AA0'       # 3 char
        'AA'        # 2 char
        'A'         # 1 char
        '0000AA',   # numeric in alpha 6 char
        'AA0000',   # numeric in alpha 6 char
        '0000AA00',   # numeric in alpha 8 char
        'AA000000',   # numeric in alpha 8 char
        'AA0AAA',   # alpha in numeric 6 char
        'AAA0AA',   # alpha in numeric 6 char
        'AAAAAA00',   # alpha in numeric 8 char
        'AA00AAAA',   # alpha in numeric 8 char
        'AA00AAA0',   # alpha in numeric 8 char
        1,  # int not str
        1.5, # float not str
        -2, # Neg int
        3.0e4, # float with exponent not str
        )

    def test_check_correct_locators(self):
        """Check for correctly formated 6 or 8 character locators."""

        for loc in self.correct_locators:
            with self.subTest(loc=loc):
                self.assertEqual(checkformat.checkLocator(loc), True, loc)

    def test_check_incorrect_locators(self):
        """Check that incorrectly formated locators fail."""

        for loc in self.incorrect_locators:
            with self.subTest(loc=loc):
                self.assertEqual(checkformat.checkLocator(loc), False, loc)

class Test_checkdates_test(unittest.TestCase):
    correct_dates = (
        '1970/01/01;',  # Minimum 1970
        '2069/12/31;',   # Maximum 2069
        '2069/12/31;1970/01/01;',               # 2 dates
        '2069/12/31;2018/02/24;1970/01/01;',    # 3 dates
        )

    incorrect_dates = (
        '1970/01/01',  # Minimum 1970, no `;`
        '0970/01/01;',  # wrong century
        '1870/01/01;',  # wrong century
        '2069:12/31;',   # Maximum 2069, wrong separator
        '2069/12/311970/01/01;',                # 2 dates, no separator
        '2069123119700101;',                    # 2 dates, no separators
        '2069/12/31;1970/01/01',                # 2 dates, no end separator
        1,
        1.5,
        -2,
        3.0e4, # float with exponent not str
        ''                                      # null string
        )

    def test_check_correct_dates(self):
        """Check for correctly formated dates."""

        for d in self.correct_dates:
            with self.subTest(d=d):
                self.assertEqual(checkformat.checkDates(d), True, d)

    def test_check_incorrect_dates(self):
        """Check that incorrectly formated dates fail."""

        for d in self.incorrect_dates:
            with self.subTest(d=d):
                self.assertEqual(checkformat.checkDates(d), False, d)

class Test_checkcallsign_test(unittest.TestCase):
    correct_calls = (
        'G4AUC',
        'M4D',
        'MM0AUC',
        'C31AZ',
        '2E0AAA',
        'EI2A',
        'G4AUC/P',
        'G4AUC/MM',
        'F/G4AUC',
        'C3/G4AUC',
        '5B/G4AUC',
        'GW100RSGB',
        'JY1',
        'G4AUC/VE3',
        'W1AB/3',
        'VE6SBB',
        'VK2ECX',
        )

    incorrect_calls = (
        '4AUC',
        'G4AU3C',
        'G4AUC3',
        'MMM4AUC',
        '43M4D',
        'C31A4Z',
        '2E0AAA3',
        'A2E0AAA',
        'E2I2A',
        '34AUC/P',
        'F&G4AUC',
        '31F/G4AUC',
        '0B5AUC',
        'g4auc',
        1,
        1.5,
        -2,
        3.0e4, # float with exponent not str
        ''              # null string
        )

    def test_check_correct_callsigns(self):
        """Check for correctly formated callsigns."""

        for c in self.correct_calls:
            with self.subTest(c=c):
                self.assertEqual(checkformat.checkCallsign(c), True, c)

    def test_check_incorrect_callsigns(self):
        """Check that incorrectly formated callsigns fail."""

        for c in self.incorrect_calls:
            with self.subTest(c=c):
                self.assertEqual(checkformat.checkCallsign(c), False, c)

class Test_checkline_test(unittest.TestCase):
    """Tests checkTimesWorked and checkExchange as well during checkLine tests."""

    correct_lines = (
        '"2E0NEY","IO81VK","",1,"2017/03/07;"',
        '"F8BRK","IN99VF","",2,"2017/04/04;2017/03/07;"',
        '"G0GJV","IO91OK","RG",2,"2017/04/04;2017/03/07;"',
        '"G0ODQ","IO91MR23","",2,"2017/04/04;2017/03/07;"',
        'G0SKA,IO91QN,,2,2017/04/04;2017/03/07;,fred,,',
        '"G4AUC","IO91RH",""'
        )

    incorrect_lines = (
        '"A2E0NEY","IO81VK","",1,"2017/03/07;"',
        '"2E0NEY","IO81VK","",1,"2017/03,/07;"',
        '"F8BRK","I099VZ","",2,"2017/04/04;2017/03/07;"',
        '"G0GJV","IO91OK","RG","Fred","2017/04/04;2017/03/07;"',
        '"G0ODQ","IO91MRQZ","",2,"2017/04/042017/03/07;"',
        '"G0SKA","IO91QN","",-2,"2017/04/04;2017/03/07;"',
        '"31F/G4AUC","IO91RH",""',
        '',
        ',',
        1,
        1.5,
        -2,
        3.0e4, # float with exponent not str
        )

    def test_check_incorrect_exchange(self):
        """Check integer field causes checkExchange failure."""

        self.assertEqual(checkformat.checkExchange(1), False, "1 is not a string")

    def test_check_correct_lines(self):
        """Check for correctly formated lines."""

        for d in self.correct_lines:
            with self.subTest(d=d):
                self.assertEqual(checkformat.checkLine(d), True, d)

    def test_check_incorrect_lines(self):
        """Check that incorrectly formated lines fail."""

        for d in self.incorrect_lines:
            with self.subTest(d=d):
                with self.assertRaises(checkformat.CheckFormatError, msg=d) as cm:
                    checkformat.checkLine(d)


if __name__ == '__main__':
    unittest.main(verbosity=2)
