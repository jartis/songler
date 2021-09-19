import requests
import json
import re
from html import unescape


def getVideoId(link):
    """
    Takes a youtube link and returns the trimmed video ID.
    <link>: The youtube link to parse.
    """
    if (link == ''):
        return ''
    query = urlparse(link)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urlparse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return ''

def getYTArtistTitle(yturl):
    """
    Returns *SOME* {artist, title} object for any YouTube video link.
    <yturl> - the URL for the youtube video to scan
    NOTE: Since this isn't based on an API, it will probably break at some point.
    """
    title = None
    artist = None
    r = requests.get(yturl)
    raw_matches = re.findall(
        '(\{"metadataRowRenderer":.*?\})(?=,{"metadataRowRenderer")', r.text)
    # [Song Data, Artist Data]
    json_objects = [json.loads(
        m) for m in raw_matches if '{"simpleText":"Song"}' in m or '{"simpleText":"Artist"}' in m]
    if len(json_objects) == 2:
        song_contents = json_objects[0]["metadataRowRenderer"]["contents"][0]
        artist_contents = json_objects[1]["metadataRowRenderer"]["contents"][0]
        if "runs" in song_contents:
            title = song_contents["runs"][0]["text"]
        else:
            title = song_contents["simpleText"]
        if "runs" in artist_contents:
            artist = artist_contents["runs"][0]["text"]
        else:
            artist = artist_contents["simpleText"]
    if (title is None and artist is None):
        raw_matches = re.findall('<title>(.*)</title>', r.text)
        vidname = unescape(requests.utils.unquote(raw_matches[0]))
        vidname = re.sub(r'(^\([0-9]*\)\s)', '', vidname)
        if (vidname.endswith(' - YouTube')):
            vidname = vidname[:-10]
        parts = vidname.split(' - ')
        if (len(parts) > 1):
            title = parts[1]
            artist = parts[0]
        else:
            title = parts[0]
    return {'title': title, 'artist': artist}
