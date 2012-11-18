NAME = L('Title')
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.kanal5play.se'
API_URL = BASE_URL + '/api'
PROGRAMS_URL = API_URL + '/listPrograms'
VIDEO_LIST_URL = API_URL + '/listVideos?programId=%s&format=FLASH'
VIDEO_URL = BASE_URL + '/play/program/%s/video/%s'

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/kanal5play', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()
	HTTP.PreCache(PROGRAMS_URL)

	oc.add(DirectoryObject(key=Callback(ShowSubMenu, section_type="Program"), title=L('Shows'), summary=L('Program_summary'), thumb=R('ikon-tvprogram.png')))
	oc.add(DirectoryObject(key=Callback(ShowSubMenu, section_type="Klipp"), title=L('Clip'), summary=L('Klipp_summary'), thumb=R('ikon-klipp.png')))
	oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.kanal5play', title=L('Search'), summary=L('Search_summary'), prompt=L('Searchsubtitle'), thumb=R('ikon-sok.png')))

	return oc

####################################################################################################
@route('video/kanal5play/showsubmenu')
def ShowSubMenu(section_type):

	oc = ObjectContainer(title2=section_type)
	shows = JSON.ObjectFromURL(PROGRAMS_URL)

	for show in shows:
		title = show['name']
		summary = show['description']
		show_id = show['id']
		thumb = show['photoWithLogoUrl']

		if section_type == "Program":
			if int(show['playableEpisodesCount']) > 0:
				oc.add(DirectoryObject(key=Callback(ProgramShowMenu, show_id=show_id, show_title=title), title=title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
			else:
				if int(show['playableVideosCount']) > 0:
					oc.add(DirectoryObject(key=Callback(KlippShowMenu, show_id=show_id, show_title=title), title=title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_video'))
	else:
		return oc

####################################################################################################
@route('/video/kanal5play/programshowmenu')
def ProgramShowMenu(show_id, show_title):

	oc = ObjectContainer(title2=unicode(show_title))
	data_url = VIDEO_LIST_URL % show_id
	results = JSON.ObjectFromURL(data_url, cacheTime=0)

	for video in results:
		if video['type'] != 'TVTV_EPISODE':
			continue

		title = video['title']
		summary = video['description']
		try: duration = int(video['length'])
		except: duration = None
		episode = int(video['episodeNumber'])
		season = int(video['seasonNumber'])
		try: airdate = Datetime.FromTimestamp(int(video['shownOnTvDateTimestamp'])/1000)
		except: airdate = None
		thumb = video['posterUrl']
		video_id = video['id']
		url = VIDEO_URL % (show_id, video_id)

		oc.add(EpisodeObject(url=url, title=title, summary=summary, show=show_title, duration=duration, index=episode, season=season, originally_available_at=airdate, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_Programs'))
	else:
		return oc

####################################################################################################
@route('/video/kanal5play/klippshowmenu')
def KlippShowMenu(show_id, show_title):

	oc = ObjectContainer(title2=unicode(show_title))
	data_url = VIDEO_LIST_URL % show_id
	results = JSON.ObjectFromURL(data_url, cacheTime=0)

	for video in results:
		if video['type'] == 'TVTV_EPISODE':
			continue

		title = video['title']
		summary = video['description']
		try: duration = int(video['length'])
		except: duration = None
		try: airdate = Datetime.FromTimestamp(int(video['shownOnTvDateTimestamp'])/1000)
		except: airdate = None
		thumb = video['posterUrl']
		video_id = video['id']
		url = VIDEO_URL % (show_id, video_id)

		oc.add(EpisodeObject(url=url, title=title, summary=summary, duration=duration, originally_available_at=airdate, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_Programs'))
	else:
		return oc
