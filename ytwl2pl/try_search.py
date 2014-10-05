import requests
import json

API_KEY = open("public_api_key", "r").read().strip()

search_term = raw_input("searching for: ")
search_term = requests.utils.quote(search_term)

url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q='+search_term+'&key='+API_KEY

response = requests.get(url)

videos = json.loads(response.text)

result = []

for video in videos['items']:
    if video['id']['kind'] == 'youtube#video':
        result.append(video['snippet']['title'] +
                        '\nhttp://youtube.com/watch?v='+video['id']['videoId'])

result.sort()

print('\nresults:\n')

for item in result:
    print(item+'\n')
