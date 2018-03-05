import configparser
import os
import json

class LocatorSquaresError(ValueError):
    """Raised when there is a problem in the module."""

# Globals
prefixes = {}
locatorsquares = None

def loadjsonFile():
    """Try to load a prefixes Dictionary using json."""

    global prefixes

    if os.path.exists('prefixes.json'):
        with open('prefixes.json', 'r') as json_file:
            prefixes = json.load(json_file)

def LookUpCall(call):
        """Look up the call using partial matches.

            Returns -> The main prefix for the country of the call if the call is found,
                null string otherwise."""

        global prefixes

        call = call.upper()

        # progressivly reduce length of string
        for i in reversed(range(1,  len(call) + 1)):

            call_part = call[:i]

            if call_part in prefixes:
                # there is a match at this string length

                # get the country details for the prefix/callsign
                details = prefixes[call_part]

                return details['mainprefix']
        else:
	        # gets here when 'for' is exhausted
            return ''

def isLocInCountry(call: str, locator: str)-> bool:
    """Checks whether the first four
        characters of the location are appropriate
        for the country indicated by the callsign.

        Returns -> False if the locator does not match the callsign
            for a supported country, True otherwise.
        """

    global locatorsquares

    if locatorsquares is None:
        raise LocatorSquaresError('Module locsquares.py not initialised.')

    locator = locator.upper()

    mainprefix = LookUpCall(call)

    if mainprefix in locatorsquares.sections():
        pr = locatorsquares[mainprefix]
        if pr.getint(locator[:4], 0):
            # Locator correct
            return True
        else:
            # Locator incorrect
            return False
    else:
        return True # Default for an unsupported country or unknown prefix

def initModule():
    """Initialise the module."""

    global locatorsquares

    locatorsquares = configparser.ConfigParser()
    locatorsquares.read('LocSquares.ini')

    loadjsonFile()


