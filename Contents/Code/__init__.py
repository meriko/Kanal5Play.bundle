NAME = L('Title')
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_5_URL     = 'http://www.kanal5play.se'
BASE_9_URL     = 'http://www.kanal9play.se'
API_EXT        = '/api'
PROGRAMS_5_URL = BASE_5_URL + API_EXT + '/listPrograms'
PROGRAMS_9_URL = BASE_9_URL + API_EXT + '/listPrograms'
VIDEO_URL_EXT  = '/play/program/%s/video/%s'

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR

@handler('/video/kanal5play', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()
	HTTP.PreCache(PROGRAMS_5_URL)
	HTTP.PreCache(PROGRAMS_9_URL)

        oc = AddShows(oc, JSON.ObjectFromURL(PROGRAMS_5_URL), BASE_5_URL)
        ## Seems some shows exists in both Kanal5 and Kanal9 - so check for duplicates.
        oc = AddShows(oc, JSON.ObjectFromURL(PROGRAMS_9_URL), BASE_9_URL, True)

	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_video'))
	else:
                oc.objects.sort(key=lambda obj: obj.title)
                oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.kanal5play', title=L('Search'), summary=L('Search_summary'), prompt=L('Searchsubtitle'), thumb=R('ikon-sok.png')))
                return oc

def AddShows(oc, shows, base_url, check_duplicates=False):
	for show in shows:
                if int(show['playableEpisodesCount']) > 0:
                        if check_duplicates:
                                duplicate = False
                                for s in oc.objects:
                                        if show['name'] == s.title:
                                                duplicate = True
                                                continue
                                if duplicate:
                                        continue
                        title   = show['name']
                        summary = show['description']
                        show_id = show['id']
                        thumb   = show['photoWithLogoUrl']
                        oc.add(DirectoryObject(key=Callback(ProgramShowMenu, show_id=show_id, show_title=title, thumb=show['photoWithLogoUrl'],base_url=base_url), title=title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

        return oc



####################################################################################################
@route('/video/kanal5play/programshowmenu')
def ProgramShowMenu(show_id, show_title, thumb, base_url):

	oc = ObjectContainer(title2=unicode(show_title))
	data_url = base_url + API_EXT + ("/getMobileProgramContent?programId=%s" % show_id)
	results = JSON.ObjectFromURL(data_url, cacheTime=0)
        for season in results['program']['seasonNumbersWithContent']:
                season_url = base_url + API_EXT + ("/getMobileSeasonContent?programId=%s&seasonNumber=%s&format=FLASH" % (show_id, season))
                title = unicode(show_title + " - " + ("SÃ¤song%s" % season))
                if len(results['program']['seasonNumbersWithContent']) > 1:
                        oc.add(CreateDirObject(unicode("SÃ¤song %s" % season),
                                               Callback(Episodes,
                                                        title        = title,
                                                        show_id      = show_id,
                                                        show_title   = show_title,
                                                        base_url     = base_url,
                                                        season_url   = season_url
                                                        ),
                                               thumb
                                               )
                               )
                else:
                        return Episodes(title, show_id, show_title, base_url, season_url)

	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_Programs'))
	else:
		return oc
####################################################################################################
@route('/video/kanal5play/Episodes')
def Episodes(title, show_id, show_title, base_url, season_url):

	oc          = ObjectContainer(title2=unicode(title))
	results     = JSON.ObjectFromURL(season_url, cacheTime=0)
        clips_found = False

	for video in results['episodes']:
		if video['type'] != 'TVTV_EPISODE' and video['type'] != 'WEB_EPISODE':
                        clips_found = True
			continue
		title = video['episodeText'] + " - " + video['title']
		summary = video['description']
		try: duration = int(video['length'])
		except: duration = None
		episode = int(video['episodeNumber'])
		season = int(video['seasonNumber'])
		try: airdate = Datetime.FromTimestamp(int(video['shownOnTvDateTimestamp'])/1000)
		except: airdate = None
		thumb = video['posterUrl']
		video_id = video['id']
		url = base_url + (VIDEO_URL_EXT % (show_id, video_id))

		oc.add(EpisodeObject(url=url, title=title, summary=summary, show=show_title, duration=duration, index=episode, season=season, originally_available_at=airdate, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

        sortOnAirData(oc)

        if clips_found:
                new_oc = ObjectContainer(title2=unicode(title))
                new_oc.add(CreateDirObject("Klipp",
                                           Callback(Clips,
                                                    title        = unicode(show_title + " - " + ("SÃ¤song%s" % season)),
                                                    show_id      = show_id,
                                                    show_title   = show_title,
                                                    base_url     = base_url,
                                                    season_url   = season_url
                                                    )
                                           ))
                for ep in oc.objects:
                        new_oc.add(ep)
                return new_oc
        else:
                return oc

####################################################################################################
@route('/video/kanal5play/Clips')
def Clips(title, show_id, show_title, base_url, season_url):

	oc      = ObjectContainer(title2=unicode(title))
	results = JSON.ObjectFromURL(season_url, cacheTime=0)

	for video in results['episodes']:
		if video['type'] == 'TVTV_EPISODE' or video['type'] == 'WEB_EPISODE':
			continue

		title = video['episodeText'] + " - " + video['title']
		summary = video['description']
		try: duration = int(video['length'])
		except: duration = None
		try: airdate = Datetime.FromTimestamp(int(video['shownOnTvDateTimestamp'])/1000)
		except: airdate = None
		season = int(video['seasonNumber'])
		thumb = video['posterUrl']
		video_id = video['id']
		url = base_url + (VIDEO_URL_EXT % (show_id, video_id))

		oc.add(EpisodeObject(url=url, title=title, summary=summary, duration=duration, season=season, originally_available_at=airdate, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_Programs'))
	else:
                sortOnAirData(oc)
		return oc

def CreateDirObject(name, key, thumb=R(ICON), summary=None):
        myDir         = DirectoryObject()
        myDir.title   = name
        myDir.key     = key
        myDir.summary = summary
        myDir.thumb   = thumb
        myDir.art     = R(ART)
        return myDir

def sortOnAirData(Objects):
    for obj in Objects.objects:
        if obj.originally_available_at == None:
            Log("JTDEBUG - air date missing for %s" % obj.title)
            return Objects.objects.reverse()
    return Objects.objects.sort(key=lambda obj: (obj.originally_available_at,obj.title))
