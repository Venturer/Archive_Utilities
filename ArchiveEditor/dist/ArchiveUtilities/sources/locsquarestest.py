"""Test module for locsquares.py using unittest."""

import locsquares
import unittest

class InitialisationTests(unittest.TestCase):

    def test_loadjsonfile_loads(self):
        "JSON file prefixes.json should load correctly."

        locsquares.loadjsonFile()
        self.assertNotEqual(locsquares.prefixes, {})

    def test_isLocInCountry_raises_exception(self):
        """Should raise exception if module not initialised."""

        # Must be called before KnownValues, which will initialise

        self.assertRaises(locsquares.LocatorSquaresError, locsquares.isLocInCountry, 'G4AUC', 'IO91')


class KnownValues(unittest.TestCase):

    known_values = (
        ('G4AUC', 'IO91oj', True),  # Correct LOC, supported country
        ('G4AUC', 'IO01oj', False), # Incorrect LOC, supported country
        ('PY4AUC', 'IO91oj', True), # Unsupported country
        ('ZZ4AUC', 'IO91oj', True), # Unsupported country, not main prefix
        ('ZE4AUC', 'IO91oj', True), # Prefix does not exist
        ('HE0AUC', 'IO910j', False), # Incorrect LOC, supported country, not main prefix
        ('HE0AUC', 'JN470j', True), # Correct LOC, supported country, not main prefix
        ('HB0AUC', 'JN470j', True), # # Correct LOC, supported country, main prefix
        ('g4auc', 'io91oj', True),  # Correct LOC, supported country, lowercase
        ('G4AUC', 'IO91', True),  # Correct LOC, supported country, 4 char LOC
        ('G4AUC', 'IO9', False),  # Short LOC, supported country
        ('G4AUC', 'IO91oj10', True),  # Correct 8 char LOC, supported country
    )

    def test_isLocInCountry_known_values(self):
        '''Should give known result with known input'''
        
        locsquares.initModule()
        print()
        for call, locator, correct in self.known_values:
            result = locsquares.isLocInCountry(call, locator)
            print(call, locator, correct, result)
            self.assertEqual(correct, result)

     
if __name__ == '__main__':
    unittest.main(verbosity=2)