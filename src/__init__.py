from gettext import bindtextdomain, dgettext, gettext

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS


def localeInit():
	bindtextdomain('MTGPlay', resolveFilename(SCOPE_PLUGINS,
		'Extensions/MTGPlay/locale'))


def _(txt):
	t = dgettext('MTGPlay', txt)
	if t == txt:
		t = gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
