# indigo-pmset

This Indigo plugin provides a basic interface to pmset for monitoring power settings,
battery levels and supply status.  The devices allow a user to trigger on power failures /
restoration, battery levels, etc.

You can run the command `pmset -g batt` to see the data used by this plugin.

## Devices

### Power Supply

Represents the main power supply for the computer.

### Battery

Represents a battery known to the computer.  The plugin will automatically detect the
available batteries and present them to the user.
