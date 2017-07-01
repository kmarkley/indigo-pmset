#!/usr/bin/env python2.5

import time
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
    def deviceStartComm(self, device):
        self.debugLog('Starting device: ' + device.name)
        self._updateDevice(device)

    #---------------------------------------------------------------------------
    def deviceStopComm(self, device):
        self.debugLog('Stopping device: ' + device.name)

    #---------------------------------------------------------------------------
    def getBatteryNameList(self, filter='', valuesDict=None, typeId='', targetId=0):
        self.debugLog("getBatteryNameList valuesDict: %s" % str(valuesDict))
        battNames = []
        batts = pmset.getBatteryInfo()

        if len(batts) < 1:
            battNames.append('- No Batteries Found -')

        for batt in batts:
            battNames.append(batt.name)

        return battNames

    #---------------------------------------------------------------------------
    def refreshDeviceStatus(self):
        indigo.server.log('Updating device status.')
        self._updateAllDevices()

    #---------------------------------------------------------------------------
    def toggleDebugging(self):
        self.debug = not self.debug
        self.pluginPrefs['debug'] = self.debug

    #---------------------------------------------------------------------------
    def runConcurrentThread(self):
        try:

            while not self.stopThread:
                self._runLoopStep()

        except self.StopThread:
            pass

    #---------------------------------------------------------------------------
    def _runLoopStep(self):
        # devices are updated when added, so we'll start with a sleep
        updateInterval = int(self.pluginPrefs.get('updateInterval', 5))
        self.debugLog('Next update in %d minutes' % updateInterval)

        # sleep for the designated time (convert to seconds)
        self.sleep(updateInterval * 60)

        self._updateAllDevices()

    #---------------------------------------------------------------------------
    def _updateAllDevices(self):
        for device in indigo.devices.itervalues('self'):
            if device.enabled:
                self._updateDevice(device)
            else:
                self.debugLog('Device disabled: %s' % device.name)

    #---------------------------------------------------------------------------
    def _updateDevice(self, device):
        self.debugLog('Update device: ' + device.name)

        type = device.deviceTypeId
        props = device.pluginProps

        if type == 'PowerSupply':
            self._updateDevice_PowerSupply(device)
        elif type == 'Battery':
            self._updateDevice_Battery(device)

    #---------------------------------------------------------------------------
    def _updateDevice_Battery(self, device):
        name = device.pluginProps['name']
        self.debugLog('Updating battery: %s' % name)

        batt = pmset.getBatteryInfo(name)

        if batt is None:
            self.debugLog('Unknown battery: %s' % name)
            device.updateStateOnServer('present', False)

        else:
            self.debugLog('Battery: %s [%s] - %s' % (batt.name, batt.level, batt.status))
            device.updateStateOnServer('level', batt.level)
            device.updateStateOnServer('status', batt.status)
            device.updateStateOnServer('displayStatus', '%d%%' % batt.level)
            device.updateStateOnServer('lastUpdatedAt', time.strftime('%c'))
            device.updateStateOnServer('estimate', batt.estimate)
            device.updateStateOnServer('present', batt.present)
            device.updateStateOnServer('chargeMinutes', batt.chargeMinutes)
            device.updateStateOnServer('dischargeMinutes', batt.dischargeMinutes)

        if not device.states['present']:
            stateImage = indigo.kStateImageSel.SensorTripped
        elif device.states['status'] == "discharging":
            stateImage = indigo.kStateImageSel.TimerOn
        elif device.states['level'] == 100 or batt.status == "charged":
            stateImage = indigo.kStateImageSel.SensorOff
        elif device.states['status'] == "charging":
            stateImage = indigo.kStateImageSel.TimerOff
        else:
            stateImage = indigo.kStateImageSel.AvPaused
        device.updateStateImageOnServer(stateImage)

    #---------------------------------------------------------------------------
    def _updateDevice_PowerSupply(self, device):
        power = pmset.getCurrentPowerInfo()

        self.debugLog('Power source: %s [%s]' % (
            power.source, 'external' if power.isExternal else 'internal'
        ))

        device.updateStateOnServer('source', power.source)
        device.updateStateOnServer('hasExternalPower', power.isExternal)
        device.updateStateOnServer('displayStatus', 'on' if power.isExternal else 'off')
        device.updateStateOnServer('lastUpdatedAt', time.strftime('%c'))
