# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

from . import PrintTemperatureOffset
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("PrintTemperatureOffset")

def getMetaData():
    return {}

def register(app):
    return {"extension": PrintTemperatureOffset.PrintTemperatureOffset()}
