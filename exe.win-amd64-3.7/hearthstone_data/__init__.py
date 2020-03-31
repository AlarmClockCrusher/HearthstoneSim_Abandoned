import os
import pkg_resources


__version__ = pkg_resources.require("hearthstone_data")[0].version


def get_carddefs_path():
	return pkg_resources.resource_filename("hearthstone_data", "CardDefs.xml")


def get_strings_file(locale="enUS", filename="GLOBAL.txt"):
	path = os.path.join("Strings", locale, filename)

	return pkg_resources.resource_filename("hearthstone_data", path)
