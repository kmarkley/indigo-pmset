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
## TEST ENTRY
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='pmset test interface.')
    parser.add_argument('-c', '--current', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()

    if args.current:
        print('--CURRENT POWER INFO--')
        power = getCurrentPowerInfo()
        print(str(power))

    if args.test:
        doc = minidom.parse('test_cases.xml')
        tests = doc.getElementsByTagName('TestCase')

        for tc in tests:
            name = tc.attributes['name'].value
            rawOutput = tc.firstChild.nodeValue.strip()

            print('--BEGIN TEST: %s--' % name)

            power = _parsePowerInfo(rawOutput)
            print(str(power))

