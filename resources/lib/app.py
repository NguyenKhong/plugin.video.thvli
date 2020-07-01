# -*- coding: utf-8 -*-
# Module: app
# Author: Zero-0
# Created on: 29/06/2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys, os
import math
from urllib import urlencode, quote
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmc
import HttpRequest


_BASE_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])
http = HttpRequest.Http()

def try_get(src, getter, expected_type=None):
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v
    return None

def buildUrl(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_BASE_URL, urlencode(kwargs))

def parseHomeMenu():
    result = http.get("https://api.thvli.vn/backend/cm/menu/e3f56e40-94b0-4e1f-9830-7c7f0d1bd354/").json()
    return list(result)

def showHomeMenu():
    xbmcplugin.setPluginCategory(_HANDLE, "web")
    xbmcplugin.setContent(_HANDLE, "videos")

    url = buildUrl(action="search")
    xbmcplugin.addDirectoryItem(_HANDLE, url, xbmcgui.ListItem(label="[COLOR yellow][B] Tìm kiếm... [/B][/COLOR]"), True)

    for cat in parseHomeMenu():
        if u"trực tuyến" in cat["name"].lower(): continue
        items = xbmcgui.ListItem(label=cat["name"])
        url = buildUrl(action = "page", slug = cat["slug"])
        xbmcplugin.addDirectoryItem(_HANDLE, url, items, True)
    xbmcplugin.endOfDirectory(_HANDLE, cacheToDisc=True)

def getListRibbon(slug):
    obj = http.get("https://api.thvli.vn/backend/cm/page/%s/?platform=web" % slug).json()
    return obj.get("ribbons", [])

def listPage(slug):
    xbmcplugin.setPluginCategory(_HANDLE, "page")
    xbmcplugin.setContent(_HANDLE, "movies")
    for page in getListRibbon(slug):
        items = xbmcgui.ListItem(label=page["name"])
        thumb_src = page["items"][0]["images"]["thumbnail"]
        items.setArt({"thumb": thumb_src, "fanart": thumb_src})
        url = buildUrl(action="ribbon_detail", id = page["id"])
        xbmcplugin.addDirectoryItem(_HANDLE, url, items, True)
    xbmcplugin.endOfDirectory(_HANDLE, cacheToDisc=True)

def RibbonDetail(id):
    obj = http.get("https://api.thvli.vn/backend/cm/ribbon/%s/?page=0" % id).json()
    for item in  obj["items"]:
        yield item
    limit = try_get(obj, lambda x: x["metadata"]["limit"])
    total = try_get(obj, lambda x: x["metadata"]["total"])
    if limit and total:
        num_pages = int(math.ceil(float(total)/float(limit)))
        for num_page in range(1, num_pages):
            obj = http.get("https://api.thvli.vn/backend/cm/ribbon/%s/?page=%d" % (id, num_page)).json()
            for item in obj["items"]:
                yield item
    return 

def showRibbon(id):
    xbmcplugin.setPluginCategory(_HANDLE, "Ribbon")
    xbmcplugin.setContent(_HANDLE, "movies")
    for i in RibbonDetail(id):
        items = xbmcgui.ListItem(label=i["title"])
        thumb_src = i["images"]["thumbnail"]
        items.setArt({"thumb": thumb_src,
                    "fanart": thumb_src
            })
        if i["type"] == 1:
            items.setProperty("IsPlayable", "true")
            items.setInfo("video", {"title": i["title"]})
            url = buildUrl(action="play", id = i["id"], title=i["title"].encode("utf-8"))
            xbmcplugin.addDirectoryItem(_HANDLE, url, items, False)
        else:
            url = buildUrl(action="listVideos", slug = i["slug"])
            xbmcplugin.addDirectoryItem(_HANDLE, url, items, True)
    # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE, cacheToDisc=True)

def getDetail(slug):
    obj = http.get("https://api.thvli.vn/backend/cm/detail/%s/" % slug).json()
    return obj

def getEpisodes(id):
    obj = http.get("https://api.thvli.vn/backend/cm/season_by_id/%s/" % id).json()
    return obj.get("episodes", [])

def listMovies(slug):
    details = getDetail(slug)
    seasons = details.get("seasons", None)
    if not seasons:
        return
    xbmcplugin.setPluginCategory(_HANDLE, "detail")
    xbmcplugin.setContent(_HANDLE, "movies")
    ids = [season["id"] for season in seasons]
    for id in ids:
        for episode in getEpisodes(id):
            items = xbmcgui.ListItem(label=episode["title"])
            items.setInfo("video", {"title": episode["title"]})
            thumb_src = episode["images"]["thumbnail"]
            items.setArt({"thumb": thumb_src,
                        "fanart": thumb_src
                })
            items.setProperty("IsPlayable", "true")
            url = buildUrl(action="play", id = episode["id"],  title = episode["title"].encode("utf-8"))
            xbmcplugin.addDirectoryItem(_HANDLE, url, items, False)

    # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE, cacheToDisc=True)

def play(id, title):
    # web_pdb.set_trace()
    r = http.get("https://api.thvli.vn/backend/cm/detail/%s/" % id)
    result = r.json()
    link = result["play_info"]["data"]["hls_link_play"]
    play_item = xbmcgui.ListItem()
    play_item.setInfo('video', {'title': title})
    play_item.setPath(link)
    play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent=%s' % HttpRequest.USER_AGENT)
    play_item.setContentLookup(False)
    play_item.setProperty('IsPlayable', 'true')

    xbmcplugin.setResolvedUrl(_HANDLE, True, play_item)

def fecthSearchItems(text):
    url_template = "https://api.thvli.vn/backend/cm/search/%s/?page=%d&limit=20"
    obj = http.get(url_template % (text, 0)).json()
    for item in  obj["items"]:
        yield item
    limit = try_get(obj, lambda x: x["metadata"]["limit"])
    total = try_get(obj, lambda x: x["metadata"]["total"])
    if limit and total:
        num_pages = int(math.ceil(float(total)/float(limit)))
        for num_page in range(1, num_pages):
            obj = http.get(url_template % (text, num_page)).json()
            for item in obj["items"]:
                yield item
            # items.append(obj["items"])
    return 

def doSearch():
    xbmcplugin.setPluginCategory(_HANDLE, "Search result")
    xbmcplugin.setContent(_HANDLE, "movies")
    keyboard = xbmc.Keyboard("", "Tiềm kiếm")
    keyboard.doModal()
    text = ""
    if keyboard.isConfirmed():
        text = keyboard.getText()
    if not text: return
    
    xbmcplugin.setPluginCategory(_HANDLE, "Ribbon")
    xbmcplugin.setContent(_HANDLE, "movies")
    for item in fecthSearchItems(quote(text)):
        list_items = xbmcgui.ListItem(label=item["title"])
        thumb_src = item["images"]["thumbnail"]
        list_items.setArt({"thumb": thumb_src,
                    "fanart": thumb_src
            })
        if item["type"] == 1:
            list_items.setProperty("IsPlayable", "true")
            list_items.setInfo("video", {"title": item["title"]})
            url = buildUrl(action="play", id = item["id"], title=item["title"].encode("utf-8"))
            xbmcplugin.addDirectoryItem(_HANDLE, url, list_items, False)
        else:
            url = buildUrl(action="listVideos", slug = item["slug"])
            xbmcplugin.addDirectoryItem(_HANDLE, url, list_items, True)
    # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_HANDLE, cacheToDisc=True)
    
def router():

    args = dict(parse_qsl(sys.argv[2][1:]))
    if not args: 
        showHomeMenu()
        return
    if args["action"] == "page":
        listPage(args["slug"])
    elif args["action"] == "ribbon_detail":
        showRibbon(args["id"])
    elif args["action"] == "listVideos":
        listMovies(args["slug"])
    elif args["action"] == "play":
        play(args["id"], args["title"])
    elif args["action"] == "search":
        doSearch()
    else:
        raise ValueError('Invalid paramstring: {0}!'.format(args))

if __name__ == '__main__':
    router()
