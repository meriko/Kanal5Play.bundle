TITLE  = 'Kanal 5 Play'
ART    = 'art-default.jpg'
PREFIX = '/video/kanal5'

BASE_URL        = 'http://www.kanal%splay.se'
API_URL         = BASE_URL + '/api'
START_URL       = API_URL + '/getMobileStartContent?format=FLASH'
PROGRAMS_URL    = API_URL + '/getMobileFindProgramsContent'
LIVE_EVENTS_URL = API_URL + '/live/getCurrentEvents'

GetChannelThumb    = SharedCodeService.kanal5lib.GetChannelThumb
GetShows           = SharedCodeService.kanal5lib.GetShows
GetEpisodes        = SharedCodeService.kanal5lib.GetEpisodes
ShowSeasons        = SharedCodeService.kanal5lib.ShowSeasons
ProgramShowMenu    = SharedCodeService.kanal5lib.ProgramShowMenu
GetNoShowContainer = SharedCodeService.kanal5lib.GetNoShowContainer
CHANNEL_LIST       = SharedCodeService.kanal5lib.CHANNEL_LIST

####################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    HTTP.CacheTime      = CACHE_1HOUR 

####################################################################################################
@handler(PREFIX, TITLE, art = ART)
def MainMenu():
    oc = ObjectContainer()

    for channelNo in CHANNEL_LIST:
        page = HTML.ElementFromURL(BASE_URL % channelNo)
        
        try:
            description = unicode(page.xpath('//meta[@property="og:description"]/@content')[0])
        except:
            description = None

        thumb = GetChannelThumb(channelNo)
            
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
        oc = GetNoShowContainer(oc)
        oc.message = unicode('Inga Live events tillgängliga för tillfället') 
       
    return oc 

####################################################################################################
@route(PREFIX + '/popularshows')
def PopularShows(channelNo):
    oc   = ObjectContainer(title1 = unicode("Populära program"))
    data = JSON.ObjectFromURL(START_URL % channelNo)

    oc = GetShows(oc, data['hottestPrograms'], channelNo)

    if len(oc) < 1:
        oc = GetNoShowContainer(oc)
       
    return oc 

####################################################################################################
@route(PREFIX + '/latestvideos')
def LatestVideos(channelNo):
    oc   = ObjectContainer(title1 = unicode("Senast tillagt"))
    data = JSON.ObjectFromURL(START_URL % channelNo)

    oc = GetEpisodes(oc, data['newEpisodeVideos'], channelNo)
    
    if len(oc) < 1:
        oc = GetNoShowContainer(oc)
       
    return oc 

####################################################################################################
@route(PREFIX + '/shows')
def AllShows(channelNo):

    oc   = ObjectContainer(title1 = "Kanal" + channelNo)
    data = JSON.ObjectFromURL(PROGRAMS_URL % channelNo)

    oc = GetShows(oc, data['programsWithTemperatures'], channelNo)

    if len(oc) < 1:
        oc = GetNoShowContainer(oc)
        
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
