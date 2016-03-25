#!/usr/bin/env python2.5

import re
import subprocess

from xml.dom import minidom
from collections import namedtuple

PowerInfo = namedtuple('PowerInfo', ['source', 'isExternal'])
BatteryInfo = namedtuple('BatteryInfo', ['name', 'level', 'status'])

################################################################################
def getCurrentPowerInfo():
    proc = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
    rawOutput = proc.communicate()[0]

    return _parsePowerInfo(rawOutput)

################################################################################
def getBatteryInfo(name=None):
    proc = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
    rawOutput = proc.communicate()[0]

    batts = _parseBatteryInfo(rawOutput)
    if name is None: return batts

    for batt in batts:
        if batt.name == name:
            return batt

    return None

################################################################################
def _parsePowerInfo(rawOutput):
    rawLines = rawOutput.splitlines()
    powerLine = rawLines.pop(0)

    match = re.search('["\'](.+)["\']', powerLine)
    if not match: return None

    power = PowerInfo(
        source = match.group(1),
        isExternal = 'AC' in match.group(1)
    )

    return power

################################################################################
def _parseBatteryInfo(rawOutput):
    batts = [ ]

    rawLines = rawOutput.splitlines()
    powerLine = rawLines.pop(0)

    for line in rawLines:
        match = re.search('-(.+)\t(\d+)%;\s*(.+)\s*$', line)

        if match:
            batt = BatteryInfo(
                name = match.group(1),
                level = int(match.group(2)),
                status = match.group(3)
            )
            print (str(batt))
            batts.append(batt)

    return batts

################################################################################
def _printPowerInfo(power):
    if power:
        print('Power source: %s [%s]' % (
            power.source, 'external' if power.isExternal else 'internal'
        ))
    else:
        print('None')

################################################################################
def _runTestCase(tc):
    id = tc.attributes['id'].value
    name = tc.attributes['name'].value
    rawOutput = tc.firstChild.nodeValue.strip()

    print('--BEGIN TEST [%s]: %s--' % (id, name))

    power = _parsePowerInfo(rawOutput)
    _printPowerInfo(power)

    batts = _parseBatteryInfo(rawOutput)

################################################################################
## TEST ENTRY
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='pmset test interface.')
    parser.add_argument('-c', '--current', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('tests', metavar='id', type=str, nargs='*', help='test case id')
    args = parser.parse_args()

    doc = minidom.parse('test_cases.xml')
    tests = doc.getElementsByTagName('TestCase')

    if args.current:
        print('--CURRENT POWER INFO--')
        _printPowerInfo(getCurrentPowerInfo())

    for tc in tests:
        id = tc.attributes['id'].value
        if args.all or id in args.tests:
            _runTestCase(tc)

