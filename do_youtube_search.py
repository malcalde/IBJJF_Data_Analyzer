#!/usr/bin/python
import ConfigParser
import dateutil.parser

from sets import Set

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

config = ConfigParser.RawConfigParser()
config.read('my_ibjjf_data_analyzer.cfg')

YOUTUBE_API_KEY = config.get('GOOGLE','YOUTUBE_APP_KEY')
YOUTUBE_KEYWORDS = config.get('GOOGLE','YOUTUBE_KEYWORD').split('#')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = None
def doYoutubeSearch(query, maxresults=10):
  global youtube
  
  if youtube is None:  
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    part="id,snippet",
    order="date",
    maxResults=maxresults
  ).execute()

  videos = []
  channels = []
  playlists = []

  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video" and isUsefulMedia(search_result):
        published = dateutil.parser.parse(search_result["snippet"]["publishedAt"])
        videos.append(["{%s} %s"%(published.strftime("%d/%b/%Y"), search_result["snippet"]["title"]),search_result["id"]["videoId"]])
  return videos

def isUsefulMedia(media):
    title = media["snippet"]["title"].lower()
    description = media["snippet"]["description"].lower()
    
    rst = False
    for keyword in YOUTUBE_KEYWORDS:
        rst = rst or (-1 != title.find(keyword)) or (-1 != description.find(keyword))
    
    #if (False == rst): print "[DESCARTADO]Video %s (%s)"%(title.encode('ascii', 'ignore'), description.encode('ascii', 'ignore'))
    
    return rst
