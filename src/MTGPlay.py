import os
from json import loads
from twisted.web.client import downloadPage
from urllib2 import Request, urlopen

from enigma import ePicLoad, eServiceReference, getDesktop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar, MoviePlayer
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from . import _


class MTGPlayer(MoviePlayer):
	def __init__(self, session, service):
		MoviePlayer.__init__(self, session, service)
		self.skinName = 'MoviePlayer'
		self.servicelist = InfoBar.instance and InfoBar.instance.servicelist

	def leavePlayer(self):
		self.session.openWithCallback(self.leavePlayerConfirmed,
			MessageBox, _('Stop playing this movie?'))

	def leavePlayerConfirmed(self, answer):
		if answer:
			self.close()

	def doEofInternal(self, playing):
		self.close()

	def getPluginList(self):
		from Components.PluginComponent import plugins
		list = []
		for p in plugins.getPlugins(where=PluginDescriptor.WHERE_EXTENSIONSMENU):
			if p.name != _('MTG Play'):
				list.append(((boundFunction(self.getPluginName, p.name),
					boundFunction(self.runPlugin, p), lambda: True), None))
		return list

	def showMovies(self):
		pass

	def openServiceList(self):
		if hasattr(self, 'toggleShow'):
			self.toggleShow()


class MTGPlayMenu(Screen):
	screenWidth = getDesktop(0).size().width()
	if screenWidth and screenWidth == 1280:
		skin = """
			<screen position="center,center" size="720,400">
				<widget source="list" render="Listbox" position="10,10" size="360,330" \
					scrollbarMode="showOnDemand" >
					<convert type="TemplatedMultiContent" >
					{
						"template": [MultiContentEntryText(pos=(10, 1), size=(340, 30), \
								font=0, flags=RT_HALIGN_LEFT, text=0)],
						"fonts": [gFont("Regular", 20)],
						"itemHeight": 30
					}
					</convert>
				</widget>
				<widget name="pic" position="400,10" size="290,162" alphatest="on" />
				<widget name="descr" position="380,175" size="330,170" halign="center" font="Regular;18" />
				<ePixmap position="154,351" size="140,40" pixmap="skin_default/buttons/red.png" \
					transparent="1" alphatest="on" />
				<ePixmap position="418,351" size="140,40" pixmap="skin_default/buttons/green.png" \
					transparent="1" alphatest="on" />
				<widget source="key_red" render="Label" position="150,358" zPosition="2" size="148,30" \
					valign="center" halign="center" font="Regular;22" transparent="1" />
				<widget source="key_green" render="Label" position="410,358" zPosition="2" size="148,30" \
					valign="center" halign="center" font="Regular;22" transparent="1" />
			</screen>"""
	elif screenWidth and screenWidth == 1920:
		skin = """
			<screen position="center,center" size="1080,600">
				<widget source="list" render="Listbox" position="15,15" size="540,495" \
					scrollbarMode="showOnDemand" >
					<convert type="TemplatedMultiContent" >
					{
						"template": [MultiContentEntryText(pos=(15, 1), size=(510, 45), \
								font=0, flags=RT_HALIGN_LEFT, text=0)],
						"fonts": [gFont("Regular", 30)],
						"itemHeight": 45
					}
					</convert>
				</widget>
				<widget name="pic" position="672,15" size="290,162" alphatest="on" />
				<widget name="descr" position="570,181" size="495,339" halign="center" font="Regular;27" />
				<ePixmap position="231,526" size="210,60" pixmap="skin_default/buttons/red.png" \
					transparent="1" alphatest="on" />
				<ePixmap position="627,526" size="210,60" pixmap="skin_default/buttons/green.png" \
					transparent="1" alphatest="on" />
				<widget source="key_red" render="Label" position="225,535" zPosition="2" size="222,45" \
					valign="center" halign="center" font="Regular;33" transparent="1" />
				<widget source="key_green" render="Label" position="615,535" zPosition="2" size="222,45" \
					valign="center" halign="center" font="Regular;33" transparent="1" />
			</screen>"""
	else:
		skin = """
			<screen position="center,center" size="620,400">
				<widget source="list" render="Listbox" position="10,10" size="280,330" \
					scrollbarMode="showOnDemand" >
					<convert type="TemplatedMultiContent" >
					{
						"template": [MultiContentEntryText(pos=(10, 1), size=(260, 30), \
								font=0, flags=RT_HALIGN_LEFT, text=0)],
						"fonts": [gFont("Regular", 20)],
						"itemHeight": 30
					}
					</convert>
				</widget>
				<widget name="pic" position="310,10" size="290,162" alphatest="on" />
				<widget name="descr" position="300,175" size="320,164" halign="center" font="Regular;18" />
				<ePixmap position="104,351" size="140,40" pixmap="skin_default/buttons/red.png" \
					transparent="1" alphatest="on" />
				<ePixmap position="368,351" size="140,40" pixmap="skin_default/buttons/green.png" \
					transparent="1" alphatest="on" />
				<widget source="key_red" render="Label" position="100,358" zPosition="2" size="148,30" \
					valign="center" halign="center" font="Regular;22" transparent="1" />
				<widget source="key_green" render="Label" position="360,358" zPosition="2" size="148,30" \
					valign="center" halign="center" font="Regular;22" transparent="1" />
			</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_('MTG Play'))
		self.session = session
		self['key_red'] = StaticText(_('Exit'))
		self['key_green'] = StaticText(_('Ok'))
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'],
				{
					'cancel': self.close,
					'ok': self.Ok,
					'green': self.Ok,
					'red': self.close,
				})
		self['list'] = List([])
		self['list'].onSelectionChanged.append(self.SelectionChanged)
		self['pic'] = Pixmap()
		self['descr'] = Label()
		self.menulist = 0
		self.storedContent = {}
		self.pictures = {}
		self.picloads = {}
		self.curPic = None
		self.defPic = None
		self.sc = AVSwitch().getFramebufferScale()
		self.onLayoutFinish.append(self.LayoutFinish)
		self.onClose.append(self.cleanVariables)

	def cleanVariables(self):
		del self.storedContent
		del self.pictures
		del self.picloads

	def LayoutFinish(self):
		self.picSize = [self['pic'].instance.size().width(),
						self['pic'].instance.size().height()]
		content = [('tvplay.skaties.lv', None, 'tvplay.skaties.lv', ''),
					('gossip.no', None, 'gossip.no', ''),
					('juicyplay.dk', None, 'juicyplay.dk', ''),
					('juicyplay.se', None, 'juicyplay.se', ''),
					('play.novatv.bg', None, 'play.novatv.bg', ''),
					('play.tv3.lt', None, 'play.tv3.lt', ''),
					('tv10play.se', None, 'tv10play.se', ''),
					('tv3play.dk', None, 'tv3play.dk', ''),
					('tv3play.no', None, 'tv3play.no', ''),
					('tv3play.se', None, 'tv3play.se', ''),
					('tv3play.tv3.ee', None, 'tv3play.tv3.ee', ''),
					('tv6play.se', None, 'tv6play.se', ''),
					('tv8play.se', None, 'tv8play.se', ''),
					('viagame.com', None, 'viagame.com', '')]
		self.storedContent[0] = content
		self['list'].setList(content)
		image = resolveFilename(SCOPE_PLUGINS,
				'Extensions/MTGPlay/defpic.png')
		self.decodePic(image)

	def decodePic(self, image):
		self.picloads[image] = ePicLoad()
		self.picloads[image].PictureData.get().append(
				boundFunction(self.FinishDecode, image))
		self.picloads[image].setPara((
				self.picSize[0], self.picSize[1],
				self.sc[0], self.sc[1], False, 0, '#00000000'))
		self.picloads[image].startDecode(image)

	def FinishDecode(self, image, picInfo=None):
		ptr = self.picloads[image].getData()
		if ptr:
			pic = image.rsplit('/', 1)[1]
			self.pictures[pic] = ptr
			del self.picloads[image]
			if image[:4] == '/tmp':
				os.remove(image)
			else:
				self.defPic = pic
				self.setImage(pic)

	def setImage(self, image):
		if image and image != self.defPic:
			image = image.rsplit('/', 1)[1]
		if not image or image not in self.pictures:
			image = self.defPic
		if self.curPic != image and image in self.pictures:
			self.curPic = image
			self['pic'].instance.setPixmap(self.pictures[image])

	def SelectionChanged(self):
		current = self['list'].getCurrent()
		self['descr'].setText(current[3])
		self.setImage(current[1])

	def Ok(self):
		current = self['list'].getCurrent()
		if current:
			print '[MTG Play] Select:', current[2], current[0]
			if current[2] == 'back':
				self.menulist -= 1
				content = self.storedContent[self.menulist]
			else:
				self.menulist += 1
				if self.menulist == 4 and '&page=' not in str(current[2]):
					self.playVideo(current[0], self.getVideoStream(current[2]))
				else:
					if self.menulist == 1:
						content = self.listChannels(current[2])
					elif self.menulist == 2:
						content = self.listFormatsChannel(current[2])
					elif self.menulist == 3:
						content = self.listVideosFormat(current[2])
					elif self.menulist == 4:
						self.menulist = 3
						content = self.listVideosFormat(current[2])
					content.insert(0, (_('Return back...'), None, 'back', ''))
					self.storedContent[self.menulist] = content
			if self.menulist > 3:
				self.menulist = 3
			else:
				self['list'].setList(content)
				self['descr'].setText('')
				self.setImage(self.defPic)
				if self.menulist > 1:
					self.createPictures(content)

	def createPictures(self, content):
		for entry in content:
			if entry[1]:
				image = entry[1].rsplit('/', 1)[1]
				if image not in self.pictures:
					image = os.path.join('/tmp/', image)
					downloadPage(entry[1], image)\
							.addCallback(boundFunction(self.downloadFinished, image))\
							.addErrback(boundFunction(self.downloadFailed, image))

	def downloadFinished(self, image, result):
		self.decodePic(image)

	def downloadFailed(self, image, result):
		print '[MTG Play] Failed download:', image

	def listChannels(self, hostname):
		content = []
		next = 'channels?page=1'
		while next:
			channels, next = self.getChannels(next, hostname)
			content.extend(channels)
		return content

	def getChannels(self, channels, hostname):
		content = []
		next = None
		formats = self.callApi(channels)
		try:
			for x in formats['_embedded']['channels']:
				if x['hostname'] == hostname:
					content.append((str(x['name']), None, x['id'], ''))
		except:
			pass
		try:
			if 'next' in formats['_links']:
				next = str(formats['_links']['next']['href']).rsplit('/v3/', 1)[1]
		except:
			next = None
		return content, next

	def listFormatsChannel(self, channelId):
		content = []
		next = 'formats?channel=%i&page=1' % channelId
		count = 0
		while next and count < 6:  # More than 6 pages are too long
			count += 1
			videos, next = self.callFormatsChannel(next)
			content.extend(videos)
		content.sort(key=lambda x: x[0])
		return content

	def callFormatsChannel(self, videos):
		content = []
		next = None
		formats = self.callApi(videos)
		try:
			for x in formats['_embedded']['formats']:
				content.append((
						str(x['title']).encode('utf-8'),
						str(x['_links']['image']['href']).replace('{size}', '290x162'),
						x['id'], ''))
		except:
			pass
		try:
			if 'next' in formats['_links']:
				next = str(formats['_links']['next']['href']).rsplit('/v3/', 1)[1]
		except:
			next = None
		return content, next

	def listVideosFormat(self, channelId):
		content = []
		if '&page=' in str(channelId):
			next = channelId
		else:
			next = 'videos?format=%i&page=1' % channelId
		count = 0
		while next and count < 2:  # For faster work using only 2 pages
			count += 1
			videos, next = self.callVideosFormat(next)
			content.extend(videos)
		if next:
			content.append((_('Next videos...'), None, next, ''))
		return content

	def callVideosFormat(self, videos):
		content = []
		next = None
		formats = self.callApi(videos+'&order=-airdate')
		try:
			for x in formats['_embedded']['videos']:
				content.append((
						str(x['title']).encode('utf-8'),
						str(x['_links']['image']['href']).replace('{size}', '290x162'),
						x['id'],
						str(x['description']).encode('utf-8')))
		except:
			pass
		try:
			if 'next' in formats['_links']:
				next = str(formats['_links']['next']['href']).rsplit('/v3/', 1)[1]
		except:
			next = None
		return content, next

	def getVideoStream(self, channelId):
		formats = self.callApi('videos/stream/%i' % channelId)
		try:
			if formats['streams']['hls']:
				return str(formats['streams']['hls'])
			elif formats['streams']['medium']:
				return str(formats['streams']['medium'])\
						.replace('cache/', 'cache//')\
						.replace('.flv', '.mp4')\
						.replace('/flv:', '/mp4:')
		except:
			pass
		return ''

	def callApi(self, urlType):
		url = 'http://playapi.mtgx.tv/v3/%s' % urlType
		try:
			response = urlopen(Request(url=url, headers={
						'user-agent': 'MTG Play/1.0.3 CFNetwork/548.0.4 Darwin/11.0.0'
					}))
			return loads(response.read())
		except Exception as ex:
			print '[MTG Play] Error', ex
			return []

	def playVideo(self, title, stream):
		if stream:
			ref = eServiceReference(4097, 0, stream)
			ref.setName(title)
			print '[MTG Play] Play:', title
			self.session.open(MTGPlayer, ref)
		else:
			print '[MTG Play] Not found stream to play', title
			self.session.open(MessageBox,
					_('Can not play: %s\nPerhaps content is not provided for this region.')
					% title, MessageBox.TYPE_ERROR)
