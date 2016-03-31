from Plugins.Plugin import PluginDescriptor
from enigma import getDesktop

from . import _


def main(session, **kwargs):
	from MTGPlay import MTGPlayMenu
	session.open(MTGPlayMenu)


def Plugins(**kwargs):
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		icon = "piconhd.png"
	else:
		icon = "picon.png"
	return [PluginDescriptor(
		name=_('MTG Play'),
		description=_('Watch MTG play online services'),
		where=[
				PluginDescriptor.WHERE_PLUGINMENU,
				PluginDescriptor.WHERE_EXTENSIONSMENU
			],
		icon=icon,
		fnc=main
		)]
