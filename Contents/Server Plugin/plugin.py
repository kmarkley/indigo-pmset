#!/usr/bin/env python2.5

import os
import subprocess

from collections import namedtuple

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
        power = self._update()

        indigo.server.log('Power source: %s [%s]' % (
            power.source,
            'external' if power.isExternal else 'internal'
        ))

    #---------------------------------------------------------------------------
    def toggleDebugging(self):
        self.debug = not self.debug
        self.pluginPrefs['debug'] = self.debug

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

        proc = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
        rawOutput = proc.communicate()[0]
        rawLines = rawOutput.splitlines()

        # TODO error checking

        powerLine = rawLines.pop(0)
        self.debugLog(powerLine)

        source = powerLine.split("'")[1]
        external = 'AC' in source and not 'Battery' in source

        power = PowerInfo(source=source, isExternal=external)

        return power

