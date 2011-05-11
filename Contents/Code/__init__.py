VIDEO_PREFIX = "/video/kanal5play"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.jpg'
ICON          = 'icon-default.png'

#URLs to xml/player
START_URL = "http://www.kanal5play.se"
STREAM_URL = "http://www.kanal5play.se/program/play/%s"

PROGRAM_API_URL	= "http://www.kanal5play.se/api/videos?videoType=PROGRAM&programTag=%s&page=0&itemsPerPage=100&sortKey=PUBLISH_DATE&ascending=false"
KLIPP_API_URL	= "http://www.kanal5play.se/api/videos?videoType=CLIP&programTag=%s&page=0&itemsPerPage=100&sortKey=PUBLISH_DATE&ascending=false"
LATEST_API_URL = "http://www.kanal5play.se/api/videos?videoType=%s&page=0&itemsPerPage=100&sortKey=PUBLISH_DATE&ascending=false"
PROGRAM_URL = "http://www.kanal5play.se/program"
PROGRAM_SIDA_URL = "http://www.kanal5play.se/program/%s"
SEARCH_API_URL = "http://www.kanal5play.se/api/videos/search/%s"

####################################################################################################

def Start():

    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    HTTP.CacheTime=3600*3


####################################################################################################

def UpdateCache():

	Log("Cache HTML")
	HTTP.PreCache(PROGRAM_URL)

	Log("Caching images")
	
	htmlPage = HTML.ElementFromURL(PROGRAM_URL, errors='ignore')
	menuItems = htmlPage.xpath('//div[@class="k5-AToZPanel-program-wrapper"]')

	for menuItem in menuItems:
		subpage_url = String.Quote(menuItem.xpath('./a')[0].get('href').encode("utf-8"), usePlus=False)
		replacements = {'/program/':''}
		for i, j in replacements.iteritems():
			show_id = subpage_url.replace(i, j)
			image_url = PROGRAM_SIDA_URL % show_id
			Log(image_url)
			HTTP.PreCache(image_url)


# see:
#  http://dev.plexapp.com/docs/Functions.html#CreatePrefs
#  http://dev.plexapp.com/docs/mod_Prefs.html#Prefs.Add
def CreatePrefs():
    Prefs.Add(id='username', type='text', default='', label='Your Username')
    Prefs.Add(id='password', type='text', default='', label='Your Password', option='hidden')

# see:
#  http://dev.plexapp.com/docs/Functions.html#ValidatePrefs
def ValidatePrefs():
    u = Prefs.Get('username')
    p = Prefs.Get('password')
    ## do some checks and return a
    ## message container
    if( u and p ):
        return MessageContainer(
            "Success",
            "User and password provided ok"
        )
    else:
        return MessageContainer(
            "Error",
            "You need to provide both a user and password"
        )

  


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def VideoMainMenu():
	
	# Preload html files not needed due to changes on website
    #Thread.Create(UpdateCache())
    #UpdateCache()
    
    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="InfoList")


    # see:
    #  http://dev.plexapp.com/docs/Objects.html#DirectoryItem
    #  http://dev.plexapp.com/docs/Objects.html#function-objects
    dir.Append(
        Function(
            DirectoryItem(
                ShowSubMenu,
                L('Shows'),
                summary=L('Program_summary'),
                thumb=R("ikon-tvprogram.png"),
                art=R(ART),
            ), section_type="Program"
        )
    )
    
    dir.Append(
        Function(
            DirectoryItem(
                ShowSubMenu,
                L('Clip'),
                summary=L('Klipp_summary'),
                thumb=R("ikon-klipp.png"),
                art=R(ART),
            ), section_type="Klipp"
        )
    )
    
    dir.Append(
        Function(
            DirectoryItem(
                LatestMenu,
                L('LatestShows'),
                summary=L('Program_summary'),
                thumb=R("ikon-senasteprogram.png"),
                art=R(ART),
            ), section_type="Program"
        )
    )
    
    dir.Append(
        Function(
            DirectoryItem(
                LatestMenu,
                L('LatestClips'),
                summary=L('Klipp_summary'),
                thumb=R("ikon-senasteklipp.png"),
                art=R(ART),
            ), section_type="Klipp"
        )
    )

      
    # Part of the "search" example 
    # see also:
    #   http://dev.plexapp.com/docs/Objects.html#InputDirectoryItem
    dir.Append(
        Function(
            InputDirectoryItem(
                SearchResults,
                L('Search'),
                L('Searchsubtitle'),
                summary=L('Search_summary'),
                thumb=R("ikon-sok.png"),
                art=R(ART)
            )
        )
    )

    # ... and then return the container
    return dir

def CallbackExample(sender):

    ## you might want to try making me return a MediaContainer
    ## containing a list of DirectoryItems to see what happens =)

    return MessageContainer(
        "Not implemented",
        "In real life, you'll make more than one callback,\nand you'll do something useful.\nsender.itemTitle=%s" % sender.itemTitle
    )

# Part of the "search" example 
# query will contain the string that the user entered
# see also:
#   http://dev.plexapp.com/docs/Objects.html#InputDirectoryItem
def SearchResults(sender,query=None,section_type="Search"):

	dir = MediaContainer(title2=L(section_type), viewGroup="InfoList")
	
	data_url = SEARCH_API_URL % String.Quote(query, usePlus=False)

	Log(data_url)

	result = JSON.ObjectFromURL(data_url, cacheTime=0)

#print result

#item = parser.items[-1]

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
    

####

def ShowSubMenu(sender, section_type):

	dir = MediaContainer(title2=L(sender.itemTitle), viewGroup="InfoList")
	
	Log("Program Sektion")
	Log("sender.itemName=%s" % section_type)
	htmlPage = HTML.ElementFromURL(PROGRAM_URL, errors='ignore')
        menuItems = htmlPage.xpath('//div[@class="k5-AToZPanel-program-wrapper"]')

        for menuItem in menuItems:
                title = menuItem.xpath('./a')[0].text.strip()
                summary = menuItem.xpath('./a')[0].get('title')
                Log(title)
                #subtitle = menuItem.xpath('./p')[0].text
                subpage_url = String.Quote(menuItem.xpath('./a')[0].get('href').encode("utf-8"), usePlus=False)
                replacements = {'/program/':'','/visa':''}
                for i, j in replacements.iteritems():
                	subpage_url = subpage_url.replace(i, j)
				
                Log(subpage_url)
                #
                if section_type == "Program":
                	dir.Append(Function(DirectoryItem(ProgramShowMenu,title,summary=summary,art=R(ART)), show_id=subpage_url))
                else:
                    dir.Append(Function(DirectoryItem(KlippShowMenu,title,summary=summary,art=R(ART)), show_id=subpage_url))
                #GetShowImage(subpage_url)
	
	
	if len(dir) == 0:
		return MessageContainer(L('No_Results'),L('No_video'))
	else:
		return dir
		
def ProgramShowMenu(sender, show_id):

	dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
	
	Log("Program Show Sektion")
	
	data_url = PROGRAM_API_URL % show_id
	Log(data_url)

	result = JSON.ObjectFromURL(data_url, cacheTime=0)
	

#print result

#item = parser.items[-1]

	for program in result["items"]:
		name = ""
		subtitle = ""
		thumb=R(ICON)
		summary = ""
		url = ""
		duration = ""
		title = ""
		
		try:
			title = program["name"]
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
		#print program["shownOnTVDate"]
		#print 
		#subtitle = "Säsong %s, Avsnitt %s" % (str(program["season"]) + " ", str(program["episode"]))
		
		dir.Append(Function(WebVideoItem(PlayVideo, title=title, duration=duration, subtitle=subtitle, summary=summary, thumb=thumb), url=url, kind="Program"))
			#dir.Append(Function(WebVideoItem(PlayVideo, title=title, duration=program["length"], summary=program["shortDescription"], thumb=program["videoStillURL"], art=R(ART)), url=program["referenceId"]))
		
	
	if len(dir) == 0:
		return MessageContainer(L('No_Results'),L('No_Programs'))
	else:
		return dir

def KlippShowMenu(sender, show_id):

	dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
	
	Log("Klipp Show Sektion")
	
	data_url = KLIPP_API_URL % show_id
	Log(data_url)

	result = JSON.ObjectFromURL(data_url, cacheTime=0)

	for program in result["items"]:
		name = ""
		subtitle = ""
		thumb=R(ICON)
		summary = ""
		url = ""
		duration = ""
		title = ""
		
		try:
			title = program["name"]
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
		#print program["shownOnTVDate"]
		#print 
		#subtitle = "Säsong %s, Avsnitt %s" % (str(program["season"]) + " ", str(program["episode"]))
		
		dir.Append(Function(WebVideoItem(PlayVideo, title=title, duration=duration, subtitle=subtitle, summary=summary, thumb=thumb), url=url, kind="Klipp"))
			#dir.Append(Function(WebVideoItem(PlayVideo, title=title, duration=program["length"], summary=program["shortDescription"], thumb=program["videoStillURL"], art=R(ART)), url=program["referenceId"]))
		
	
	if len(dir) == 0:
		return MessageContainer(L('No_Results'),L('No_Clips'))
	else:
		return dir

def GetShowImage(show_id):
	
	image_url = PROGRAM_SIDA_URL % show_id
	src = HTML.ElementFromURL(image_url, errors='ignore').xpath('//div[@id="program-player-image"]/img')[0].get('src')
	image = START_URL + src
	
	Log(image)
	
	return image

def LatestMenu(sender, section_type):

	dir = MediaContainer(title2=L(section_type), viewGroup="InfoList")

	
	if section_type == "Klipp":
  		data_url = LATEST_API_URL % "CLIP"
  	else:
		data_url = LATEST_API_URL % "PROGRAM"
	
	
	
	Log(data_url)

	result = JSON.ObjectFromURL(data_url, cacheTime=0)

#print result

#item = parser.items[-1]

	for program in result["items"]:
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

def PlayVideo(sender, url, kind):
  Log('Hey, were in PlayVideo!')
  # Find the final video, and/or do some tracking/logging stuff here
  
  play_url = STREAM_URL % url
  
  Log(play_url)
  return Redirect(WebVideoItem(play_url))