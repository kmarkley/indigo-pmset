#!/usr/bin/env python2.5

import os
import subprocess

from collections import namedtuple
from xml.dom import minidom

PowerInfo = namedtuple('PowerInfo', ['source', 'isExternal'])
BatteryInfo = namedtuple('BatteryInfo', ['name', 'level', 'isCharging'])

# pmset -g batt
#
# Now drawing from 'AC Power'
#  -InternalBattery-0	100%; charged; 0:00 remaining present: true
#
# Now drawing from 'Battery Power'
#  -InternalBattery-0	100%; discharging; (no estimate) present: true
#  -UPS CP600	100%; charging present: true

################################################################################
class Plugin(indigo.PluginBase):

    #---------------------------------------------------------------------------
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.debug = pluginPrefs.get('debug', False)

    #---------------------------------------------------------------------------
    def __del__(self):
        indigo.PluginBase.__del__(self)

    #---------------------------------------------------------------------------
    def startup(self):
        self.debugLog('-- Plugin STARTUP --')

    #---------------------------------------------------------------------------
    def shutdown(self):
        self.debugLog('-- Plugin SHUTDOWN --')

    #---------------------------------------------------------------------------
    def deviceStartComm(self, device):
        self.debugLog('Starting device: %s' % device.name)
        #TODO update device level

    #---------------------------------------------------------------------------
    def deviceStopComm(self, device):
        self.debugLog('Stopping device: %s' % device.name)

    #---------------------------------------------------------------------------
    def refreshPowerStatus(self):
        power = self._getPowerInfo()

        indigo.server.log('Power source: %s [%s]' % (
            power.source,
            'external' if power.isExternal else 'internal'
        ))

    #---------------------------------------------------------------------------
    def toggleDebugging(self):
        self.debug = not self.debug
        self.pluginPrefs['debug'] = self.debug

    #---------------------------------------------------------------------------
    def runTestCases(self):
        doc = minidom.parse('test_cases.xml')
        tests = doc.getElementsByTagName('TestCase')

        for tc in tests:
            name = tc.attributes['name'].value
            value = tc.firstChild.nodeValue.strip()
            self._testCommandParsing(name, value)

    #---------------------------------------------------------------------------
    def runConcurrentThread(self):
        while True:
            # update once then go to sleep
            self._update()

            updateInterval = int(self.pluginPrefs.get('updateInterval', 5))
            self.debugLog('Next update in %d minutes' % updateInterval)

            # sleep for the designated time (convert to seconds)
            self.sleep(updateInterval * 60)

    #---------------------------------------------------------------------------
    def _update(self):
        self.debugLog('Updating power status')

        self._getPowerInfo()

    #---------------------------------------------------------------------------
    def _getPowerInfo(self):
        proc = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
        rawOutput = proc.communicate()[0]
        return self._parsePowerInfo(rawOutput)

    #---------------------------------------------------------------------------
    def _parsePowerInfo(self, rawOutput):
        # TODO error checking

        rawLines = rawOutput.splitlines()

        powerLine = rawLines.pop(0)
        self.debugLog(powerLine)

        source = powerLine.split("'")[1]
        external = 'AC' in source and not 'Battery' in source

        return PowerInfo(source=source, isExternal=external)

    #---------------------------------------------------------------------------
    def _testCommandParsing(self, name, raw):
        indigo.server.log('--BEGIN TEST: %s--' % name)

        power = self._parsePowerInfo(raw)
        indigo.server.log(str(power))

        indigo.server.log('--END TEST: %s--' % name)

