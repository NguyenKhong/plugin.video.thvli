# -*- coding: utf-8 -*-
# Module: HttpRequest
# Author: Zero-0
# Created on: 29/06/2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from requests import Session
import time
from hashlib import md5

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"

HOST = "https://www.thvli.vn"
API = "https://api.thvli.vn/backend/cm"
REACT_APP_ACCESS_KEY_DATE = "Kh0ngDuLieu"
REACT_APP_ACCESS_KEY_TIME = "C0R0i"
REACT_APP_ACCESS_KEY_SECRET = "Kh0aAnT0an"
TIME_DIFF = 26

class Http(Session):
    """docstring for http"""
    def __init__(self, *args, **kwargs):
        headers = kwargs.pop("headers", 
            {
                "User-Agent": USER_AGENT,
                "Referer": HOST + "/",
                "Origin": HOST,
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Accept": "application/json, text/plain, */*",
                "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                "sec-ch-ua-mobile": "?0"      
            }
        )
        Session.__init__(self, *args, **kwargs)
        self.headers.update(headers)
        self.timeout = 60

    def request(self, method, url, *args, **kwargs):
        kwargs["timeout"] = kwargs.pop("timeout", self.timeout)
        kwargs["verify"] = False
        retry_backoff = kwargs.pop("retry_backoff", 0.3)
        retry_max_backoff = kwargs.pop("retry_max_backoff", 10.0)
        total_retries = kwargs.pop("retries", 0)
        current_time = time.localtime(time.time() - TIME_DIFF)
        date_v = time.strftime("%Y%m%d", current_time)
        time_v = time.strftime("%H%M%S", current_time)
        md5_v = md5(date_v + time_v).hexdigest()
        key_v = md5_v[0:3] + md5_v[len(md5_v)-3:]
        key_access = REACT_APP_ACCESS_KEY_DATE + date_v + REACT_APP_ACCESS_KEY_TIME + time_v + REACT_APP_ACCESS_KEY_SECRET + key_v 
        headers = kwargs.pop("headers", {})
        headers.update({
                "X-SFD-Key": md5(key_access).hexdigest(),
                "X-SFD-Date": date_v + time_v
            })
        kwargs["headers"] = headers
        if not url.startswith("http"):
            url = API + url
        r = None
        retries = 0
        while True:
            try:
                r = Session.request(self, method, url, *args, **kwargs)
                if r.status_code >= 300:
                    r.raise_for_status()
                return r
            except Exception as err:
                retries += 1
                if retries >= total_retries:
                    raise Exception("Unable to open URL: %s with error: %s" % (url, err))
                delay = min(retry_max_backoff, retry_backoff * (2 ** (retries - 1)))
                time.sleep(delay)
        return r