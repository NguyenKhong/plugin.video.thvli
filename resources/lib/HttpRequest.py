# -*- coding: utf-8 -*-
# Module: HttpRequest
# Author: Zero-0
# Created on: 29/06/2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from requests import Session

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/59.0.3071.115 Safari/537.36"
)

HOST = "https://www.thvli.vn"

class Http(Session):
    """docstring for http"""
    def __init__(self, *args, **kwargs):
        super(Http, self).__init__(*args, **kwargs)
        
        headers = kwargs.pop("headers", 
                                {"User-Agent": USER_AGENT,
                                "Referer": HOST + "/",
                                "Origin": HOST      
                                }
                            )
        self.headers.update(headers)
        self.timeout = 60

    def request(self, method, url, *args, **kwargs):
        kwargs["timeout"] = kwargs.pop("timeout", self.timeout)
        kwargs["verify"] = False
        r = Session.request(self, method, url, *args, **kwargs)
        if r.status_code >= 300:
            r.raise_for_status()
        return r