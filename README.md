# CuraPlugin-PrintTemperatureOffset
A Cura plugin to add an offset to the printing temperature.

Set a temperature offset with a value between -30 and positive 30. This plugin will modify the resulting gcode so that every call to M104 or M109 will be increased or decreased by
the amount specified. This is useful when you have a default printing temperature set for the material that works well most of the time, but you need to adjust the temperature for a specific
profile, such as when using a larger nozzle or printing at a faster speed. This plugin allows you to modify that temperature without modifying the material settings.

M104 and M109 commands that set the temperature to 0 (turning the heater off) are not modified.

###Examples
Print temperature set to 215, Printing Temperature Offset set to 10: Modified temperature will be 225

Print temperature set to 215, Printing Temperature Offset set to -10: Modified temperature will be 205

###Why?
My default material temperatures work great on my 0.4 and 0.6 nozzles, but I was seeing layer de-lamination with my 1.0 nozzle. With this plugin, I can offset the printing temperature on my 1.0mm nozzle profile and print successfully with any filament.


