#!/usr/bin/python

import httplib2
# import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from operator  import itemgetter

CLIENT_SECRETS_FILE = "client_secrets.json"
STORAGE = "%s-oauth2.json"

# This OAuth 2.0 access scope allows for full read/write access to the authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_youtube():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                  message="WARNING: Please configure OAuth 2.0",
                                  scope=YOUTUBE_READ_WRITE_SCOPE)
  storage = Storage(STORAGE % sys.argv[0])
  credentials = storage.get()
  http = httplib2.Http()

  if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)
  else:
    credentials.refresh(http)

  http = credentials.authorize(httplib2.Http())
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=http)
  return youtube

def get_watch_later_playlist_id(youtube):
  channels_list_response = youtube.channels().list(
    part="contentDetails",
    mine=True
    ).execute()
  watchLaterId = channels_list_response["items"][0]["contentDetails"]["relatedPlaylists"]["watchLater"]
  print("the WatchLater playlist ID is: "+watchLaterId)
  return watchLaterId

def get_playlist_videos_list(youtube, playlistId):
  """
  returns a list of (videoId, title) tuples of all the videos in given playlist
  """
  result = []
  playlist_items_list_response = youtube.playlistItems().list(
    part="snippet,contentDetails",
    maxResults=50,
    playlistId=playlistId #"WLOe0Uyi5SHmTe8BvXO_HRvw"
    ).execute()

  for video in playlist_items_list_response["items"]:
    _video = (video["contentDetails"]["videoId"], video["snippet"]["title"])
    result.append(_video)
  nextPageToken = playlist_items_list_response.get("nextPageToken", False)
  while (nextPageToken):
    playlist_items_list_response = youtube.playlistItems().list(
    part="snippet,contentDetails",
    maxResults=50,
    playlistId=playlistId,
    pageToken=nextPageToken
    ).execute()
    for video in playlist_items_list_response["items"]:
      _video = (video["contentDetails"]["videoId"], video["snippet"]["title"])
      result.append(_video)
    nextPageToken = playlist_items_list_response.get("nextPageToken", False)

  return result

def create_playlist(youtube, title, description, status):
# This code creates a new, private playlist in the authorized user's channel.
  playlists_insert_response = youtube.playlists().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
        title=title,
        description=description
      ),
      status=dict(
        privacyStatus=status
      )
    )
  ).execute()
  newListId = playlists_insert_response["id"]
  print "New playlist id: %s" % newListId
  return newListId

def is_video_in_playist(youtube, playlistId, videoId):
  return videoId in [itemgetter(0)(video) for video in get_playlist_videos_list(youtube, playlistId)]

def add_video_to_playlist(youtube, playlistId, videoId):
  if is_video_in_playist(youtube, playlistId, videoId):
    print("'{}' is already in the list".format(videoId))
    return
  response = youtube.playlistItems().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
        playlistId=playlistId,
        resourceId=dict(
          videoId=videoId,
          kind="youtube#video"
        ),
        position=0
      )
    )
  ).execute()
  return response

def add_videos_to_playlist(youtube, playlistId, videoIds):
  for i, videoId in enumerate(videoIds):
    if is_video_in_playist(youtube, playlistId, videoId):
      print("{}: '{}' is already in the list".format(i, videoId))
      continue
    try:
      response = add_video_to_playlist(youtube, playlistId, videoId)
    except HttpError, ex:
      try:
        search_results = youtube.search().list(part="snippet", q="id={}".format(videoId)).execute()["items"]
        if not search_results:
          continue
        alter_id = search_results[0]["id"]["videoId"]
        print("{} was probably deleted, but found alternative: {}".format(videoId, alter_id))
        add_video_to_playlist(youtube, playlistId, alter_id)
      except HttpError, ex:
        print(ex)
        # raise
    if 'response' in locals() and response:
      print("{}: ".format(i)+response["snippet"]["title"]+"\twas added...")

def main():

  youtube = get_youtube()

  playlistId = get_watch_later_playlist_id(youtube)

  videos = get_playlist_videos_list(youtube, playlistId)
  print("retrieved a list of {} videos".format(len(videos)))

  newListId = create_playlist(youtube,
                              title="ToWatchLater",
                              description="A private playlist created with the YouTube API v3",
                              status="private")
  # newListId = "PLAErNLsU3tism8B6_8s8jnMTD4n3oKN3s"

  add_videos_to_playlist(youtube, newListId, [itemgetter(0)(video) for video in videos])

  raw_input("Press ENTER to finish.")

if __name__ == '__main__':
  main()
