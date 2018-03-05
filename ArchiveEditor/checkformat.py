"""Routines to check the format of csl files."""

# Version 1.0, February 2018

import re

class CheckFormatError(ValueError):
    """Raised when a format error is detected in the csv line."""

def checkDates(dates: str)-> bool:
    """Check the dates field for the correct format.

        Format should be a string of dates YYYY/MM/DD; e.g.
        2018/11/19;1975/06/29;
        """

    if not isinstance(dates, str):
        return False

    if dates:
        pattern = '([1-2][0,9][0-9][0-9][/][0-1][0-9][/][0-3][0-9][;])*'

        R = re.fullmatch(pattern, dates)
        correct = R is not None
    else:
        correct = False

    return correct

def checkCallsign(callsign: str)-> bool:
    """Check that the callsign field contains an acceptable callsign.
        """

    if not isinstance(callsign, str):
        return False

    callsign_prefix_pattern = '(([1-9][A-Z])|([A-Z]){1,2}?)([0-9])*'
    callsign_body_pattern = '(([1-9][A-Z])|([A-Z]){1,2}?)([0-9])+([A-Z])*'
    callsign_suffix_pattern = '(([0-9,A-Z])|([A-Z]){1,2}?)' # /P, /MM, /3 etc

    if callsign:
        if '/' not in callsign:
            body_match = re.fullmatch(callsign_body_pattern, callsign)
            correct = body_match is not None
        else:
            strokes = callsign.count('/')

            if strokes == 1:
                parts = callsign.split('/')

                body_match_before_stroke = re.fullmatch(callsign_body_pattern, parts[0])
                body_match_after_stroke = re.fullmatch(callsign_body_pattern, parts[1])
                suffix_match = re.fullmatch(callsign_suffix_pattern, parts[1])
                prefix_match_before_stroke = re.fullmatch(callsign_prefix_pattern, parts[0])
                prefix_match_after_stroke = re.fullmatch(callsign_prefix_pattern, parts[1])

                correct = (body_match_before_stroke is not None and suffix_match is not None) \
                    or (prefix_match_before_stroke is not None and body_match_after_stroke is not None) \
                    or (body_match_before_stroke is not None and prefix_match_after_stroke is not None)

            elif strokes == 2:
                correct = False

            else:
                correct = False
    else:
        correct = False

    return correct

def checkLocator(locator: str)-> bool:
    """Check the locator field for the correct format.

        AA99AA or AA99AA99


        Returns True if the locator is valid, False otherwise.

        Checks that it is a correctly formed 6 or 8 character Maidenhead locator.
        """

    if not isinstance(locator, str):
        return False

    # use regular expressions to try to match the correct patterns

    if len(locator) == 6:
        R = re.match('[A-R][A-R][0-9][0-9][A-X][A-X]', locator)
        valid = R is not None
    elif len(locator) == 8:
        R = re.match('[A-R][A-R][0-9][0-9][A-X][A-X][0-9][0-9]', locator)
        valid = R is not None
    else:
        valid = False

    return valid

def checkTimesWorked(timesWorked: str)-> bool:
    """Check that TimesWorked will evaluate to an integer."""

    if not isinstance(timesWorked, str):
        return False

    if sum(1 for ch in timesWorked if ch not in '0123456789'):
        return False
    else:
        return True

def checkExchange(exchange: str)-> bool:
    """Check that exchange is a string."""

    return isinstance(exchange, str)


def checkLine(line: str)-> bool:
    """Check the csl file line for the correct format.

        callsign,locator,exchange,[times_worked,[dates]]

        Raises -> `CheckFormatError` if the check fails.
        """

    check_functions = [(checkCallsign, ': callsign is not correctly formatted!'),
                    (checkLocator, ': locator is not correctly formatted!'),
                    (checkExchange, ': exchange is not correctly formatted!'),
                    (checkTimesWorked, ': not a correct integer value!'),
                    (checkDates, ': date(s) are not correctly formatted!')
                    ]

    if not isinstance(line, str):
        raise CheckFormatError('The argument passed to checkLine: {} is not a string!'.format(line))

    errorMessage = ''

    fields = line.split(',')

    if len(fields) < 3:
        raise CheckFormatError('The line: {} must have at least three comma separated fields!'.format(line))

    for i, field in enumerate(fields):

        if i > 4:
            break # do not check fields after dates

        f = check_functions[i][0]

        if not f(field.strip('"')):
            errorMessage += '{} {}\n'.format(field, check_functions[i][1])

    if errorMessage:
        raise CheckFormatError('The line: {} is not correctly formatted:\n{}'.format(line, errorMessage))


    return True