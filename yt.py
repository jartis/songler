import requests
import json
import re
from html import unescape
 
def get_yt_song_and_artist(youtube_url):
    song_name = None
    artist_name = None
 
    r = requests.get(youtube_url)
 
    raw_matches = re.findall('(\{"metadataRowRenderer":.*?\})(?=,{"metadataRowRenderer")', r.text)
    json_objects = [json.loads(m) for m in raw_matches if '{"simpleText":"Song"}' in m or '{"simpleText":"Artist"}' in m] # [Song Data, Artist Data]
 
    if len(json_objects) == 2:
        song_contents = json_objects[0]["metadataRowRenderer"]["contents"][0]
        artist_contents = json_objects[1]["metadataRowRenderer"]["contents"][0]
 
        if "runs" in song_contents:
            song_name = song_contents["runs"][0]["text"]
        else:
            song_name = song_contents["simpleText"]
            
        if "runs" in artist_contents:
            artist_name = artist_contents["runs"][0]["text"]
        else:
            artist_name = artist_contents["simpleText"]

    if (song_name is None and artist_name is None):
        raw_matches = re.findall('<title>(.*)</title>', r.text)
        vidname = unescape(requests.utils.unquote(raw_matches[0]))
        if (vidname.endswith(' - YouTube')):
            vidname = vidname[:-10]
        parts = vidname.split(' - ')
        if (len(parts) > 1):
            song_name = parts[1]
            artist_name = parts[0]
        else:
            song_name = parts[0]

    return song_name, artist_name
