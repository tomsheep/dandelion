# -*- coding: utf-8 -*-
import web


class CookieStore(web.session.Store):
    """Store for saving session using cookie.

    TODO: Put your code here

    """
    def __init__(self, cookie_name):
        pass

    def __contains__(self, key):
        pass

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def _setcookie(self, value, expires='', **kw):
        pass

    def __delitem__(self, key):
        pass

    def cleanup(self, timeout):
        pass
