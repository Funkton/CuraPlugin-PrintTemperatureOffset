# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

import os, json, re

from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Logger import Logger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("DefaultTemperatureOffset")


class PrintTemperatureOffset(Extension):
    def __init__(self):
        super().__init__()

        self._application = Application.getInstance()

        self._i18n_catalog = None

        self._setting_key = "printing_temperature_offset"
        self._setting_dict = {
            "label": "Printing Temperature Offset",
            "description": "Adds or subtracts a small temperature offset from the printing temperature to help with e.g. printing faster or with a larger nozzle.",
            "type": "float",
            "unit": "°C",
            "default_value": 0,
            "minimum_value": -30,
            "maximum_value": 30,
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
        }

        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)

        self._application.globalContainerStackChanged.connect(self._onGlobalContainerStackChanged)
        self._onGlobalContainerStackChanged()

        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode)


    def _onContainerLoadComplete(self, container_id):
        container = ContainerRegistry.getInstance().findContainers(id=container_id)[0]
        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        self.create_and_attach_setting(container, self._setting_key, self._setting_dict, "material")

    def _onGlobalContainerStackChanged(self):
        self._global_container_stack = self._application.getGlobalContainerStack()

    def _filterGcode(self, output_device):

        scene = self._application.getController().getScene()
        # get settings from Cura

        offset_temp = self._global_container_stack.getProperty(self._setting_key, "value")
        if offset_temp == 0:
            return

        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict:  # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return

        m104orM109 = re.compile("(M10[4|9]\s.*S)(\d*\.?\d*)(.*)")

        for plate_id in gcode_dict:
            gcode_list = gcode_dict[plate_id]
            if len(gcode_list) < 2:
                Logger.log("w", "Plate %s does not contain any layers", plate_id)
                continue

            if ";Ajdusted temp by" not in gcode_list[1]:
                for layer_num, gcodes in enumerate(gcode_list):
                    lines = gcodes.split("\n")

                    for (line_nr, line) in enumerate(lines):
                        result = m104orM109.fullmatch(line);
                        if result:
                            existing_temp = float(result.group(2))
                            if existing_temp != 0:
                                adjusted = offset_temp + existing_temp
                                lines[line_nr] = result.group(1) + str(adjusted) + result.group(3) + " ;Ajdusted temp by {}".format(offset_temp)
                    gcode_list[layer_num] = "\n".join(lines)
                gcode_dict[plate_id] = gcode_list
            else:
                Logger.log("d", "Plate %s has already been processed", plate_id)
                continue

            setattr(scene, "gcode_dict", gcode_dict)

    def create_and_attach_setting(self, container, setting_key, setting_dict, parent):
        parent_category = container.findDefinitions(key=parent)
        definition = container.findDefinitions(key=setting_key)
        if parent_category and not definition:
            # this machine doesn't have a scalable extra prime setting yet
            parent_category = parent_category[0]
            setting_definition = SettingDefinition(setting_key, container, parent_category, self._i18n_catalog)
            setting_definition.deserialize(setting_dict)

            parent_category._children.append(setting_definition)
            container._definition_cache[setting_key] = setting_definition
            container._updateRelations(setting_definition)



