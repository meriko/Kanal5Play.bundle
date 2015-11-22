TITLE  = 'Dplay'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'
PREFIX = '/video/dplay'

API_BASE_URL = 'http://www.dplay.se/api/v2/content/device/%s'
IMAGE_BASE_URL = 'http://a5.res.cloudinary.com/dumrsasw1/image/upload/%s'

MAX_PAGES_TO_SEARCH = 10
MOST_POPULAR_ITEMS = 10
MOST_RECENT_ITEMS = 10
API_ITEM_LIMIT = 10

URL_TEMPLATE = 'http://www.dplay.se/?p=%s'

PREMIUM_ID = 42

####################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    DirectoryObject.art = R(ART)
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User_Agent'] = 'play/3.0.0 (iPad; iOS 9.0.2; Scale/1.00)'

####################################################################################################
@handler(PREFIX, TITLE, art = ART)
def MainMenu():
    oc = ObjectContainer()
    
    title = unicode("Senaste")
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    MostRecent,
                    title = title
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    title = unicode("Mest populära programmen")  
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    MostPopular,
                    title = title
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    title = unicode("Rekommenderade program")  
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Recommended,
                    title = title
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    title = unicode("Alla program")  
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    AllShows,
                    title = title
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    title = unicode("Sök")
    oc.add(
        InputDirectoryObject(
            key = Callback(Search),
            title = title,
            prompt = title,
            thumb = R('search.png'),
            art = R(ART)
        )
    )
    
    return oc

####################################################################################################
# NOTE! Can't have a route on this one since Samsung can't handle it!
def Search(query):

    oc = ObjectContainer(title2 = 'Resultat')
    
    json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/search?appVersion=3.0.0&embed=videos,shows,top_results&platform=IPHONE&platformVersion=9.0.2&query=%s&realm=DPLAYSE&site=SE' % String.Quote(query))
    
    if json_data['data']['videos']:
        for item in json_data['data']['videos']:
            episode_object = CreateEpisodeObject(item)
            
            if episode_object:
                oc.add(episode_object)
    
    if len(oc) < 1:
        return ObjectContainer(
            header = unicode('Resultat'),
            message = unicode('Kunde ej hitta något för: ' + unicode(query))
        ) 
    
    return oc

####################################################################################################
@route(PREFIX + '/mostrecent')
def MostRecent(title):
    oc = ObjectContainer(title2 = unicode(title))
    
    for page in range(0, MAX_PAGES_TO_SEARCH - 1):
        json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/videos/recent?appVersion=3.0.0&embed=package,show,season&limit=%s&platform=IPHONE&platformVersion=9.0.2&realm=DPLAYSE&site=SE&sort=sort_date_desc&video_type=episode,standalone,trailer,clip,follow-up&page=%s' % (API_ITEM_LIMIT, page))
            
        for item in json_data['data']:
            episode_object = CreateEpisodeObject(item)
            
            if episode_object:
                oc.add(episode_object)
                
            if len(oc) >= MOST_RECENT_ITEMS:
                return oc
       
    return oc 

####################################################################################################
@route(PREFIX + '/mostpopular')
def MostPopular(title):
    oc = ObjectContainer(title2 = unicode(title))
       
    for page in range(0, MAX_PAGES_TO_SEARCH - 1):
        json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/shows/popular?appVersion=3.0.0&embed=package,show&limit=%s&platform=IPHONE&platformVersion=9.0.2&realm=DPLAYSE&site=SE&page=%s' % (API_ITEM_LIMIT, page))
            
        for item in json_data['data']:
            tvshow_object = CreateTVShowObject(item)
            
            if tvshow_object:
                oc.add(tvshow_object)
            
        if len(oc) >= MOST_POPULAR_ITEMS:
            break
       
    return oc  

####################################################################################################
@route(PREFIX + '/recommended')
def Recommended(title):
    oc = ObjectContainer(title2 = unicode(title))

    json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/shows/recommended?appVersion=3.0.0&embed=reference&platform=IPHONE&platformVersion=9.0.2&realm=DPLAYSE&site=SE')
        
    for recommended_item in json_data['data']:
        item = recommended_item['reference']
        tvshow_object = CreateTVShowObject(item)
        
        if tvshow_object:
            oc.add(tvshow_object)
       
    return oc  

####################################################################################################
@route(PREFIX + '/allshows')
def AllShows(title):
    oc = ObjectContainer(title2 = unicode(title))

    json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/shows?appVersion=3.0.0&embed=genres%2Chome_channel%2Cpackage&limit=1337&page=0&platform=IPHONE&platformVersion=9.0.2&realm=DPLAYSE&site=SE')
        
    for item in json_data['data']:
        tvshow_object = CreateTVShowObject(item)
        
        if tvshow_object:
            oc.add(tvshow_object)
    
    oc.objects.sort(key = lambda obj: obj.title)
    
    return oc

####################################################################################################
@route(PREFIX + '/seasons')
def Seasons(title, id, thumb, art):
    show = unicode(title)
    oc = ObjectContainer(title2 = show)
    
    json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/shows/%s/seasons?appVersion=3.0.0&platform=IPHONE&platformVersion=9.0.2&realm=DPLAYSE&site=SE' % id)
    
    for item in json_data['data']:
        if not item['type'] == 'season':
            continue
            
        if item['episodes_available'] < 1:
            continue
        
        summary = item['description']
        season_id = str(item['id'])
        episode_count = item['episodes_available']
        index = item['season_number']
        title = unicode('Säsong %s' % index)
        
        oc.add(
            SeasonObject(
                key = Callback(Episodes, title = title, season = str(index), season_id = season_id, show_id = id, thumb = thumb, art = thumb),
                rating_key = id,
                title = title,
                summary = summary,
                show = show,
                episode_count = episode_count,
                thumb = thumb,
                art = thumb,
                index = index
            )
        )
    
    oc.objects.sort(key = lambda obj: obj.index, reverse = True)    
    
    return oc

####################################################################################################
@route(PREFIX + '/episodes')
def Episodes(title, season, season_id, show_id, thumb, art):
    
    oc = ObjectContainer(title2 = unicode(title))
    
    json_data = JSON.ObjectFromURL('http://www.dplay.se/api/v2/content/device/shows/%s/videos?appVersion=3.0.0&embed=package,show&limit=1337&platform=IPHONE&platformVersion=9.0.2&realm=DPLAYSE&site=SE&page=%s' % (show_id, 0))
        
    for item in json_data['data']:
        try:
            if not (str(item['season']['id']) == season_id):
                continue
        except:
            continue
            
        episode_object = CreateEpisodeObject(item)
        
        if episode_object:
            oc.add(episode_object)
    
    if len(oc) < 1:
        return ObjectContainer(
            header = 'Inga program funna',
            message = unicode('Det kan t.ex. bero på rättighetsskäl (DRM)')
        )
    
    return oc 

####################################################################################################
def CreateTVShowObject(item):

    if not item['type'] == 'show':
        return None

    # Skip show requiring premium subscription
    try:
        if 'name' in item['package'][0]:
            if item['package'][0]['name'] == 'Premium':
                return None
        else:
            if item['package'][0]['id'] == PREMIUM_ID:
                return None
    except:
        pass
    
    try:
        title = unicode(item['title'])
        id = str(item['id'])
    except:
        return None
        
    summary = unicode(item['description']) if 'description' in item else None
    
    try: thumb = IMAGE_BASE_URL % item['poster_image']['file']
    except: thumb = none
    
    try: tags = [item['tagline']]
    except: tags = none
    
    try: episode_count = int(item['episodes_available'])
    except: episode_count = None
    
    return TVShowObject(
        key = Callback(Seasons, title = title, id = id, thumb = thumb, art = thumb),
        rating_key = id,
        title = title,
        summary = summary,
        thumb = thumb,
        art = thumb,
        tags = tags,
        episode_count = episode_count
    )

####################################################################################################
def CreateEpisodeObject(item):
    # Skip non video content
    try:
        if not item['type'] == 'video':
            return None
    except:
        pass
    
    # Skip videos with DRM
    try:
        if item['rights']['drm']:
            return None
    except:
        pass
        
    # Skip videos requiring premium subscription
    try:
        if 'name' in item['package'][0]:
            if item['package'][0]['name'] == 'Premium':
                return None
        else:
            if item['package'][0]['id'] == 42:  # 42 = Premium
                return None
    except:
        pass
    
    try:
        url = URL_TEMPLATE % item['id']
        title = unicode(item['title'])
    except:
        return None
    
    summary = unicode(item['description']) if 'description' in item else None
    
    try: thumb = IMAGE_BASE_URL % item['thumbnail_image']['file']
    except: thumb = None
    
    try: originally_available_at = Datetime.ParseDate(item['available_from'].split('T')[0]).date()
    except: originally_available_at = None
    
    try: art = IMAGE_BASE_URL % item['show']['poster_image']['file']
    except: art = None
    
    try: show = unicode(item['show']['title'])
    except: show = None
    
    try: index = int(item['episode_number'])
    except: index = None
    
    try: season = int(item['season']['season_number'])
    except: season = None
    
    try: duration = int(item['duration'])
    except: duration = None
    
    return EpisodeObject(
        url = URL_TEMPLATE % item['id'],
        title = title,
        summary = summary,
        thumb = thumb,
        originally_available_at = originally_available_at,
        art = art,
        show = show,
        index = index,
        season = season,
        duration = duration
    )