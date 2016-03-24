#!/usr/bin/env python2.5

import subprocess

from xml.dom import minidom
from collections import namedtuple

PowerInfo = namedtuple('PowerInfo', ['source', 'isExternal'])
BatteryInfo = namedtuple('BatteryInfo', ['name', 'level', 'isCharging'])

################################################################################
def getCurrentPowerInfo():
    proc = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
    rawOutput = proc.communicate()[0]

    return _parsePowerInfo(rawOutput)

################################################################################
def _parsePowerInfo(rawOutput):
    # TODO error checking

    rawLines = rawOutput.splitlines()
    powerLine = rawLines.pop(0)

    source = powerLine.split("'")[1]
    external = 'AC' in source and not 'Battery' in source

    return PowerInfo(source=source, isExternal=external)

################################################################################
def _printPowerInfo(power):
    print('Power source: %s [%s]' % (
        power.source, 'external' if power.isExternal else 'internal'
    ))

################################################################################
def _runTestCase(tc):
    id = tc.attributes['id'].value
    name = tc.attributes['name'].value
    rawOutput = tc.firstChild.nodeValue.strip()

    print('--BEGIN TEST [%s]: %s--' % (id, name))

    power = _parsePowerInfo(rawOutput)
    _printPowerInfo(power)

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

