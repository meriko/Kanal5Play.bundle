NAME = L('Title')

ART           = 'art-default.jpg'
ICON          = 'icon-default.png'

#URLs to xml/player
BASE_URL	= 'http://www.kanal5play.se'
API_URL		= BASE_URL + '/api'
PROGRAMS_URL	= API_URL + '/listPrograms'
VIDEOL_LIST_URL	= API_URL + '/listVideos?programId=%s&format=FLASH'

VIDEO_URL	= BASE_URL + '/play/program/%s/video/%s'

SEARCH_API_URL = "http://www.kanal5play.se/api/videos/search/%s"

####################################################################################################

def Start():

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)

####################################################################################################
@handler('/video/kanal5play', NAME, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(ShowSubMenu, section_type="Program"), title=L('Shows'), summary=L('Program_summary'), thumb=R('ikon-tvprogram.png')))
    oc.add(DirectoryObject(key=Callback(ShowSubMenu, section_type="Klipp"), title=L('Clip'), summary=L('Klipp_summary'), thumb=R('ikon-klipp.png')))
    oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.kanal5play', title=L('Search'), summary=L('Search_summary'), prompt=L('Searchsubtitle'), thumb=R('ikon-sok.png')))
    
    return oc

####################################################################################################
@route('video/kanal5play/showsubmenu')
def ShowSubMenu(section_type):
        oc = ObjectContainer(title2=section_type)
        
        shows = JOSN.ObjectFromURL(PROGRAMS_URL)

        for show in shows:
                title = show['name']
                summary = show['description']
                show_id = show['id']
                thumb = show['photoWithLogoUrl']
                
                if section_type == "Program":
                        if int(show['playableEpisodesCount']) > 0:
                                oc.add(DirectoryObject(key=Callback(ProgramShowMenu, show_id=show_id, show_title=title), title=title, summary=summary, thumb=Resource.ContentsofURLWithFallback(url=thumb, fallback=ICON)))
                else:
                        if int(show['playableVideosCount']) > 0:
                                oc.add(DirectoryObject(key=Callback(KlippShowMenu, show_id=show_id, show_title=title), title=title, summary=summary, thumb=Resource.ContentsofURLWithFallback(url=thumb, fallback=ICON)))
                                
        if len(oc) == 0:
                return ObjectContainer(header=L('No_Results'), message=L('No_video'))
        else:
                return oc

####################################################################################################
@route('/video/kanal5play/programshowmenu')
def ProgramShowMenu(show_id, show_title):
	oc = ObjectContainer(title2=show_title)
	
	Log.Debug("Program Show Sektion")
	data_url = VIDEO_LIST_URL % show_id
	result = JSON.ObjectFromURL(data_url, cacheTime=0)

	for video in result["items"]:
		if video['type'] != 'TVTV_EPISODE':
			continue
		
		title = video['title']
		summary = video['description']
		duration = int(video['length'])
		episode = int(video['episodeNumber'])
		season = int(video['seasonNumber'])
		airdate = Datetime.FromTimestamp(video['shownOnTvDateTimestamp'])
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
	oc = ObjectContainer(title2=show_title)
	
	Log.Debug("Klipp Show Sektion")
	data_url = VIDEO_LIST_URL % show_id
	result = JSON.ObjectFromURL(data_url, cacheTime=0)

	for video in result["items"]:
		if video['type'] == 'TVTV_EPISODE':
			continue
		
		title = video['title']
		summary = video['description']
		duration = int(video['length'])
		airdate = Datetime.FromTimestamp(video['shownOnTvDateTimestamp'])
		thumb = video['posterUrl']
		video_id = video['id']
		url = VIDEO_URL % (show_id, video_id)
		
		oc.add(EpisodeObject(url=url, title=title, summary=summary, duration=duration, originally_available_at=airdate, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
		
	if len(oc) == 0:
		return ObjectContainer(header=L('No_Results'), message=L('No_Programs'))
	else:
		return oc

####################################################################################################

def SearchResults(sender,query='the',section_type="Search"):
	dir = MediaContainer(title2=L(section_type), viewGroup="InfoList")
	
	data_url = SEARCH_API_URL % String.Quote(query, usePlus=False)

	Log(data_url)

	result = JSON.ObjectFromURL(data_url, cacheTime=0)

	for program in result:
		name = ""
		subtitle = ""
		thumb=R(ICON)
		summary = ""
		url = ""
		duration = ""
		title = ""
		
		try:
			title = program["programName"] + ": " + program["name"]
		except:
			Log("Failed to load name")
		

		try:
			subtitle = subtitle + L('Season') + str(program["season"]) + " "
		except:
			Log("Failed to load season")
		
		try:
			subtitle = subtitle + L('Episode') + str(program["episode"])
		except:
			Log("Failed to load episode")
		
		try:
			thumb = program["videoStillURL"]
		except:
			Log("Failed to load thumb")
		try:
			summary = program["shortDescription"]
		except:
			Log("Failed to load summary")
		
		try:
			url = program["referenceId"]
		except:
			Log("Failed to load url")
			
		try:	
			duration = program["length"]
		except:
			Log("Failed to load duration")
		
		dir.Append(Function(WebVideoItem(PlayVideo, title=title, duration=duration, subtitle=subtitle, summary=summary, thumb=thumb), url=url, kind=section_type))		
	
	if len(dir) == 0:
		return MessageContainer(L('No_Results'),L('No_video'))
	else:
		return dir
    