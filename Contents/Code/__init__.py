TITLE  = 'Kanal 5 Play'
ART    = 'art-default.jpg'
PREFIX = '/video/kanal5'

BASE_URL        = 'http://www.kanal%splay.se'
API_URL         = BASE_URL + '/api'
START_URL       = API_URL + '/getMobileStartContent?format=FLASH'
PROGRAMS_URL    = API_URL + '/getMobileFindProgramsContent'
VIDEO_LIST_URL  = API_URL + '/getMobileSeasonContent?programId=%s&seasonNumber=%s&format=FLASH'
VIDEO_URL       = BASE_URL + '/play/program/%s/video/%s'
LIVE_EVENTS_URL = API_URL + '/live/getCurrentEvents'

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

    for channelNo in ["5", "9", "11"]:
        page = HTML.ElementFromURL(BASE_URL % channelNo)
        
        try:
            description = unicode(page.xpath('//meta[@property="og:description"]/@content')[0])
        except:
            description = None
        
        if channelNo == "5":
            thumb = R('icon-kanal5.png')
        elif channelNo == "9":
            thumb = R('icon-kanal9.png')
        else:
            thumb = R('icon-kanal11.png')
            
        title = "Kanal" + channelNo
    
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        MainChannelMenu, 
                        channelNo = channelNo,
                        thumb = thumb
                    ),
                title = title,
                summary = description,
                thumb = thumb
            )
        )
        
    oc.add(
        SearchDirectoryObject(
            identifier = 'com.plexapp.plugins.kanal5play',
            title = unicode('Sök'),
            summary = unicode('Sök efter program och klipp på Kanal 5/9/11 Play'),
            prompt = unicode('Sök på Kanal 5/9/11 Play'),
            thumb = R('ikon-sok.png')
        )
    ) 
    
    return oc

####################################################################################################
@route(PREFIX + '/mainchannelmenu')
def MainChannelMenu(channelNo, thumb):
    oc = ObjectContainer(title1 = "Kanal" + channelNo)
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    PopularShows,
                    channelNo = channelNo
                ),
            title = unicode("Populära program"),
            thumb = thumb
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    LatestVideos,
                    channelNo = channelNo
                ),
            title = unicode("Senast tillagt"),
            thumb = thumb
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    AllShows,
                    channelNo = channelNo
                ),
            title = unicode("Alla program"),
            thumb = thumb
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Live,
                    channelNo = channelNo
                ),
            title = unicode("Live"),
            thumb = thumb
        )
    )
    
    return oc

####################################################################################################
@route(PREFIX + '/live')
def Live(channelNo):
    oc   = ObjectContainer(title2 = "Live")
    data = JSON.ObjectFromURL(LIVE_EVENTS_URL % channelNo, cacheTime = 0)
    
    for event in data['liveEvents']:
        if 'liveStreamingParams' in event:
            oc.add(
                CreateVideoClipObject(
                    url = event['liveStreamingParams']['streams'][0]['source'],
                    title = unicode(event['title'].strip()), 
                    thumb = event['photoUrl'],
                    desc = unicode(event['description'].strip())
                )
            )

    if len(oc) < 1:
        oc.header  = NO_PROGRAMS_FOUND_HEADER
        oc.message = unicode('Inga Live events tillgängliga för tillfället') 
       
    return oc 

####################################################################################################
@route(PREFIX + '/popularshows')
def PopularShows(channelNo):
    oc   = ObjectContainer(title1 = unicode("Populära program"))
    data = JSON.ObjectFromURL(START_URL % channelNo)
    
    for show in data['hottestPrograms']:
        if not show['premium'] and int(show['playableEpisodesCount']) > 0: 
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
                            ShowSeasons,
                            title = title, 
                            channelNo = channelNo,
                            show_id = show_id,
                            show_title = title,
                            summary = summary,
                            thumb = thumb
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
@route(PREFIX + '/latestvideos')
def LatestVideos(channelNo):
    oc   = ObjectContainer(title1 = unicode("Senast tillagt"))
    data = JSON.ObjectFromURL(START_URL % channelNo)
    
    for video in data['newEpisodeVideos']:
        if not video['premium'] and not video['widevineRequired']: 
            title   = unicode(video['title'])
            summary = unicode(video['description'])
            show    = unicode(video['program']['name'])
        
            try: 
                duration = int(video['length'])
                if not duration > 0:
                    continue
            except:
                continue

            episode = int(video['episodeNumber'])
            season  = int(video['seasonNumber'])
            
            try:
                airdate = Datetime.FromTimestamp(int(video['shownOnTvDateTimestamp'])/1000)
            except: 
                airdate = None
        
            thumb    = video['posterUrl']
            video_id = video['id']
            show_id  = video['program']['id']
            url      = VIDEO_URL % (channelNo, show_id, video_id)

            oc.add(
                EpisodeObject(
                    url = url,
                    title = title,
                    summary = summary,
                    show = show,
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
       
    return oc 

####################################################################################################
@route(PREFIX + '/shows')
def AllShows(channelNo):

    oc   = ObjectContainer(title1 = "Kanal" + channelNo)
    data = JSON.ObjectFromURL(PROGRAMS_URL % channelNo)

    for program in data['programsWithTemperatures']:
        show = program['program']
        
        if not show['premium'] and int(show['playableEpisodesCount']) > 0: 
            title   = unicode(show['name'])
            summary = unicode(show['description'])
            show_id = str(show['id'])
        
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
                            ShowSeasons,
                            title = title, 
                            channelNo = channelNo,
                            show_id = show_id,
                            show_title = title,
                            summary = summary,
                            thumb = thumb
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
@route(PREFIX + '/showseasons')
def ShowSeasons(title, channelNo, show_id, show_title, summary, thumb):
    title   = unicode(title)
    summary = unicode(summary)
    
    oc   = ObjectContainer(title1 = title)
    data = JSON.ObjectFromURL(PROGRAMS_URL % channelNo)

    for program in data['programsWithTemperatures']:
        show = program['program']
        
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
                                seasonNo = season
                            ),
                        title = unicode("Säsong " + str(season)),
                        summary = summary,
                        thumb = thumb
                    )
                )
    
    oc.objects.sort(key = lambda obj: obj.title, reverse = True)
    
    if len(oc) == 1:
        return ProgramShowMenu(
            channelNo = channelNo,
            show_id = show_id,
            show_title = title,
            seasonNo = season
        )
    
    return oc 

####################################################################################################
@route(PREFIX + '/programshowmenu', seasonNo = int)
def ProgramShowMenu(channelNo, show_id, show_title, seasonNo):
    show_title = unicode(show_title)

    oc       = ObjectContainer(title2 = show_title)
    data_url = VIDEO_LIST_URL % (channelNo, show_id, seasonNo)
    results  = JSON.ObjectFromURL(data_url)
    
    widevine = False

    for video in results["episodes"]:            
        if video['widevineRequired']:
            widevine = True
            continue
            
        title   = unicode(video['title'])
        summary = unicode(video['description'])
        
        try:
            duration = int(video['length'])
            if not duration > 0:
                continue
        except:
            continue

        episode = int(video['episodeNumber'])
        season  = int(video['seasonNumber'])
            
        if not season == seasonNo:
            continue
            
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

        if widevine:
            oc.message = oc.message + unicode('\r\nProgrammet kan ej visas pga rättighetsskäl\r\n')     
        
    else:
        oc.objects.sort(key = lambda obj: obj.index, reverse = True)
          
    return oc

####################################################################################################
@route(PREFIX + '/createvideoclipobject')
def CreateVideoClipObject(url, title, thumb, desc, include_container=False):

  videoclip_obj = VideoClipObject(
      key = Callback(CreateVideoClipObject, url=url, title=title, thumb=thumb, desc=desc, include_container=True),
      rating_key = url,
      title = title,
      thumb = thumb,
      summary = desc,
      items = [
        MediaObject(
          parts = [
            PartObject(key=HTTPLiveStreamURL(url))
          ],
          video_resolution = 'sd',
          audio_channels = 2,
          optimized_for_streaming = True
        )
      ]
  )

  if include_container:
      return ObjectContainer(objects=[videoclip_obj])
  else:
      return videoclip_obj
