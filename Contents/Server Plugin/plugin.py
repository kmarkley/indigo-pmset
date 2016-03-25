#!/usr/bin/env python2.5

import pmset

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
    def refreshPowerStatus(self):
        power = pmset.getCurrentPowerInfo()

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
        try:

            while True:
                self._runLoopStep()

        except self.StopThread:
            pass

    #---------------------------------------------------------------------------
    def _runLoopStep(self):
        # update once then go to sleep
        self._update()

        updateInterval = int(self.pluginPrefs.get('updateInterval', 5))
        self.debugLog('Next update in %d minutes' % updateInterval)

        # sleep for the designated time (convert to seconds)
        self.sleep(updateInterval * 60)

    #---------------------------------------------------------------------------
    def _update(self):
        self.debugLog('Updating power status')

        power = pmset.getCurrentPowerInfo()
        self.debugLog('Power source: %s' % power.source)

