TITLE  = 'Kanal 5 Play'
ART    = 'art-default.jpg'
PREFIX = '/video/kanal5'

BASE_URL       = 'http://www.kanal%splay.se'
API_URL        = BASE_URL + '/api'
PROGRAMS_URL   = API_URL + '/listPrograms'
VIDEO_LIST_URL = API_URL + '/listVideos?programId=%s&format=FLASH'
VIDEO_URL      = BASE_URL + '/play/program/%s/video/%s'

NO_PROGRAMS_FOUND_HEADER  = "Inga program funna"
NO_PROGRAMS_FOUND_MESSAGE = unicode("Kunde ej hitta några program.")

####################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    HTTP.CacheTime      = CACHE_1HOUR 

####################################################################################################
@handler(PREFIX, TITLE, art = ART)
def MainMenu():
    oc = ObjectContainer()

    for channelNo in ["5", "9"]:
        page = HTML.ElementFromURL(BASE_URL % channelNo)
        
        try:
            description = unicode(page.xpath('//meta[@property="og:description"]/@content')[0])
        except:
            description = None
        
        if channelNo == "5":
            thumb = R('icon-kanal5.png')
        else:
            thumb = R('icon-kanal9.png')
            
        title = "Kanal" + channelNo
    
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Shows, 
                        channelNo = channelNo,
                    ),
                title = title,
                summary = description,
                thumb = thumb
            )
        )
 
    return oc

####################################################################################################
@route(PREFIX + '/shows')
def Shows(channelNo):

    oc    = ObjectContainer(title1 = "Kanal" + channelNo)
    shows = JSON.ObjectFromURL(PROGRAMS_URL % channelNo)

    for show in shows:
        if not show['premium'] and (int(show['playableEpisodesCount']) > 0 or int(show['playableVideosCount']) > 0): 
            title   = unicode(show['name'])
            summary = unicode(show['description'])
            show_id = show['id']
        
            try:
                thumb = show['photoWithLogoUrl']
            except:
                try:
                    thumb = show['photoUrl']
                except:
                    thumb = None

            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            ProgramShowChoiceMenu,
                            title = title,
                            channelNo = channelNo,
                            show_id = show_id,
                            show_title = title,
                            hasEpisodes = int(show['playableEpisodesCount']) > 0,
                            hasClips = int(show['playableVideosCount']) > 0,
                            thumb = thumb,
                            summary = summary
                        ),
                    title = title,
                    summary = summary,
                    thumb = thumb
                )
            )

    if len(oc) < 1:
        oc.header  = NO_PROGRAMS_FOUND_HEADER
        oc.message = NO_PROGRAMS_FOUND_MESSAGE
        
    return oc

####################################################################################################
@route(PREFIX + '/programshowchoicemenu', hasEpisodes = bool, hasClips = bool)
def ProgramShowChoiceMenu(title, channelNo, show_id, show_title, hasEpisodes, hasClips, thumb, summary):
    title   = unicode(title)
    summary = unicode(summary) 

    oc = ObjectContainer(title1 = title)
    
    if hasEpisodes and hasClips:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        ShowSeasons,
                        title = title, 
                        channelNo = channelNo,
                        show_id = show_id,
                        show_title = show_title,
                        summary = summary,
                        thumb = thumb
                    ),
                title = "Hela program",
                thumb = thumb,
                summary = summary
            )
        )
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        ProgramShowMenu,
                        channelNo = channelNo,
                        show_id = show_id,
                        show_title = show_title,
                        episodeReq = False,
                    ),
                title = "Klipp",
                thumb = thumb,
                summary = summary
            )
        )
        
    elif hasEpisodes:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        ShowSeasons,
                        title = title, 
                        channelNo = channelNo,
                        show_id = show_id,
                        show_title = show_title
                    ),
                title = "Hela program",
                thumb = thumb,
                summary = summary
            )
        )
        
    elif hasClips:
        return ProgramShowMenu(
                    channelNo = channelNo,
                    show_id = show_id,
                    show_title = show_title,
                    episodeReq = False,
        )
                               
    return oc


####################################################################################################
@route(PREFIX + '/showseasons')
def ShowSeasons(title, channelNo, show_id, show_title, summary, thumb):
    title   = unicode(title)
    summary = unicode(summary)
    
    oc    = ObjectContainer(title1 = title)
    shows = JSON.ObjectFromURL(PROGRAMS_URL % channelNo)

    for show in shows:
        if str(show['id']) == show_id:
            for season in show['seasonNumbersWithContent']:
                oc.add(
                    DirectoryObject(
                        key = 
                            Callback(
                                ProgramShowMenu,
                                channelNo = channelNo,
                                show_id = show_id,
                                show_title = title,
                                episodeReq = True,
                                seasonNo = season
                            ),
                        title = unicode("Säsong " + str(season)),
                        summary = summary,
                        thumb = thumb
                    )
                )
    
    oc.objects.sort(key = lambda obj: obj.title, reverse = True)
    
    return oc 

####################################################################################################
@route(PREFIX + '/programshowmenu', episodeReq = bool, seasonNo = int)
def ProgramShowMenu(channelNo, show_id, show_title, episodeReq, seasonNo = None):
    show_title = unicode(show_title)

    oc       = ObjectContainer(title1 = show_title)
    data_url = VIDEO_LIST_URL % (channelNo, show_id)
    results  = JSON.ObjectFromURL(data_url)

    for video in results:
        if (video['type'] != 'TVTV_EPISODE' and episodeReq) or (video['type'] == 'TVTV_EPISODE' and not episodeReq):
            continue

        title   = unicode(video['title'])
        summary = unicode(video['description'])
        
        try: 
            duration = int(video['length'])
        except: 
            duration = None
        
        if episodeReq:
            episode = int(video['episodeNumber'])
            season  = int(video['seasonNumber'])
            
            if not season == seasonNo:
                continue
        else:
            episode = None
            season  = None
            
        try:
            airdate = Datetime.FromTimestamp(int(video['shownOnTvDateTimestamp'])/1000)
        except: 
            airdate = None
        
        thumb    = video['posterUrl']
        video_id = video['id']
        url      = VIDEO_URL % (channelNo, show_id, video_id)

        oc.add(
            EpisodeObject(
                url = url,
                title = title,
                summary = summary,
                show = show_title,
                duration = duration, 
                index = episode,
                season = season,
                originally_available_at = airdate,
                thumb = thumb
            )
        )



    if len(oc) < 1:
        oc.header  = NO_PROGRAMS_FOUND_HEADER
        oc.message = NO_PROGRAMS_FOUND_MESSAGE
        
    elif episodeReq:
        oc.objects.sort(key = lambda obj: obj.index, reverse = True)
          
    return oc


